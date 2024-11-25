#!/bin/bash

LOG_FILE="removal_results.txt"

> $LOG_FILE

for dir in */; do
    if [ -f "$dir/serverless.yml" ]; then
        echo "Eliminando el servicio en la carpeta: $dir"
        cd "$dir" || exit

        REMOVE_OUTPUT=$(sls remove 2>&1)
        echo "$REMOVE_OUTPUT"

        echo "Resultados de eliminación para $dir:" >> "../$LOG_FILE"
        echo "$REMOVE_OUTPUT" >> "../$LOG_FILE"
        echo "-----------------------------" >> "../$LOG_FILE"

        cd ..
    fi
done

echo "Eliminación completada. Los resultados se han guardado en $LOG_FILE."
cat $LOG_FILE
