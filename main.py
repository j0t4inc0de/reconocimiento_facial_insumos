import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import cv2
import face_recognition
import os
from datetime import datetime # type: ignore
from PIL import Image, ImageTk

# Paths
icon_path = "img/icono.ico"
reconociendo_path = "img/reconociendo_rostro.png"

class VentanaInicio:
    def __init__(self, root, codificaciones):
        self.root = root
        self.codificaciones = codificaciones
        self.frame = ttk.Frame(self.root, padding=50)
        self.frame.pack(expand=True)

        # Boton Iniciar
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
            padding=10
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
        self.imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)  # Guardar como atributo de la clase

        self.label_imagen = ttk.Label(self.cam_window, image=self.imagen_tk)
        self.label_imagen.pack(pady=(20, 10))

        #100 ms
        self.cam_window.after(100, self.iniciar_camara)

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
        self.tool_window.iconbitmap(icon_path)
        self.tool_window.attributes('-fullscreen', True)
        self.tool_window.state("zoomed")

        self.frame = ttk.Frame(self.tool_window, padding=50)
        self.frame.pack(expand=True)

        # Bienvenido
        ttk.Label(
            self.frame,
            text=f"Bienvenido, {self.nombre}",
            font=("Arial", 15)  # Aumentar el tamaño de la fuente
        ).pack(pady=10)

        # Lista de herramientas
        herramientas = ["Martillo", "Destornillador", "Llave inglesa", "Taladro", "Sierra"]
        self.seleccion_herramientas = {}

        estilo = ttk.Style()
        estilo.configure(
            "Tactil.TCheckbutton",
            font=("Arial", 15),  # Fuente más grande para los checkboxes
            padding=5  # Relleno interno
        )

        for herramienta in herramientas:
            var = tk.BooleanVar(value=False)
            self.seleccion_herramientas[herramienta] = var
            checkbox = ttk.Checkbutton(
                self.frame,
                text=herramienta,
                variable=var,
                style="Tactil.TCheckbutton"
            )
            checkbox.pack(anchor="w", padx=10, pady=5)  # Espaciado externo para mayor comodidad

        # Boton Listo
        btn_guardar = ttk.Button(
            self.frame,
            text="Listo",
            command=self.guardar_seleccion,
            style="Tactil.TButton"
        )
        btn_guardar.pack(pady=10)

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