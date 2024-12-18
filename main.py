import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from ttkthemes import ThemedTk
import cv2
import face_recognition
import os
from datetime import datetime # type: ignore
from PIL import Image, ImageTk
import pandas as pd  # Nueva importación para manejar Excel tambien el modulo openpyxl
import time

# Paths
icon_path = "img/icono.ico"
logo_path = "img/inacap_logo.png"
reconociendo_path = "img/reconociendo_rostro.png"
inventario_path = "Excel/Inventario.xlsx"
database_path = "inventario.db"

class VentanaInicio:
    def __init__(self, root, codificaciones):
        self.root = root
        self.root.configure(bg="white")
        self.codificaciones = codificaciones
        
        print("- - - - - - - - - - - - - - -\nSe abrio Ventana Inicio\n- - - - - - - - - - - - - - - \n") # Validacion
        
        # Frame
        estilo_frame = ttk.Style()
        estilo_frame.configure("Custom.TFrame", background="#ffffff")

        self.frame = ttk.Frame(self.root, padding=50, style="Custom.TFrame")
        self.frame.pack(expand=True)
        
        # Logo INACAP
        try:
            logo_img = Image.open(logo_path)
            logo_img.thumbnail((800, 350)) # Ancho, Alto
            self.logo_tk = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(self.frame, image=self.logo_tk, bg="white")
            logo_label.pack(pady=(0, 28))
        except Exception as e:
            tk.Label(self.frame, text="No se pudo cargar el logo.", bg="white").pack()

        # Botón Iniciar
        btn_iniciar = tk.Button(
            self.frame,
            text="Iniciar",
            command=self.abrir_ventana_camara,
            font=("Arial", 14, "bold"),  # Tamaño y estilo de la fuente
            bg="red",                    # Fondo rojo
            fg="white",                  # Texto blanco
            activebackground="#cc0000",  # Fondo rojo más oscuro al presionar
            activeforeground="white",    # Texto blanco al presionar
            relief="raised",             # Estilo de borde
            width=20,                    # Ancho del botón
            height=2                     # Alto del botón
        )
        btn_iniciar.pack(padx=5, pady=5)

    def abrir_ventana_camara(self):
        print("- - - - - - - - - - - - - - -\nSe abrirá la Ventana Camara\n- - - - - - - - - - - - - - - \n") # Validacion
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

        print("- - - - - - - - - - - - - - -\nSe abrio Ventana Camara\n- - - - - - - - - - - - - - - \n") # Validacion
        
        self.lbl_status = ttk.Label(self.cam_window, text="Detectando rostro...", background="white", font=("Arial", 16))
        self.lbl_status.pack(pady=20)
        
        imagen_original = Image.open(reconociendo_path).convert("RGB")
        imagen_redimensionada = imagen_original.resize((800, 800))
        self.imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)
        self.label_imagen = ttk.Label(self.cam_window, image=self.imagen_tk)
        self.label_imagen.image = self.imagen_tk  # Asegura que no se elimine la referencia
        self.label_imagen.pack(pady=(20, 10))
        self.cam_window.update_idletasks()  # Fuerza la actualización de la ventana

            
        # 50 ms
        self.cam_window.after(20, self.iniciar_camara)

    def iniciar_camara(self):
        print("- - - - - - - - - - - - - - -\nSe abrió la cámara\n- - - - - - - - - - - - - - - \n")  # Validación
        
        cap = cv2.VideoCapture(0)
        reconocida = False
        tiempo_inicio = time.time()
        
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

            tiempo_actual = time.time()
            if tiempo_actual - tiempo_inicio > 10:
                print("Tiempo agotado: No se reconoció a nadie en 10 segundos")
                break

        cap.release()
        cv2.destroyAllWindows()
        self.cam_window.destroy()
        self.root.deiconify()
        print("- - - - - - - - - - - - - - -\nCámara cerrada\n- - - - - - - - - - - - - - - \n")


