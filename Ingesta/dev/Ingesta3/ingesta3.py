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

<<<<<<< HEAD:Ingesta/Ingesta3/ingesta3.py
tabla_dynamo = 'dev-t_playlist'  
nombre_bucket = 'f-l-t-1-2-3'  
=======
tabla_dynamo = 'dev-t_playlist'  # Tabla que almacena playlists y posiblemente canciones
nombre_bucket = 'ingesta-stage-prod'  
>>>>>>> main:Ingesta/dev/Ingesta3/ingesta3.py
archivo_csv_playlist = 'stage-prod-playlist.csv'  
archivo_csv_playlist_song = 'stage-prod-playlist-song.csv'  
glue_database = 'stage-prod'  
glue_table_playlist = 'stage-prod-playlist'  
glue_table_playlist_song = 'stage-prod-playlist-song'  # Tabla en Glue para canciones relacionadas con las playlists

def exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv_playlist, archivo_csv_playlist_song):
<<<<<<< HEAD:Ingesta/Ingesta3/ingesta3.py
    logger.info(f"Iniciando exportación desde DynamoDB ({tabla_dynamo})...")
    try:
        tabla = dynamodb.Table(tabla_dynamo)
        scan_kwargs = {}

        playlists = []
        playlist_song_relations = []

        with open(archivo_csv_playlist, 'w', newline='') as archivo_playlist, open(archivo_csv_playlist_song, 'w', newline='') as archivo_playlist_song:
            escritor_csv_playlist = csv.writer(archivo_playlist)
            escritor_csv_playlist_song = csv.writer(archivo_playlist_song)

            escritor_csv_playlist.writerow(['provider_id', 'playlist_id', 'created_at', 'playlist_name', 'user_id'])
            escritor_csv_playlist_song.writerow(['playlist_id', 'song_id'])

            while True:
                respuesta = tabla.scan(**scan_kwargs)
                items = respuesta['Items']

                if not items:
                    logger.info("No se encontraron más elementos en DynamoDB.")
                    break

                for item in items:
                    try:
                        playlist_id = item.get('playlist_id', 0)
                        provider_id = item.get('provider_id', '')
                        created_at = item.get('created_at', '')
                        playlist_name = item.get('playlist_name', '')
                        user_id = item.get('user_id', 0)
                        song_ids = item.get('song_ids', [])

                        playlists.append([provider_id, playlist_id, created_at, playlist_name, user_id])

                        for song_id in song_ids:
                            playlist_song_relations.append([playlist_id, song_id])
                    except Exception as e:
                        logger.warning(f"Error procesando un elemento de DynamoDB: {e}")

                if 'LastEvaluatedKey' in respuesta:
                    scan_kwargs['ExclusiveStartKey'] = respuesta['LastEvaluatedKey']
                else:
                    break

            # Escribir en los archivos
            for playlist in playlists:
                escritor_csv_playlist.writerow(playlist)
            for relation in playlist_song_relations:
                escritor_csv_playlist_song.writerow(relation)

        logger.info(f"Datos exportados a {archivo_csv_playlist} y {archivo_csv_playlist_song}.")
    except Exception as e:
        logger.error(f"Error exportando datos desde DynamoDB: {e}")

def subir_csv_a_s3(archivo_csv_playlist, archivo_csv_playlist_song, nombre_bucket):
    carpeta_destino_playlist = 'playlists/'
=======
    print(f"Exportando datos desde DynamoDB ({tabla_dynamo})...")
    tabla = dynamodb.Table(tabla_dynamo)
    scan_kwargs = {}

    with open(archivo_csv_playlist, 'w', newline='') as archivo_playlist, open(archivo_csv_playlist_song, 'w', newline='') as archivo_playlist_song:
        escritor_csv_playlist = csv.writer(archivo_playlist)
        escritor_csv_playlist_song = csv.writer(archivo_playlist_song)

        while True:
            respuesta = tabla.scan(**scan_kwargs)
            items = respuesta['Items']

            if not items:
                break

            for item in items:
                try:
                    user_id = int(item.get('user_id', 0))
                except ValueError:
                    user_id = 0
                
                try:
                    playlist_id = int(item.get('playlist_id', 0))
                except ValueError:
                    playlist_id = 0

                row_playlist = [
                    item.get('provider_id', ''),
                    playlist_id,
                    user_id,
                    item.get('created_at', ''),
                    item.get('playlist_name', '')
                ]
                escritor_csv_playlist.writerow(row_playlist)


                if 'song_ids' in item: 
                    for song in item['song_ids']:
                        try:
                            song_id = int(song) 
                        except ValueError:
                            song_id = 0

                        provider_id = item.get('provider_id', '') 

                        row_playlist_song = [
                            playlist_id,
                            song_id,
                            provider_id
                        ]
                        escritor_csv_playlist_song.writerow(row_playlist_song)
                

            if 'LastEvaluatedKey' in respuesta:
                scan_kwargs['ExclusiveStartKey'] = respuesta['LastEvaluatedKey']
            else:
                break

    print(f"Datos exportados a {archivo_csv_playlist} y {archivo_csv_playlist_song}")

