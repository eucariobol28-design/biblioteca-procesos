import tkinter as tk

from database.conexion import Database
from core.router import Router
from views.layout_base import LayoutBase
import views.vista_recepcion as recepcion_view
import views.vista_catalogacion as catalogacion_view
import views.vista_reportes as reportes_view
import views.vista_distribucion as distribucion_view
import views.vista_catalogos as catalogos_view
import views.vista_usuarios as usuarios_view
import views.vista_login as login_view


def main():
    Database.initialize()

    root = tk.Tk()
    
    def iniciar_aplicacion(usuario):
        for widget in root.winfo_children():
            widget.destroy()
        root.geometry("1100x650")
        layout = LayoutBase(root)
        layout.set_user(f"{usuario['nombre']} ({usuario['role']})")
        router = Router(layout)
        layout.set_router(router)

        router.register("recepcion", recepcion_view.render, "Recepción de Libros")
        router.register("catalogacion", catalogacion_view.render, "Catalogación y Ficha")
        router.register("distribucion", distribucion_view.render, "Distribución Satélite")
        router.register("reportes", reportes_view.render, "Reportes Mensuales")
        if usuario["role"] == "administrador":
            router.register("catalogos", catalogos_view.render, "Catálogos")
        if usuario["role"] == "administrador":
            router.register("usuarios", usuarios_view.render, "Gestión de Usuarios")

        layout.add_sidebar_button("recepcion", "Recepción de Libros")
        layout.add_sidebar_button("catalogacion", "Catalogación y Ficha")
        layout.add_sidebar_button("distribucion", "Distribución Satélite")
        layout.add_sidebar_button("reportes", "Reportes Mensuales")
        if usuario["role"] == "administrador":
            layout.add_sidebar_button("usuarios", "Gestión de Usuarios")
            layout.add_sidebar_button("catalogos", "Catálogos")

        router.navigate("recepcion")

    root.geometry("500x320")
    login_view.render_login(root, iniciar_aplicacion)
    root.mainloop()


if __name__ == "__main__":
    main()
