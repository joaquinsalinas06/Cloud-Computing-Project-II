import boto3
import csv
import os
import time

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
s3 = boto3.client('s3', region_name='us-east-1')
glue = boto3.client('glue', region_name='us-east-1')

tabla_dynamo = 'dev-t_album' 
nombre_bucket = 'ingesta-stage-test'  
archivo_csv_album = 'stage-test-album.csv'
archivo_csv_song = 'stage-test-album-songs.csv'
glue_database = 'stage-test'  
glue_table_name_album = 'stage-test-album'
glue_table_name_song = 'stage-test-album-songs'

def exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv_album, archivo_csv_song):
    print(f"Exportando datos desde DynamoDB ({tabla_dynamo})...")
    tabla = dynamodb.Table(tabla_dynamo)
    scan_kwargs = {}
    
    album_rows = []  
    song_rows = []  
    
    while True:
        respuesta = tabla.scan(**scan_kwargs)
        items = respuesta['Items']
        
        if not items:
            break
        
        for item in items:
            try:
                album_id = int(item.get('album_id', 0))  
            except ValueError:
                album_id = 0
                
            try:
                songs_count = int(item.get('songs_count', 0))  
            except ValueError:
                songs_count = 0

            try:
                artist_id = int(item.get('artist_id', 0))  
            except ValueError:
                artist_id = 0

            song_ids = item.get('song_ids', [])
            if isinstance(song_ids, str):
                song_ids = song_ids.strip("{}").split(",")  
            song_ids = [int(id) for id in song_ids] 
            
            album_row = [
                item.get('provider_id', ''),
                album_id,
                artist_id,
                item.get('cover_image_url', ''),
                item.get('release_date', ''),
                songs_count,
                item.get('spotify_url', ''),
                item.get('title', '')
            ]
            album_rows.append(album_row)
            
            for song_id in song_ids:
                song_row = [
                    int(song_id),  
                    album_id,  
                    item.get('provider_id', ''),
                ]
                song_rows.append(song_row)
            
        if 'LastEvaluatedKey' in respuesta:
            scan_kwargs['ExclusiveStartKey'] = respuesta['LastEvaluatedKey']
        else:
            break
    
    with open(archivo_csv_album, 'w', newline='') as archivo:
        escritor_csv = csv.writer(archivo)  
        escritor_csv.writerows(album_rows)
    
    with open(archivo_csv_song, 'w', newline='') as archivo:
        escritor_csv = csv.writer(archivo)  
        escritor_csv.writerows(song_rows)
    
    print(f"Datos exportados a {archivo_csv_album} y {archivo_csv_song}")


          



def subir_csv_a_s3(archivo_csv_album, archivo_csv_song, nombre_bucket):
    carpeta_destino_album = 'album/albums/'  
    carpeta_destino_song = 'album/songs/'   
    
    archivo_s3_album = f"{carpeta_destino_album}{archivo_csv_album}" 
    archivo_s3_song = f"{carpeta_destino_song}{archivo_csv_song}"
    
    print(f"Subiendo {archivo_csv_album} a S3 en la carpeta 'album/albums'...")
    print(f"Subiendo {archivo_csv_song} a S3 en la carpeta 'album/songs'...")
    
    try:
        s3.upload_file(archivo_csv_album, nombre_bucket, archivo_s3_album)
        s3.upload_file(archivo_csv_song, nombre_bucket, archivo_s3_song)
        print(f"Archivos subidos exitosamente a S3 en las carpetas correspondientes.")
        return True
    except Exception as e:
        print(f"Error al subir los archivos a S3: {e}")
        return False

def crear_base_de_datos_en_glue(glue_database):
    """Crear base de datos en Glue si no existe."""
    try:
        glue.get_database(Name=glue_database)  
        print(f"La base de datos {glue_database} ya existe.")
    except glue.exceptions.EntityNotFoundException:
        print(f"La base de datos {glue_database} no existe. Creando base de datos...")
        glue.create_database(
            DatabaseInput={
                'Name': glue_database,
                'Description': 'Base de datos para almacenamiento de álbumes y canciones en Glue.'
            }
        )
        print(f"Base de datos {glue_database} creada exitosamente.")
    except Exception as e:
        print(f"Error al verificar o crear la base de datos en Glue: {e}")
        return False
    return True

def registrar_datos_en_glue(glue_database, glue_table_name_album, glue_table_name_song, nombre_bucket, archivo_csv_album, archivo_csv_song):
    """Registrar los datos en Glue Data Catalog."""
    print(f"Registrando datos en Glue Data Catalog...")
    input_path_album = f"s3://{nombre_bucket}/album/albums"
    input_path_album_songs = f"s3://{nombre_bucket}/album/songs"
    
    try:
        glue.create_table(
            DatabaseName=glue_database,
            TableInput={
                'Name': glue_table_name_album,
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'provider_id', 'Type': 'string'},
                        {'Name': 'album_id', 'Type': 'bigint'},
                        {'Name': 'artist_id', 'Type': 'bigint'},
                        {'Name': 'cover_image_url', 'Type': 'string'},
                        {'Name': 'release_date', 'Type': 'string'},
                        {'Name': 'songs_count', 'Type': 'bigint'},
                        {'Name': 'spotify_url', 'Type': 'string'},
                        {'Name': 'title', 'Type': 'string'}
                    ],
                    'Location': input_path_album,
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
        
        glue.create_table(
            DatabaseName=glue_database,
            TableInput={
                'Name': glue_table_name_song,
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'song_id', 'Type': 'bigint'},
                        {'Name': 'album_id', 'Type': 'bigint'},
                        {'Name': 'provider_id', 'Type': 'string'},
                    ],
                    'Location': input_path_album_songs,
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
        
        print(f"Tablas {glue_table_name_album} y {glue_table_name_song} registradas exitosamente en la base de datos {glue_database}.")
    except Exception as e:
        print(f"Error al registrar las tablas en Glue: {e}")


if __name__ == "__main__":
    if crear_base_de_datos_en_glue(glue_database):
        exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv_album, archivo_csv_song)
    
        if subir_csv_a_s3(archivo_csv_album, archivo_csv_song, nombre_bucket):
            registrar_datos_en_glue(glue_database, glue_table_name_album, glue_table_name_song, nombre_bucket, archivo_csv_album, archivo_csv_song)
        else:
            print("No se pudo completar el proceso porque hubo un error al subir los archivos a S3.")
    else:
        print("Error en la creación de la base de datos Glue. No se continuará con el proceso.")
    
    print("Proceso completado.")
