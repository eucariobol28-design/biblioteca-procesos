import tkinter as tk
from tkinter import ttk, messagebox

from database.conexion import Database
from controllers.recepcion_controller import RecepcionController


def render(workspace, router):
    conn = Database.get_connection()
    controller = RecepcionController(conn)

    form_frame = ttk.Frame(workspace)
    form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    ttk.Label(form_frame, text="Recepción de Libros", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky=tk.W)

    ttk.Label(form_frame, text="Título:").grid(row=1, column=0, sticky=tk.W, pady=6)
    titulo_entry = ttk.Entry(form_frame, width=60)
    titulo_entry.grid(row=1, column=1, sticky=tk.W, pady=6)

    ttk.Label(form_frame, text="Autor:").grid(row=2, column=0, sticky=tk.W, pady=6)
    autor_entry = ttk.Entry(form_frame, width=60)
    autor_entry.grid(row=2, column=1, sticky=tk.W, pady=6)

    ttk.Label(form_frame, text="Código Dewey:").grid(row=3, column=0, sticky=tk.W, pady=6)
    dewey_entry = ttk.Entry(form_frame, width=30)
    dewey_entry.grid(row=3, column=1, sticky=tk.W, pady=6)

    ttk.Label(form_frame, text="ISBN:").grid(row=4, column=0, sticky=tk.W, pady=6)
    isbn_entry = ttk.Entry(form_frame, width=30)
    isbn_entry.grid(row=4, column=1, sticky=tk.W, pady=6)

    ttk.Label(form_frame, text="Origen del ejemplar:").grid(row=5, column=0, sticky=tk.W, pady=6)
    origen_combobox = ttk.Combobox(form_frame, state="readonly", width=45)
    origen_combobox.grid(row=5, column=1, sticky=tk.W, pady=6)

    ttk.Label(form_frame, text="Cantidad:").grid(row=6, column=0, sticky=tk.W, pady=6)
    cantidad_spinbox = ttk.Spinbox(form_frame, from_=1, to=9999, width=10)
    cantidad_spinbox.set(1)
    cantidad_spinbox.grid(row=6, column=1, sticky=tk.W, pady=6)

    status_label = ttk.Label(form_frame, text="", foreground="green")
    status_label.grid(row=7, column=0, columnspan=2, pady=10, sticky=tk.W)

    origenes = controller.cargar_origenes()
    origen_map = {str(item["id"]): item["nombre"] for item in origenes}
    origen_names = [item["nombre"] for item in origenes]
    origen_combobox["values"] = origen_names
    if origen_names:
        origen_combobox.current(0)

    def guardar():
        titulo = titulo_entry.get().strip()
        autor = autor_entry.get().strip()
        codigo_dewey = dewey_entry.get().strip()
        isbn = isbn_entry.get().strip()
        cantidad = int(cantidad_spinbox.get())
        origen_nombre = origen_combobox.get().strip()
        origen_id = next((item["id"] for item in origenes if item["nombre"] == origen_nombre), None)

        if not titulo or not autor or not codigo_dewey or not isbn or origen_id is None:
            messagebox.showwarning("Validación", "Complete todos los campos antes de guardar.")
            return

        try:
            controller.guardar_libro(titulo, autor, codigo_dewey, isbn, origen_id, cantidad)
            status_label.config(text="Libro recibido y stock inicializado en Sede Central.")
            titulo_entry.delete(0, tk.END)
            autor_entry.delete(0, tk.END)
            dewey_entry.delete(0, tk.END)
            isbn_entry.delete(0, tk.END)
            cantidad_spinbox.set(1)
        except Exception as err:
            messagebox.showerror("Error", f"No se pudo guardar el libro:\n{err}")

    guardar_button = ttk.Button(form_frame, text="Guardar Recepción", command=guardar)
    guardar_button.grid(row=8, column=0, columnspan=2, pady=15)