def subir_csv_a_s3(archivo_csv_playlist, archivo_csv_playlist_song, nombre_bucket):
    carpeta_destino_playlist = 'playlists/playlist/'  
>>>>>>> main:Ingesta/dev/Ingesta3/ingesta3.py
    carpeta_destino_playlist_song = 'playlists/songs/'

    archivo_s3_playlist = f"{carpeta_destino_playlist}{archivo_csv_playlist}"
    archivo_s3_playlist_song = f"{carpeta_destino_playlist_song}{archivo_csv_playlist_song}"

    try:
        logger.info(f"Subiendo {archivo_csv_playlist} a S3 en {archivo_s3_playlist}...")
        s3.upload_file(archivo_csv_playlist, nombre_bucket, archivo_s3_playlist)

        logger.info(f"Subiendo {archivo_csv_playlist_song} a S3 en {archivo_s3_playlist_song}...")
        s3.upload_file(archivo_csv_playlist_song, nombre_bucket, archivo_s3_playlist_song)

        logger.info("Archivos subidos exitosamente a S3.")
        return True
    except Exception as e:
        logger.error(f"Error al subir los archivos a S3: {e}")
        return False

def crear_base_de_datos_en_glue(glue_database):
    try:
        glue.get_database(Name=glue_database)
        logger.info(f"La base de datos {glue_database} ya existe.")
    except glue.exceptions.EntityNotFoundException:
        try:
            logger.info(f"La base de datos {glue_database} no existe. Creando base de datos...")
            glue.create_database(
                DatabaseInput={
                    'Name': glue_database,
                    'Description': 'Base de datos para almacenamiento de playlists y relaciones en Glue.'
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

def registrar_datos_en_glue(glue_database, glue_table_playlist, glue_table_playlist_song, nombre_bucket, archivo_csv_playlist, archivo_csv_playlist_song):
<<<<<<< HEAD:Ingesta/Ingesta3/ingesta3.py
    try:
        input_path_playlist = f"s3://{nombre_bucket}/playlists/"
        input_path_playlist_song = f"s3://{nombre_bucket}/playlists/songs/"
        logger.info(f"Registrando tablas en Glue para {glue_database}...")

=======
    """Registrar datos en Glue Data Catalog."""
    print(f"Registrando datos en Glue Data Catalog...")

    input_path_playlist = f"s3://{nombre_bucket}/playlists/playlist/"
    input_path_playlist_song = f"s3://{nombre_bucket}/playlists/songs/"

    try:
>>>>>>> main:Ingesta/dev/Ingesta3/ingesta3.py
        glue.create_table(
            DatabaseName=glue_database,
            TableInput={
                'Name': glue_table_playlist,
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'provider_id', 'Type': 'string'},
                        {'Name': 'playlist_id', 'Type': 'bigint'},
                        {'Name': 'user_id', 'Type': 'bigint'},
                        {'Name': 'created_at', 'Type': 'string'},
                        {'Name': 'playlist_name', 'Type': 'string'}
                    ],
                    'Location': input_path_playlist,
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
                        'Parameters': {'field.delim': ','}
                    }
                },
                'TableType': 'EXTERNAL_TABLE',
                'Parameters': {'classification': 'csv'}
            }
        )

        glue.create_table(
            DatabaseName=glue_database,
            TableInput={
                'Name': glue_table_playlist_song,
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'playlist_id', 'Type': 'bigint'},
                        {'Name': 'song_id', 'Type': 'bigint'},
                        {'Name': 'provider_id', 'Type': 'string'}
                    ],
                    'Location': input_path_playlist_song,
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
                        'Parameters': {'field.delim': ','}
                    }
                },
                'TableType': 'EXTERNAL_TABLE',
                'Parameters': {'classification': 'csv'}
            }
        )
<<<<<<< HEAD:Ingesta/Ingesta3/ingesta3.py

        logger.info(f"Tablas registradas exitosamente en {glue_database}.")
    except glue.exceptions.AlreadyExistsException:
        logger.info(f"La tabla {glue_table_playlist_song} ya existe en la base de datos {glue_database}.")
    except Exception as e:
        logger.error(f"Error al registrar las tablas en Glue: {e}")

=======
        print(f"Tablas {glue_table_playlist} y {glue_table_playlist_song} registradas exitosamente en la base de datos {glue_database}.")
    except Exception as e:
        print(f"Error al registrar las tablas en Glue: {e}")

>>>>>>> main:Ingesta/dev/Ingesta3/ingesta3.py
if __name__ == "__main__":
    logger.info("Iniciando proceso completo...")

    if crear_base_de_datos_en_glue(glue_database):
        exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv_playlist, archivo_csv_playlist_song)

        if subir_csv_a_s3(archivo_csv_playlist, archivo_csv_playlist_song, nombre_bucket):
            registrar_datos_en_glue(glue_database, glue_table_playlist, glue_table_playlist_song, nombre_bucket, archivo_csv_playlist, archivo_csv_playlist_song)
        else:
            logger.warning("Proceso interrumpido: Error al subir archivos a S3.")
    else:
        logger.error("Proceso interrumpido: Error al crear la base de datos Glue.")

    logger.info("Proceso completado.")
