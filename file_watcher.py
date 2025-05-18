import os
import time
import difflib
from datetime import datetime  # <-- Import necesario para save_changes_to_file

def save_initial_state(folder_path: str) -> dict:
    state = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".java", ".py", ".js", ".ts", ".cpp")):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        state[path] = f.read()
                except Exception:
                    pass
    return state

def compare_files(initial_state: dict, folder_path: str) -> dict:
    changes = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".java", ".py", ".js", ".ts", ".cpp")):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        current = f.read()
                    initial = initial_state.get(path, "")
                    if initial != current:
                        diff = list(difflib.unified_diff(initial.splitlines(), current.splitlines(), lineterm=''))
                        if diff:
                            changes[path] = diff
                except Exception:
                    pass
    return changes

def generate_code_from_diff(changes: dict) -> str:
    combined_code = ""
    for file, diff in changes.items():
        combined_code += f"\n// Cambios en: {os.path.basename(file)}\n"
        for line in diff:
            if line.startswith('+ ') and not line.startswith('+++'):
                combined_code += line[2:] + "\n"
            elif line.startswith('- ') and not line.startswith('---'):
                combined_code += line[2:] + "\n"
    return combined_code[:4000]

def save_changes_to_file(changes: dict, folder_path: str, start_time: datetime, end_time: datetime):
    if not changes:
        return  # No hay cambios para guardar

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
