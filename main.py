import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import cv2
import face_recognition
import os
from datetime import datetime # type: ignore
from PIL import Image, ImageTk
import pandas as pd  # Nueva importación para manejar Excel tambien el modulo openpyxl

# Paths
icon_path = "img/icono.ico"
logo_path = "img/inacap_logo.png"
reconociendo_path = "img/reconociendo_rostro.png"
inventario_path = "Inventario.xlsx"

class CarruselImagenes:
    def __init__(self, parent, images, interval=2000):
        self.parent = parent
        self.images = images
        self.interval = interval
        self.current_index = 0

        # Crear un Frame para el carrusel dentro del parent
        self.frame = ttk.Frame(self.parent)
        self.frame.pack()

        # Crear un Label para mostrar las imágenes
        self.label = tk.Label(self.frame)
        self.label.pack()

        # Cargar las imágenes
        self.loaded_images = [
            ImageTk.PhotoImage(Image.open(img).resize((1000, 400)))
            for img in self.images
        ]

        # Iniciar el carrusel
        self.show_image()

    def show_image(self):
        # Mostrar la imagen actual
        self.label.config(image=self.loaded_images[self.current_index])
        # Actualizar el índice para la siguiente imagen
        self.current_index = (self.current_index + 1) % len(self.loaded_images)
        # Llamar a esta función de nuevo después de `interval` ms
        self.parent.after(self.interval, self.show_image)

class VentanaInicio:
    def __init__(self, root, codificaciones):
        self.root = root
        self.root.configure(bg="white")  # Fondo blanco para la ventana principal
        self.codificaciones = codificaciones

        # Crear un estilo para que el frame tenga fondo blanco
        estilo_frame = ttk.Style()
        estilo_frame.configure("Custom.TFrame", background="#ffffff")

        # Crear el frame con el estilo personalizado
        self.frame = ttk.Frame(self.root, padding=50, style="Custom.TFrame")
        self.frame.pack(expand=True)

        # Logo encima del carrusel
        logo_path = "img/inacap_logo.png"  # Ruta del logo
        try:
            logo_img = Image.open(logo_path).resize((300, 100))  # Ajusta el tamaño según sea necesario
            self.logo_tk = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(self.frame, image=self.logo_tk, bg="white")
            logo_label.pack(pady=(0, 20))  # Espaciado entre el logo y el carrusel
        except Exception as e:
            tk.Label(self.frame, text="No se pudo cargar el logo.", bg="white").pack()

        # Carrusel de imágenes
        ruta_imagenes = "imagenes_carrusel"  # Carpeta donde están las imágenes
        imagenes = [
            os.path.join(ruta_imagenes, img)
            for img in os.listdir(ruta_imagenes)
            if img.endswith(("png", "jpg", "jpeg"))
        ]
        if imagenes:
            self.carrusel = CarruselImagenes(self.frame, imagenes, interval=5000)
        else:
            tk.Label(self.frame, text="No se encontraron imágenes.", bg="white").pack()

        # Botón Iniciar
        btn_iniciar = ttk.Button(
            self.frame,
            text="Iniciar",
            command=self.abrir_ventana_camara
        )
        btn_iniciar.pack(padx=5, pady=5)
        btn_iniciar.config(
            width=15,
            style="Tactil.TButton"
        )
        estilo = ttk.Style()
        estilo.configure(
            "Tactil.TButton",
            font=("Arial", 10),
            padding=5
        )

    def abrir_ventana_camara(self):
        self.root.withdraw()
        VentanaCamara(self.root, self.codificaciones)

