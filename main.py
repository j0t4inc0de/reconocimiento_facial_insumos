import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import cv2
import face_recognition
import os
from datetime import datetime # type: ignore

class sistema_panol:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reconocimiento Facial")
        self.root.attributes('-fullscreen',True)
        self.root.state("zoomed")
        self.root.resizable(False, False)
        self.dataset_dir = "Dataset"
        self.codificaciones = self.cargar_imagenes_alumnos()
        self.inicializar_ventana_principal()

    # Ventana 1: Inicio -------------------------------------
    def inicializar_ventana_principal(self):
        frame = ttk.Frame(self.root, padding=50)
        frame.pack(expand=True)

        btn_iniciar = ttk.Button(frame, text="Iniciar", command=self.abrir_ventana_camara)
        btn_iniciar.pack()

    # Ventana 2: Camara -------------------------------------
    def abrir_ventana_camara(self):
        self.root.withdraw()
        cam_window = tk.Toplevel(self.root)
        cam_window.title("Camara")
        cam_window.attributes('-fullscreen',True)
        cam_window.state("zoomed")
        cam_window.configure(bg="white")

        lbl_status = ttk.Label(cam_window, text="Detectando rostro...", background="white", font=("Arial", 16))
        lbl_status.pack(pady=20)

        def iniciar_camara():
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
                            lbl_status.config(text=f"Reconocido: {nombre}")
                            reconocida = True
                            cap.release()
                            cv2.destroyAllWindows()
                            cam_window.destroy()
                            self.abrir_ventana_herramientas(nombre)
                            return

                if not reconocida:
                    lbl_status.config(text="No se reconoce a la persona")
                    cv2.imshow("Cámara", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
            cap.release()
            cv2.destroyAllWindows()
            cam_window.destroy()
            self.root.deiconify()

        cam_window.after(100, iniciar_camara)

    # Ventana 3: Herramientas -------------------------------------
    def abrir_ventana_herramientas(self, nombre):
        tool_window = tk.Toplevel(self.root)
        tool_window.title("Ventana de Herramientas")
        tool_window.geometry("1920x1080")
        # tool_window.attributes('-fullscreen',True)
        tool_window.state("zoomed")
        frame = ttk.Frame(tool_window, padding=50)
        frame.pack(expand=True)

        ttk.Label(frame, text=f"Bienvenido, {nombre}", font=("Arial", 16)).pack(pady=10)

        # Lista de herramientas
        herramientas = ["Martillo", "Destornillador", "Llave inglesa", "Taladro", "Sierra"]
        # Variables para checkboxes
        seleccion_herramientas = {}  # Diccionario para almacenar las variables

        # Checkboxes
        for herramienta in herramientas:
            var = tk.BooleanVar(value=False)  # Crear una variable para el estado del checkbox
            seleccion_herramientas[herramienta] = var  # Guardar la variable en el diccionario
            checkbox = ttk.Checkbutton(frame, text=herramienta, variable=var)  # Vincular el checkbox con la variable
            checkbox.pack(anchor="w", padx=20)

        def guardar_seleccion():
            # Obtener herramientas
            herramientas_seleccionadas = [
                herramienta for herramienta, var in seleccion_herramientas.items() if var.get()
            ]
            # Imprimir
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Usuario: {nombre}\nFecha y hora: {fecha_hora}\nHerramientas seleccionadas: {herramientas_seleccionadas}")

            # Guardar herramientas en 'registro_herramientas.txt'
            with open("registro_herramientas.txt", "a", encoding="utf-8") as file:
                file.write(f"\nUsuario: {nombre}\n")
                file.write(f"Fecha y hora: {fecha_hora}\n")
                file.write(f"Herramientas seleccionadas: {', '.join(herramientas_seleccionadas)}\n")
                file.write("-" * 50 + "\n")

            messagebox.showinfo("Confirmación", "Selección guardada correctamente.")
            tool_window.destroy()
            self.root.deiconify()  # Volver a la Ventana 1

        btn_guardar = ttk.Button(
            frame,
            text="Listo",
            command=guardar_seleccion
        )
        btn_guardar.pack(pady=20)

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
    app = sistema_panol(root)
    root.mainloop()