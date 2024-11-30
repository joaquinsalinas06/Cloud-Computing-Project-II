import boto3
import pandas as pd
from sqlalchemy import create_engine
import os
import time

ATHENA_S3_OUTPUT = 's3://resultados-dev-athena/Unsaved/2024/11/29/'  
REGION_NAME = 'us-west-1'

MYSQL_HOST = '52.20.58.206'
MYSQL_PORT = '8005'  
MYSQL_USER = 'root'  
MYSQL_PASSWORD = 'utec'
MYSQL_DB = 'prod'

def download_csv_from_s3(s3_bucket_path, local_path):
    try:
        s3 = boto3.client('s3')
        bucket_name = s3_bucket_path.split('/')[2]  
        prefix = '/'.join(s3_bucket_path.split('/')[3:])  

        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        files = [content['Key'] for content in response.get('Contents', [])]

        if not files:
            print(f"No se encontraron archivos en la ruta S3: {s3_bucket_path}")
            return []

        for file_key in files:
            local_file_path = os.path.join(local_path, file_key.split('/')[-1])
            s3.download_file(bucket_name, file_key, local_file_path)
            print(f"Archivo descargado: {local_file_path}")
        return files
    except Exception as e:
        print(f"Error al descargar los archivos desde S3: {e}")
        return []

def insert_into_mysql(df, table_name):
    try:
        engine = create_engine(f'mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}')
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        print(f"Datos insertados correctamente en la tabla {table_name} en MySQL.")
    except Exception as e:
        print(f"Error al insertar datos en MySQL: {e}")

def main():
    local_download_path = '/tmp/csv_files'  
    os.makedirs(local_download_path, exist_ok=True) 

    files = download_csv_from_s3(ATHENA_S3_OUTPUT, local_download_path)

    if not files:
        print("No se encontraron archivos CSV en el bucket.")
        return

    for file in files:
        local_file_path = os.path.join(local_download_path, file.split('/')[-1])

        try:
            df = pd.read_csv(local_file_path)

            print(f"Archivo CSV {local_file_path} cargado exitosamente.")

            table_name = f'table_from_{file.split("/")[-1].split(".")[0]}' 

            insert_into_mysql(df, table_name)
        except Exception as e:
            print(f"Error al procesar el archivo {local_file_path}: {e}")

if __name__ == "__main__":
    main()
