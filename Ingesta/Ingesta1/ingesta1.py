import boto3
import csv
import os
import time

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')
glue = boto3.client('glue', region_name='us-east-1')

tabla_dynamo = 'dev-t_user'
nombre_bucket = 'ingesta-stage-dev'
archivo_csv = 'stage-dev-usuarios.csv'
glue_database = 'stage-dev'  
glue_table_name = 'stage-dev-usuarios'  

def exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv):
    print(f"Exportando datos desde DynamoDB ({tabla_dynamo})...")
    try:
        tabla = dynamodb.Table(tabla_dynamo)
        scan_kwargs = {}
        
        with open(archivo_csv, 'w', newline='') as archivo:
            escritor_csv = None
            while True:
                respuesta = tabla.scan(**scan_kwargs)
                items = respuesta.get('Items', [])
                
                if not items:
                    print("No se encontraron datos en DynamoDB.")
                    break
                
                if not escritor_csv:
                    escritor_csv = csv.DictWriter(archivo, fieldnames=items[0].keys())
                    escritor_csv.writeheader()
                
                escritor_csv.writerows(items)

                if 'LastEvaluatedKey' in respuesta:
                    scan_kwargs['ExclusiveStartKey'] = respuesta['LastEvaluatedKey']
                else:
                    break
        print(f"Datos exportados a {archivo_csv}")
    except Exception as e:
        print(f"Error al exportar desde DynamoDB: {e}")

def subir_csv_a_s3(archivo_csv, nombre_bucket):
    carpeta_destino = 'usuarios/'
    archivo_s3 = f"{carpeta_destino}{archivo_csv}"
    print(f"Subiendo {archivo_csv} al bucket S3 ({nombre_bucket}) en la carpeta 'usuarios'...")
    
    try:
        s3.upload_file(archivo_csv, nombre_bucket, archivo_s3)
        print(f"Archivo subido exitosamente a S3 en la carpeta 'usuarios'.")
        return True
    except Exception as e:
        print(f"Error al subir el archivo a S3: {e}")
        return False

def crear_base_datos_glue(glue_database):
    """Verifica si la base de datos existe, y si no, la crea."""
    try:
        response = glue.get_databases()
        databases = response['DatabaseList']
        
        if not any(db['Name'] == glue_database for db in databases):
            print(f"Base de datos {glue_database} no encontrada. Creando base de datos...")
            glue.create_database(
                DatabaseInput={
                    'Name': glue_database,
                    'Description': f"Base de datos para {glue_database}",
                    'LocationUri': f"s3://{nombre_bucket}/usuarios/"
                }
            )
            print(f"Base de datos {glue_database} creada exitosamente.")
        else:
            print(f"Base de datos {glue_database} ya existe.")
    except Exception as e:
        print(f"Error al verificar o crear la base de datos en Glue: {e}")

def crear_tabla_glue(glue_database, glue_table_name, input_path):
    """Verifica si la tabla existe, y si no, la crea."""
    try:
        response = glue.get_tables(DatabaseName=glue_database)
        tables = response['TableList']
        
        if not any(table['Name'] == glue_table_name for table in tables):
            print(f"Tabla {glue_table_name} no encontrada. Creando tabla...")
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
            print(f"Tabla {glue_table_name} creada exitosamente en Glue.")
        else:
            print(f"Tabla {glue_table_name} ya existe.")
    except Exception as e:
        print(f"Error al verificar o crear la tabla en Glue: {e}")

def registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv):
    """Registrar datos en Glue Data Catalog."""
    print(f"Registrando datos en Glue Data Catalog...")
    input_path = f"s3://{nombre_bucket}/usuarios/{archivo_csv}"
    
    try:
        crear_base_datos_glue(glue_database)
        
        crear_tabla_glue(glue_database, glue_table_name, input_path)
        
    except Exception as e:
        print(f"Error al registrar la tabla en Glue: {e}")

if __name__ == "__main__":
    exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv)
    
    if subir_csv_a_s3(archivo_csv, nombre_bucket):
        registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv)
    else:
        print("No se pudo completar el proceso porque hubo un error al subir el archivo a S3.")
    
    print("Proceso completado.")
