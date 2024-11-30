import boto3
import pandas as pd
from pyathena import connect
from sqlalchemy import create_engine
import os
import time

ATHENA_DATABASE = 'stage-prod'  
ATHENA_S3_OUTPUT = 's3://resultados-dev-athena/'  
REGION_NAME = 'us-west-1'

MYSQL_HOST = '52.20.58.206'  
MYSQL_PORT = '8005' 
MYSQL_USER = 'root'  
MYSQL_PASSWORD = 'utec'
MYSQL_DB = 'prod'

RESULTS_DIR = 's3://resultados-dev-athena/queries/'  

def query_athena(query, query_name):
    try:
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        query_folder = f"{RESULTS_DIR}query_{query_name}_{timestamp}/" 

        conn = connect(s3_staging_dir=ATHENA_S3_OUTPUT, region_name=REGION_NAME, database=ATHENA_DATABASE)
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        print(f"Error al ejecutar la consulta Athena: {e}")
        return None

def insert_into_mysql(df, table_name):
    try:
        engine = create_engine(f'mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}')
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        print(f"Datos insertados correctamente en la tabla {table_name} en MySQL.")
    except Exception as e:
        print(f"Error al insertar datos en MySQL: {e}")

def extract_data(query_name):
    query = """
       SELECT 
        p.provider_id, 
        sa.artist_id, 
        a.name AS artist_name, 
        COUNT(p.song_id) AS post_count
    FROM "stage-prod-post" p
    JOIN "stage-prod-song" sa ON p.song_id = sa.song_id
    JOIN "stage-prod-artist" a ON sa.artist_id = a.artist_id
    GROUP BY p.provider_id, sa.artist_id, a.name
    ORDER BY p.provider_id, post_count DESC;
    """
    data = query_athena(query, query_name)
    return data

def main():
    data = extract_data(query_name="1")

    if data is not None:
        insert_into_mysql(data, 'top_artists_by_provider')  

if __name__ == "__main__":
    main()
