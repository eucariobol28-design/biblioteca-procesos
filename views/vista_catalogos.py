import tkinter as tk
from tkinter import ttk, messagebox

from controllers.biblioteca_controller import BibliotecaController


def render(workspace, router):
    controller = BibliotecaController()

    frame = ttk.Frame(workspace)
    frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

    title = ttk.Label(frame, text="Catálogos Parametrizados", font=("Segoe UI", 16, "bold"))
    title.pack(anchor=tk.W, pady=(0, 12))

    tabs = ttk.Notebook(frame)
    tabs.pack(fill=tk.BOTH, expand=True)

    # Bibliotecas
    bibliotecas_tab = ttk.Frame(tabs)
    tabs.add(bibliotecas_tab, text="Bibliotecas")
    bibliotecas_tree = ttk.Treeview(bibliotecas_tab, columns=("id", "nombre", "parroquia", "encargado", "tipo"), show="headings", height=10)
    for col, heading in [("id", "ID"), ("nombre", "Nombre"), ("parroquia", "Parroquia"), ("encargado", "Encargado"), ("tipo", "Tipo")]:
        bibliotecas_tree.heading(col, text=heading)
        bibliotecas_tree.column(col, width=140, anchor=tk.W)
    bibliotecas_tree.column("id", width=50, anchor=tk.CENTER)
    bibliotecas_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    bibliotecas_form = ttk.Frame(bibliotecas_tab)
    bibliotecas_form.pack(fill=tk.X)

    bib_fields = {
        "Nombre": ttk.Entry(bibliotecas_form, width=32),
        "Parroquia": ttk.Entry(bibliotecas_form, width=32),
        "Encargado": ttk.Entry(bibliotecas_form, width=32),
        "Tipo": ttk.Combobox(bibliotecas_form, state="readonly", width=30),
    }
    bib_fields["Tipo"]["values"] = ["Sede Central", "Sede Satélite"]
    bib_fields["Tipo"].current(1)

    for idx, (label_text, widget) in enumerate(bib_fields.items()):
        ttk.Label(bibliotecas_form, text=f"{label_text}:").grid(row=idx, column=0, sticky=tk.W, pady=6)
        widget.grid(row=idx, column=1, sticky=tk.W, pady=6)

    def cargar_bibliotecas():
        for row in bibliotecas_tree.get_children():
            bibliotecas_tree.delete(row)
        for biblioteca in controller.listar_bibliotecas(include_central=True):
            bibliotecas_tree.insert(
                "",
                tk.END,
                values=(
                    biblioteca["id"],
                    biblioteca["nombre"],
                    biblioteca["parroquia"],
                    biblioteca["encargado"],
                    biblioteca["tipo"],
                ),
            )

    def crear_biblioteca():
        nombre = bib_fields["Nombre"].get().strip()
        parroquia = bib_fields["Parroquia"].get().strip()
        encargado = bib_fields["Encargado"].get().strip()
        tipo = bib_fields["Tipo"].get().strip()
        if not (nombre and parroquia and encargado and tipo):
            messagebox.showwarning("Validación", "Complete todos los campos de la biblioteca.")
            return
        controller.crear_biblioteca(nombre, parroquia, encargado, tipo)
        cargar_bibliotecas()
        messagebox.showinfo("Éxito", "Biblioteca creada correctamente.")

    def eliminar_biblioteca():
        seleccionado = bibliotecas_tree.selection()
        if not seleccionado:
            messagebox.showwarning("Validación", "Seleccione una biblioteca para eliminar.")
            return
        biblioteca_id = int(bibliotecas_tree.item(seleccionado[0])["values"][0])
        if messagebox.askyesno("Eliminar biblioteca", "¿Está seguro de eliminar esta biblioteca?"):
            controller.eliminar_biblioteca(biblioteca_id)
            cargar_bibliotecas()

    bib_buttons = ttk.Frame(bibliotecas_tab)
    bib_buttons.pack(fill=tk.X, pady=(10, 0))
    ttk.Button(bib_buttons, text="Crear", command=crear_biblioteca).pack(side=tk.LEFT, padx=4)
    ttk.Button(bib_buttons, text="Eliminar", command=eliminar_biblioteca).pack(side=tk.LEFT, padx=4)

    # Salas
    salas_tab = ttk.Frame(tabs)
    tabs.add(salas_tab, text="Salas")
    salas_tree = ttk.Treeview(salas_tab, columns=("id", "nombre"), show="headings", height=10)
    salas_tree.heading("id", text="ID")
    salas_tree.heading("nombre", text="Nombre")
    salas_tree.column("id", width=60, anchor=tk.CENTER)
    salas_tree.column("nombre", width=260, anchor=tk.W)
    salas_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    sala_form = ttk.Frame(salas_tab)
    sala_form.pack(fill=tk.X)
    sala_nombre = ttk.Entry(sala_form, width=40)
    ttk.Label(sala_form, text="Nombre: ").grid(row=0, column=0, sticky=tk.W, pady=6)
    sala_nombre.grid(row=0, column=1, sticky=tk.W, pady=6)

    def cargar_salas():
        for row in salas_tree.get_children():
            salas_tree.delete(row)
        for sala in controller.listar_salas():
            salas_tree.insert("", tk.END, values=(sala["id"], sala["nombre"]))

    def crear_sala():
        nombre = sala_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Validación", "Ingrese el nombre de la sala.")
            return
        controller.crear_sala(nombre)
        cargar_salas()
        messagebox.showinfo("Éxito", "Sala creada correctamente.")

    def eliminar_sala():
        seleccionado = salas_tree.selection()
        if not seleccionado:
            messagebox.showwarning("Validación", "Seleccione una sala para eliminar.")
            return
        sala_id = int(salas_tree.item(seleccionado[0])["values"][0])
        if messagebox.askyesno("Eliminar sala", "¿Está seguro de eliminar esta sala?"):
            controller.eliminar_sala(sala_id)
            cargar_salas()

    sala_buttons = ttk.Frame(salas_tab)
    sala_buttons.pack(fill=tk.X, pady=(10, 0))
    ttk.Button(sala_buttons, text="Crear", command=crear_sala).pack(side=tk.LEFT, padx=4)
    ttk.Button(sala_buttons, text="Eliminar", command=eliminar_sala).pack(side=tk.LEFT, padx=4)

    # Géneros
    generos_tab = ttk.Frame(tabs)
    tabs.add(generos_tab, text="Géneros")
    generos_tree = ttk.Treeview(generos_tab, columns=("id", "nombre", "metodo_wely_code"), show="headings", height=10)
    generos_tree.heading("id", text="ID")
    generos_tree.heading("nombre", text="Nombre")
    generos_tree.heading("metodo_wely_code", text="Método Wely Code")
    generos_tree.column("id", width=60, anchor=tk.CENTER)
    generos_tree.column("nombre", width=180, anchor=tk.W)
    generos_tree.column("metodo_wely_code", width=180, anchor=tk.W)
    generos_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    genero_form = ttk.Frame(generos_tab)
    genero_form.pack(fill=tk.X)
    genero_nombre = ttk.Entry(genero_form, width=30)
    genero_metodo = ttk.Entry(genero_form, width=30)
    ttk.Label(genero_form, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=6)
    genero_nombre.grid(row=0, column=1, sticky=tk.W, pady=6)
    ttk.Label(genero_form, text="Método Wely Code:").grid(row=1, column=0, sticky=tk.W, pady=6)
    genero_metodo.grid(row=1, column=1, sticky=tk.W, pady=6)

    def cargar_generos():
        for row in generos_tree.get_children():
            generos_tree.delete(row)
        for genero in controller.listar_generos():
            generos_tree.insert(
                "",
                tk.END,
                values=(genero["id"], genero["nombre"], genero["metodo_wely_code"]),
            )

    def crear_genero():
        nombre = genero_nombre.get().strip()
        metodo = genero_metodo.get().strip()
        if not nombre or not metodo:
            messagebox.showwarning("Validación", "Complete todos los campos del género.")
            return
        controller.crear_genero(nombre, metodo)
        cargar_generos()
        messagebox.showinfo("Éxito", "Género creado correctamente.")

    def eliminar_genero():
        seleccionado = generos_tree.selection()
        if not seleccionado:
            messagebox.showwarning("Validación", "Seleccione un género para eliminar.")
            return
        genero_id = int(generos_tree.item(seleccionado[0])["values"][0])
        if messagebox.askyesno("Eliminar género", "¿Está seguro de eliminar este género?"):
            controller.eliminar_genero(genero_id)
            cargar_generos()

    genero_buttons = ttk.Frame(generos_tab)
    genero_buttons.pack(fill=tk.X, pady=(10, 0))
    ttk.Button(genero_buttons, text="Crear", command=crear_genero).pack(side=tk.LEFT, padx=4)
    ttk.Button(genero_buttons, text="Eliminar", command=eliminar_genero).pack(side=tk.LEFT, padx=4)

    cargar_bibliotecas()
    cargar_salas()
    cargar_generos()
