"""View logs from DBBasic services"""

import subprocess
import typer
from rich.console import Console
import time
from pathlib import Path

from .config import SERVICES, DBBASIC_DIR, get_pid
import psutil

console = Console()

def logs(
    service: str = typer.Argument(None, help="Service to show logs for (omit for all)"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    tail: int = typer.Option(50, "--tail", "-n", help="Number of lines to show")
):
    """View logs from DBBasic services"""
    
    if service and service not in SERVICES:
        console.print(f"[red]Unknown service: {service}[/red]")
        console.print(f"Available: {', '.join(SERVICES.keys())}")
        raise typer.Exit(1)
    
    console.print(f"[bold]Showing logs{' (following)' if follow else ''}[/bold]\n")
    
    # For now, inform user about log locations
    # In production, we'd capture logs to files or use journald
    
    if service:
        svc = SERVICES[service]
        pid = get_pid(service)
        if pid and psutil.pid_exists(pid):
            console.print(f"[green]✅ {svc['name']} is running (PID: {pid})[/green]")
            console.print(f"Port: {svc['port']}")
            console.print(f"URL: {svc['url']}")
        else:
            console.print(f"[yellow]⚠️  {svc['name']} is not running[/yellow]")
    else:
        # Show status of all services
        for svc_name, svc in SERVICES.items():
            pid = get_pid(svc_name)
            if pid and psutil.pid_exists(pid):
                console.print(f"[green]✅ {svc['name']}[/green] (PID: {pid}) on port {svc['port']}")
            else:
                console.print(f"[dim]❌ {svc['name']} not running[/dim]")
    
    console.print("\n[dim]Note: In a future version, logs will be captured and displayed here.[/dim]")
    console.print("[dim]For now, services output to their respective terminals.[/dim]")
    
    if follow:
        console.print("\n[yellow]Press Ctrl+C to stop following logs[/yellow]")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold]Stopped following logs[/bold]")