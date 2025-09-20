#!/usr/bin/env python3
"""
DBBasic CLI - Main application
"""

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path

from .commands import start, status, stop, logs, ports, open_service
from .commands import crm, shop, blog

console = Console()
app = typer.Typer(
    name="dbbasic",
    help="DBBasic - The crate engine for web apps. Zero to running app in 30 seconds.",
    no_args_is_help=True,
    add_completion=False,
)

# Phase 1: Core service commands
app.command("start")(start.start)
app.command("stop")(stop.stop)
app.command("status")(status.status)
app.command("logs")(logs.logs)
app.command("ports")(ports.ports)
app.command("open")(open_service.open_service)

# Phase 2: Instant app generators
app.command("crm")(crm.create_crm)
app.command("shop")(shop.create_shop)
app.command("blog")(blog.create_blog)

@app.callback()
def callback():
    """
    DBBasic - Replace your entire stack with one command.

    Quick start:
        dbbasic crm     # Instant CRM app
        dbbasic shop    # Instant e-commerce
        dbbasic blog    # Instant blog
    """
    pass

@app.command()
def version():
    """Show version information"""
    from . import __version__
    console.print(f"[bold blue]DBBasic CLI[/bold blue] version {__version__}")
    console.print("The crate engine for web apps 🚀")

@app.command()
def doctor():
    """Diagnose and fix common issues"""
    console.print("[bold]🏥 Running diagnostics...[/bold]\n")

    checks = []

    # Check if DuckDB is available
    try:
        import duckdb
        checks.append(("DuckDB", "✅", duckdb.__version__))
    except ImportError:
        checks.append(("DuckDB", "❌", "Not installed"))

    # Check if FastAPI is available
    try:
        import fastapi
        checks.append(("FastAPI", "✅", fastapi.__version__))
    except ImportError:
        checks.append(("FastAPI", "❌", "Not installed"))

    # Check if ports are available
    import socket
    for port in [8000, 8003, 8004, 8005, 8007]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        if result == 0:
            checks.append((f"Port {port}", "⚠️", "In use"))
        else:
            checks.append((f"Port {port}", "✅", "Available"))

    # Display results
    table = Table(title="System Check")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Info")

    for component, status, info in checks:
        table.add_row(component, status, info)

    console.print(table)

    # Check for issues
    issues = [c for c in checks if c[1] != "✅"]
    if issues:
        console.print("\n[yellow]⚠️  Found issues that may need attention[/yellow]")
    else:
        console.print("\n[green]✅ All systems operational![/green]")

if __name__ == "__main__":
    app()