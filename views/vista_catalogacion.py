import tkinter as tk
from tkinter import ttk, messagebox

from controllers.biblioteca_controller import BibliotecaController


def render(workspace, router):
    controller = BibliotecaController()

    frame = ttk.Frame(workspace)
    frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

    header = ttk.Label(frame, text="Catalogación Automatizada y Emisión de Ficha", font=("Segoe UI", 16, "bold"))
    header.pack(anchor=tk.W, pady=(0, 12))

    content = ttk.Frame(frame)
    content.pack(fill=tk.BOTH, expand=True)

    tree_frame = ttk.Frame(content)
    tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    columns = ("id", "num_registro", "titulo", "autor", "genero", "codigo_dewey", "cota")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=18)
    for col in columns:
        tree.heading(col, text=col.replace("_", " ").capitalize())
        tree.column(col, width=120, anchor=tk.W)
    tree.column("titulo", width=220)
    tree.column("num_registro", width=130)
    tree.pack(fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    detail_frame = ttk.Frame(content)
    detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

    selected_label = ttk.Label(detail_frame, text="Libro seleccionado: Ninguno", font=("Segoe UI", 11, "bold"), wraplength=260)
    selected_label.pack(anchor=tk.W, pady=(0, 12))

    cota_label = ttk.Label(detail_frame, text="Cota calculada:")
    cota_label.pack(anchor=tk.W)
    cota_entry = ttk.Entry(detail_frame, width=38)
    cota_entry.pack(anchor=tk.W, pady=(4, 12))

    preview_label = ttk.Label(detail_frame, text="Vista previa de catalogación:")
    preview_label.pack(anchor=tk.W)
    preview_text = tk.Text(detail_frame, width=40, height=10, wrap=tk.WORD)
    preview_text.pack(anchor=tk.W, pady=(4, 8))

    last_resultado = {"data": None}

    status_label = ttk.Label(detail_frame, text="", foreground="#006400")
    status_label.pack(anchor=tk.W, pady=(4, 0))

    selected_libro = {"id": None, "titulo": "", "autor": "", "codigo_dewey": ""}

    def cargar_libros():
        for row in tree.get_children():
            tree.delete(row)
        pendientes = controller.listar_libros_pendientes()
        for libro in pendientes:
            tree.insert(
                "",
                tk.END,
                values=(
                    libro["id"],
                    libro.get("num_registro", ""),
                    libro["titulo"],
                    libro["autor"],
                    libro["genero"],
                    libro["codigo_dewey"],
                    libro.get("cota", ""),
                ),
            )

    def on_select(event=None):
        selection = tree.selection()
        if not selection:
            return
        values = tree.item(selection[0])["values"]
        selected_libro["id"] = int(values[0])
        selected_libro["titulo"] = values[2]
        selected_libro["autor"] = values[3]
        selected_libro["codigo_dewey"] = values[5]
        selected_label.config(text=f"Libro seleccionado: {selected_libro['titulo']} - {selected_libro['autor']}")
        cota = controller.calcular_cota(selected_libro["autor"], selected_libro["titulo"], selected_libro["codigo_dewey"])
        cota_entry.delete(0, tk.END)
        cota_entry.insert(0, cota)
        status_label.config(text="")

    tree.bind("<<TreeviewSelect>>", on_select)

    def aprobar():
        if selected_libro["id"] is None:
            messagebox.showwarning("Validación", "Seleccione un libro para aprobar la ficha.")
            return
        cota = cota_entry.get().strip()
        if not cota:
            messagebox.showwarning("Validación", "La cota no puede estar vacía.")
            return
        try:
            controller.aprobar_y_generar_ficha(selected_libro["id"], cota)
            status_label.config(text="Ficha aprobada y cota enviada a cola de impresión.")
            messagebox.showinfo(
                "Ficha generada",
                "La ficha bibliográfica ha sido registrada y la cota está lista para impresión.",
            )
            cargar_libros()
            selected_label.config(text="Libro seleccionado: Ninguno")
            cota_entry.delete(0, tk.END)
        except Exception as error:
            messagebox.showerror("Error de catalogación", str(error))
            status_label.config(text="")

    aprobar_button = ttk.Button(detail_frame, text="Aprobar y Generar Ficha", command=aprobar)
    aprobar_button.pack(anchor=tk.CENTER, pady=(15, 0))

    def ejecutar_experto():
        if selected_libro["id"] is None:
            messagebox.showwarning("Validación", "Seleccione un libro para procesar.")
            return
        libro = controller.obtener_libro(selected_libro["id"])
        registro = {
            "num_registro": libro.get("num_registro"),
            "titulo": libro.get("titulo"),
            "autor": libro.get("autor"),
            "editorial": libro.get("editorial") if "editorial" in libro else "",
            "ciudad": libro.get("ciudad") if "ciudad" in libro else "",
            "year": libro.get("year") if "year" in libro else libro.get("ano") if "ano" in libro else None,
            "paginas": libro.get("paginas") if "paginas" in libro else None,
            "dimensiones": libro.get("dimensiones"),
            "isbn": libro.get("isbn"),
            "cantidad": 1,
            "observaciones": libro.get("observaciones"),
            "genero": libro.get("genero"),
        }
        resultado = controller.procesar_catalogacion_experta(registro)
        last_resultado["data"] = resultado
        # mostrar preview
        preview_text.delete("1.0", tk.END)
        import json

        preview_text.insert(tk.END, json.dumps(resultado, ensure_ascii=False, indent=2))
        # rellenar cota sugerida
        sugerida = resultado.get("fase_3", {}).get("cota", "")
        cota_entry.delete(0, tk.END)
        cota_entry.insert(0, sugerida)
        status_label.config(text="Catalogación experta completada (vista previa).")

    def aplicar_experto():
        if selected_libro["id"] is None or not last_resultado["data"]:
            messagebox.showwarning("Validación", "No hay resultado experto para aplicar.")
            return
        try:
            controller.aplicar_resultado_experto(selected_libro["id"], last_resultado["data"], encolar=True)
            status_label.config(text="Resultado aplicado: cota guardada y encolada para impresión.")
            messagebox.showinfo("Aplicado", "Cota guardada y enviada a la cola de impresión.")
            cargar_libros()
            preview_text.delete("1.0", tk.END)
            selected_label.config(text="Libro seleccionado: Ninguno")
            cota_entry.delete(0, tk.END)
        except Exception as error:
            messagebox.showerror("Error", str(error))

    experto_button = ttk.Button(detail_frame, text="Ejecutar Catalogación Experta", command=ejecutar_experto)
    experto_button.pack(anchor=tk.CENTER, pady=(8, 0))

    aplicar_button = ttk.Button(detail_frame, text="Aplicar Resultado Experto", command=aplicar_experto)
    aplicar_button.pack(anchor=tk.CENTER, pady=(8, 8))

    cargar_libros()
