"""Open DBBasic services in browser"""

import webbrowser
import typer
from rich.console import Console

from .config import SERVICES

console = Console()

def open_service(service: str = typer.Argument(None, help="Service to open (omit for dashboard)")):
    """Open DBBasic service in browser"""
    
    # Default to monitor dashboard
    if not service:
        service = "monitor"
    
    if service == "docs":
        # Special case for API docs
        url = f"{SERVICES['crud']['url']}/docs"
        console.print(f"Opening API documentation: [blue]{url}[/blue]")
        webbrowser.open(url)
        return
    
    if service not in SERVICES:
        console.print(f"[red]Unknown service: {service}[/red]")
        console.print(f"Available: {', '.join(SERVICES.keys())} or 'docs' for API docs")
        raise typer.Exit(1)
    
    svc = SERVICES[service]
    console.print(f"Opening {svc['name']}: [blue]{svc['url']}[/blue]")
    webbrowser.open(svc['url'])