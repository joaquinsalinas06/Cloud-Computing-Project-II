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

tabla_dynamo = 'dev-t_song' 
nombre_bucket = 'f-l-t-1-2-3'  
archivo_csv = 'stage-test-song.csv'
glue_database = 'stage-test'  
glue_table_name = 'stage-test-song'

def exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv):
    logger.info(f"Exportando datos desde DynamoDB ({tabla_dynamo})...")
    tabla = dynamodb.Table(tabla_dynamo)
    scan_kwargs = {}
    
    with open(archivo_csv, 'w', newline='') as archivo:
        escritor_csv = csv.writer(archivo)  
        
        while True:
            respuesta = tabla.scan(**scan_kwargs)
            items = respuesta['Items']
            
            if not items:
                break
            
            for item in items:
                try:
                    song_id = int(item.get('song_id', 0))  
                except ValueError:
                    song_id = 0
                
                try:
                    album_id = int(item.get('album_id', 0))  
                except ValueError:
                    album_id = 0
                
                try:
                    times_played = int(item.get('times_played', 0))  
                except ValueError:
                    times_played = 0

                try:
                    artist_id = int(item.get('artist_id', 0))  
                except ValueError:
                    artist_id = 0

                row = [
                    item.get('provider_id', ''),
                    song_id,
                    album_id,
                    artist_id,
                    item.get('cover_image_url', ''),
                    item.get('duration', ''),
                    item.get('genre', ''),
                    item.get('preview_music_url', ''),
                    item.get('release_date', ''),
                    item.get('song_url',''),
                    times_played,
                    item.get('title','')  
                ]
                
                escritor_csv.writerow(row)
            
            if 'LastEvaluatedKey' in respuesta:
                scan_kwargs['ExclusiveStartKey'] = respuesta['LastEvaluatedKey']
            else:
                break
                
    logger.info(f"Datos exportados a {archivo_csv}")

def subir_csv_a_s3(archivo_csv, nombre_bucket):
    carpeta_destino = 'songs/'  
    archivo_s3 = f"{carpeta_destino}{archivo_csv}" 
    logger.info(f"Subiendo {archivo_csv} al bucket S3 ({nombre_bucket}) en la carpeta 'song'...")
    
    try:
        s3.upload_file(archivo_csv, nombre_bucket, archivo_s3)
        logger.info(f"Archivo subido exitosamente a S3 en la carpeta 'song'.")
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
    """Registrar datos en Glue Data Catalog."""
    logger.info(f"Registrando datos en Glue Data Catalog...")
    input_path = f"s3://{nombre_bucket}/songs/"
    
    try:
        glue.create_table(
            DatabaseName=glue_database,
            TableInput={
                'Name': glue_table_name,
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'provider_id', 'Type': 'string'},
                        {'Name': 'song_id', 'Type': 'bigint'},
                        {'Name': 'album_id', 'Type': 'bigint'},
                        {'Name': 'artist_id', 'Type': 'bigint'},
                        {'Name': 'cover_image_url', 'Type': 'string'},
                        {'Name': 'duration', 'Type': 'string'},
                        {'Name': 'genre', 'Type': 'string'},
                        {'Name': 'preview_music_url', 'Type': 'string'},
                        {'Name': 'release_date', 'Type': 'string'},
                        {'Name': 'song_url', 'Type': 'string'},
                        {'Name': 'times_played', 'Type': 'bigint'},
                        {'Name': 'title', 'Type': 'string'},
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
    if crear_base_de_datos_en_glue(glue_database):
        exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv)
    
        if subir_csv_a_s3(archivo_csv, nombre_bucket):
            registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv)
        else:
            logger.error("No se pudo completar el proceso porque hubo un error al subir el archivo a S3.")
    else:
        logger.error("Error en la creación de la base de datos Glue. No se continuará con el proceso.")
    
    logger.info("Proceso completado.")
