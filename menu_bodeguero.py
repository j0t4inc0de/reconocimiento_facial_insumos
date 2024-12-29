import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox as mb
import os
import shutil

# Ruta de la base de datos y directorio de imágenes

# database_path = "C:/Users/FabLab1/Desktop/Sistema Panol - 7/Database/inventario.db"
# dataset_dir = "C:/Users/FabLab1/Desktop/Sistema Panol - 7/Dataset"
# database_path = "Database/inventario.db"
# dataset_dir = "Dataset"
database_path = "E:/OneDrive/OneDrive - INACAP/Desktop/Ficheros Panol/reconocimiento_facial_insumos-4/Database/inventario.db"
dataset_dir = "E:/OneDrive/OneDrive - INACAP/Desktop/Ficheros Panol/reconocimiento_facial_insumos-4/Dataset"

icon_path = "icono.ico"
class VentanaInicio(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        ttk.Label(self, text="Lista de Pedidos", font=("Arial", 18)).pack(pady=10)

        # Style letras mas grande
        style = ttk.Style()
        style.configure('Treeview', font=('Arial', 11))
        style.configure('Treeview.Heading', font=('Arial', 12))

        columnas = ("id", "usuario", "fechaHora", "herramientas", "estado")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings", style='Treeview')
        self.tree.heading("id", text="N° Pedido")
        self.tree.heading("usuario", text="Usuario")
        self.tree.heading("fechaHora", text="Fecha y Hora")
        self.tree.heading("herramientas", text="Herramientas")
        self.tree.heading("estado", text="Estado")

        self.tree.column("id", width=2, anchor="center")
        self.tree.column("usuario", width=90, anchor="center")
        self.tree.column("fechaHora", width=110, anchor="center")
        self.tree.column("herramientas", width=500, anchor="center")
        self.tree.column("estado", width=90, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Cargar los datos desde la base de datos
        self.cargar_pedidos()

    def cargar_pedidos(self):
        """Carga los datos de la tabla 'pedidos' en el Treeview."""
        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pedidos")
            registros = cursor.fetchall()
            conn.close()
            for registro in registros:
                self.tree.insert("", "end", values=registro)

        except sqlite3.Error as e:
            mb.showerror("Error", f"Ocurrió un error al cargar los pedidos: {e}")
            
class VentanaHistorial(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        ttk.Label(self, text="Historial", font=("Arial", 18)).pack(pady=10)

        columnas = ("N° Pedido", "herramientas", "fechaHora")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings")
        
        self.tree.heading("N° Pedido", text="N° Pedido")
        self.tree.heading("fechaHora", text="Fecha y Hora")
        self.tree.heading("herramientas", text="Herramientas")
        self.tree.heading("fechaHora", text="fechaHora")
        self.tree.column("N° Pedido", width=20, anchor="center")
        self.tree.column("herramientas", width=550, anchor="center")
        self.tree.column("fechaHora", width=50, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.cargar_pedidos()

    def cargar_pedidos(self):
        """Carga los datos de la tabla 'pedidos' en el Treeview."""
        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()

            cursor.execute("SELECT pedido_id, herramientas, fechaHora FROM historial")
            registros = cursor.fetchall()
            conn.close()
            for registro in registros:
                self.tree.insert("", "end", values=registro)

        except sqlite3.Error as e:
            mb.showerror("Error", f"Ocurrió un error al cargar los pedidos: {e}")

class VentanaEscaner(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Solicitar contraseña al abrir la ventana
        self.solicitar_contrasena()

        # Contenido de la ventana
        ttk.Label(self, text="Escaneo de Herramientas", font=("Arial", 18)).pack(pady=10)

        # Entrada para el ID del pedido
        ttk.Label(self, text="Ingresa el ID del pedido:", font=("Arial", 12)).pack(pady=5)
        self.id_pedido_entry = ttk.Entry(self, font=("Arial", 12))
        self.id_pedido_entry.pack(pady=5, padx=20, fill="x")

        # Botón para buscar pedido
        ttk.Button(self, text="Buscar Pedido", command=self.buscar_pedido).pack(pady=10)

        # Lista de herramientas solicitadas
        self.lista_herramientas_label = ttk.Label(self, text="", font=("Arial", 12), wraplength=800, justify="left")
        self.lista_herramientas_label.pack(pady=10)

        # Campo para el escaneo de herramientas
        ttk.Label(self, text="Escanea las herramientas solicitadas:", font=("Arial", 12)).pack(pady=5)
        self.herramienta_entry = ttk.Entry(self, font=("Arial", 12))
        self.herramienta_entry.pack(pady=5, padx=20, fill="x")
        self.herramienta_entry.bind("<Return>", self.registrar_herramienta)  # Detectar cuando se escanea una herramienta

        # Lista de herramientas escaneadas con sus códigos
        self.herramientas_escaneadas_label = ttk.Label(self, text="", font=("Arial", 12), wraplength=800, justify="left")
        self.herramientas_escaneadas_label.pack(pady=10)

        # Botón para finalizar pedido
        self.finalizar_btn = ttk.Button(self, text="Finalizar Pedido", command=self.finalizar_pedido, state="disabled")
        self.finalizar_btn.pack(pady=10)

        # Mensaje de confirmación
        self.mensaje_label = ttk.Label(self, text="", font=("Arial", 12), foreground="green")
        self.mensaje_label.pack(pady=10)

        self.herramientas_solicitadas = []  # Lista de herramientas solicitadas en el pedido
        self.herramientas_escaneadas = []  # Lista de códigos escaneados (ordenados)
        self.pedido_id = None  # ID del pedido actual

    def solicitar_contrasena(self):
        """Solicita una contraseña antes de permitir el acceso a la ventana."""
        # Bandera para evitar que el mensaje de error se muestre varias veces
        self.mostrando_error = False

        def validar_contrasena(event=None):  # Permitir que funcione tanto con un clic como con ENTER
            contrasena = contrasena_entry.get()
            if contrasena == "2003":  # Contraseña esperada
                modal.destroy()  # Cerrar la ventana modal
            else:
                if not self.mostrando_error:
                    self.mostrando_error = True  # Marcar que se está mostrando el error
                    mb.showerror("Error", "Contraseña incorrecta.")
                    self.mostrando_error = False  # Resetear la bandera después de cerrarlo
                # Limpiar el campo de contraseña para intentarlo de nuevo
                contrasena_entry.delete(0, tk.END)

        def cerrar_modal():
            # Usamos una bandera para evitar cuadros de diálogo duplicados
            if not hasattr(cerrar_modal, "ya_mostrado"):
                cerrar_modal.ya_mostrado = True  # Marcar que ya se mostró el cuadro de advertencia
                mb.showwarning("Advertencia", "Debe ingresar la contraseña para continuar.")
                cerrar_modal.ya_mostrado = False  # Resetear la bandera después de cerrarlo

        # Crear una ventana modal
        modal = tk.Toplevel(self)
        modal.title("Autenticación")
        modal.geometry("300x150")
        modal.transient(self)  # Mantener la ventana sobre su ventana principal
        modal.grab_set()  # Bloquear interacción con la ventana principal

        ttk.Label(modal, text="Ingrese la contraseña (4 dígitos):", font=("Arial", 12)).pack(pady=10)
        contrasena_entry = ttk.Entry(modal, font=("Arial", 12), show="*")
        contrasena_entry.pack(pady=5, padx=20, fill="x")

        # Vincular la tecla ENTER al botón "Aceptar"
        contrasena_entry.bind("<Return>", validar_contrasena)

        ttk.Button(modal, text="Aceptar", command=validar_contrasena).pack(pady=10)

        # Deshabilitar el cierre directo de la ventana modal
        modal.protocol("WM_DELETE_WINDOW", cerrar_modal)

        # Pausar la ejecución de la ventana principal hasta que la modal sea cerrada correctamente
        self.wait_window(modal)

    def buscar_pedido(self):
        """Verifica si el pedido existe y obtiene su lista de herramientas."""
        pedido_id = self.id_pedido_entry.get().strip()
        if not pedido_id.isdigit():
            mb.showerror("Error", "El ID del pedido debe ser un número.")
            return

        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            # Buscar el pedido
            cursor.execute("SELECT herramientas, estado FROM pedidos WHERE id = ?", (pedido_id,))
            pedido = cursor.fetchone()
            conn.close()

            if pedido is None:
                mb.showerror("Error", f"El pedido con ID {pedido_id} no existe.")
                return

            herramientas, estado = pedido
            if estado == "FINALIZADO":
                mb.showinfo("Pedido Finalizado", f"El pedido con ID {pedido_id} ya está finalizado.")
                return

            # Mostrar herramientas asociadas al pedido
            self.herramientas_solicitadas = herramientas.split(",")
            self.lista_herramientas_label.config(
                text=f"Herramientas solicitadas: {', '.join(self.herramientas_solicitadas)}\n\n"
                     f"Escanea cada herramienta en el orden solicitado."
            )
            self.herramientas_escaneadas = []
            self.finalizar_btn.config(state="normal")
            self.pedido_id = pedido_id  # Guardar ID del pedido para usarlo más tarde

        except sqlite3.Error as e:
            mb.showerror("Error", f"Ocurrió un error al buscar el pedido: {e}")

    def registrar_herramienta(self, event):
        """Registra consecutivamente un código de herramienta escaneado."""
        herramienta_codigo = self.herramienta_entry.get().strip()
        self.herramienta_entry.delete(0, tk.END)  # Limpiar campo de entrada

        if not herramienta_codigo:
            return

        # Verificar si hay más herramientas por escanear
        if len(self.herramientas_escaneadas) >= len(self.herramientas_solicitadas):
            mb.showwarning("Escaneo Completado", "Ya se han registrado todas las herramientas solicitadas.")
            return

        # Asociar el código escaneado a la herramienta correspondiente
        herramienta_actual = self.herramientas_solicitadas[len(self.herramientas_escaneadas)]
        self.herramientas_escaneadas.append((herramienta_actual, herramienta_codigo))

        # Mostrar mensaje de confirmación
        mb.showinfo("Herramienta Registrada", f"Herramienta '{herramienta_actual}' asociada con código '{herramienta_codigo}'.")

        # Actualizar la lista de herramientas escaneadas
        herramientas_escaneadas_texto = "\n".join([f"{herr}: {cod}" for herr, cod in self.herramientas_escaneadas])
        self.herramientas_escaneadas_label.config(text=f"Herramientas escaneadas:\n{herramientas_escaneadas_texto}")

    def finalizar_pedido(self):
        """Marca el pedido como finalizado y registra la salida de las herramientas."""
        if len(self.herramientas_escaneadas) != len(self.herramientas_solicitadas):
            mb.showerror("Error", "Debes escanear todas las herramientas solicitadas antes de finalizar.")
            return

        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()

            # Actualizar el estado del pedido a "FINALIZADO"
            cursor.execute("UPDATE pedidos SET estado = 'FINALIZADO' WHERE id = ?", (self.pedido_id,))

            # Guardar en la tabla historial
            herramientas_finalizadas = ", ".join([f"{herr}: {cod}" for herr, cod in self.herramientas_escaneadas])
            cursor.execute(
                "INSERT INTO historial (pedido_id, herramientas, fechaHora) VALUES (?, ?, datetime('now'))",
                (self.pedido_id, herramientas_finalizadas)
            )
            conn.commit()
            conn.close()

            # Mostrar mensaje de éxito
            self.mensaje_label.config(
                text=f"PEDIDO: N°{self.pedido_id}, HERRAMIENTAS: {herramientas_finalizadas}"
            )
            mb.showinfo("Pedido Finalizado", f"PEDIDO: N°{self.pedido_id}, HERRAMIENTAS: {herramientas_finalizadas}")
            self.finalizar_btn.config(state="disabled")

        except sqlite3.Error as e:
            mb.showerror("Error", f"Ocurrió un error al finalizar el pedido: {e}")

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

        # Copiar imágenes seleccionadas a la carpeta del estudiante
        try:
            for imagen in self.imagenes_seleccionadas:
                nombre_archivo = os.path.basename(imagen)  # Obtener el nombre del archivo
                destino = os.path.join(estudiante_dir, nombre_archivo)  # Ruta destino en la carpeta del estudiante
                shutil.copy2(imagen, destino)  # Copiar la imagen al destino
        except Exception as e:
            mb.showerror("Error", f"Ocurrió un error al copiar las imágenes: {e}")
            return

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

            mb.showinfo("Éxito", "Estudiante registrado correctamente con sus imágenes.")

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
        self.menu_bar.add_command(label="Pedidos", command=self.mostrar_inicio)
        self.menu_bar.add_command(label="Escanear", command=self.mostrar_escaner)
        self.menu_bar.add_command(label="Historial", command=self.mostrar_historial)
        self.menu_bar.add_command(label="Añadir Estudiante", command=self.mostrar_registro_estudiantes)

        # Contenedor para cambiar entre frames
        self.contenedor = tk.Frame(self)
        self.contenedor.pack(fill="both", expand=True)

        # Diccionario de ventanas
        self.ventanas = {}

        # Cargar la ventana inicial
        self.mostrar_inicio()

    def mostrar_inicio(self):
        self.cambiar_ventana(VentanaInicio)
        
    def mostrar_escaner(self):
        self.cambiar_ventana(VentanaEscaner)
        
    def mostrar_historial(self):
        self.cambiar_ventana(VentanaHistorial)

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
