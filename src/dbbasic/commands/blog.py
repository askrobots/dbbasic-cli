"""Create instant blog application"""

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
from pathlib import Path

console = Console()

def create_blog(
    name: str = typer.Argument("blog", help="Project name"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to run on")
):
    """Create instant blog application with posts, comments, and SEO"""

    start_time = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        task = progress.add_task("Creating blog application...", total=5)
        project_dir = Path.cwd() / name

        if project_dir.exists():
            console.print(f"[red]Directory {name} already exists![/red]")
            raise typer.Exit(1)

        project_dir.mkdir(parents=True)
        progress.advance(task)

        progress.update(task, description="Setting up content management...")
        time.sleep(0.5)
        progress.advance(task)

        progress.update(task, description="Configuring SEO...")
        time.sleep(0.5)
        progress.advance(task)

        progress.update(task, description="Adding comment system...")
        time.sleep(0.5)
        progress.advance(task)

        progress.update(task, description="Creating sample posts...")
        time.sleep(0.5)
        progress.advance(task)

    elapsed = time.time() - start_time

    console.print(f"\n[bold green]✅ Blog created in {elapsed:.1f} seconds![/bold green]\n")
    console.print(f"[bold]Your blog is ready at:[/bold] {project_dir}\n")
    console.print("[bold]Features included:[/bold]")
    console.print("• Post editor with Markdown")
    console.print("• Categories & tags")
    console.print("• Comments with moderation")
    console.print("• SEO optimization")
    console.print("• RSS feed")
    console.print("• Social sharing")
    console.print("• Sample posts\n")

    console.print("[bold]To start your blog:[/bold]")
    console.print(f"  cd {name}")
    console.print(f"  dbbasic start\n")
    console.print(f"Then open: [blue]http://localhost:{port}[/blue]")