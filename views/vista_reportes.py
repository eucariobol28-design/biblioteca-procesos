import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from controllers.biblioteca_controller import BibliotecaController


def render(workspace, router):
    controller = BibliotecaController()

    frame = ttk.Frame(workspace)
    frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

    header = ttk.Label(frame, text="Reportes Mensuales y Buzón de Impresión", font=("Segoe UI", 16, "bold"))
    header.pack(anchor=tk.W, pady=(0, 12))

    buttons_frame = ttk.Frame(frame)
    buttons_frame.pack(fill=tk.X, pady=(0, 12))

    def mostrar_previsualizacion():
        items = controller.listar_cola_impresion()
        if not items:
            messagebox.showinfo("Previsualización", "No hay cotas en cola de impresión.")
            return

        ventana = tk.Toplevel(workspace)
        ventana.title("Previsualización de Cotas - Hoja Carta")
        ventana.geometry("900x620")
        ventana.resizable(False, False)

        preview_frame = ttk.Frame(ventana)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols = 3
        ancho = 280
        alto = 90
        padding_x = 10
        padding_y = 10
        for index, item in enumerate(items):
            col = index % cols
            row = index // cols
            x = 10 + col * (ancho + padding_x)
            y = 10 + row * (alto + padding_y)
            etiqueta = ttk.Label(
                preview_frame,
                text=f"{item['cota']}\n{item['titulo']}\n{item['autor']}",
                relief=tk.RIDGE,
                justify=tk.LEFT,
                anchor=tk.W,
                width=40,
                padding=8,
            )
            etiqueta.place(x=x, y=y, width=ancho, height=alto)

        def confirmar():
            controller.limpiar_cola_impresion()
            messagebox.showinfo("Impresión", "La cola ha sido limpiada tras la previsualización de cotas.")
            ventana.destroy()

        confirmar_button = ttk.Button(ventana, text="Confirmar Impresión y Limpiar Cola", command=confirmar)
        confirmar_button.pack(pady=12)

    def generar_reporte():
        month_key = datetime.now().strftime("%Y-%m")
        resumen = controller.reporte_mensual(month_key)
        for row in tree.get_children():
            tree.delete(row)
        for item in resumen:
            tree.insert(
                "",
                tk.END,
                values=(item["destino"], item["genero"], item["titulos_enviados"], item["volumen_total"]),
            )
        if not resumen:
            messagebox.showinfo("Reporte mensual", "No hay distribuciones registradas para este mes.")

    preview_button = ttk.Button(buttons_frame, text="Previsualizar Cola de Impresión", command=mostrar_previsualizacion)
    preview_button.pack(side=tk.LEFT, padx=(0, 10))

    reporte_button = ttk.Button(buttons_frame, text="Generar Reporte Mensual", command=generar_reporte)
    reporte_button.pack(side=tk.LEFT)

    tree_frame = ttk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    columns = ("destino", "genero", "titulos", "volumen")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
    tree.heading("destino", text="Biblioteca Destino")
    tree.heading("genero", text="Género")
    tree.heading("titulos", text="Títulos Enviados")
    tree.heading("volumen", text="Volumen Total")
    for col in columns:
        tree.column(col, width=200, anchor=tk.W)

    tree.pack(fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
