import tkinter as tk
from tkinter import ttk, messagebox

from controllers.biblioteca_controller import BibliotecaController


def render(workspace, router):
    controller = BibliotecaController()

    frame = ttk.Frame(workspace)
    frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

    title = ttk.Label(frame, text="Distribución Logística Satélite y Emisión de Documentos", font=("Segoe UI", 16, "bold"))
    title.pack(anchor=tk.W, pady=(0, 12))

    form = ttk.Frame(frame)
    form.pack(fill=tk.X)

    ttk.Label(form, text="Libro catalogado:").grid(row=0, column=0, sticky=tk.W, pady=8)
    libro_combobox = ttk.Combobox(form, state="readonly", width=65)
    libro_combobox.grid(row=0, column=1, sticky=tk.W, pady=8)

    ttk.Label(form, text="Sala origen (Central):").grid(row=1, column=0, sticky=tk.W, pady=8)
    origen_combobox = ttk.Combobox(form, state="readonly", width=65)
    origen_combobox.grid(row=1, column=1, sticky=tk.W, pady=8)

    ttk.Label(form, text="Biblioteca destino:").grid(row=2, column=0, sticky=tk.W, pady=8)
    destino_combobox = ttk.Combobox(form, state="readonly", width=65)
    destino_combobox.grid(row=2, column=1, sticky=tk.W, pady=8)

    ttk.Label(form, text="Sala destino:").grid(row=3, column=0, sticky=tk.W, pady=8)
    sala_destino_combobox = ttk.Combobox(form, state="readonly", width=65)
    sala_destino_combobox.grid(row=3, column=1, sticky=tk.W, pady=8)

    ttk.Label(form, text="Cantidad a enviar:").grid(row=4, column=0, sticky=tk.W, pady=8)
    cantidad_spinbox = ttk.Spinbox(form, from_=1, to=9999, width=20)
    cantidad_spinbox.set(1)
    cantidad_spinbox.grid(row=4, column=1, sticky=tk.W, pady=8)

    stock_label = ttk.Label(form, text="Stock en Sede Central: 0")
    stock_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(6, 0))

    status_label = ttk.Label(frame, text="", foreground="#006400")
    status_label.pack(anchor=tk.W, pady=(14, 0))

    libros_catalogados = controller.listar_libros_catalogados()
    opciones_libros = [f"{libro['id']} - {libro['titulo']}" for libro in libros_catalogados]
    libro_combobox["values"] = opciones_libros
    if opciones_libros:
        libro_combobox.current(0)

    origenes = controller.listar_salas()
    opciones_origen = [f"{sala['id']} - {sala['nombre']}" for sala in origenes]
    origen_combobox["values"] = opciones_origen
    if opciones_origen:
        origen_combobox.current(0)

    destinos = controller.listar_bibliotecas(include_central=False)
    opciones_destinos = [f"{destino['id']} - {destino['nombre']}" for destino in destinos]
    destino_combobox["values"] = opciones_destinos
    if opciones_destinos:
        destino_combobox.current(0)

    salasal = controller.listar_salas()
    opciones_salas = [f"{sala['id']} - {sala['nombre']}" for sala in salasal]
    sala_destino_combobox["values"] = opciones_salas
    if opciones_salas:
        sala_destino_combobox.current(0)

    selected_libro_id = None

    def actualizar_stock(event=None):
        nonlocal selected_libro_id
        seleccionado = libro_combobox.get()
        if not seleccionado:
            stock_label.config(text="Stock en Sede Central: 0")
            selected_libro_id = None
            return
        selected_libro_id = int(seleccionado.split(" - ")[0])
        origen_texto = origen_combobox.get()
        origen_sala_id = int(origen_texto.split(" - ")[0]) if origen_texto else None
        stock = controller.obtener_stock_central_por_sala(selected_libro_id, origen_sala_id) if origen_sala_id else 0
        stock_label.config(text=f"Stock en Sede Central: {stock}")

    libro_combobox.bind("<<ComboboxSelected>>", actualizar_stock)
    origen_combobox.bind("<<ComboboxSelected>>", actualizar_stock)
    actualizar_stock()

    def abrir_documentos(textos: dict):
        ventana = tk.Toplevel(workspace)
        ventana.title("Documentos de Distribución")
        ventana.geometry("760x520")
        ventana.resizable(False, False)

        tabs = ttk.Notebook(ventana)
        tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for key, contenido in textos.items():
            panel = ttk.Frame(tabs)
            tabs.add(panel, text=key.capitalize())
            texto_widget = tk.Text(panel, wrap=tk.WORD, state=tk.NORMAL)
            texto_widget.insert(tk.END, contenido)
            texto_widget.config(state=tk.DISABLED)
            texto_widget.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def enviar():
        if selected_libro_id is None:
            messagebox.showwarning("Validación", "Seleccione un libro catalogado.")
            return
        try:
            cantidad = int(cantidad_spinbox.get())
        except ValueError:
            messagebox.showwarning("Validación", "Ingrese una cantidad válida.")
            return
        destino_texto = destino_combobox.get()
        origen_texto = origen_combobox.get()
        sala_destino_texto = sala_destino_combobox.get()
        if not destino_texto or not origen_texto or not sala_destino_texto:
            messagebox.showwarning("Validación", "Seleccione origen, destino y sala destino.")
            return
        destino_id = int(destino_texto.split(" - ")[0])
        origen_sala_id = int(origen_texto.split(" - ")[0])
        destino_sala_id = int(sala_destino_texto.split(" - ")[0])

        try:
            libro = controller.obtener_libro(selected_libro_id)
            acta_numero = controller.distribuir_libro(selected_libro_id, cantidad, origen_sala_id, destino_id, destino_sala_id)
            destino = controller.obtener_destino(destino_id)
            documentos = controller.generar_documentos(libro, cantidad, destino, acta_numero)
            status_label.config(text=f"Distribución realizada. Acta {acta_numero} generada.")
            messagebox.showinfo(
                "Distribución completada",
                f"Distribución registrada con acta {acta_numero}.",
            )
            abrir_documentos(documentos)
            actualizar_stock()
        except Exception as error:
            messagebox.showerror("Error de distribución", str(error))
            status_label.config(text="")

    enviar_button = ttk.Button(frame, text="Enviar Libro", command=enviar)
    enviar_button.pack(anchor=tk.E, pady=12)
