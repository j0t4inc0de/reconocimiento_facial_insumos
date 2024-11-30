import tkinter as tk
from PIL import Image, ImageTk
import os

class CarruselImagenes:
    def __init__(self, root, images, interval=2000):
        self.root = root
        self.images = images
        self.interval = interval
        self.current_index = 0

        # Crear un Label para mostrar las imágenes
        self.label = tk.Label(self.root)
        self.label.pack()

        # Cargar las imágenes
        self.loaded_images = [ImageTk.PhotoImage(Image.open(img).resize((900, 400))) for img in self.images]

        # Iniciar el carrusel
        self.show_image()

    def show_image(self):
        # Mostrar la imagen actual
        self.label.config(image=self.loaded_images[self.current_index])
        # Actualizar el índice para la siguiente imagen
        self.current_index = (self.current_index + 1) % len(self.loaded_images)
        # Llamar a esta función de nuevo después de `interval` ms
        self.root.after(self.interval, self.show_image)

if __name__ == "__main__":
    # Configurar la ventana principal
    root = tk.Tk()
    root.title("Carrusel de Imágenes")
    root.attributes('-fullscreen', True)

    # Ruta a las imágenes (coloca aquí tus propias imágenes)
    ruta_imagenes = "imagenes_carrusel"  # Carpeta donde están las imágenes
    imagenes = [os.path.join(ruta_imagenes, img) for img in os.listdir(ruta_imagenes) if img.endswith(("png", "jpg", "jpeg"))]

    # Crear el carrusel
    if imagenes:
        carrusel = CarruselImagenes(root, imagenes, interval=5000)  # Cambia la imagen cada 3 segundos
    else:
        tk.Label(root, text="No se encontraron imágenes en la carpeta.").pack()

    root.mainloop()
