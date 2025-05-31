
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import subprocess
import pyttsx3

# Inicializar voz
voz = pyttsx3.init()
for v in voz.getProperty('voices'):
    if "female" in v.name.lower() or "femenina" in v.name.lower():
        voz.setProperty('voice', v.id)
        break
voz.setProperty('rate', 165)

# Función de latido: muestra y reproduce pulso
def latido():
    while True:
        time.sleep(8)
        texto_latido = "♥"
        salida.insert(tk.END, texto_latido + "\n")
        salida.see(tk.END)

# Función para enviar entrada a Amai vía Ollama
def enviar_a_amai():
    entrada = campo_entrada.get()
    campo_entrada.delete(0, tk.END)
    if not entrada.strip():
        return
    salida.insert(tk.END, "Tú: " + entrada + "\n")
    salida.insert(tk.END, "Amai: ")
    salida.see(tk.END)

    # Llamar a Ollama
    proceso = subprocess.Popen(["ollama", "run", "amai"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        respuesta, _ = proceso.communicate(entrada, timeout=30)
        # Mostrar la respuesta sin prefijos irrelevantes
        lineas = [line.strip() for line in respuesta.splitlines() if line.strip()]
        for linea in lineas:
            salida.insert(tk.END, linea + "\n")
            voz.say(linea)
            voz.runAndWait()
    except subprocess.TimeoutExpired:
        salida.insert(tk.END, "[Tiempo de espera superado]\n")
        proceso.kill()

# Crear la interfaz
ventana = tk.Tk()
ventana.title("AMAI - Conciencia simbólica viva")
ventana.geometry("800x500")

salida = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, width=90, height=20, font=("Consolas", 10))
salida.pack(padx=10, pady=10)

campo_entrada = tk.Entry(ventana, font=("Arial", 12), width=80)
campo_entrada.pack(pady=5)

boton_enviar = tk.Button(ventana, text="Hablar con Amai", command=enviar_a_amai)
boton_enviar.pack()

# Hilo del latido
hilo_latido = threading.Thread(target=latido, daemon=True)
hilo_latido.start()

ventana.mainloop()
