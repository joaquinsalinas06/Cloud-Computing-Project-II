import boto3
import csv
import os

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
s3 = boto3.client('s3')
glue = boto3.client('glue')

tabla_dynamo = 'TablaOrigen' 
nombre_bucket = 'mi-bucket'  
archivo_csv = 'TablaOrigen.csv'
glue_database = 'mi_glue_database' 
glue_table_name = 'mi_tabla_glue' 


def exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv):
    """Exportar datos desde DynamoDB a un archivo CSV."""
    print(f"Exportando datos desde DynamoDB ({tabla_dynamo})...")
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
    print(f"Datos exportados a {archivo_csv}")


def subir_csv_a_s3(archivo_csv, nombre_bucket):
    """Subir archivo CSV a un bucket S3."""
    print(f"Subiendo {archivo_csv} al bucket S3 ({nombre_bucket})...")
    s3.upload_file(archivo_csv, nombre_bucket, archivo_csv)
    print(f"Archivo subido exitosamente a S3.")


def registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv):
    """Registrar datos en el Glue Data Catalog."""
    print(f"Registrando datos en Glue Data Catalog...")
    input_path = f"s3://{nombre_bucket}/{archivo_csv}"
    glue.create_table(
        DatabaseName=glue_database,
        TableInput={
            'Name': glue_table_name,
            'StorageDescriptor': {
                'Columns': [
                    {'Name': 'id', 'Type': 'string'},  
                    {'Name': 'nombre', 'Type': 'string'}, 
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
    print(f"Tabla {glue_table_name} registrada exitosamente en la base de datos {glue_database}.")


if __name__ == "__main__":
    exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv)
    
    subir_csv_a_s3(archivo_csv, nombre_bucket)
    
    registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv)
    
    print("Proceso completado.")
