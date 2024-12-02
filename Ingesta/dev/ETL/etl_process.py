import boto3
import pandas as pd
import mysql.connector
from loguru import logger
import os
from datetime import datetime
import time

ATHENA_S3_OUTPUT = 's3://flauta-dev-c2/Unsaved/2024/12/01/'  
REGION_NAME = 'us-east-1'

MYSQL_HOST = '54.205.43.36'
MYSQL_PORT = '8005'  
MYSQL_USER = 'root'  
MYSQL_PASSWORD = 'utec'
MYSQL_DB = 'analytics'


# Configuración de logs
log_directory = "./logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = f"{log_directory}/etl.log"
logger.add(log_file, format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}", level="INFO", rotation="10 MB", retention="7 days", serialize=False, enqueue=True)

# Configuración de conexiones
athena_client = boto3.client('athena', region_name='us-east-1')

def run_athena_query(tablename, query):
    start_time = datetime.now()
    status = "SUCCESS"
    error_message = None
    num_records = 0
    results = None
    execution_time = 0
    query_type = query.split()[0].upper()  # Determina el tipo de consulta, asumiendo que el primer palabra es el tipo

    logger.info(f"Ejecutando consulta Athena para la tabla: {tablename}. Tipo de consulta: {query_type}. Consulta: {query}")

    try:
        # Configuración de Athena
        athena_client = boto3.client('athena', region_name='us-east-1')  # Cambiar la región si es necesario
        output_location = ATHENA_S3_OUTPUT

        # Ejecutar la consulta en Athena
        logger.info(f"Iniciando la ejecución de la consulta Athena...")
        response = athena_client.start_query_execution(
            QueryString=query,
            ResultConfiguration={
                'OutputLocation': output_location,
            },
            QueryExecutionContext={
               'Database': 'stage-prod'  # Especificar la base de datos
            }
        )

        query_execution_id = response['QueryExecutionId']
        logger.info(f"Consulta enviada con éxito. ID de ejecución: {query_execution_id}")

        # Esperar que la consulta termine
        wait_for_query_to_complete(athena_client, query_execution_id)
        logger.info(f"Consulta completada con éxito. Obteniendo los resultados...")

        # Obtener los resultados
        result_response = athena_client.get_query_results(QueryExecutionId=query_execution_id)
        num_records = len(result_response['ResultSet']['Rows']) - 1  # Restar 1 por la fila de encabezado
        results = str(result_response['ResultSet']['Rows'][1:])  # Excluye la fila de encabezado

        # Calcular el tiempo de ejecución
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        logger.info(f"Consulta completada. Tiempo de ejecución: {execution_time:.2f} segundos. Número de registros obtenidos: {num_records}")

        # Insertar los resultados en la tabla resumen
        # insert_summary_table(tablename, query, execution_time, num_records, results, start_time, end_time, status, error_message)

    except Exception as e:
        logger.error(f"Error ejecutando la consulta Athena: {e}")
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        status = "ERROR"
        error_message = str(e)

        # Insertar el resumen del error
        insert_summary_table(tablename, query, execution_time, num_records, results, start_time, end_time, status, error_message)

def wait_for_query_to_complete(athena_client, query_execution_id):
    logger.info(f"Esperando la finalización de la consulta Athena (ID: {query_execution_id})...")
    while True:
        response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        status = response['QueryExecution']['Status']['State']
        
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        time.sleep(2)  # Poll every 2 seconds

    if status != 'SUCCEEDED':
        logger.error(f"Consulta Athena fallida o cancelada. Estado: {status}")
        raise ValueError(f"Query failed or was cancelled. Status: {status}")
    
    logger.info(f"Consulta Athena completada con estado: {status}")

def process_query_file(query_file, table_name):
    """Procesa un archivo de consulta SQL y ejecuta el proceso ETL"""
    logger.info(f"Procesando archivo de consulta: {query_file}")
    with open(query_file, 'r') as file:
        query = file.read().strip()  # Lee el archivo de consulta SQL
        logger.debug(f"Consulta leída: {query}")
        run_athena_query(table_name, query)
    # transform_and_load_to_mysql(result_location, table_name)

def insert_summary_table(table_name, query, execution_time, num_records, results, start_time, end_time, status, error_message):
    try:
        logger.info(f"Ingresando resumen a la base de datos MySQL para la tabla {table_name}...")
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            port=MYSQL_PORT,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )   
        cursor = connection.cursor()

        insert_query = f"""
        INSERT INTO {table_name} (query, execution_time, num_records, results, start_time, end_time, status, error_message)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (query, execution_time, num_records, results, start_time, end_time, status, error_message)

        cursor.execute(insert_query, values)
        connection.commit()

        logger.info(f"Resumen insertado con éxito en MySQL. ID de consulta: {cursor.lastrowid}")

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        logger.error(f"Error al insertar el resumen en MySQL: {err}")
        if connection.is_connected():
            cursor.close()
            connection.close()

def etl_process():
    """Proceso ETL que maneja múltiples archivos de consultas"""
    query_dir = '../Consultas/Queries'  # Directorio que contiene las consultas SQL
    logger.info(f"Iniciando el proceso ETL. Buscando archivos en el directorio {query_dir}")

    # Itera sobre los archivos de consultas en el directorio
    for i, query_file in enumerate(os.listdir(query_dir)):
        if query_file.endswith('.txt'):
            query_file_path = os.path.join(query_dir, query_file)
            table_name = query_file[:-5]  # Remove the last character            
            logger.info(f"Procesando archivo de consulta: {query_file_path}")
            process_query_file(query_file_path, table_name)

    logger.info("Proceso ETL completado.")

if __name__ == "__main__":
    logger.info("Iniciando el proceso ETL...")
    etl_process()  # Ejecutar el proceso ETL
    logger.info("Proceso ETL finalizado.")
