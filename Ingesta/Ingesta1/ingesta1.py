import boto3
import csv
import os
import time

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
s3 = boto3.client('s3', region_name='us-east-1')
glue = boto3.client('glue', region_name='us-east-1')

tabla_dynamo = 'dev-t_user' 
nombre_bucket = 'ingesta-stage-prod'  
archivo_csv = 'stage-prod-usuarios.csv'
glue_database = 'stage-prod'  # La base de datos en Glue
glue_table_name = 'stage-prod-usuarios'

def exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv):
    print(f"Exportando datos desde DynamoDB ({tabla_dynamo})...")
    tabla = dynamodb.Table(tabla_dynamo)
    scan_kwargs = {}
    with open(archivo_csv, 'w', newline='') as archivo:
        escritor_csv = None
        while True:
            respuesta = tabla.scan(**scan_kwargs)
            items = respuesta['Items']
            
            if not escritor_csv:
                # Usamos la primera fila para determinar los campos (suponemos que todas las filas tienen los mismos atributos)
                writer_fields = []
                for item in items:
                    for key, value in item.items():
                        if isinstance(value, dict):
                            if 'S' in value:
                                writer_fields.append(key)
                            elif 'N' in value:
                                writer_fields.append(key)
                escritor_csv = csv.DictWriter(archivo, fieldnames=writer_fields)
                escritor_csv.writeheader()
            
            # Procesamos los items de DynamoDB para que solo contengan 'S' o 'N'
            rows = []
            for item in items:
                row = {}
                for key, value in item.items():
                    if isinstance(value, dict):
                        if 'S' in value:
                            row[key] = value['S']  # String
                        elif 'N' in value:
                            row[key] = value['N']  # Número
                rows.append(row)
            
            escritor_csv.writerows(rows)

            # Verifica si hay más datos
            if 'LastEvaluatedKey' in respuesta:
                scan_kwargs['ExclusiveStartKey'] = respuesta['LastEvaluatedKey']
            else:
                break
    print(f"Datos exportados a {archivo_csv}")

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

def crear_base_de_datos_en_glue(glue_database):
    """Crear base de datos en Glue si no existe."""
    try:
        glue.get_database(Name=glue_database)  # Verificar si la base de datos ya existe
        print(f"La base de datos {glue_database} ya existe.")
    except glue.exceptions.EntityNotFoundException:
        print(f"La base de datos {glue_database} no existe. Creando base de datos...")
        glue.create_database(
            DatabaseInput={
                'Name': glue_database,
                'Description': 'Base de datos para almacenamiento de usuarios en Glue.'
            }
        )
        print(f"Base de datos {glue_database} creada exitosamente.")
    except Exception as e:
        print(f"Error al verificar o crear la base de datos en Glue: {e}")
        return False
    return True

def registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv):
    """Registrar datos en Glue Data Catalog."""
    print(f"Registrando datos en Glue Data Catalog...")
    input_path = f"s3://{nombre_bucket}/usuarios/{archivo_csv}"
    
    try:
        glue.create_table(
            DatabaseName=glue_database,
            TableInput={
                'Name': glue_table_name,
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'provider_id', 'Type': 'string'},
                        {'Name': 'user_id', 'Type': 'string'},
                        {'Name': 'email', 'Type': 'string'},
                        {'Name': 'username', 'Type': 'string'},
                        {'Name': 'password', 'Type': 'string'},
                        {'Name': 'name', 'Type': 'string'},
                        {'Name': 'last_name', 'Type': 'string'},
                        {'Name': 'phone_number', 'Type': 'string'},
                        {'Name': 'birth_date', 'Type': 'string'},
                        {'Name': 'gender', 'Type': 'string'},
                        {'Name': 'age', 'Type': 'string'},
                        {'Name': 'active', 'Type': 'string'},
                        {'Name': 'created_at', 'Type': 'string'}
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
    if crear_base_de_datos_en_glue(glue_database):
        exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv)
    
        if subir_csv_a_s3(archivo_csv, nombre_bucket):
            registrar_datos_en_glue(glue_database, glue_table_name, nombre_bucket, archivo_csv)
        else:
            print("No se pudo completar el proceso porque hubo un error al subir el archivo a S3.")
    else:
        print("Error en la creación de la base de datos Glue. No se continuará con el proceso.")
    
    print("Proceso completado.")
