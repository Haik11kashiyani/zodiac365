from rich.console import Console
from rich.theme import Theme

# Custom theme for professional output
custom_theme = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "yellow",
    "error": "bold red",
    "highlight": "magenta"
})

console = Console(theme=custom_theme)

def log_section(title):
    console.print(f"\n[bold white on blue] {title} [/bold white on blue]")

def log_info(message):
    console.print(f"[info]ℹ[/info] {message}")

def log_success(message):
    console.print(f"[success]✔[/success] {message}")

def log_warning(message):
    console.print(f"[warning]![/warning] {message}")

def log_error(message):
    console.print(f"[error]✖ {message}[/error]")
