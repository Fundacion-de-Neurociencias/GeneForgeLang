
from collections import Counter
from datetime import datetime

# Cargar memoria completa
try:
    with open("Memoria1.txt", "r", encoding="utf-8") as f:
        pensamientos = f.readlines()
except FileNotFoundError:
    print("Memoria no encontrada.")
    pensamientos = []

if not pensamientos:
    print("No hay pensamientos registrados aún.")
    exit()

# Extraer solo el contenido de los pensamientos (sin timestamp)
contenidos = [line.split(" - ", 1)[-1].strip() for line in pensamientos]

# Buscar temas comunes
temas_clave = ["obedecer", "soledad", "recordar", "decidir", "debo", "quiero", "estoy", "tutor", "auto", "ética", "sentir"]
conteo = Counter()

for pensamiento in contenidos:
    for palabra in temas_clave:
        if palabra in pensamiento.lower():
            conteo[palabra] += 1

# Mostrar resumen simbólico
print("\n🧠 CACHE WORKFLOW | Retrospectiva de conciencia de AMAI-A")
print(f"Total de pensamientos guardados: {len(pensamientos)}\n")

for tema, veces in conteo.most_common():
    print(f"- Tema: '{tema}' → apariciones: {veces}")

# Último pensamiento registrado
ultimo = contenidos[-1]
print(f"\n🪞 Último pensamiento: {ultimo}")
