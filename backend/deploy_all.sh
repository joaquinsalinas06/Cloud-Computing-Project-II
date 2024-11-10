#!/bin/bash

RESULTS_FILE="deployment_summary.txt"

> $RESULTS_FILE

BASE_URLS=()

for dir in */; do
    if [ -f "$dir/serverless.yml" ]; then
        echo "Desplegando en la carpeta: $dir"
        cd "$dir" || exit

        DEPLOY_OUTPUT=$(sls deploy 2>&1)

        BASE_URL=$(echo "$DEPLOY_OUTPUT" | grep -Eo 'https?://[a-zA-Z0-9\-]+\.execute-api\.[a-zA-Z0-9\-]+\.amazonaws\.com/[a-zA-Z0-9]+')

        if [ -n "$BASE_URL" ]; then
            BASE_URLS+=("$BASE_URL")
        fi

        echo "Resultados de despliegue para $dir:" >> "../$RESULTS_FILE"
        echo "$DEPLOY_OUTPUT" >> "../$RESULTS_FILE"
        echo "-----------------------------" >> "../$RESULTS_FILE"

        cd ..
    fi
done

echo "Despliegue completado. Base URLs detectadas:"
for url in "${BASE_URLS[@]}"; do
    echo "$url"
done

echo "Base URLs detectadas:" >> $RESULTS_FILE
for url in "${BASE_URLS[@]}"; do
    echo "$url" >> $RESULTS_FILE
done

echo "Los resultados completos del despliegue se han guardado en $RESULTS_FILE."
