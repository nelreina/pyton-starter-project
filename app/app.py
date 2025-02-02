from textual.app import App
from textual.widgets import Header, Footer, Input, Button, Label

class  App(App):
    BINDINGS = [
        ("ctrl+c", "close_app", "Close application"),
        ("q", "close_app", "Close application"),
        ("a", "add_stopwatch", "Add stopwatch"),
    ]

    CSS_PATH = "app.css"

    def compose(self) -> None:
        yield Header(show_clock=True)
        yield Footer()
    
    def action_toggle_dark(self) -> None:
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"

    def action_close_app(self) -> None:
        self.exit()

if __name__ == "__main__":
    App().run()