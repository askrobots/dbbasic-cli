"""Create instant CRM application"""

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
from pathlib import Path
import shutil
import subprocess

from .config import DBBASIC_DIR
from ..bootstrap import ensure_dbbasic

console = Console()

def create_crm(
    name: str = typer.Argument("crm", help="Project name"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to run on")
):
    """Create instant CRM application with contacts, deals, and pipeline"""

    # Ensure DBBasic is installed
    dbbasic_dir = ensure_dbbasic()

    start_time = time.time()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Create project directory
        task = progress.add_task("Creating CRM application...", total=5)
        project_dir = Path.cwd() / name
        
        if project_dir.exists():
            console.print(f"[red]Directory {name} already exists![/red]")
            raise typer.Exit(1)
        
        project_dir.mkdir(parents=True)
        progress.advance(task)
        progress.update(task, description="Setting up database...")
        
        # Create configuration
        config = f"""
# DBBasic CRM Configuration
project:
  name: {name}
  type: crm
  port: {port}

models:
  - contacts:
      fields:
        - name: string required
        - email: email unique
        - phone: string
        - company: string
        - status: enum[lead,prospect,customer,inactive]
        - value: decimal
        - notes: text
  
  - deals:
      fields:
        - title: string required
        - contact_id: reference[contacts]
        - amount: decimal
        - stage: enum[discovery,proposal,negotiation,closed_won,closed_lost]
        - probability: integer
        - close_date: date
        - notes: text
  
  - activities:
      fields:
        - type: enum[call,email,meeting,task]
        - subject: string required
        - contact_id: reference[contacts]
        - deal_id: reference[deals]
        - due_date: datetime
        - completed: boolean
        - notes: text

views:
  - dashboard:
      type: metrics
      queries:
        - total_contacts: SELECT COUNT(*) FROM contacts
        - active_deals: SELECT COUNT(*) FROM deals WHERE stage NOT IN ('closed_won', 'closed_lost')
        - pipeline_value: SELECT SUM(amount) FROM deals WHERE stage NOT IN ('closed_won', 'closed_lost')
  
  - pipeline:
      type: kanban
      model: deals
      group_by: stage
      card_fields: [title, amount, contact_id, close_date]

services:
  - lead_scoring:
      description: "Score leads based on engagement and value"
      trigger: contacts.on_update
  
  - deal_probability:
      description: "Calculate deal win probability"
      trigger: deals.on_update
"""
        
        (project_dir / "dbbasic.yaml").write_text(config)
        progress.advance(task)
        
        # Create sample data
        progress.update(task, description="Adding sample data...")
        
        sample_data = f"""
# Sample CRM Data
INSERT INTO contacts (name, email, phone, company, status, value) VALUES
  ('John Smith', 'john@acme.com', '555-0101', 'Acme Corp', 'customer', 50000),
  ('Jane Doe', 'jane@globex.com', '555-0102', 'Globex Inc', 'prospect', 75000),
  ('Bob Wilson', 'bob@initech.com', '555-0103', 'Initech', 'lead', 25000);

INSERT INTO deals (title, contact_id, amount, stage, probability, close_date) VALUES
  ('Acme Corp - Enterprise Plan', 1, 50000, 'negotiation', 75, '2024-02-01'),
  ('Globex Inc - Starter Plan', 2, 15000, 'proposal', 50, '2024-02-15'),
  ('Initech - Custom Solution', 3, 100000, 'discovery', 25, '2024-03-01');

INSERT INTO activities (type, subject, contact_id, due_date, completed) VALUES
  ('call', 'Follow up on proposal', 1, '2024-01-20 14:00', false),
  ('meeting', 'Demo presentation', 2, '2024-01-22 10:00', false),
  ('email', 'Send contract', 3, '2024-01-21 09:00', false);
"""
        
        (project_dir / "sample_data.sql").write_text(sample_data)
        progress.advance(task)
        
        # Create startup script
        progress.update(task, description="Creating startup scripts...")
        
        startup_script = f'''#!/usr/bin/env python3
"""
DBBasic CRM - Quick Start
"""

import sys
import os
sys.path.insert(0, '{dbbasic_dir}')

from dbbasic_crud_engine import create_app
import uvicorn

if __name__ == "__main__":
    app = create_app(config_file="dbbasic.yaml")
    uvicorn.run(app, host="0.0.0.0", port={port})
'''
        
        (project_dir / "run.py").write_text(startup_script)
        (project_dir / "run.py").chmod(0o755)
        progress.advance(task)
        
        # Final setup
        progress.update(task, description="Finalizing...")
        time.sleep(0.5)  # Brief pause for effect
        progress.advance(task)
    
    elapsed = time.time() - start_time
    
    # Success message
    console.print(f"\n[bold green]✅ CRM created in {elapsed:.1f} seconds![/bold green]\n")
    console.print(f"[bold]Your CRM is ready at:[/bold] {project_dir}\n")
    console.print("[bold]Features included:[/bold]")
    console.print("• Contact management")
    console.print("• Deal pipeline (Kanban view)")
    console.print("• Activity tracking")
    console.print("• Lead scoring (AI-powered)")
    console.print("• Dashboard with metrics")
    console.print("• API with documentation")
    console.print("• Sample data\n")
    
    console.print("[bold]To start your CRM:[/bold]")
    console.print(f"  cd {name}")
    console.print(f"  python run.py\n")
    console.print(f"Then open: [blue]http://localhost:{port}[/blue]\n")
    console.print("[dim]API docs will be at:[/dim] [blue]http://localhost:{port}/docs[/blue]")