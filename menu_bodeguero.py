import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox as mb
import os

# Ruta de la base de datos y directorio de imágenes
database_path = "Database/inventario.db"
dataset_dir = "Dataset"

# Crear tabla de pedidos si no existe
def crear_tabla_pedidos():
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY,
                usuario TEXT,
                fechaHora TEXT,
                herramientas TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print("Error al crear la tabla pedidos:", e)

crear_tabla_pedidos()

class VentanaHolaMundo(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Título de la ventana
        ttk.Label(self, text="Lista de Pedidos", font=("Arial", 18)).pack(pady=10)

        # Crear el Treeview
        columnas = ("id", "usuario", "fechaHora", "herramientas", "estado")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings")
        
        # Configurar encabezados
        self.tree.heading("id", text="ID")
        self.tree.heading("usuario", text="Usuario")
        self.tree.heading("fechaHora", text="Fecha y Hora")
        self.tree.heading("herramientas", text="Herramientas")
        self.tree.heading("estado", text="Herramientas")

        # Configurar tamaños de las columnas
        self.tree.column("id", width=15, anchor="center")
        self.tree.column("usuario", width=90, anchor="center")
        self.tree.column("fechaHora", width=100, anchor="center")
        self.tree.column("herramientas", width=450, anchor="center")
        self.tree.column("estado", width=100, anchor="center")

        # Empaquetar el Treeview
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Cargar los datos desde la base de datos
        self.cargar_pedidos()

    def cargar_pedidos(self):
        """Carga los datos de la tabla 'pedidos' en el Treeview."""
        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()

            # Obtener todos los registros de la tabla pedidos
            cursor.execute("SELECT * FROM pedidos")
            registros = cursor.fetchall()
            conn.close()

            # Insertar los registros en el Treeview
            for registro in registros:
                self.tree.insert("", "end", values=registro)

        except sqlite3.Error as e:
            mb.showerror("Error", f"Ocurrió un error al cargar los pedidos: {e}")

class VentanaEscaner(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="¡Soy la ventana del escáner, para escanear códigos de barra de herramientas!", font=("Arial", 18)).pack(expand=True, pady=50)

class VentanaRegistroEstudiantes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        ttk.Label(self, text="Registro de Estudiantes", font=("Arial", 18)).pack(pady=10)

        # Campo para el RUT
        ttk.Label(self, text="RUT:", font=("Arial", 12)).pack(pady=5, anchor="w", padx=20)
        self.rut_entry = ttk.Entry(self, font=("Arial", 12))
        self.rut_entry.pack(pady=5, padx=20, fill="x")

        # Campo para el Nombre
        ttk.Label(self, text="Nombre Completo:", font=("Arial", 12)).pack(pady=5, anchor="w", padx=20)
        self.nombre_entry = ttk.Entry(self, font=("Arial", 12))
        self.nombre_entry.pack(pady=5, padx=20, fill="x")

        # Botón para seleccionar imágenes
        ttk.Button(self, text="Seleccionar Imágenes", command=self.seleccionar_imagenes).pack(pady=10)

        self.imagenes_seleccionadas = []  # Lista para almacenar las rutas de imágenes seleccionadas

        # Botón para guardar estudiante
        ttk.Button(self, text="Guardar Estudiante", command=self.guardar_estudiante).pack(pady=10)

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

class AplicacionPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicación Principal")
        self.geometry("1080x720")

        # Crear el menú principal
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # Añadir opciones al menú principal
        self.menu_bar.add_command(label="Pedidos", command=self.mostrar_hola_mundo)
        self.menu_bar.add_command(label="Escanear", command=self.mostrar_escaner)
        self.menu_bar.add_command(label="Añadir Estudiante", command=self.mostrar_registro_estudiantes)

        # Contenedor para cambiar entre frames
        self.contenedor = tk.Frame(self)
        self.contenedor.pack(fill="both", expand=True)

        # Diccionario de ventanas
        self.ventanas = {}

        # Cargar la ventana inicial
        self.mostrar_hola_mundo()

    def mostrar_hola_mundo(self):
        self.cambiar_ventana(VentanaHolaMundo)
        
    def mostrar_escaner(self):
        self.cambiar_ventana(VentanaEscaner)

    def mostrar_registro_estudiantes(self):
        self.cambiar_ventana(VentanaRegistroEstudiantes)

    def cambiar_ventana(self, ventana_clase):
        # Eliminar el frame anterior, si existe
        for widget in self.contenedor.winfo_children():
            widget.destroy()

        # Crear e inicializar la nueva ventana
        nueva_ventana = ventana_clase(self.contenedor)
        nueva_ventana.pack(fill="both", expand=True)
        self.ventanas[ventana_clase] = nueva_ventana

if __name__ == "__main__":
    app = AplicacionPrincipal()
    app.mainloop()
