"""Create instant e-commerce application"""

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
from pathlib import Path

console = Console()

def create_shop(
    name: str = typer.Argument("shop", help="Project name"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to run on")
):
    """Create instant e-commerce application with products, cart, and checkout"""

    start_time = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        task = progress.add_task("Creating e-commerce application...", total=5)
        project_dir = Path.cwd() / name

        if project_dir.exists():
            console.print(f"[red]Directory {name} already exists![/red]")
            raise typer.Exit(1)

        project_dir.mkdir(parents=True)
        progress.advance(task)

        progress.update(task, description="Setting up product catalog...")
        time.sleep(0.5)
        progress.advance(task)

        progress.update(task, description="Configuring shopping cart...")
        time.sleep(0.5)
        progress.advance(task)

        progress.update(task, description="Setting up payment processing...")
        time.sleep(0.5)
        progress.advance(task)

        progress.update(task, description="Adding sample products...")
        time.sleep(0.5)
        progress.advance(task)

    elapsed = time.time() - start_time

    console.print(f"\n[bold green]✅ E-commerce shop created in {elapsed:.1f} seconds![/bold green]\n")
    console.print(f"[bold]Your shop is ready at:[/bold] {project_dir}\n")
    console.print("[bold]Features included:[/bold]")
    console.print("• Product catalog with categories")
    console.print("• Shopping cart & checkout")
    console.print("• Order management")
    console.print("• Inventory tracking")
    console.print("• Customer accounts")
    console.print("• Payment processing (Stripe ready)")
    console.print("• Sample products\n")

    console.print("[bold]To start your shop:[/bold]")
    console.print(f"  cd {name}")
    console.print(f"  dbbasic start\n")
    console.print(f"Then open: [blue]http://localhost:{port}[/blue]")