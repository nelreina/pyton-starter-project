from textual.app import App
from textual.widgets import Header, Footer, Input, Button, Label

class  App(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> None:
        yield Header(show_clock=True)
        yield Footer()
    
    def action_toggle_dark(self) -> None:
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"

if __name__ == "__main__":
    App().run()