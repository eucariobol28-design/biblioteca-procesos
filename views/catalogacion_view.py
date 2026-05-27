import tkinter as tk
from tkinter import ttk, messagebox

from database.conexion import Database
from controllers.catalogacion_controller import CatalogacionController


def render(workspace, router):
    conn = Database.get_connection()
    controller = CatalogacionController(conn)

    container = ttk.Frame(workspace)
    container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    title_label = ttk.Label(container, text="Catalogación y Cota Automática", font=("Segoe UI", 16, "bold"))
    title_label.pack(anchor=tk.W, pady=(0, 15))

    top_frame = ttk.Frame(container)
    top_frame.pack(fill=tk.BOTH, expand=True)

    tree_frame = ttk.Frame(top_frame)
    tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    columns = ("id", "titulo", "autor", "codigo_dewey", "isbn", "origen", "cota")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse", height=18)
    for col in columns:
        tree.heading(col, text=col.capitalize())
        width = 120 if col == "titulo" else 90
        if col in ("autor", "origen"):
            width = 140
        tree.column(col, width=width, anchor=tk.W)

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    detail_frame = ttk.Frame(top_frame)
    detail_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

    ttk.Label(detail_frame, text="Libro seleccionado:", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
    selected_label = ttk.Label(detail_frame, text="Ninguno", wraplength=260)
    selected_label.pack(anchor=tk.W, pady=(0, 10))

    ttk.Label(detail_frame, text="Cota calculada:").pack(anchor=tk.W, pady=(10, 2))
    cota_entry = ttk.Entry(detail_frame, width=40)
    cota_entry.pack(anchor=tk.W)

    status_label = ttk.Label(detail_frame, text="", foreground="green")
    status_label.pack(anchor=tk.W, pady=(10, 0))

    def cargar_libros():
        for row in tree.get_children():
            tree.delete(row)
        for libro in controller.listar_libros():
            tree.insert(
                "",
                tk.END,
                values=(
                    libro["id"],
                    libro["titulo"],
                    libro["autor"],
                    libro["codigo_dewey"],
                    libro["isbn"],
                    libro["origen"],
                    libro["cota"] or "",
                ),
            )

    selected_id = None

    def on_select(event=None):
        nonlocal selected_id
        selection = tree.selection()
        if not selection:
            return
        item = tree.item(selection[0])
        values = item["values"]
        selected_id = int(values[0])
        titulo = values[1]
        autor = values[2]
        codigo_dewey = values[3]
        cota = controller.calcular_cota(autor, titulo, codigo_dewey)
        selected_label.config(text=f"{titulo} — {autor}")
        cota_entry.delete(0, tk.END)
        cota_entry.insert(0, cota)

    tree.bind("<<TreeviewSelect>>", on_select)

    def guardar_cota():
        nonlocal selected_id
        if selected_id is None:
            messagebox.showwarning("Validación", "Seleccione un libro para guardar la cota.")
            return
        cota = cota_entry.get().strip()
        if not cota:
            messagebox.showwarning("Validación", "La cota no puede estar vacía.")
            return
        try:
            controller.guardar_cota(selected_id, cota)
            status_label.config(text="Cota guardada y agregada a la cola de impresión.")
            cargar_libros()
        except Exception as err:
            messagebox.showerror("Error", f"No se pudo guardar la cota:\n{err}")

    guardar_button = ttk.Button(detail_frame, text="Guardar Cota", command=guardar_cota)
    guardar_button.pack(anchor=tk.W, pady=(15, 0))

    cargar_libros()
