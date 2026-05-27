import tkinter as tk
from tkinter import ttk, messagebox

from controllers.biblioteca_controller import BibliotecaController


def render(workspace, router):
    controller = BibliotecaController()

    frame = ttk.Frame(workspace)
    frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

    title = ttk.Label(frame, text="Gestión de Usuarios", font=("Segoe UI", 16, "bold"))
    title.pack(anchor=tk.W, pady=(0, 12))

    table_frame = ttk.Frame(frame)
    table_frame.pack(fill=tk.BOTH, expand=True)

    columns = ("id", "username", "nombre", "role", "activo")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
    headings = {
        "id": "ID",
        "username": "Usuario",
        "nombre": "Nombre",
        "role": "Rol",
        "activo": "Activo",
    }
    for col in columns:
        tree.heading(col, text=headings[col])
        tree.column(col, width=140, anchor=tk.W)
    tree.column("id", width=50, anchor=tk.CENTER)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    form_frame = ttk.Frame(frame)
    form_frame.pack(fill=tk.X, pady=(12, 0))

    campos = {
        "Usuario": ttk.Entry(form_frame, width=35),
        "Contraseña": ttk.Entry(form_frame, width=35, show="*"),
        "Nombre": ttk.Entry(form_frame, width=35),
        "Rol": ttk.Combobox(form_frame, state="readonly", width=32),
        "Activo": ttk.Combobox(form_frame, state="readonly", width=32),
    }

    row = 0
    for etiqueta, widget in campos.items():
        ttk.Label(form_frame, text=f"{etiqueta}:").grid(row=row, column=0, sticky=tk.W, pady=6)
        widget.grid(row=row, column=1, sticky=tk.W, pady=6)
        row += 1

    campos["Rol"]["values"] = controller.roles_disponibles()
    campos["Rol"].current(0)
    campos["Activo"]["values"] = ["1", "0"]
    campos["Activo"].current(0)

    status_label = ttk.Label(frame, text="", foreground="#006400")
    status_label.pack(anchor=tk.W, pady=(8, 0))

    selected_user_id = None

    def cargar_usuarios():
        nonlocal selected_user_id
        for row_id in tree.get_children():
            tree.delete(row_id)
        usuarios = controller.listar_usuarios()
        for usuario in usuarios:
            tree.insert(
                "",
                tk.END,
                values=(
                    usuario["id"],
                    usuario["username"],
                    usuario["nombre"],
                    usuario["role"],
                    "Sí" if usuario["activo"] else "No",
                ),
            )
        selected_user_id = None
        limpiar_campos()

    def limpiar_campos():
        nonlocal selected_user_id
        selected_user_id = None
        campos["Usuario"].delete(0, tk.END)
        campos["Contraseña"].delete(0, tk.END)
        campos["Nombre"].delete(0, tk.END)
        campos["Rol"].current(0)
        campos["Activo"].current(0)
        status_label.config(text="")

    def seleccionar_usuario(event=None):
        nonlocal selected_user_id
        seleccionado = tree.selection()
        if not seleccionado:
            return
        values = tree.item(seleccionado[0])["values"]
        selected_user_id = int(values[0])
        campos["Usuario"].delete(0, tk.END)
        campos["Usuario"].insert(0, values[1])
        campos["Usuario"].config(state="disabled")
        campos["Contraseña"].delete(0, tk.END)
        campos["Nombre"].delete(0, tk.END)
        campos["Nombre"].insert(0, values[2])
        campos["Rol"].set(values[3])
        campos["Activo"].set("1" if values[4] == "Sí" else "0")
        status_label.config(text=f"Usuario seleccionado: {values[1]}.")

    tree.bind("<<TreeviewSelect>>", seleccionar_usuario)

    def activar_campos_usuario():
        campos["Usuario"].config(state="normal")

    def crear():
        username = campos["Usuario"].get().strip()
        password = campos["Contraseña"].get().strip()
        nombre = campos["Nombre"].get().strip()
        role = campos["Rol"].get().strip()
        activo = int(campos["Activo"].get().strip())
        if not username or not password or not nombre or not role:
            messagebox.showwarning("Validación", "Complete todos los campos obligatorios.")
            return
        try:
            controller.crear_usuario(username, password, nombre, role, activo)
            status_label.config(text="Usuario creado correctamente.")
            cargar_usuarios()
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def actualizar():
        nonlocal selected_user_id
        if selected_user_id is None:
            messagebox.showwarning("Validación", "Seleccione un usuario antes de actualizar.")
            return
        nombre = campos["Nombre"].get().strip()
        role = campos["Rol"].get().strip()
        activo = int(campos["Activo"].get().strip())
        password = campos["Contraseña"].get().strip()
        try:
            controller.actualizar_usuario(selected_user_id, nombre, role, activo, password if password else None)
            status_label.config(text="Usuario actualizado correctamente.")
            activar_campos_usuario()
            cargar_usuarios()
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def eliminar():
        nonlocal selected_user_id
        if selected_user_id is None:
            messagebox.showwarning("Validación", "Seleccione un usuario antes de eliminar.")
            return
        if messagebox.askyesno("Eliminar usuario", "¿Está seguro de eliminar este usuario?"):
            try:
                controller.eliminar_usuario(selected_user_id)
                status_label.config(text="Usuario eliminado correctamente.")
                activar_campos_usuario()
                cargar_usuarios()
            except Exception as error:
                messagebox.showerror("Error", str(error))

    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=(12, 0))

    ttk.Button(button_frame, text="Crear", command=crear).pack(side=tk.LEFT, padx=6)
    ttk.Button(button_frame, text="Actualizar", command=actualizar).pack(side=tk.LEFT, padx=6)
    ttk.Button(button_frame, text="Eliminar", command=eliminar).pack(side=tk.LEFT, padx=6)
    ttk.Button(button_frame, text="Limpiar", command=cargar_usuarios).pack(side=tk.LEFT, padx=6)

    cargar_usuarios()
