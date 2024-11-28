import boto3
import csv
import os
import time

# Inicialización de clientes de AWS
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')
glue = boto3.client('glue', region_name='us-east-1')

# Parámetros de configuración
tabla_dynamo = 'dev-t_user'
nombre_bucket = 'ingesta-stage-dev'
archivo_csv = 'stage-prod-usuarios.csv'
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
                    print("No se encontraron elementos en la tabla de DynamoDB.")
                    break
                
                if not escritor_csv:
                    escritor_csv = csv.DictWriter(archivo, fieldnames=items[0].keys())
                    escritor_csv.writeheader()
                
                escritor_csv.writerows(items)

                # Continuar con la paginación si es necesario
                if 'LastEvaluatedKey' in respuesta:
                    scan_kwargs['ExclusiveStartKey'] = respuesta['LastEvaluatedKey']
                else:
                    break
        print(f"Datos exportados a {archivo_csv} exitosamente.")
    except Exception as e:
        print(f"Error al exportar desde DynamoDB: {e}")


def subir_csv_a_s3(archivo_csv, nombre_bucket):
    carpeta_destino = 'usuarios/'
    archivo_s3 = f"{carpeta_destino}{archivo_csv}"
    print(f"Subiendo {archivo_csv} al bucket S3 ({nombre_bucket}) en la carpeta 'usuarios'...")

    try:
        s3.upload_file(archivo_csv, nombre_bucket, archivo_s3)
        print(f"Archivo {archivo_csv} subido exitosamente a S3 en la carpeta 'usuarios'.")
        return True
    except Exception as e:
        print(f"Error al subir el archivo a S3: {e}")
        return False


def registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv):
    """Registrar datos en Glue Data Catalog."""
    print(f"Registrando datos en Glue Data Catalog...")
    input_path = f"s3://{nombre_bucket}/usuarios/{archivo_csv}"

    try:
        # Verifica si la tabla ya existe en Glue antes de crearla
        response = glue.get_tables(DatabaseName=glue_database)
        table_names = [table['Name'] for table in response['TableList']]
        if glue_table_name in table_names:
            print(f"La tabla {glue_table_name} ya existe en Glue. No se creará.")
            return

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
        print(f"Tabla {glue_table_name} registrada exitosamente en la base de datos {glue_database}.")
    except Exception as e:
        print(f"Error al registrar la tabla en Glue: {e}")


if __name__ == "__main__":
    try:
        exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv)
        
        if subir_csv_a_s3(archivo_csv, nombre_bucket):
            registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv)
        else:
            print("No se pudo completar el proceso porque hubo un error al subir el archivo a S3.")
        
    except Exception as e:
        print(f"Error general en el proceso: {e}")
    
    print("Proceso completado.")
