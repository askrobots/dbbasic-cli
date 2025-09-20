"""Check status of DBBasic services"""

import socket
import typer
from rich.console import Console
from rich.table import Table
import psutil
import httpx

from .config import SERVICES, get_pid

console = Console()

def check_port(port):
    """Check if port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def get_process_info(pid):
    """Get process information"""
    try:
        process = psutil.Process(pid)
        return {
            "cpu": f"{process.cpu_percent()}%",
            "memory": f"{process.memory_info().rss / 1024 / 1024:.1f}MB",
            "status": "Running"
        }
    except:
        return None

def status(verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information")):
    """Check status of DBBasic services"""
    
    table = Table(title="DBBasic Service Status")
    table.add_column("Service", style="cyan")
    table.add_column("Port", style="magenta")
    table.add_column("Status", style="bold")
    
    if verbose:
        table.add_column("PID")
        table.add_column("CPU")
        table.add_column("Memory")
    
    all_running = True
    
    for svc_name, svc in SERVICES.items():
        pid = get_pid(svc_name)
        port_open = check_port(svc['port'])
        
        if pid and psutil.pid_exists(pid) and port_open:
            status_icon = "✅ Running"
            status_color = "green"
            
            if verbose:
                info = get_process_info(pid)
                table.add_row(
                    svc['name'],
                    str(svc['port']),
                    f"[{status_color}]{status_icon}[/{status_color}]",
                    str(pid),
                    info['cpu'] if info else "N/A",
                    info['memory'] if info else "N/A"
                )
            else:
                table.add_row(
                    svc['name'],
                    str(svc['port']),
                    f"[{status_color}]{status_icon}[/{status_color}]"
                )
        else:
            all_running = False
            status_icon = "❌ Stopped"
            status_color = "red"
            
            if verbose:
                table.add_row(
                    svc['name'],
                    str(svc['port']),
                    f"[{status_color}]{status_icon}[/{status_color}]",
                    "-",
                    "-",
                    "-"
                )
            else:
                table.add_row(
                    svc['name'],
                    str(svc['port']),
                    f"[{status_color}]{status_icon}[/{status_color}]"
                )
    
    console.print(table)
    
    if all_running:
        console.print("\n[green]✅ All services operational![/green]")
    else:
        console.print("\n[yellow]⚠️  Some services are not running[/yellow]")
        console.print("Run [bold]dbbasic start[/bold] to start all services")