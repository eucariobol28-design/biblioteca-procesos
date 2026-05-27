import tkinter as tk
from tkinter import ttk, messagebox

from controllers.biblioteca_controller import BibliotecaController


def render_login(root, on_success):
    for widget in root.winfo_children():
        widget.destroy()

    frame = ttk.Frame(root, padding=24)
    frame.pack(fill=tk.BOTH, expand=True)

    title = ttk.Label(frame, text="Ingreso de Usuarios - Procesos Técnicos", font=("Segoe UI", 18, "bold"))
    title.pack(pady=(0, 18))

    formulario = ttk.Frame(frame)
    formulario.pack(pady=12)

    ttk.Label(formulario, text="Usuario:").grid(row=0, column=0, sticky=tk.W, pady=8)
    username_entry = ttk.Entry(formulario, width=34)
    username_entry.grid(row=0, column=1, pady=8)

    ttk.Label(formulario, text="Contraseña:").grid(row=1, column=0, sticky=tk.W, pady=8)
    password_entry = ttk.Entry(formulario, width=34, show="*")
    password_entry.grid(row=1, column=1, pady=8)

    status_label = ttk.Label(frame, text="", foreground="#006400")
    status_label.pack(pady=(10, 0))

    controller = BibliotecaController()

    def iniciar_sesion():
        usuario = controller.validar_credenciales(username_entry.get(), password_entry.get())
        if usuario is None:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")
            status_label.config(text="Intento de acceso fallido.")
            return
        status_label.config(text=f"Bienvenido {usuario['nombre']}.")
        messagebox.showinfo("Acceso permitido", f"Bienvenido {usuario['nombre']} ({usuario['role']}).")
        controller.cerrar()
        on_success(usuario)

    login_button = ttk.Button(frame, text="Ingresar", command=iniciar_sesion)
    login_button.pack(pady=18)

    root.bind("<Return>", lambda event: iniciar_sesion())
