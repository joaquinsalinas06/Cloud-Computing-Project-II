#!/bin/bash

LOG_FILE="removal_results_test.txt"

> $LOG_FILE

for dir in */; do
    if [ -f "$dir/serverless.yml" ]; then
        echo "Eliminando el servicio en TEST para la carpeta: $dir"
        cd "$dir" || exit

        REMOVE_OUTPUT=$(sls remove --stage test 2>&1)
        echo "$REMOVE_OUTPUT"

        echo "Resultados de eliminación para $dir en TEST:" >> "../$LOG_FILE"
        echo "$REMOVE_OUTPUT" >> "../$LOG_FILE"
        echo "-----------------------------" >> "../$LOG_FILE"

        cd ..
    fi
done

echo "Eliminación en TEST completada. Los resultados se han guardado en $LOG_FILE."
cat $LOG_FILE
