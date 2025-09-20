"""List ports used by DBBasic services"""

import socket
import typer
from rich.console import Console
from rich.table import Table

from .config import SERVICES

console = Console()

def check_port(port):
    """Check if port is in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def ports():
    """List ports used by DBBasic services"""
    
    table = Table(title="DBBasic Port Usage")
    table.add_column("Service", style="cyan")
    table.add_column("Port", style="magenta")
    table.add_column("Status", style="bold")
    table.add_column("URL", style="blue")
    
    for svc_name, svc in SERVICES.items():
        port_in_use = check_port(svc['port'])
        status = "✅ Active" if port_in_use else "⚪ Available"
        color = "green" if port_in_use else "dim"
        
        table.add_row(
            svc['name'],
            str(svc['port']),
            f"[{color}]{status}[/{color}]",
            svc['url']
        )
    
    console.print(table)
    
    # Check for conflicts on common ports
    console.print("\n[bold]Checking for port conflicts...[/bold]")
    conflicts = []
    
    for port in [3000, 3001, 5000, 5001, 8000, 8001, 8080, 8888]:
        if port not in [s['port'] for s in SERVICES.values()]:
            if check_port(port):
                conflicts.append(port)
    
    if conflicts:
        console.print(f"[yellow]⚠️  Other services detected on ports: {', '.join(map(str, conflicts))}[/yellow]")
    else:
        console.print("[green]✅ No port conflicts detected[/green]")