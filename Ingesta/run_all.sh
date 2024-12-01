#!/bin/bash

# Definir las carpetas y las imágenes Docker (diccionario)
declare -A carpetas
carpetas=(
    ["Ingesta1"]="ingesta1"
    ["Ingesta2"]="ingesta2"
    ["Ingesta3"]="ingesta3"
    ["Ingesta4"]="ingesta4"
    ["Ingesta5"]="ingesta5"
    ["Ingesta6"]="ingesta6"
)

# Crear el directorio de logs si no existe
mkdir -p ./logs

# Recorrer todas las carpetas del diccionario
for carpeta in "${!carpetas[@]}"; do
  imagen="${carpetas[$carpeta]}" # Obtener el nombre de la imagen correspondiente
  
  echo "Construyendo la imagen Docker para $carpeta (imagen: $imagen)..."

  # Cambiar al directorio de la carpeta correspondiente
  cd $carpeta

  # Construir la imagen Docker
  docker build -t $imagen .

  # Ejecutar el contenedor Docker en segundo plano y redirigir la salida de pantalla a archivo de log
  echo "Corriendo el contenedor para $carpeta con la imagen $imagen..."

  # Usar `docker run` con la opción `-d` para ejecución en segundo plano
  docker run -d -e CONTAINER_NAME="$carpeta" -v /home/ubuntu/.aws/credentials:/root/.aws/credentials $imagen > "../logs/ingesta${carpeta: -1}.log" 2>&1 &
  
  # Volver al directorio anterior
  cd ..

  echo "Proceso completado para $carpeta."
done

echo "¡Todos los procesos de build y run han sido completados!"
