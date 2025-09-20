"""Stop DBBasic services"""

import os
import signal
import typer
from rich.console import Console
import psutil

from .config import SERVICES, get_pid, remove_pid

console = Console()

def stop(service: str = typer.Argument(None, help="Service to stop (omit for all)")):
    """Stop DBBasic services"""
    
    if service and service not in SERVICES:
        console.print(f"[red]Unknown service: {service}[/red]")
        console.print(f"Available: {', '.join(SERVICES.keys())}")
        raise typer.Exit(1)
    
    services_to_stop = [service] if service else list(SERVICES.keys())
    
    for svc_name in services_to_stop:
        svc = SERVICES[svc_name]
        pid = get_pid(svc_name)
        
        if pid and psutil.pid_exists(pid):
            try:
                os.kill(pid, signal.SIGTERM)
                console.print(f"✅ Stopped {svc['name']}")
                remove_pid(svc_name)
            except ProcessLookupError:
                console.print(f"[yellow]{svc['name']} not running[/yellow]")
                remove_pid(svc_name)
            except Exception as e:
                console.print(f"[red]❌ Failed to stop {svc['name']}: {e}[/red]")
        else:
            console.print(f"[dim]{svc['name']} not running[/dim]")
            remove_pid(svc_name)
    
    if not service:
        console.print("\n[bold]All services stopped[/bold]")