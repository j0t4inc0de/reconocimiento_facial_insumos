import cv2
import face_recognition
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
from datetime import datetime # type: ignore
import os

# ------------------------
# Clase para reconocimiento facial
# ------------------------
class SistemaDeRegistro:
    def __init__(self, directorio_alumnos="Dataset"):
        self.directorio_alumnos = directorio_alumnos
        self.codificaciones_alumnos = {}
        self.cargar_imagenes_alumnos()

    def cargar_imagenes_alumnos(self):
        for nombre_alumno in os.listdir(self.directorio_alumnos):
            alumno_dir = os.path.join(self.directorio_alumnos, nombre_alumno)
            if os.path.isdir(alumno_dir):
                codificaciones = []
                for imagen_file in os.listdir(alumno_dir):
                    imagen_path = os.path.join(alumno_dir, imagen_file)
                    if imagen_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                        imagen = cv2.imread(imagen_path)
                        imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
                        codificacion = face_recognition.face_encodings(imagen)
                        if codificacion:
                            codificaciones.append(codificacion[0])
                if codificaciones:
                    self.codificaciones_alumnos[nombre_alumno] = sum(codificaciones) / len(codificaciones)

    def iniciar_reconocimiento(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            ubicaciones = face_recognition.face_locations(frame)
            codificaciones = face_recognition.face_encodings(frame, ubicaciones)

            for codificacion in codificaciones:
                for nombre, codificacion_ref in self.codificaciones_alumnos.items():
                    if face_recognition.compare_faces([codificacion_ref], codificacion)[0]:
                        cap.release()
                        cv2.destroyAllWindows()
                        return nombre  # Retorna el nombre del usuario identificado

            cv2.imshow("Reconocimiento Facial", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return None  # No se identificó a nadie

# ------------------------
# Interfaz gráfica
# ------------------------
class InterfazHerramientas:
    def __init__(self, usuario):
        self.usuario = usuario
        self.root = ThemedTk(theme="yaru")
        self.root.title("Interfaz de Herramientas")
        self.root.geometry("800x1080")
        self.root.configure(bg="white")

        self.crear_interfaz()
        self.root.mainloop()

    def crear_interfaz(self):
        tk.Label(self.root, text=f"Usuario: {self.usuario}", bg="white", font=("Arial", 14, "bold")).pack(pady=10)

        # Lista de herramientas
        tools = [f"Herramienta {i+1}" for i in range(10)]
        self.seleccion = []

        frame_tools = tk.Frame(self.root, bg="white")
        frame_tools.pack(pady=10)

        for tool in tools:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(
                frame_tools, text=tool, variable=var, bg="white", font=("Arial", 12)
            )
            chk.pack(anchor="w")
            self.seleccion.append((tool, var))

        ttk.Button(self.root, text="Confirmar", command=self.confirmar_seleccion).pack(pady=10)

    def confirmar_seleccion(self):
        herramientas_seleccionadas = [tool for tool, var in self.seleccion if var.get()]
        with open("registro_herramientas.txt", "a") as f:
            f.write(f"{datetime.now()} - {self.usuario} seleccionó: {', '.join(herramientas_seleccionadas)}\n")
        print(f"Herramientas seleccionadas por {self.usuario}: {herramientas_seleccionadas}")
        self.root.destroy()

# ------------------------
# Ejecución principal
# ------------------------
if __name__ == "__main__":
    sistema = SistemaDeRegistro()
    usuario = sistema.iniciar_reconocimiento()

    if usuario:
        InterfazHerramientas(usuario)
    else:
        print("No se identificó a ningún usuario.")
