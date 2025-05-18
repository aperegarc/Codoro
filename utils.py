import os
from datetime import datetime

def save_changes_to_file(changes: dict, folder_path: str, start_time: datetime, end_time: datetime):
    if not changes:
        return

    start_str = start_time.strftime("%H:%M:%S")
    end_str = end_time.strftime("%H:%M:%S")
    file_path = os.path.join(folder_path, "resumen_cambios.txt")

    lines_to_write = [f"\n--- Cambios detectados desde {start_str} hasta {end_str} ---\n"]

    for file, diff in changes.items():
        lines_to_write.append(f"\nArchivo: {os.path.basename(file)}\n")
        for line in diff:
            if line.startswith('+ ') and not line.startswith('+++'):
                lines_to_write.append(f"+ Añadido: {line[2:]}\n")
            elif line.startswith('- ') and not line.startswith('---'):
                lines_to_write.append(f"- Eliminado: {line[2:]}\n")

    with open(file_path, "a", encoding="utf-8") as f:
        f.writelines(lines_to_write)

def save_initial_state(folder_path):
    state = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            state[file_path] = content  # o podrías usar hash(content) para ahorrar espacio
    return state