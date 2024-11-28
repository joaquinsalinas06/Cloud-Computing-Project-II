#!/bin/bash

LOG_FILE="removal_results_dev.txt"

> $LOG_FILE

for dir in */; do
    if [ -f "$dir/serverless.yml" ]; then
        echo "Eliminando el servicio en DEV para la carpeta: $dir"
        cd "$dir" || exit

        REMOVE_OUTPUT=$(sls remove --stage dev 2>&1)
        echo "$REMOVE_OUTPUT"

        echo "Resultados de eliminación para $dir en DEV:" >> "../$LOG_FILE"
        echo "$REMOVE_OUTPUT" >> "../$LOG_FILE"
        echo "-----------------------------" >> "../$LOG_FILE"

        cd ..
    fi
done

echo "Eliminación en DEV completada. Los resultados se han guardado en $LOG_FILE."
cat $LOG_FILE
