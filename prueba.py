import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import cv2
import face_recognition
import os
from datetime import datetime
from PIL import Image, ImageTk
import pandas as pd  # Para manejar Excel

# Paths
icon_path = "img/icono.ico"
logo_path = "img/inacap_logo.png"
reconociendo_path = "img/reconociendo_rostro.png"
inventario_path = "Excel/Inventario.xlsx"
ruta_imagenes = "imagenes_carrusel"

class CarruselImagenes:
    def __init__(self, parent, images, interval=2000):
        self.parent = parent
        self.images = images
        self.interval = interval
        self.current_index = 0

        self.frame = ttk.Frame(self.parent)
        self.frame.pack()
        self.label = tk.Label(self.frame)
        self.label.pack()

        self.loaded_images = [
            ImageTk.PhotoImage(Image.open(img).resize((1000, 400)))
            for img in self.images
        ]
        self.show_image()

    def show_image(self):
        self.label.config(image=self.loaded_images[self.current_index])
        self.current_index = (self.current_index + 1) % len(self.loaded_images)
        self.parent.after(self.interval, self.show_image)

class VentanaInicio:
    def __init__(self, root, codificaciones):
        self.root = root
        self.root.configure(bg="white")
        self.codificaciones = codificaciones

        # Frame
        estilo_frame = ttk.Style()
        estilo_frame.configure("Custom.TFrame", background="#ffffff")

        self.frame = ttk.Frame(self.root, padding=50, style="Custom.TFrame")
        self.frame.pack(expand=True)

        # Logo INACAP
        try:
            logo_img = Image.open(logo_path).resize((300, 100))
            self.logo_tk = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(self.frame, image=self.logo_tk, bg="white")
            logo_label.pack(pady=(0, 0))
        except Exception as e:
            tk.Label(self.frame, text="No se pudo cargar el logo.", bg="white").pack()

        # Carrusel de imágenes
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
            width=17,
            style="Tactil.TButton"
        )
        estilo = ttk.Style()
        estilo.configure(
            "Tactil.TButton",
            font=("Arial", 12),
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
        self.cam_window.after(20, self.iniciar_camara)

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
                cv2.imshow("Camara", frame)
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

        marco_principal = ttk.Frame(self.tool_window)
        marco_principal.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(marco_principal)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(marco_principal, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.frame, anchor="center")

        self.frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        archivo_excel = inventario_path
        df = pd.read_excel(archivo_excel)
        df['Categoria'] = df['Categoria'].fillna(method='ffill')

        herramientas_por_categoria = {}
        for _, row in df.iterrows():
            categoria = row['Categoria']
            herramienta = row['Herramientas']
            if categoria not in herramientas_por_categoria:
                herramientas_por_categoria[categoria] = []
            herramientas_por_categoria[categoria].append(herramienta)

        self.seleccion_herramientas = {}
        for categoria, herramientas in herramientas_por_categoria.items():
            ttk.Label(self.frame, text=categoria, font=("Arial", 14, "bold")).pack(anchor="w", pady=(15, 5))
            for herramienta in herramientas:
                var = tk.BooleanVar(value=False)
                self.seleccion_herramientas[herramienta] = var
                ttk.Checkbutton(
                    self.frame,
                    text=herramienta,
                    variable=var
                ).pack(anchor="w", padx=20, pady=2)

        # Campo de código de barras
        self.codigo_barra_var = tk.StringVar()
        ttk.Label(self.tool_window, text="Registrar código de barras:", font=("Arial", 12)).pack(pady=5)
        self.entry_codigo_barra = ttk.Entry(self.tool_window, textvariable=self.codigo_barra_var, font=("Arial", 12))
        self.entry_codigo_barra.pack(pady=5)
        ttk.Button(
            self.tool_window,
            text="Agregar Código",
            command=self.agregar_codigo_barra
        ).pack(pady=10)

        ttk.Button(
            self.tool_window,
            text="Listo",
            command=self.guardar_seleccion
        ).pack(pady=20)

    def agregar_codigo_barra(self):
        codigo = self.codigo_barra_var.get().strip()
        if codigo:
            with open("codigos_de_barra.txt", "a", encoding="utf-8") as file:
                file.write(f"{codigo}\n")
            messagebox.showinfo("Código de barras", f"Código {codigo} registrado correctamente.")
            self.codigo_barra_var.set("")
        else:
            messagebox.showwarning("Advertencia", "Debe ingresar un código de barras válido.")

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

def cargar_codificaciones():
    codificaciones = {}
    carpeta = "Personas"
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".jpg") or archivo.endswith(".png"):
            imagen_path = os.path.join(carpeta, archivo)
            imagen = face_recognition.load_image_file(imagen_path)
            codificacion = face_recognition.face_encodings(imagen)[0]
            nombre = os.path.splitext(archivo)[0]
            codificaciones[nombre] = codificacion
    return codificaciones

if __name__ == "__main__":
    root = ThemedTk(theme="clam")
    root.title("Registro Facial")
    root.iconbitmap(icon_path)
    root.geometry("800x600")
    root.state("zoomed")
    codificaciones = cargar_codificaciones()
    VentanaInicio(root, codificaciones)
    root.mainloop()
