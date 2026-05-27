from core.view_engine import ViewEngine


class Router:
    def __init__(self, layout):
        self.layout = layout
        self.routes = {}

    def register(self, name: str, view_callable, title: str):
        self.routes[name] = {
            "view": view_callable,
            "title": title,
        }

    def navigate(self, name: str):
        if name not in self.routes:
            return
        route = self.routes[name]
        self.layout.set_title(route["title"])
        ViewEngine.render(self.layout.workspace, route["view"], self)

    def get_route_names(self):
        return list(self.routes.keys())
