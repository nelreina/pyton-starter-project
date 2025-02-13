from rich.console import Console
from rich.pretty import pprint
from datetime import datetime
from rich import print_json
import json

# Create console for rich output
console = Console()

class RichLogger:
    def __init__(self, console):
        self.console = console

    def _format_time(self):
        return f"[dim]{datetime.now().strftime('%H:%M:%S')}[/dim]"

    def _format_struct(self, obj):
        if isinstance(obj, str):
            try:
                # Try to parse as JSON first
                parsed = json.loads(obj)
                return print_json(json.dumps(parsed))
            except:
                return obj
        elif isinstance(obj, (dict, list)):
            return self.console.print(obj, style="blue")
        return str(obj)

    def info(self, message):
        self.console.print(f"{self._format_time()} ℹ️ {message}")

    def error(self, message):
        self.console.print(f"{self._format_time()} ❌ {message}", style="bold red")

    def debug(self, message):
        self.console.print(f"{self._format_time()} 🔍 {message}", style="dim")

    def warning(self, message):
        self.console.print(f"{self._format_time()} ⚠️ {message}", style="yellow")

    def struct(self, message, data):
        self.console.print(f"{self._format_time()} 📊 {message}")
        self.console.print("   ", end="")
        self._format_struct(data)

# Create a logger instance
logger = RichLogger(console) 