class VentanaHerramientas:
    def __init__(self, root, nombre):
        self.root = root
        self.nombre = nombre
        self.tool_window = tk.Toplevel(self.root)
        self.tool_window.title("Ventana de Herramientas")
        self.tool_window.geometry("1920x1080")
        self.tool_window.attributes('-fullscreen', True)
        self.tool_window.state("zoomed")

        print("- - - - - - - - - - - - - - -\nSe abrio la Ventana de Herramientas\n- - - - - - - - - - - - - - - \n")

        ttk.Label(
            self.tool_window,
            text=f"Bienvenido, {self.nombre}",
            font=("Arial", 15)
        ).pack(pady=10)

        # Configuración del Canvas y Scrollbar
        marco_principal = ttk.Frame(self.tool_window)
        marco_principal.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(marco_principal)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(marco_principal, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.frame, anchor="center")
        self.frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Leer datos desde SQLite
        database_path = "inventario.db"
        self.seleccion_herramientas = {}
        herramientas_por_categoria = self.obtener_herramientas_por_categoria(database_path)

        # Crear checkboxes y categorías
        estilo = ttk.Style()
        estilo.configure("Tactil.TCheckbutton", font=("Arial", 12), padding=5)

        for categoria, herramientas in herramientas_por_categoria.items():
            # Etiqueta de la categoría
            ttk.Label(
                self.frame,
                text=categoria,
                font=("Arial", 14, "bold")
            ).pack(anchor="w", pady=(15, 5))

            # Checkboxes para cada herramienta
            for herramienta_data in herramientas:
                herramienta = herramienta_data["herramienta"]
                existencias = herramienta_data["existencia"]

                texto_checkbox = f"{herramienta} \t 🡺 \t( {existencias} )"
                var = tk.BooleanVar(value=False)
                self.seleccion_herramientas[herramienta] = var

                checkbox = ttk.Checkbutton(
                    self.frame,
                    text=texto_checkbox,
                    variable=var,
                    style="Tactil.TCheckbutton"
                )
                checkbox.pack(anchor="w", padx=20, pady=2)

        # Botones "Listo" y "Salir" centrados y en fila
        frame_botones = ttk.Frame(self.tool_window)
        frame_botones.pack(pady=20)

        btn_guardar = ttk.Button(frame_botones, text="Listo", command=self.guardar_seleccion)
        btn_guardar.pack(side="left", padx=20)  # Botón "Listo"

        btn_salir = ttk.Button(frame_botones, text="Salir", command=self.salir_ventana_herramientas)
        btn_salir.pack(side="left", padx=20)  # Botón "Salir"

        
    def obtener_herramientas_por_categoria(self, db_path):
        """Consulta la base de datos SQLite y devuelve un diccionario con categorías y herramientas."""
        herramientas_por_categoria = {}

        try:
            # Conexión a la base de datos
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Consulta SQL para obtener todas las herramientas agrupadas por categoría
            query = """
                SELECT Categoria, Herramienta, Existencia
                FROM herramientas
                ORDER BY Categoria;
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

            # Procesar los resultados en un diccionario
            for categoria, herramienta, existencias in resultados:
                if categoria not in herramientas_por_categoria:
                    herramientas_por_categoria[categoria] = []
                herramientas_por_categoria[categoria].append(
                    {"herramienta": herramienta, "existencia": existencias}
                )

            conn.close()
        except sqlite3.Error as e:
            print("Error al conectar a la base de datos:", e)

        return herramientas_por_categoria
    
    def verificar_stock(self, herramientas_seleccionadas):
        """Verifica si las herramientas seleccionadas tienen stock disponible."""
        db_path = "inventario.db"
        herramientas_sin_stock = []

        try:
            # Conexión a la base de datos
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Revisar el stock para cada herramienta seleccionada
            for herramienta in herramientas_seleccionadas:
                cursor.execute("SELECT Existencia FROM herramientas WHERE Herramienta = ?", (herramienta,))
                resultado = cursor.fetchone()

                if resultado and resultado[0] <= 0:
                    herramientas_sin_stock.append(herramienta)

            conn.close()
        except sqlite3.Error as e:
            print("Error al verificar el stock en la base de datos:", e)
            mb.showerror("Error", "Hubo un problema al verificar el stock.")

        return herramientas_sin_stock

    def guardar_seleccion(self):
        print("- - - - - - - - - - - - - - -\n Se apretó el botón 'Listo' \n\tPara guardar selección de herramientas\n- - - - - - - - - - - - - - - -\n")
        herramientas_seleccionadas = [
            herramienta for herramienta, var in self.seleccion_herramientas.items() if var.get()
        ]

        if not herramientas_seleccionadas:
            mb.showwarning("Advertencia", "No has seleccionado ninguna herramienta.")
            return

        # Verificar el stock de las herramientas seleccionadas
        herramientas_sin_stock = self.verificar_stock(herramientas_seleccionadas)

        if herramientas_sin_stock:
            mensaje = f"No puedes seleccionar herramientas sin stock:\n{', '.join(herramientas_sin_stock)}"
            mb.showerror("Error", mensaje)
            print(mensaje)
            return  # Salir del método sin continuar

        # Si todas las herramientas tienen stock, continuar
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        id_ticket = self.generar_id_unico()

        # Actualizar base de datos y descontar existencias
        self.actualizar_existencias(herramientas_seleccionadas)

        # Guardar en archivo de registro
        with open("registro_herramientas.txt", "a", encoding="utf-8") as file:
            file.write("-" * 70 + "\n")
            file.write(f"ID: {id_ticket}\n")
            file.write(f"Usuario: {self.nombre}\n")
            file.write(f"Fecha y hora: {fecha_hora}\n")
            file.write(f"Herramientas seleccionadas: {', '.join(herramientas_seleccionadas)}\n")
            file.write("-" * 70 + "\n")

        mb.showinfo("Confirmación", f"Tienes el pedido Nª{id_ticket} \nVolviendo al menú principal.")
        print(f"Se guardó correctamente la selección con ID {id_ticket}.")
        self.tool_window.destroy()
        self.root.deiconify()

    def salir_ventana_herramientas(self):
        """Cierra la ventana de herramientas y vuelve a la principal."""
        print("Se apretó el botón 'Salir'. Volviendo a la ventana principal.")
        self.tool_window.destroy()  # Cierra la ventana actual
        self.root.deiconify()  # Vuelve a mostrar la ventana principal

    def actualizar_existencias(self, herramientas_seleccionadas):
        """Descuenta las existencias de las herramientas seleccionadas en la base de datos."""
        db_path = "inventario.db"

        try:
            # Conexión a la base de datos
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Actualizar existencias
            for herramienta in herramientas_seleccionadas:
                # Verificar las existencias actuales
                cursor.execute("SELECT Existencia FROM herramientas WHERE Herramienta = ?", (herramienta,))
                resultado = cursor.fetchone()

                if resultado and resultado[0] > 0:
                    nueva_existencia = resultado[0] - 1
                    cursor.execute("UPDATE herramientas SET Existencia = ? WHERE Herramienta = ?", (nueva_existencia, herramienta))
                    print(f"Existencia actualizada para {herramienta}: {nueva_existencia}")
                else:
                    print(f"Advertencia: {herramienta} no tiene existencias disponibles.")
                    mb.showwarning("Sin existencias", f"No hay existencias disponibles para {herramienta}.")

            # Guardar los cambios y cerrar la conexión
            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            print("Error al actualizar la base de datos:", e)
            mb.showerror("Error", "Hubo un problema al actualizar las existencias.")

        
    def generar_id_unico(self):
        # Ruta del archivo para almacenar el último ID
        archivo_id = "contador.txt"
        
        # Leer el último ID del archivo
        if os.path.exists(archivo_id):
            with open(archivo_id, "r", encoding="utf-8") as file:
                ultimo_id = int(file.read().strip())
        else:
            ultimo_id = 0  # Si no existe, iniciar en 0
        
        # Incrementar el ID
        nuevo_id = ultimo_id + 1
        
        # Guardar el nuevo ID en el archivo
        with open(archivo_id, "w", encoding="utf-8") as file:
            file.write(str(nuevo_id))
        
        return nuevo_id

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