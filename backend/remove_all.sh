#!/bin/bash

echo "Iniciando la eliminación en todos los entornos: DEV, TEST, PROD"

./remove_dev.sh
echo "----------------------------------"
./remove_test.sh
echo "----------------------------------"
./remove_prod.sh

echo "Eliminación en todos los entornos completada."
