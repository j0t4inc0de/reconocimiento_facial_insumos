import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox as mb
from PIL import Image, ImageTk
import os
import shutil

# Ruta de la base de datos y directorio de imágenes
database_path = "Database/inventario.db"
dataset_dir = "Dataset"

# Crear tabla de estudiantes si no existe
def crear_tabla_estudiantes():
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estudiantes (
                rut TEXT INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                dataset_dir TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print("Error al crear la tabla estudiantes:", e)

crear_tabla_estudiantes()

class VentanaRegistroEstudiantes:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro de Estudiantes")
        self.root.geometry("600x400")
        self.root.configure(bg="white")

        ttk.Label(self.root, text="Registro de Estudiantes", font=("Arial", 18)).pack(pady=10)

        # Campo para el RUT
        ttk.Label(self.root, text="RUT:", font=("Arial", 12)).pack(pady=5, anchor="w", padx=20)
        self.rut_entry = ttk.Entry(self.root, font=("Arial", 12))
        self.rut_entry.pack(pady=5, padx=20, fill="x")

        # Campo para el Nombre
        ttk.Label(self.root, text="Nombre Completo:", font=("Arial", 12)).pack(pady=5, anchor="w", padx=20)
        self.nombre_entry = ttk.Entry(self.root, font=("Arial", 12))
        self.nombre_entry.pack(pady=5, padx=20, fill="x")

        # Botón para seleccionar imágenes
        ttk.Button(self.root, text="Seleccionar Imágenes", command=self.seleccionar_imagenes).pack(pady=10)

        self.imagenes_seleccionadas = []  # Lista para almacenar las rutas de imágenes seleccionadas

        # Botón para guardar estudiante
        ttk.Button(self.root, text="Guardar Estudiante", command=self.guardar_estudiante).pack(pady=10)

    def seleccionar_imagenes(self):
        archivos = filedialog.askopenfilenames(
            title="Seleccionar imágenes del estudiante",
            filetypes=[("Imágenes", "*.jpg;*.jpeg;*.png")]
        )
        if archivos:
            self.imagenes_seleccionadas = archivos
            mb.showinfo("Imágenes Seleccionadas", f"Se seleccionaron {len(archivos)} imágenes.")
        else:
            mb.showwarning("Sin Selección", "No seleccionaste ninguna imagen.")

    def guardar_estudiante(self):
        rut = self.rut_entry.get().strip()
        nombre = self.nombre_entry.get().strip()

        if not rut or not nombre:
            mb.showerror("Error", "Debes completar todos los campos.")
            return

        if not self.imagenes_seleccionadas:
            mb.showerror("Error", "Debes seleccionar al menos una imagen.")
            return

        # Crear directorio para el estudiante
        estudiante_dir = os.path.join(dataset_dir, nombre)
        if not os.path.exists(estudiante_dir):
            os.makedirs(estudiante_dir)

        # Copiar imágenes seleccionadas al directorio del estudiante
        for imagen in self.imagenes_seleccionadas:
            shutil.copy(imagen, estudiante_dir)

        # Guardar datos en la base de datos
        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO estudiantes (rut, nombre, dataset_dir) VALUES (?, ?, ?)",
                (rut, nombre, estudiante_dir)
            )
            conn.commit()
            conn.close()

            mb.showinfo("Éxito", "Estudiante registrado correctamente.")

            # Limpiar campos
            self.rut_entry.delete(0, tk.END)
            self.nombre_entry.delete(0, tk.END)
            self.imagenes_seleccionadas = []
        except sqlite3.IntegrityError:
            mb.showerror("Error", "El RUT ya está registrado.")
        except sqlite3.Error as e:
            mb.showerror("Error", f"Ocurrió un error al guardar: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaRegistroEstudiantes(root)
    root.mainloop()
