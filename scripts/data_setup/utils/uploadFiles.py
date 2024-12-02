import boto3
import json
import time
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

s3 = boto3.client('s3', region_name='us-east-1')
dynamodb = boto3.client('dynamodb', region_name='us-east-1')

bucket_name = "flt-data-cloud"
tablas_archivos = {
    #"dev-t_album": ["albumsV1.json", "albumsV2.json"],
    "dev-t_album": ["albumsV1.json", "albumsV2.json", "albumsData.json"], #// Uncomment this line to include the albumsData.json file for Data Science

    #"dev-t_artist": ["artistsV1.json", "artistsV2.json"],
    "dev-t_artist": ["artistsV1.json", "artistsV2.json", "artistsData.json"], #// Uncomment this line to include the artistsData.json file for Data Science

    "dev-t_post": ["posts.json"],

    #"dev-t_song": ["songsV1.json", "songsV2.json"],
    "dev-t_song": ["songsV1.json", "songsV2.json", "songsData.json"], #// Uncomment this line to include the songsData.json file for Data Science

    "dev-t_user": ["users.json"],
    "dev-t_comment": ["commentsV1.json","commentsV2.json"],
    "dev-t_playlist": ["playlists.json"],
}


def descargar_archivo_s3(bucket, key):
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        contenido = response['Body'].read().decode('utf-8')
        return json.loads(contenido)
    except Exception as e:
        print(f"Error al descargar {key} de S3: {e}")
        raise


def batch_write_to_dynamodb(table_name, items, max_retries=5):
    lotes = [items[i:i + 25] for i in range(0, len(items), 25)]
    for lote in lotes:
        request_items = {table_name: [{'PutRequest': {'Item': item}} for item in lote]}
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = dynamodb.batch_write_item(RequestItems=request_items)
                if 'UnprocessedItems' not in response or not response['UnprocessedItems']:
                    break
            except Exception:
                break

            if 'UnprocessedItems' in response and response['UnprocessedItems']:
                request_items = response['UnprocessedItems']
                time.sleep(2 ** retry_count)
                retry_count += 1




def main():
    for tabla, archivos_s3 in tablas_archivos.items():
        for archivo_s3 in archivos_s3:
            print(f"Descargando datos desde {archivo_s3} para la tabla {tabla}...")
            try:
                items = descargar_archivo_s3(bucket_name, archivo_s3)
                if not isinstance(items, list):
                    print(f"El archivo {archivo_s3} no contiene una lista de JSONs. Saltando...")
                    continue

                print(f"Importando datos en la tabla {tabla}...")
                batch_write_to_dynamodb(tabla, items)
                print(f"Importación completada para la tabla {tabla} desde {archivo_s3}.")
            except Exception as e:
                print(f"Error procesando {archivo_s3}: {e}")

            time.sleep(5)

if __name__ == "__main__":
    main()
