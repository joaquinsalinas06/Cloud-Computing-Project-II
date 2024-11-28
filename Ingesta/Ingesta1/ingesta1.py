import boto3
import csv
import os
import time

# Configuración de servicios de AWS
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
s3 = boto3.client('s3', region_name='us-east-1')
glue = boto3.client('glue', region_name='us-east-1')

# Parámetros de configuración
tabla_dynamo = 'dev-t_user' 
nombre_bucket = 'ingesta-stage-prod'  
archivo_csv = 'stage-prod-usuarios.csv'
glue_database = 'stage-prod'  # La base de datos en Glue
glue_table_name = 'stage-prod-usuarios'

# Función para exportar datos desde DynamoDB a CSV
def exportar_dynamodb_a_csv(tabla_dynamo, archivo_csv):
    print(f"Exportando datos desde DynamoDB ({tabla_dynamo})...")
    tabla = dynamodb.Table(tabla_dynamo)
    scan_kwargs = {}
    
    with open(archivo_csv, 'w', newline='') as archivo:
        escritor_csv = csv.writer(archivo)  # Usamos csv.writer para escribir los datos
        
        while True:
            respuesta = tabla.scan(**scan_kwargs)
            items = respuesta['Items']
            
            if not items:
                break
            
            for item in items:
                # Convertir 'user_id' y 'age' a enteros (si es posible)
                try:
                    user_id = int(item.get('user_id', 0))  # Convertir a int (por defecto 0 si no es un número)
                except ValueError:
                    user_id = 0
                
                try:
                    age = int(item.get('age', 0))  # Convertir a int (por defecto 0 si no es un número)
                except ValueError:
                    age = 0

                # Aseguramos que los datos se escriben en el orden correcto
                row = [
                    item.get('birth_date', ''),
                    item.get('created_at', ''),
                    item.get('provider_id', ''),
                    item.get('email', ''),
                    item.get('name', ''),
                    item.get('gender', ''),
                    item.get('active', ''),
                    item.get('password', ''),
                    user_id,  # Aseguramos que 'user_id' sea un int
                    item.get('last_name', ''),
                    item.get('phone_number', ''),
                    item.get('username', ''),
                    age  # Aseguramos que 'age' sea un int
                ]
                
                escritor_csv.writerow(row)
            
            # Verifica si hay más datos
            if 'LastEvaluatedKey' in respuesta:
                scan_kwargs['ExclusiveStartKey'] = respuesta['LastEvaluatedKey']
            else:
                break
                
    print(f"Datos exportados a {archivo_csv}")

# Función para subir el archivo CSV a S3
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

# Función para crear la base de datos en Glue si no existe
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

# Función para registrar los datos del archivo CSV en Glue
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
                        {'Name': 'birth_date', 'Type': 'string'},
                        {'Name': 'created_at', 'Type': 'string'},
                        {'Name': 'provider_id', 'Type': 'string'},
                        {'Name': 'email', 'Type': 'string'},
                        {'Name': 'name', 'Type': 'string'},
                        {'Name': 'gender', 'Type': 'string'},
                        {'Name': 'active', 'Type': 'string'},
                        {'Name': 'password', 'Type': 'string'},
                        {'Name': 'user_id', 'Type': 'bigint'},  # 'user_id' debe ser de tipo bigint (entero)
                        {'Name': 'last_name', 'Type': 'string'},
                        {'Name': 'phone_number', 'Type': 'string'},
                        {'Name': 'username', 'Type': 'string'},
                        {'Name': 'age', 'Type': 'bigint'}  # 'age' debe ser de tipo bigint (entero)
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

# Función principal para ejecutar el flujo
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
