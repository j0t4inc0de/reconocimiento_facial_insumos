import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class GestionHerramientas:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Herramientas")

        # Datos simulados
        self.categorias = {
            "Carpintería": [
                {"nombre": "Martillo", "stock": 5},
                {"nombre": "Sierra", "stock": 2},
                {"nombre": "Destornillador", "stock": 10}
            ],
            "Jardinería": [
                {"nombre": "Pala", "stock": 3},
                {"nombre": "Rastrillo", "stock": 1},
                {"nombre": "Tijeras de podar", "stock": 4}
            ]
        }

        self.crear_interfaz()

    def crear_interfaz(self):
        # Contenedor principal
        frame_principal = ttk.Frame(self.root, padding="10")
        frame_principal.grid(row=0, column=0, sticky="NSEW")

        # Label de título
        ttk.Label(frame_principal, text="Categorías de herramientas", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=10)

        # Lista desplegable de categorías
        self.categoria_seleccionada = tk.StringVar()
        self.categoria_combobox = ttk.Combobox(
            frame_principal, textvariable=self.categoria_seleccionada, state="readonly"
        )
        self.categoria_combobox["values"] = list(self.categorias.keys())
        self.categoria_combobox.grid(row=1, column=0, pady=10)
        self.categoria_combobox.bind("<<ComboboxSelected>>", self.mostrar_herramientas)

        # Frame para mostrar herramientas
        self.frame_herramientas = ttk.Frame(frame_principal, padding="10", borderwidth=2, relief="groove")
        self.frame_herramientas.grid(row=2, column=0, pady=10, sticky="NSEW")

        # Botón de salir
        ttk.Button(frame_principal, text="Salir", command=self.root.quit).grid(row=3, column=0, pady=10)

    def mostrar_herramientas(self, event):
        # Limpiar el contenido previo del frame
        for widget in self.frame_herramientas.winfo_children():
            widget.destroy()

        # Obtener la categoría seleccionada
        categoria = self.categoria_seleccionada.get()
        herramientas = self.categorias.get(categoria, [])

        # Encabezados de columnas
        ttk.Label(self.frame_herramientas, text="Herramienta", font=("Arial", 12, "bold"), anchor="center").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.frame_herramientas, text="Disponibles", font=("Arial", 12, "bold"), anchor="center").grid(row=0, column=1, padx=5, pady=5)

        # Mostrar herramientas y existencias
        for i, herramienta in enumerate(herramientas):
            ttk.Label(self.frame_herramientas, text=herramienta["nombre"], anchor="w").grid(row=i+1, column=0, padx=5, pady=5, sticky="W")
            ttk.Label(self.frame_herramientas, text=str(herramienta["stock"]), anchor="center").grid(row=i+1, column=1, padx=5, pady=5, sticky="E")

if __name__ == "__main__":
    root = tk.Tk()
    app = GestionHerramientas(root)
    root.mainloop()
