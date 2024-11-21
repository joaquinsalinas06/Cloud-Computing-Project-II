import boto3
import json
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

s3 = boto3.client('s3', region_name='us-east-1')
dynamodb = boto3.client('dynamodb', region_name='us-east-1')

bucket_name = "jss-proyecto2"
tablas_archivos = {
    "dev-t_song": "songs.json",
}


def descargar_archivo_s3(bucket, key):
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        contenido = response['Body'].read().decode('utf-8')
        return json.loads(contenido)
    except NoCredentialsError:
        print("Error: Credenciales de AWS no configuradas.")
        raise
    except PartialCredentialsError:
        print("Error: Configuración de credenciales incompleta.")
        raise
    except Exception as e:
        print(f"Error al descargar {key} de S3: {e}")
        raise


def batch_write_to_dynamodb(table_name, items):
    lotes = [items[i:i + 25] for i in range(0, len(items), 25)]

    for lote in lotes:
        request_items = {table_name: [{'PutRequest': {'Item': item}} for item in lote]}
        response = dynamodb.batch_write_item(RequestItems=request_items)

    while 'UnprocessedItems' in response and response['UnprocessedItems']:
        print(f"Reintentando elementos no procesados en la tabla {table_name}...")
        for table, items in response['UnprocessedItems'].items():
            print(f"Tabla: {table}")
            for item in items:
                print(f"Elemento no procesado: {item}")
        response = dynamodb.batch_write_item(RequestItems=response['UnprocessedItems'])


def main():
    for tabla, archivo_s3 in tablas_archivos.items():
        print(f"Descargando datos desde {archivo_s3} para la tabla {tabla}...")

        try:
            items = descargar_archivo_s3(bucket_name, archivo_s3)

            if not isinstance(items, list):
                print(f"El archivo {archivo_s3} no contiene una lista de JSONs. Saltando...")
                continue

            print(f"Importando datos en la tabla {tabla}...")
            batch_write_to_dynamodb(tabla, items)
            print(f"Importación completada para la tabla {tabla}.")
        except Exception as e:
            print(f"Error procesando {archivo_s3}: {e}")


if __name__ == "__main__":
    main()
