import tkinter as tk
from tkinter import ttk, messagebox

from database.conexion import Database
from controllers.distribucion_controller import DistribucionController


def render(workspace, router):
    conn = Database.get_connection()
    controller = DistribucionController(conn)

    frame = ttk.Frame(workspace)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    title_label = ttk.Label(frame, text="Distribución Logística Satélite", font=("Segoe UI", 16, "bold"))
    title_label.pack(anchor=tk.W, pady=(0, 15))

    form_frame = ttk.Frame(frame)
    form_frame.pack(fill=tk.X, padx=10)

    ttk.Label(form_frame, text="Seleccione libro:").grid(row=0, column=0, sticky=tk.W, pady=8)
    libro_combobox = ttk.Combobox(form_frame, state="readonly", width=55)
    libro_combobox.grid(row=0, column=1, pady=8, sticky=tk.W)

    ttk.Label(form_frame, text="Sede destino:").grid(row=1, column=0, sticky=tk.W, pady=8)
    sede_combobox = ttk.Combobox(form_frame, state="readonly", width=55)
    sede_combobox.grid(row=1, column=1, pady=8, sticky=tk.W)

    ttk.Label(form_frame, text="Cantidad a enviar:").grid(row=2, column=0, sticky=tk.W, pady=8)
    cantidad_spinbox = ttk.Spinbox(form_frame, from_=1, to=9999, width=12)
    cantidad_spinbox.set(1)
    cantidad_spinbox.grid(row=2, column=1, pady=8, sticky=tk.W)

    stock_label = ttk.Label(form_frame, text="Stock en Sede Central: 0")
    stock_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

    status_label = ttk.Label(frame, text="", foreground="green")
    status_label.pack(anchor=tk.W, pady=(12, 0), padx=10)

    libros = controller.listar_libros()
    libro_items = [f"{libro['id']} - {libro['titulo']}" for libro in libros]
    libro_combobox["values"] = libro_items
    if libro_items:
        libro_combobox.current(0)

    destinos = controller.listar_destinos()
    destino_items = [f"{destino['id']} - {destino['nombre']}" for destino in destinos]
    sede_combobox["values"] = destino_items
    if destino_items:
        sede_combobox.current(0)

    selected_libro_id = None

    def actualizar_stock(event=None):
        nonlocal selected_libro_id
        seleccionado = libro_combobox.get()
        if not seleccionado:
            stock_label.config(text="Stock en Sede Central: 0")
            return
        selected_libro_id = int(seleccionado.split(" - ")[0])
        stock = controller.obtener_stock_central(selected_libro_id)
        stock_label.config(text=f"Stock en Sede Central: {stock}")

    libro_combobox.bind("<<ComboboxSelected>>", actualizar_stock)
    actualizar_stock()

    def enviar():
        if selected_libro_id is None:
            messagebox.showwarning("Validación", "Seleccione un libro para enviar.")
            return
        cantidad = int(cantidad_spinbox.get())
        destino_text = sede_combobox.get()
        if not destino_text:
            messagebox.showwarning("Validación", "Seleccione una sede de destino.")
            return
        sede_destino_id = int(destino_text.split(" - ")[0])

        try:
            acta = controller.enviar_a_sede(selected_libro_id, cantidad, sede_destino_id)
            status_label.config(text=f"Distribución registrada con acta {acta}.")
            actualizar_stock()
        except Exception as err:
            messagebox.showerror("Error", f"No se pudo completar la distribución:\n{err}")

    enviar_button = ttk.Button(frame, text="Enviar a Sede", command=enviar)
    enviar_button.pack(anchor=tk.W, pady=15, padx=10)
