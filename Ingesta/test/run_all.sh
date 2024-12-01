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
    ["Ingesta7"]="ingesta7"

)

for carpeta in "${!carpetas[@]}"; do
  imagen="${carpetas[$carpeta]}" 
  
  echo "Construyendo la imagen Docker para $carpeta (imagen: $imagen)..."

  cd $carpeta

  docker build -t $imagen .

  echo "Corriendo el contenedor para $carpeta con la imagen $imagen..."
  docker run -v /home/ubuntu/.aws/credentials:/root/.aws/credentials $imagen

  cd ..

  echo "Proceso completado para $carpeta."
done

echo "¡Todos los procesos de build y run han sido completados!"
