#!/bin/bash

# Ruta de las carpetas de ingesta (Ingesta1 a Ingesta6)
carpetas=("Ingesta1" "Ingesta2" "Ingesta3" "Ingesta4" "Ingesta5" "Ingesta6")

# Recorrer todas las carpetas
for carpeta in "${carpetas[@]}"; do
  echo "Construyendo la imagen Docker para $carpeta..."

  # Cambiar al directorio de la carpeta correspondiente
  cd $carpeta

  # Construir la imagen Docker
  docker build -t $carpeta .

  # Ejecutar el contenedor Docker
  echo "Corriendo el contenedor para $carpeta..."
  docker run -v /home/ubuntu/.aws/credentials:/root/.aws/credentials $carpeta

  # Volver al directorio anterior
  cd ..

  echo "Proceso completado para $carpeta."
done

echo "¡Todos los procesos de build y run han sido completados!"
