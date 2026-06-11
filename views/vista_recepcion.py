import tkinter as tk
from tkinter import ttk, messagebox

from controllers.biblioteca_controller import BibliotecaController


def render(workspace, router):
    controller = BibliotecaController()

    frame = ttk.Frame(workspace)
    frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

    title = ttk.Label(frame, text="Recepción, Análisis Físico y Registro Inicial", font=("Segoe UI", 16, "bold"))
    title.pack(anchor=tk.W, pady=(0, 12))

    form = ttk.Frame(frame)
    form.pack(fill=tk.X)

    labels = [
        ("Número de registro:", 0),
        ("Título:", 1),
        ("Autor:", 2),
        ("Género/Área:", 3),
        ("Código Dewey:", 4),
        ("ISBN:", 5),
        ("Cantidad:", 6),
        ("Dimensiones (cm):", 7),
        ("Peso (gramos):", 8),
        ("Sala interna:", 9),
        ("Observaciones:", 10),
    ]

    entries = {}
    for text, row in labels:
        label = ttk.Label(form, text=text)
        label.grid(row=row, column=0, sticky=tk.W, pady=6)
        if text == "Sala interna:":
            entry = ttk.Combobox(form, state="readonly", width=44)
            entry["values"] = [f"{s['id']} - {s['nombre']}" for s in controller.listar_salas()]
            if entry["values"]:
                entry.current(0)
        elif text == "Género/Área:":
            entry = ttk.Combobox(form, state="readonly", width=44)
            entry["values"] = [f"{g['id']} - {g['nombre']}" for g in controller.listar_generos()]
            if entry["values"]:
                entry.current(0)
        elif text == "Cantidad:":
            entry = ttk.Spinbox(form, from_=1, to=9999, width=15)
            entry.set(1)
        elif text == "Peso (gramos):":
            entry = ttk.Spinbox(form, from_=1, to=99999, width=15)
            entry.set(100)
        elif text == "Observaciones:":
            entry = ttk.Entry(form, width=48)
        else:
            entry = ttk.Entry(form, width=48)
        entry.grid(row=row, column=1, pady=6, sticky=tk.W)
        entries[text] = entry

    status_label = ttk.Label(frame, text="", foreground="#006400")
    status_label.pack(anchor=tk.W, pady=(10, 0))

    def limpiar_formulario():
        for key, widget in entries.items():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Spinbox):
                widget.set(1 if key == "Cantidad:" else 100)
            elif isinstance(widget, ttk.Combobox):
                widget.current(0)

    def guardar():
        try:
            num_registro = entries["Número de registro:"].get().strip()
            titulo = entries["Título:"].get().strip()
            autor = entries["Autor:"].get().strip()
            genero = entries["Género/Área:"].get().strip()
            codigo_dewey = entries["Código Dewey:"].get().strip()
            isbn = entries["ISBN:"].get().strip()
            cantidad = int(entries["Cantidad:"].get())
            dimensiones = entries["Dimensiones (cm):"].get().strip()
            peso = int(entries["Peso (gramos):"].get())
            sala_text = entries["Sala interna:"].get().strip()
            observaciones = entries["Observaciones:"].get().strip()

            genero_id = int(genero.split(" - ")[0]) if genero else None
            sala_id = int(sala_text.split(" - ")[0]) if sala_text else None

            if not (titulo and autor and genero and codigo_dewey and isbn and dimensiones and sala_id):
                raise ValueError("Todos los campos deben estar completos.")

            libro_id = controller.guardar_libro(
                num_registro,
                titulo,
                autor,
                genero_id,
                codigo_dewey,
                isbn,
                cantidad,
                dimensiones,
                peso,
                sala_id,
                observaciones,
            )
            status_label.config(text="Libro registrado correctamente y stock inicial asignado a Sede Central.")
            messagebox.showinfo(
                "Recepción completada",
                "El libro ha sido recibido y registrado en el inventario central.",
            )
            # Si el usuario marcó la opción, ejecutar catalogación experta y aplicar resultado
            if ejecutar_experto_var.get():
                registro = {
                    "num_registro": num_registro,
                    "titulo": titulo,
                    "autor": autor,
                    "editorial": "",
                    "ciudad": "",
                    "year": None,
                    "paginas": None,
                    "dimensiones": dimensiones,
                    "isbn": isbn,
                    "cantidad": cantidad,
                    "observaciones": observaciones,
                    "genero": None,
                }
                resultado = controller.procesar_catalogacion_experta(registro)
                try:
                    controller.aplicar_resultado_experto(libro_id, resultado, encolar=True)
                    status_label.config(text="Catalogación experta aplicada: cota guardada y encolada.")
                    messagebox.showinfo("Catalogación experta", f"Cota aplicada: {resultado.get('fase_3', {}).get('cota')}")
                except Exception as e:
                    messagebox.showerror("Error al aplicar catalogación experta", str(e))
                    status_label.config(text="")
            limpiar_formulario()
        except Exception as error:
            messagebox.showerror("Error de recepción", str(error))
            status_label.config(text="")

    guardar_button = ttk.Button(frame, text="Guardar Recepción", command=guardar)
    guardar_button.pack(anchor=tk.E, pady=16)

    ejecutar_experto_var = tk.BooleanVar(value=False)
    ejecutar_experto_cb = ttk.Checkbutton(frame, text="Ejecutar catalogación experta después de guardar", variable=ejecutar_experto_var)
    ejecutar_experto_cb.pack(anchor=tk.W, pady=(0, 8))
