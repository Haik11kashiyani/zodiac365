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

import time, random
from rich.progress import track

def wait_random(min_seconds, max_seconds, label="Cooling down..."):
    """Pauses execution for a random duration to avoid rate limits."""
    duration = random.uniform(min_seconds, max_seconds)
    steps = int(duration * 10)
    
    # Use rich track for a nice progress bar during the wait
    for _ in track(range(steps), description=f"[cyan]{label}"):
        time.sleep(0.1)
