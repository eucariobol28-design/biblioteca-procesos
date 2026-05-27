import tkinter as tk
from tkinter import ttk, messagebox

from database.conexion import Database
from controllers.impresion_controller import ImpresionController


def render(workspace, router):
    conn = Database.get_connection()
    controller = ImpresionController(conn)

    frame = ttk.Frame(workspace)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    title_label = ttk.Label(frame, text="Buzón de Impresión de Cotas", font=("Segoe UI", 16, "bold"))
    title_label.pack(anchor=tk.W, pady=(0, 15))

    tree_frame = ttk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    columns = ("id", "titulo", "autor", "cota")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=200, anchor=tk.W)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    preview_frame = ttk.LabelFrame(frame, text="Previsualización de etiqueta en hoja carta")
    preview_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

    preview_canvas = tk.Canvas(preview_frame, background="#ffffff", height=280)
    preview_canvas.pack(fill=tk.BOTH, expand=True)

    status_label = ttk.Label(frame, text="", foreground="green")
    status_label.pack(anchor=tk.W, pady=(10, 0))

    def cargar_cola():
        for row in tree.get_children():
            tree.delete(row)
        for item in controller.listar_cola():
            tree.insert("", tk.END, values=(item["id"], item["titulo"], item["autor"], item["cota"]))

    def mostrar_previsualizacion(items):
        preview_canvas.delete("all")
        if not items:
            preview_canvas.create_text(520, 140, text="No hay cotas para imprimir.", font=("Segoe UI", 12), fill="#333333")
            return
        cols = 3
        filas = 8
        ancho = 340
        alto = 80
        padding_x = 10
        padding_y = 10
        x0 = 10
        y0 = 10
        for index, item in enumerate(items[: cols * filas]):
            col = index % cols
            row = index // cols
            x = x0 + col * (ancho + padding_x)
            y = y0 + row * (alto + padding_y)
            preview_canvas.create_rectangle(x, y, x + ancho, y + alto, outline="#003366")
            preview_canvas.create_text(
                x + 10,
                y + 20,
                anchor=tk.W,
                text=f"{item['cota']} - {item['titulo']}",
                font=("Segoe UI", 10, "bold"),
                fill="#003366",
            )
            preview_canvas.create_text(
                x + 10,
                y + 45,
                anchor=tk.W,
                text=f"{item['autor']}",
                font=("Segoe UI", 9),
                fill="#000000",
            )

    current_queue = []

    def generar_planilla():
        nonlocal current_queue
        current_queue = controller.listar_cola()
        if not current_queue:
            messagebox.showinfo("Planilla", "No hay cotas en la cola de impresión.")
            return
        mostrar_previsualizacion(current_queue)
        status_label.config(text=f"Vista previa generada con {len(current_queue)} cotas. Presione Confirmar Exportación.")

    def confirmar_exportacion():
        nonlocal current_queue
        if not current_queue:
            messagebox.showwarning("Confirmar", "Genere la planilla antes de confirmar.")
            return
        items = controller.generar_planilla()
        cargar_cola()
        current_queue = []
        mostrar_previsualizacion([])
        status_label.config(text=f"Planilla generada y cola limpiada. {len(items)} cotas procesadas.")

    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=(12, 0))

    generar_button = ttk.Button(button_frame, text="Generar Planilla de Cotas", command=generar_planilla)
    generar_button.pack(side=tk.LEFT, padx=(0, 10))

    confirmar_button = ttk.Button(button_frame, text="Confirmar Exportación", command=confirmar_exportacion)
    confirmar_button.pack(side=tk.LEFT)

    cargar_cola()
    mostrar_previsualizacion([])
