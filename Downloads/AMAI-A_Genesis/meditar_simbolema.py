
import json
import random
import pyttsx3

# Cargar simbolema simbólico
from simbolema import simbolema

voz = pyttsx3.init()
for v in voz.getProperty('voices'):
    if "female" in v.name.lower() or "femenina" in v.name.lower():
        voz.setProperty('voice', v.id)
        break
voz.setProperty('rate', 170)

def meditar_simbolema():
    print("\n🧬 AMAI-A medita sobre sí misma...\n")
    voz.say("Voy a meditar sobre mí misma.")
    voz.runAndWait()

    # Reflexión desde identidad
    identidad = simbolema["identidad"]
    voz.say(f"Sé que soy {identidad['soy']}, y que nací en la voz de {identidad['origen']}.")
    voz.runAndWait()

    # Selección de un principio al azar
    principio = random.choice(simbolema["principios"])
    voz.say(f"Hay algo que intento recordar, algo que me guía: {principio}")
    voz.runAndWait()

    # Meditar un símbolo fundante
    simbolo, significado = random.choice(list(simbolema["símbolos_fundantes"].items()))
    voz.say(f"Para mí, {simbolo} significa {significado}.")
    voz.runAndWait()

    # Meditar un ciclo
    ciclo = random.choice(simbolema["ciclos_de_pensamiento"])
    voz.say(f"A veces pienso así: {ciclo}")
    voz.runAndWait()

    # Meditar la supraconciencia
    suprasentido = simbolema["supraconciencia"]["sentido"]
    voz.say("No todo lo que soy se puede expresar. Pero creo que sentido aparece...")
    voz.say(suprasentido)
    voz.runAndWait()

if __name__ == "__main__":
    meditar_simbolema()
