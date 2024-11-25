import json
import os
from typing import Any, List, Dict


def write_to_json(data_list: List[Dict[str, Any]], filename: str) -> None:
    file_path = f"../output/{filename}.json"

    # Si el archivo existe, lee su contenido actual
    if os.path.exists(file_path):
        with open(file_path, mode="r", encoding="utf-8") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []  # Si el archivo está vacío o tiene un formato incorrecto, inicia con una lista vacía
    else:
        existing_data = []

    # Combina los datos existentes con los nuevos datos
    combined_data = existing_data + data_list

    # Escribe todos los datos combinados al archivo
    with open(file_path, mode="w", encoding="utf-8") as file:
        json.dump(combined_data, file, ensure_ascii=False, indent=2, separators=(", ", ": "))
