from textual.app import App
from textual.widgets import Header, Footer, Input, Button, Label
from os import environ

service_name = environ.get("SERVICE_NAME")
theme = environ.get("THEME", "textual-dark")

class  App(App):
    BINDINGS = [
        ("ctrl+c", "close_app", "Close application"),
        ("q", "close_app", "Close application"),
    ]

    CSS_PATH = "app.tcss"
    def compose(self) -> None:
        self.title = service_name
        self.theme = theme
        yield Header(show_clock=True)
        yield Footer()
    
    def action_toggle_dark(self) -> None:
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"

    def action_close_app(self) -> None:
        self.exit()

if __name__ == "__main__":
    App().run()
