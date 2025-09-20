"""Start DBBasic services"""

import subprocess
import time
from pathlib import Path
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import psutil

from .config import SERVICES, DBBASIC_DIR, save_pid, get_pid

console = Console()

def start(service: str = typer.Argument(None, help="Service to start (omit for all)")):
    """Start DBBasic services"""
    
    if service and service not in SERVICES:
        console.print(f"[red]Unknown service: {service}[/red]")
        console.print(f"Available: {', '.join(SERVICES.keys())}")
        raise typer.Exit(1)
    
    services_to_start = [service] if service else list(SERVICES.keys())
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        for svc_name in services_to_start:
            svc = SERVICES[svc_name]
            task = progress.add_task(f"Starting {svc['name']}...", total=1)
            
            # Check if already running
            pid = get_pid(svc_name)
            if pid and psutil.pid_exists(pid):
                progress.update(task, description=f"[yellow]{svc['name']} already running[/yellow]")
                progress.advance(task)
                continue
            
            # Start the service
            try:
                process = subprocess.Popen(
                    ["python", f"{svc['module']}.py"],
                    cwd=str(DBBASIC_DIR),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                
                # Save PID
                save_pid(svc_name, process.pid)
                
                # Wait a moment to check if it started
                time.sleep(1)
                
                if process.poll() is None:
                    progress.update(task, description=f"[green]✅ {svc['name']} started on port {svc['port']}[/green]")
                else:
                    progress.update(task, description=f"[red]❌ {svc['name']} failed to start[/red]")
                    
            except Exception as e:
                progress.update(task, description=f"[red]❌ {svc['name']}: {str(e)}[/red]")
            
            progress.advance(task)
    
    # Show summary
    if not service:
        console.print("\n[bold green]DBBasic services started![/bold green]")
        console.print("\nAccess points:")
        console.print(f"  📊 Dashboard: http://localhost:{SERVICES['monitor']['port']}")
        console.print(f"  🔧 CRUD Engine: http://localhost:{SERVICES['crud']['port']}")
        console.print(f"  📚 API Docs: http://localhost:{SERVICES['crud']['port']}/docs")
        console.print("\nRun [bold]dbbasic status[/bold] to check service health")