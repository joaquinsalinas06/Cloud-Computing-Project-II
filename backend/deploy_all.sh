#!/bin/bash

echo "Iniciando despliegue en todos los entornos: DEV, TEST, PROD"

./deploy_dev.sh
echo "----------------------------------"
./deploy_test.sh
echo "----------------------------------"
./deploy_prod.sh

echo "Despliegue en todos los entornos completado."
