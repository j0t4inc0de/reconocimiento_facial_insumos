import tkinter as tk
from tkinter import messagebox
from datetime import datetime # type: ignore

# Lista de herramientas
herramientas = ["Martillo", "Destornillador", "Alicate", "Taladro", "Sierra"]

def guardar_seleccion():
    seleccionadas = [herramientas[i] for i, var in enumerate(variables) if var.get()]
    
    usuario = "Usuario1"
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje = f"Usuario: {usuario}\nFecha y Hora: {fecha_hora}\nHerramientas seleccionadas:\n" + "\n".join(seleccionadas)
    messagebox.showinfo("Selección guardada", mensaje)

root = tk.Tk()
root.title("Selección de Herramientas")

variables = [tk.BooleanVar() for _ in herramientas]
for i, herramienta in enumerate(herramientas):
    tk.Checkbutton(root, text=herramienta, variable=variables[i]).pack(anchor="w")

# Botón "Listo"
btn_guardar = tk.Button(root, text="Listo", command=guardar_seleccion)
btn_guardar.pack(pady=10)

root.mainloop()