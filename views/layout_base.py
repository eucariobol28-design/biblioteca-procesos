import tkinter as tk
from tkinter import ttk


class LayoutBase:
    def __init__(self, root):
        self.root = root
        self.root.title("Procesos Técnicos - Biblioteca Central Rómulo Gallegos")
        self.root.geometry("1100x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Sidebar.TFrame", background="#003366")
        style.configure("Header.TFrame", background="#004c99")
        style.configure("Header.TLabel", background="#004c99", foreground="#ffffff", font=("Segoe UI", 14, "bold"))
        style.configure("Sidebar.TButton", background="#003366", foreground="#ffffff", font=("Segoe UI", 11), padding=10)
        style.map(
            "Sidebar.TButton",
            background=[("active", "#0055a1"), ("pressed", "#002244")],
        )

        self.header_frame = ttk.Frame(self.root, style="Header.TFrame", height=60)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        self.header_title = ttk.Label(
            self.header_frame,
            text="Biblioteca Central Rómulo Gallegos - Procesos Técnicos",
            style="Header.TLabel",
        )
        self.header_title.pack(side=tk.LEFT, padx=20, pady=15)

        self.user_label = ttk.Label(
            self.header_frame,
            text="",
            style="Header.TLabel",
        )
        self.user_label.pack(side=tk.RIGHT, padx=20, pady=15)

        self.container = ttk.Frame(self.root)
        self.container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.sidebar = ttk.Frame(self.container, style="Sidebar.TFrame", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.workspace = ttk.Frame(self.container)
        self.workspace.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.buttons = {}
        self.router = None

    def set_router(self, router):
        self.router = router

    def add_sidebar_button(self, key: str, label: str):
        if self.router is None:
            return
        button = ttk.Button(
            self.sidebar,
            text=label,
            style="Sidebar.TButton",
            command=lambda: self.router.navigate(key),
        )
        button.pack(fill=tk.X, padx=10, pady=8)
        self.buttons[key] = button

    def set_title(self, title: str):
        self.header_title.config(text=title)

    def set_user(self, user_text: str):
        self.user_label.config(text=user_text)
