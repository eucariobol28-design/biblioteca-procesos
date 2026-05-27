from tkinter import ttk


class ViewEngine:
    @staticmethod
    def render(workspace: ttk.Frame, view_callable, *args, **kwargs):
        for child in workspace.winfo_children():
            child.destroy()
        view_callable(workspace, *args, **kwargs)
