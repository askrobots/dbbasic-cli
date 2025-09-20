"""
Bootstrap DBBasic core for new installations
"""

import os
import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def get_dbbasic_home():
    """Get or create DBBasic home directory"""
    dbbasic_home = Path.home() / ".dbbasic"
    dbbasic_home.mkdir(exist_ok=True)
    return dbbasic_home

def is_dbbasic_installed():
    """Check if DBBasic core is installed"""
    dbbasic_home = get_dbbasic_home()
    core_dir = dbbasic_home / "core"
    return core_dir.exists() and (core_dir / "dbbasic_crud_engine.py").exists()

def install_dbbasic():
    """Install DBBasic core from GitHub"""
    dbbasic_home = get_dbbasic_home()
    core_dir = dbbasic_home / "core"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        # Clone repository
        task = progress.add_task("Installing DBBasic core...", total=4)

        if core_dir.exists():
            # Update existing installation
            progress.update(task, description="Updating DBBasic core...")
            subprocess.run(
                ["git", "pull"],
                cwd=str(core_dir),
                capture_output=True,
                check=False
            )
        else:
            # Fresh installation
            progress.update(task, description="Downloading DBBasic core...")
            result = subprocess.run(
                ["git", "clone", "https://github.com/askrobots/dbbasic.git", str(core_dir)],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                console.print(f"[red]Failed to download DBBasic: {result.stderr}[/red]")
                raise SystemExit(1)

        progress.advance(task)

        # Install dependencies
        progress.update(task, description="Installing dependencies...")
        requirements_file = core_dir / "requirements.txt"

        # Create minimal requirements if file doesn't exist
        if not requirements_file.exists():
            requirements = """
fastapi>=0.100.0
uvicorn>=0.24.0
duckdb>=0.9.0
pyyaml>=6.0
httpx>=0.25.0
websockets>=11.0
jinja2>=3.1.0
python-multipart>=0.0.5
pystructui>=0.1.0
"""
            requirements_file.write_text(requirements.strip())

        # Install requirements
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-r", str(requirements_file)],
            capture_output=True
        )
        progress.advance(task)

        # Create templates directory
        progress.update(task, description="Setting up templates...")
        templates_dir = core_dir / "templates"
        templates_dir.mkdir(exist_ok=True)

        # Create a basic CRM template if it doesn't exist
        crm_template_dir = templates_dir / "crm"
        crm_template_dir.mkdir(exist_ok=True)

        crm_config = crm_template_dir / "config.yaml"
        if not crm_config.exists():
            crm_config.write_text("""
# CRM Template Configuration
name: CRM
description: Customer Relationship Management

models:
  contacts:
    fields:
      - {name: name, type: string, required: true}
      - {name: email, type: email, unique: true}
      - {name: phone, type: string}
      - {name: company, type: string}
      - {name: status, type: enum, values: [lead, prospect, customer]}

  deals:
    fields:
      - {name: title, type: string, required: true}
      - {name: contact_id, type: reference, model: contacts}
      - {name: amount, type: decimal}
      - {name: stage, type: enum, values: [discovery, proposal, negotiation, closed]}
      - {name: close_date, type: date}

views:
  - {name: dashboard, type: dashboard}
  - {name: contacts, type: table, model: contacts}
  - {name: pipeline, type: kanban, model: deals, group_by: stage}
""")
        progress.advance(task)

        # Create minimal working engine if needed
        progress.update(task, description="Finalizing installation...")
        crud_engine = core_dir / "dbbasic_crud_engine.py"
        if not crud_engine.exists():
            # Create a minimal working CRUD engine
            crud_engine.write_text('''
"""
DBBasic CRUD Engine - Minimal working version
"""

from fastapi import FastAPI
import uvicorn
import yaml
from pathlib import Path

def create_app(config_file="dbbasic.yaml"):
    """Create FastAPI application from config"""
    app = FastAPI(title="DBBasic App")

    # Load configuration
    config_path = Path(config_file)
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
    else:
        config = {"project": {"name": "DBBasic App"}}

    @app.get("/")
    async def root():
        return {
            "message": f"Welcome to {config.get('project', {}).get('name', 'DBBasic')}",
            "status": "running",
            "config": config_file
        }

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')

        progress.advance(task)

    console.print("\n[green]✅ DBBasic core installed successfully![/green]")
    return core_dir

def ensure_dbbasic():
    """Ensure DBBasic is installed, install if not"""
    if not is_dbbasic_installed():
        console.print("[yellow]DBBasic core not found. Installing...[/yellow]")
        return install_dbbasic()
    else:
        dbbasic_home = get_dbbasic_home()
        return dbbasic_home / "core"

def get_dbbasic_dir():
    """Get the DBBasic directory, installing if necessary"""
    # First check if we're in development mode (local dbbasic exists)
    local_dbbasic = Path("/Users/danq/websheet/dbbasic")
    if local_dbbasic.exists():
        return local_dbbasic

    # Otherwise ensure it's installed
    return ensure_dbbasic()