class VentanaCamara:
    def __init__(self, root, codificaciones):
        self.root = root
        self.codificaciones = codificaciones
        self.cam_window = tk.Toplevel(self.root)
        self.cam_window.title("Cámara")
        self.cam_window.attributes('-fullscreen', True)
        self.cam_window.state("zoomed")
        self.cam_window.configure(bg="white")

        self.lbl_status = ttk.Label(self.cam_window, text="Detectando rostro...", background="white", font=("Arial", 16))
        self.lbl_status.pack(pady=20)

        imagen_original = Image.open(reconociendo_path)
        imagen_redimensionada = imagen_original.resize((800, 800))
        self.imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)

        self.label_imagen = ttk.Label(self.cam_window, image=self.imagen_tk)
        self.label_imagen.pack(pady=(20, 10))

        self.cam_window.after(50, self.iniciar_camara)

    def iniciar_camara(self):
        cap = cv2.VideoCapture(0)
        reconocida = False
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rostros = face_recognition.face_locations(frame_rgb)
            codificaciones_rostros = face_recognition.face_encodings(frame_rgb, rostros)

            for codificacion in codificaciones_rostros:
                for nombre, referencia in self.codificaciones.items():
                    if face_recognition.compare_faces([referencia], codificacion)[0]:
                        self.lbl_status.config(text=f"Reconocido: {nombre}")
                        reconocida = True
                        cap.release()
                        cv2.destroyAllWindows()
                        self.cam_window.destroy()
                        VentanaHerramientas(self.root, nombre)
                        return

            if not reconocida:
                self.lbl_status.config(text="No se reconoce a la persona")
                cv2.imshow("Cámara", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        cap.release()
        cv2.destroyAllWindows()
        self.cam_window.destroy()
        self.root.deiconify()

class VentanaHerramientas:
    def __init__(self, root, nombre):
        self.root = root
        self.nombre = nombre
        self.tool_window = tk.Toplevel(self.root)
        self.tool_window.title("Ventana de Herramientas")
        self.tool_window.geometry("1920x1080")
        self.tool_window.attributes('-fullscreen', True)
        self.tool_window.state("zoomed")

        ttk.Label(
            self.tool_window,
            text=f"Bienvenido, {self.nombre}",
            font=("Arial", 15)
        ).pack(pady=10)

        # Marco principal para contener el canvas y el scrollbar
        marco_principal = ttk.Frame(self.tool_window)
        marco_principal.pack(fill="both", expand=True, padx=10, pady=10)

        # Canvas para mostrar los checkboxes
        canvas = tk.Canvas(marco_principal)
        canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(marco_principal, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Frame interno dentro del canvas
        self.frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.frame, anchor="center")

        # Detectar cambios en el tamaño del frame
        self.frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Leer las herramientas y Categorias desde el archivo Excel
        archivo_excel = inventario_path
        df = pd.read_excel(archivo_excel)

        # Rellenar las Categorias NaN con el valor anterior
        df['Categoria'] = df['Categoria'].fillna(method='ffill')

        # Crear un diccionario de Categorias
        herramientas_por_categoria = {}
        for _, row in df.iterrows():
            categoria = row['Categoria']
            herramienta = row['Herramientas']
            if categoria not in herramientas_por_categoria:
                herramientas_por_categoria[categoria] = []
            herramientas_por_categoria[categoria].append(herramienta)

        self.seleccion_herramientas = {}
        estilo = ttk.Style()
        estilo.configure(
            "Tactil.TCheckbutton",
            font=("Arial", 12),  # Ajusta la fuente según el diseño
            padding=5
        )

        # Crear las Categorias y checkboxes
        for categoria, herramientas in herramientas_por_categoria.items():
            # Label de la Categoria
            ttk.Label(
                self.frame,
                text=categoria,
                font=("Arial", 14, "bold")
            ).pack(anchor="w", pady=(15, 5))  # Espaciado extra antes de cada Categoria

            # Crear los checkboxes para las herramientas de esta Categoria
            for herramienta in herramientas:
                var = tk.BooleanVar(value=False)
                self.seleccion_herramientas[herramienta] = var
                checkbox = ttk.Checkbutton(
                    self.frame,
                    text=herramienta,
                    variable=var,
                    style="Tactil.TCheckbutton"
                )
                checkbox.pack(anchor="w", padx=20, pady=2)  # Aumentar margen para alineación clara 

        # Botón "Listo"
        btn_guardar = ttk.Button(
            self.tool_window,
            text="Listo",
            command=self.guardar_seleccion,
            style="Tactil.TButton"
        )
        btn_guardar.pack(pady=20)

    def guardar_seleccion(self):
        herramientas_seleccionadas = [
            herramienta for herramienta, var in self.seleccion_herramientas.items() if var.get()
        ]
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("registro_herramientas.txt", "a", encoding="utf-8") as file:
            file.write(f"\nUsuario: {self.nombre}\n")
            file.write(f"Fecha y hora: {fecha_hora}\n")
            file.write(f"Herramientas seleccionadas: {', '.join(herramientas_seleccionadas)}\n")
            file.write("-" * 50 + "\n")

        messagebox.showinfo("Confirmación", "Selección guardada correctamente.")
        self.tool_window.destroy()
        self.root.deiconify()

class SistemaPanol:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reconocimiento Facial")
        self.root.attributes('-fullscreen', True)
        self.root.state("zoomed")
        self.root.resizable(False, False)
        self.root.iconbitmap(icon_path)
        self.dataset_dir = "Dataset"
        self.codificaciones = self.cargar_imagenes_alumnos()

        VentanaInicio(self.root, self.codificaciones)

    def cargar_imagenes_alumnos(self):
        codificaciones = {}
        for nombre_alumno in os.listdir(self.dataset_dir):
            alumno_dir = os.path.join(self.dataset_dir, nombre_alumno)
            if os.path.isdir(alumno_dir):
                for imagen_file in os.listdir(alumno_dir):
                    imagen_path = os.path.join(alumno_dir, imagen_file)
                    if imagen_path.lower().endswith((".jpg", ".jpeg", ".png")):
                        imagen = face_recognition.load_image_file(imagen_path)
                        codificacion = face_recognition.face_encodings(imagen)
                        if codificacion:
                            codificaciones[nombre_alumno] = codificacion[0]
                            break
        return codificaciones


if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = SistemaPanol(root)
    root.mainloop()