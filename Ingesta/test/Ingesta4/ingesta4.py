import boto3
import csv
import os
import time
from loguru import logger

# Variables de entorno o valores por defecto
nombre_contenedor = os.getenv("CONTAINER_NAME", "contenedor_default")
log_directory = "/mnt/logs"  # Directorio compartido para logs

# Configuración de logs
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = f"{log_directory}/{nombre_contenedor}.log"
logger.add(
    log_file,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {extra[container]} | {message}",
    level="INFO",
    rotation="10 MB",
    retention="7 days",
    serialize=False,
    enqueue=True,
)
logger = logger.bind(container=nombre_contenedor)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
s3 = boto3.client('s3', region_name='us-east-1')
glue = boto3.client('glue', region_name='us-east-1')

tabla_dynamo = 'dev-t_artist' 
nombre_bucket = 'f-l-t-1-2-3'  
archivo_csv = 'stage-test-artist.csv'
glue_database = 'stage-test'  
glue_table_name = 'stage-test-artist'

def exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv):
    """Exportar datos de DynamoDB a un archivo CSV."""
    logger.info(f"Exportando datos desde DynamoDB ({tabla_dynamo}) a {archivo_csv}...")
    try:
        tabla = dynamodb.Table(tabla_dynamo)
        scan_kwargs = {}

        with open(archivo_csv, 'w', newline='') as archivo:
            escritor_csv = csv.writer(archivo)
            escritor_csv.writerow(['provider_id', 'artist_id', 'birth_date', 'country', 
                                   'cover_image_url', 'genre', 'name', 'status'])

            while True:
                respuesta = tabla.scan(**scan_kwargs)
                items = respuesta.get('Items', [])

                if not items:
                    logger.info("No se encontraron más elementos en la tabla DynamoDB.")
                    break

                for item in items:
                    try:
                        artist_id = int(item.get('artist_id', 0))
                    except ValueError:
                        artist_id = 0
                        logger.warning("artist_id inválido, asignado como 0.")

                    row = [
                        item.get('provider_id', ''),
                        artist_id,
                        item.get('birth_date', ''),
                        item.get('country', ''),
                        item.get('cover_image_url', ''),
                        item.get('genre', ''),
                        item.get('name', ''),
                        item.get('status', '')
                    ]
                    escritor_csv.writerow(row)

                if 'LastEvaluatedKey' in respuesta:
                    scan_kwargs['ExclusiveStartKey'] = respuesta['LastEvaluatedKey']
                else:
                    break

        logger.info(f"Datos exportados correctamente a {archivo_csv}.")
    except Exception as e:
        logger.error(f"Error al exportar datos desde DynamoDB: {e}")

def subir_csv_a_s3(archivo_csv, nombre_bucket):
    """Subir archivo CSV a S3."""
    carpeta_destino = 'artist/'
    archivo_s3 = f"{carpeta_destino}{archivo_csv}"
    logger.info(f"Subiendo {archivo_csv} al bucket S3 ({nombre_bucket}) en la carpeta 'artist'...")

    try:
        s3.upload_file(archivo_csv, nombre_bucket, archivo_s3)
        logger.info("Archivo subido exitosamente a S3.")
        return True
    except Exception as e:
        logger.error(f"Error al subir el archivo a S3: {e}")
        return False

def crear_base_de_datos_en_glue(glue_database):
    """Crear base de datos en Glue si no existe."""
    try:
        glue.get_database(Name=glue_database)
        logger.info(f"La base de datos {glue_database} ya existe.")
    except glue.exceptions.EntityNotFoundException:
        logger.info(f"La base de datos {glue_database} no existe. Creando base de datos...")
        try:
            glue.create_database(
                DatabaseInput={
                    'Name': glue_database,
                    'Description': 'Base de datos para almacenamiento de datos de artistas en Glue.'
                }
            )
            logger.info(f"Base de datos {glue_database} creada exitosamente.")
        except Exception as e:
            logger.error(f"Error al crear la base de datos en Glue: {e}")
            return False
    except Exception as e:
        logger.error(f"Error verificando la base de datos en Glue: {e}")
        return False
    return True

def registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv):
    """Registrar datos en Glue Data Catalog."""
    logger.info(f"Registrando tabla {glue_table_name} en Glue Data Catalog...")
    input_path = f"s3://{nombre_bucket}/artist/"

    try:
        glue.create_table(
            DatabaseName=glue_database,
            TableInput={
                'Name': glue_table_name,
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'provider_id', 'Type': 'string'},
                        {'Name': 'artist_id', 'Type': 'bigint'},
                        {'Name': 'birth_date', 'Type': 'string'},
                        {'Name': 'country', 'Type': 'string'},
                        {'Name': 'cover_image_url', 'Type': 'string'},
                        {'Name': 'genre', 'Type': 'string'},
                        {'Name': 'name', 'Type': 'string'},
                        {'Name': 'status', 'Type': 'string'},
                    ],
                    'Location': input_path,
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'Compressed': False,
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
                        'Parameters': {'field.delim': ','}
                    }
                },
                'TableType': 'EXTERNAL_TABLE',
                'Parameters': {'classification': 'csv'}
            }
        )
        logger.info(f"Tabla {glue_table_name} registrada exitosamente en Glue.")
    except glue.exceptions.AlreadyExistsException:
        logger.info(f"La tabla {glue_table_name} ya existe en la base de datos {glue_database}.")
    except Exception as e:
        logger.error(f"Error al registrar la tabla en Glue: {e}")

if __name__ == "__main__":
    logger.info("Iniciando proceso completo...")
    
    if crear_base_de_datos_en_glue(glue_database):
        exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv)

        if subir_csv_a_s3(archivo_csv, nombre_bucket):
            registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv)
        else:
            logger.warning("Proceso interrumpido: Error al subir el archivo a S3.")
    else:
        logger.error("Proceso interrumpido: Error al crear la base de datos Glue.")

    logger.info("Proceso completado.")
