import os
from llama_cpp import Llama

# Limitar número de threads para evitar crashes por multihilo
os.environ["OMP_NUM_THREADS"] = "1"

try:
    llm = Llama(model_path="./modelos/mistral-7b-instruct-v0.1.Q2_K.gguf", n_ctx=2048)
except Exception as e:
    print(f"Error cargando el modelo: {e}")
    llm = None  # No cargar modelo para evitar fallo app

def summarize_code(code_snippet: str) -> str:
    if not code_snippet.strip():
        return "No se detectaron cambios relevantes."
    if llm is None:
        return "Modelo no disponible."
    prompt = f"Resume los cambios que te doy a continuación:\n{code_snippet}"
    try:
        output = llm(prompt, max_tokens=300)
        return output["choices"][0]["text"].strip()
    except Exception as e:
        print(f"Error en inferencia: {e}")
        return "Error generando resumen."
