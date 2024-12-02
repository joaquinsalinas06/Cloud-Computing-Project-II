import boto3
import csv
import os
import time
from loguru import logger

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
s3 = boto3.client('s3', region_name='us-east-1')
glue = boto3.client('glue', region_name='us-east-1')

tabla_dynamo = 'dev-t_post' 
nombre_bucket = 'f-l-t-1-2-3'  
archivo_csv = 'stage-test-post.csv'
glue_database = 'stage-test'  
glue_table_name = 'stage-test-post'

nombre_contenedor = os.getenv("CONTAINER_NAME", "contenedor_default")
log_directory = "/mnt/logs"  # Directorio compartido para logs
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

def exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv):
    logger.info(f"Exportando datos desde DynamoDB ({tabla_dynamo}) a {archivo_csv}...")
    tabla = dynamodb.Table(tabla_dynamo)
    scan_kwargs = {}  # Initial scan parameters

    with open(archivo_csv, 'w', newline='') as archivo:
        escritor_csv = csv.writer(archivo)
        
        # Write the header row (optional)
        escritor_csv.writerow([
            'provider_id', 'post_id', 'album_id', 'song_id', 'user_id', 'created_at', 'description'
        ])

        item_count = 0  # Counter to track number of processed items
        iteration = 0   # Track loop iterations for logging/debugging
        
        while True:
            iteration += 1
            try:
                respuesta = tabla.scan(**scan_kwargs)
            except Exception as e:
                logger.error(f"Error al escanear DynamoDB: {e}")
                break
            
            items = respuesta.get('Items', [])
            logger.info(f"Iteración {iteration}: Escaneados {len(items)} elementos.")
            
            # Write items to CSV
            for item in items:
                try:
                    post_id = int(item.get('post_id', 0))
                except ValueError:
                    post_id = 0
                
                try:
                    album_id = int(item.get('album_id', 0))
                except ValueError:
                    album_id = 0
                
                try:
                    song_id = int(item.get('song_id', 0))
                except ValueError:
                    song_id = 0
                
                try:
                    user_id = int(item.get('user_id', 0))
                except ValueError:
                    user_id = 0
                
                row = [
                    item.get('provider_id', ''),
                    post_id,
                    album_id,
                    song_id,
                    user_id,
                    item.get('created_at', ''),
                    item.get('description', '')
                ]
                escritor_csv.writerow(row)
                item_count += 1

            # Break if no LastEvaluatedKey (end of scan)
            if 'LastEvaluatedKey' in respuesta:
                scan_kwargs['ExclusiveStartKey'] = respuesta['LastEvaluatedKey']
            else:
                logger.info(f"No hay más datos para escanear. Proceso completado con {item_count} elementos exportados.")
                break

            # Additional safeguard: stop if no new items are found
            if len(items) == 0:
                logger.warning("No se encontraron elementos nuevos en esta iteración. Saliendo del bucle.")
                break

    logger.info(f"Exportación completada con éxito: {item_count} registros escritos en {archivo_csv}.")

def subir_csv_a_s3(archivo_csv, nombre_bucket):
    carpeta_destino = 'posts/'  
    archivo_s3 = f"{carpeta_destino}{archivo_csv}" 
    logger.info(f"Subiendo {archivo_csv} al bucket S3 ({nombre_bucket}) en la carpeta 'posts'...")
    
    try:
        s3.upload_file(archivo_csv, nombre_bucket, archivo_s3)
        logger.info(f"Archivo subido exitosamente a S3 en la carpeta 'posts'.")
        return True
    except Exception as e:
        logger.error(f"Error al subir el archivo a S3: {e}")
        return False

def crear_base_de_datos_en_glue(glue_database):
    try:
        glue.get_database(Name=glue_database)  
        logger.info(f"La base de datos {glue_database} ya existe.")
    except glue.exceptions.EntityNotFoundException:
        logger.info(f"La base de datos {glue_database} no existe. Creando base de datos...")
        glue.create_database(
            DatabaseInput={
                'Name': glue_database,
                'Description': 'Base de datos para almacenamiento de posts en Glue.'
            }
        )
        logger.info(f"Base de datos {glue_database} creada exitosamente.")
    except Exception as e:
        logger.error(f"Error al verificar o crear la base de datos en Glue: {e}")
        return False
    return True

def registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv):
    logger.info(f"Registrando datos en Glue Data Catalog...")
    input_path = f"s3://{nombre_bucket}/posts/"
    
    try:
        glue.create_table(
            DatabaseName=glue_database,
            TableInput={
                'Name': glue_table_name,
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'provider_id', 'Type': 'string'},
                        {'Name': 'post_id', 'Type': 'bigint'},
                        {'Name': 'album_id', 'Type': 'bigint'},
                        {'Name': 'song_id', 'Type': 'bigint'},
                        {'Name': 'user_id', 'Type': 'bigint'},
                        {'Name': 'created_at', 'Type': 'string'},
                        {'Name': 'description', 'Type': 'string'},
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
        logger.info(f"Tabla {glue_table_name} registrada exitosamente en la base de datos {glue_database}.")
    except glue.exceptions.AlreadyExistsException:
        logger.info(f"La tabla {glue_table_name} ya existe en la base de datos {glue_database}.")
    except Exception as e:
        logger.error(f"Error al registrar la tabla en Glue: {e}")

if __name__ == "__main__":
    logger.info(f"Inicio del proceso en contenedor: {nombre_contenedor}")
    if crear_base_de_datos_en_glue(glue_database):
        exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv)
    
        if subir_csv_a_s3(archivo_csv, nombre_bucket):
            registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv)
        else:
            logger.error("No se pudo completar el proceso porque hubo un error al subir el archivo a S3.")
    else:
        logger.error("Error en la creación de la base de datos Glue. No se continuará con el proceso.")
    
    logger.info(f"Proceso completado en contenedor: {nombre_contenedor}")
