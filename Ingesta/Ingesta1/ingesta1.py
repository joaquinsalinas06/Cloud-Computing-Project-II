import boto3
import csv
import os
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

# Clientes de AWS
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3')
glue = boto3.client('glue')

# Constantes
tabla_dynamo = 'dev-t_user'
nombre_bucket = 'f-l-t-1-2-3'  
archivo_csv = 'stage-prod-usuarios.csv'
glue_database = 'stage-prod'
glue_table_name = 'stage-prod-usuarios'

def exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv):
    try:
        logger.info(f"Iniciando exportación de {tabla_dynamo} a CSV.")
        tabla = dynamodb.Table(tabla_dynamo)
        scan_kwargs = {}
        
        with open(archivo_csv, 'w', newline='') as archivo:
            escritor_csv = None
            while True:
                respuesta = tabla.scan(**scan_kwargs)
                items = respuesta['Items']
                
                if not escritor_csv:
                    escritor_csv = csv.DictWriter(archivo, fieldnames=items[0].keys())
                    escritor_csv.writeheader()
                
                escritor_csv.writerows(items)

                if 'LastEvaluatedKey' in respuesta:
                    scan_kwargs['ExclusiveStartKey'] = respuesta['LastEvaluatedKey']
                else:
                    break
        
        logger.info(f"Exportación completada. Archivo generado: {archivo_csv}.")
    except Exception as e:
        logger.error(f"Error al exportar la tabla {tabla_dynamo} a CSV: {e}")
        raise

def subir_csv_a_s3(archivo_csv, nombre_bucket):
    carpeta_destino = 'usuarios/'
    archivo_s3 = f"{carpeta_destino}{archivo_csv}"
    logger.info(f"Iniciando subida de {archivo_csv} al bucket {nombre_bucket} en la carpeta 'usuarios'.")
    
    try:
        s3.upload_file(archivo_csv, nombre_bucket, archivo_s3)
        logger.info(f"Archivo subido exitosamente a S3: {archivo_s3}.")
        return True
    except s3.exceptions.NoSuchBucket:
        logger.error(f"El bucket S3 {nombre_bucket} no existe.")
        return False
    except Exception as e:
        logger.error(f"Error al subir el archivo {archivo_csv} a S3: {e}")
        return False

def registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv):
    logger.info(f"Registrando datos en Glue Data Catalog para la tabla {glue_table_name}.")
    input_path = f"s3://{nombre_bucket}/usuarios/{archivo_csv}"
    
    try:
        glue.create_table(
            DatabaseName=glue_database,
            TableInput={
                'Name': glue_table_name,
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'provider_id', 'Type': 'string'},
                        {'Name': 'user_id', 'Type': 'int'},
                        {'Name': 'email', 'Type': 'string'},
                        {'Name': 'username', 'Type': 'string'},
                        {'Name': 'password', 'Type': 'string'},
                        {'Name': 'name', 'Type': 'string'},
                        {'Name': 'last_name', 'Type': 'string'},
                        {'Name': 'phone_number', 'Type': 'string'},
                        {'Name': 'birth_date', 'Type': 'string'},
                        {'Name': 'gender', 'Type': 'string'},
                        {'Name': 'age', 'Type': 'int'},
                        {'Name': 'active', 'Type': 'string'},
                        {'Name': 'datecreated', 'Type': 'string'}
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
        logger.warning(f"La tabla {glue_table_name} ya existe en la base de datos Glue {glue_database}.")
    except Exception as e:
        logger.error(f"Error al registrar la tabla {glue_table_name} en Glue: {e}")

if __name__ == "__main__":
    logger.info("Iniciando proceso de ingesta de datos.")
    try:
        exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv)
        
        if subir_csv_a_s3(archivo_csv, nombre_bucket):
            registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv)
        else:
            logger.warning("El proceso no se pudo completar debido a errores durante la subida del archivo.")
    except Exception as e:
        logger.critical(f"Fallo crítico en el proceso de ingesta: {e}")
    finally:
        logger.info("Proceso de ingesta de datos completado.")
