#!/bin/bash

RESULTS_FILE="deployment_summary_prod.txt"

> $RESULTS_FILE

declare -A BASE_URLS

for dir in */; do
    if [ -f "$dir/serverless.yml" ]; then
        echo "Desplegando en PROD para la carpeta: $dir"
        cd "$dir" || exit
        DEPLOY_OUTPUT=$(sls deploy --stage prod 2>&1)
        BASE_URL=$(echo "$DEPLOY_OUTPUT" | grep -Eo 'https?://[a-zA-Z0-9\-]+\.execute-api\.[a-zA-Z0-9\-]+\.amazonaws\.com/prod')
        if [ -n "$BASE_URL" ]; then
            BASE_URLS["$BASE_URL"]="$dir"
        fi
        cd ..
    fi
done

echo "Despliegue en PROD completado. Base URLs detectadas:"
for url in "${!BASE_URLS[@]}"; do
    echo "BaseURL de ${BASE_URLS[$url]}: $url"
done

echo "Base URLs detectadas:" > $RESULTS_FILE
for url in "${!BASE_URLS[@]}"; do
    echo "BaseURL de ${BASE_URLS[$url]}: $url" >> $RESULTS_FILE
done
