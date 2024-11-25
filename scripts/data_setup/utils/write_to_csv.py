import csv
import os

def write_to_csv(data_list: list, filename: str) -> None:
    if not data_list:
        raise ValueError("The data list is empty")

    headers = data_list[0].keys()
    file_path = f"../output/{filename}.csv"
    write_headers = not os.path.exists(file_path)  # Escribe los encabezados solo si el archivo no existe

    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if write_headers:
            writer.writeheader()  # Solo escribe los encabezados si el archivo es nuevo
        writer.writerows(data_list)
