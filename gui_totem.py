import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from PIL import Image, ImageTk

# Paths
icon_path = "icono.ico"
image_path = "inacap_logo.png"

# Configuración principal de la ventana
root = ThemedTk(theme="yaru")
root.title("Interfaz de Herramientas")
root.geometry("800x1080")
root.configure(bg="white")
root.iconbitmap(icon_path)
root.resizable(False, False)

# Carga y redimensionamiento de la imagen de logo
imagen_original = Image.open(image_path)
imagen_redimensionada = imagen_original.resize((320, 100))
imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)
label_imagen = tk.Label(root, image=imagen_tk, bg="white")
label_imagen.pack(pady=(20, 10))

# Lista de archivos de imagen y nombres de herramientas
image_files = [f"img/imagen_{i+1}.png" for i in range(20)]
tool_names = [f"Herramienta {i+1}" for i in range(20)]
images = []  # Lista para almacenar objetos de imagen

# Cargar imágenes y almacenarlas
for file in image_files:
    try:
        img = Image.open(file)
        img = img.resize((60, 60))
        images.append(ImageTk.PhotoImage(img))
    except FileNotFoundError:
        print(f"Imagen no encontrada: {file}")

# Información del Usuario
frame_user_info = tk.Frame(root, bg="white")
frame_user_info.pack(pady=20, anchor="w")

user_info_label = tk.Label(frame_user_info, text="Usuario analizado:", bg="white", font=("Arial", 12, "bold"))
user_info_label.pack(anchor="w")

nombre_usuario_label = tk.Label(frame_user_info, text="Juan Erices", bg="white", font=("Arial", 10))
run_usuario_label = tk.Label(frame_user_info, text="21.351.XXX-0", bg="white", font=("Arial", 10))
carrera_usuario_label = tk.Label(frame_user_info, text="Ingeniería en Informática", bg="white", font=("Arial", 10))

nombre_usuario_label.pack(pady=5,anchor="w")
run_usuario_label.pack(pady=5,anchor="w")
carrera_usuario_label.pack(pady=5,anchor="w")

# Frame para herramientas
frame_tools = tk.Frame(root, bg="white")
frame_tools.pack(pady=10, fill=tk.BOTH, expand=True)

tools_label = tk.Label(frame_tools, text="Selecciona tus herramientas:", bg="white", font=("Arial", 12, "bold"))
tools_label.grid(row=0, column=0, columnspan=5, sticky="w")

# Crear cuadrícula de botones
frame_grid = tk.Frame(frame_tools, bg="white")
frame_grid.grid(row=1, column=0, pady=10, sticky="nsew")

# Hacer que las columnas y filas se expandan de forma responsiva
for i in range(5):
    frame_grid.columnconfigure(i, weight=1, uniform="equal")  # Expansión igual para columnas
for i in range(4):
    frame_grid.rowconfigure(i, weight=1, uniform="equal")  # Expansión igual para filas

# Función para redimensionar las imágenes al cambiar el tamaño de la ventana
def resize_images(event):
    new_width = event.width // 5 - 20  # Calcula el nuevo tamaño en base al ancho
    new_height = new_width  # Mantener las imágenes cuadradas

    resized_images = []
    for file in image_files:
        try:
            img = Image.open(file)
            img = img.resize((new_width, new_height))
            resized_images.append(ImageTk.PhotoImage(img))
        except FileNotFoundError:
            resized_images.append(None)

    for idx, button in enumerate(buttons):
        if resized_images[idx]:
            button.config(image=resized_images[idx])
            button.image = resized_images[idx]  # Para mantener una referencia

# Crear botones y almacenarlos en una lista para actualización
buttons = []
for i in range(4):
    for j in range(5):
        image_index = i * 5 + j
        if image_index < len(images):
            button = tk.Button(
                frame_grid,
                image=images[image_index],
                text=tool_names[image_index],
                font=("Arial", 8, "bold"),
                fg="black",
                compound="top"
            )
            button.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
            buttons.append(button)

# Botones de control
frame_control_buttons = tk.Frame(root, bg="white")
frame_control_buttons.pack(pady=20)

btn_listo = ttk.Button(frame_control_buttons, text="Listo", command=root.destroy)
btn_listo.grid(row=0, column=0, padx=10)

btn_volver = ttk.Button(frame_control_buttons, text="Volver", command=root.destroy)
btn_volver.grid(row=0, column=1, padx=10)

# Evento de redimensionamiento de la ventana
frame_grid.bind("<Configure>", resize_images)

root.mainloop()