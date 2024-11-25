import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Lista de herramientas
herramientas = ["Martillo", "Destornillador", "Alicate", "Taladro", "Sierra"]

# Función para manejar el botón "Listo"
def guardar_seleccion():
    seleccionadas = [herramientas[i] for i, var in enumerate(variables) if var.get()]
    
    # Obtener el nombre del usuario (aquí como un ejemplo está fijo, podrías pedirlo en otra parte de tu app)
    usuario = "Usuario1"
    # Fecha y hora actual
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Crear mensaje con las herramientas seleccionadas
    mensaje = f"Usuario: {usuario}\nFecha y Hora: {fecha_hora}\nHerramientas seleccionadas:\n" + "\n".join(seleccionadas)
    
    # Mostrar el mensaje en un cuadro de diálogo (puedes cambiarlo para imprimir en consola si prefieres)
    messagebox.showinfo("Selección guardada", mensaje)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Selección de Herramientas")

# Variables para los checkboxes
variables = [tk.BooleanVar() for _ in herramientas]

# Crear checkboxes dinámicamente
for i, herramienta in enumerate(herramientas):
    tk.Checkbutton(root, text=herramienta, variable=variables[i]).pack(anchor="w")

# Botón "Listo"
btn_guardar = tk.Button(root, text="Listo", command=guardar_seleccion)
btn_guardar.pack(pady=10)

# Ejecutar la aplicación
root.mainloop()
