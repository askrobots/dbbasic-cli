"""
DBBasic Engine - Unified App Server
The crate engine that replaces your entire stack
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import duckdb
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import asyncio
from datetime import datetime
import hashlib
from collections import defaultdict, OrderedDict
import uvicorn

# In-memory stores (will be backed by DuckDB)
QUEUES = defaultdict(list)
CACHE = OrderedDict()
CACHE_MAX_SIZE = 1000
JOBS = []
METRICS = defaultdict(int)

class DBBasicEngine:
    """The unified app server - one process to rule them all"""

    def __init__(self, config_file="dbbasic.yaml"):
        self.config_file = config_file
        self.app = FastAPI(title="DBBasic App")
        self.db = None
        self.config = {}
        self.models = {}

        # Load configuration
        self.load_config()

        # Initialize database
        self.init_database()

        # Setup all endpoints
        self.setup_routes()
        self.setup_crud_routes()
        self.setup_queue_routes()
        self.setup_cache_routes()
        self.setup_job_routes()
        self.setup_ui_routes()

    def load_config(self):
        """Load YAML configuration"""
        config_path = Path(self.config_file)
        if config_path.exists():
            with open(config_path) as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {
                "project": {"name": "DBBasic App", "type": "default"},
                "models": {}
            }

    def init_database(self):
        """Initialize DuckDB with schema from config"""
        self.db = duckdb.connect("dbbasic.db")

        # Create tables for each model
        if "models" in self.config:
            for model_def in self.config["models"]:
                if isinstance(model_def, dict):
                    for model_name, model_config in model_def.items():
                        self.create_model_table(model_name, model_config)

    def create_model_table(self, name: str, config: dict):
        """Create a DuckDB table from model config"""
        fields = config.get("fields", [])

        # Build CREATE TABLE statement
        columns = ["id INTEGER PRIMARY KEY"]

        for field in fields:
            field_name = field.get("name")
            field_type = field.get("type", "string")

            if not field_name:
                continue

            # Map types to DuckDB
            type_map = {
                "string": "VARCHAR",
                "text": "TEXT",
                "integer": "INTEGER",
                "decimal": "DECIMAL(10, 2)",
                "boolean": "BOOLEAN",
                "date": "DATE",
                "datetime": "TIMESTAMP",
                "email": "VARCHAR",
                "reference": "INTEGER"
            }

            # Handle enum specially
            if field_type == "enum" or "enum[" in str(field):
                sql_type = "VARCHAR"
            else:
                sql_type = type_map.get(field_type, "VARCHAR")

            # Add constraints
            constraints = []
            if field.get("required"):
                constraints.append("NOT NULL")
            if field.get("unique"):
                constraints.append("UNIQUE")

            column_def = f"{field_name} {sql_type}"
            if constraints:
                column_def += " " + " ".join(constraints)

            columns.append(column_def)

        # Create table
        create_sql = f"CREATE TABLE IF NOT EXISTS {name} ({', '.join(columns)})"
        self.db.execute(create_sql)

        self.models[name] = config

    def setup_routes(self):
        """Setup basic routes"""

        @self.app.get("/")
        async def root():
            return HTMLResponse(self.render_home())

        @self.app.get("/health")
        async def health():
            METRICS["health_checks"] += 1
            return {"status": "healthy", "app": self.config.get("project", {}).get("name")}

        @self.app.get("/api/config")
        async def get_config():
            return self.config

        @self.app.get("/api/metrics")
        async def get_metrics():
            return dict(METRICS)

    def setup_crud_routes(self):
        """Setup CRUD routes for all models"""

        for model_name in self.models:
            # List/Create
            @self.app.get(f"/api/{model_name}")
            async def list_items(model=model_name):
                METRICS[f"{model}_list"] += 1
                result = self.db.execute(f"SELECT * FROM {model}").fetchall()
                return [dict(zip([d[0] for d in self.db.description], row)) for row in result]

            @self.app.post(f"/api/{model_name}")
            async def create_item(data: dict, model=model_name):
                METRICS[f"{model}_create"] += 1

                # Build INSERT statement
                fields = list(data.keys())
                values = list(data.values())
                placeholders = ", ".join(["?" for _ in values])

                sql = f"INSERT INTO {model} ({', '.join(fields)}) VALUES ({placeholders})"
                self.db.execute(sql, values)

                # Queue event
                QUEUES[f"{model}_events"].append({
                    "action": "created",
                    "model": model,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                })

                return {"success": True, "model": model, "data": data}

            # Get/Update/Delete
            @self.app.get(f"/api/{model_name}/{{item_id}}")
            async def get_item(item_id: int, model=model_name):
                METRICS[f"{model}_get"] += 1
                result = self.db.execute(f"SELECT * FROM {model} WHERE id = ?", [item_id]).fetchone()
                if result:
                    return dict(zip([d[0] for d in self.db.description], result))
                raise HTTPException(status_code=404, detail="Not found")

    def setup_queue_routes(self):
        """Setup message queue routes (Kafka replacement)"""

        @self.app.post("/api/queue/{queue_name}/publish")
        async def publish_message(queue_name: str, message: dict):
            METRICS["queue_publish"] += 1
            QUEUES[queue_name].append({
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            return {"success": True, "queue": queue_name, "size": len(QUEUES[queue_name])}

        @self.app.get("/api/queue/{queue_name}/consume")
        async def consume_message(queue_name: str):
            METRICS["queue_consume"] += 1
            if QUEUES[queue_name]:
                return QUEUES[queue_name].pop(0)
            return None

        @self.app.get("/api/queue/{queue_name}/size")
        async def queue_size(queue_name: str):
            return {"queue": queue_name, "size": len(QUEUES[queue_name])}

    def setup_cache_routes(self):
        """Setup cache routes (Redis replacement)"""

        @self.app.get("/api/cache/{key}")
        async def get_cache(key: str):
            METRICS["cache_get"] += 1
            if key in CACHE:
                # Move to end (LRU)
                CACHE.move_to_end(key)
                METRICS["cache_hits"] += 1
                return CACHE[key]
            METRICS["cache_misses"] += 1
            return None

        @self.app.post("/api/cache/{key}")
        async def set_cache(key: str, value: dict):
            METRICS["cache_set"] += 1

            # Implement LRU eviction
            if len(CACHE) >= CACHE_MAX_SIZE:
                CACHE.popitem(last=False)

            CACHE[key] = {
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
            return {"success": True, "key": key}

        @self.app.delete("/api/cache/{key}")
        async def delete_cache(key: str):
            if key in CACHE:
                del CACHE[key]
                return {"success": True}
            return {"success": False, "error": "Key not found"}

    def setup_job_routes(self):
        """Setup job routes (Celery replacement)"""

        @self.app.post("/api/jobs")
        async def create_job(job: dict):
            METRICS["jobs_created"] += 1
            job_id = hashlib.md5(json.dumps(job).encode()).hexdigest()[:8]

            job_record = {
                "id": job_id,
                "status": "pending",
                "created": datetime.now().isoformat(),
                **job
            }

            JOBS.append(job_record)

            # Simulate job execution
            asyncio.create_task(self.execute_job(job_record))

            return {"job_id": job_id, "status": "queued"}

        @self.app.get("/api/jobs/{job_id}")
        async def get_job_status(job_id: str):
            for job in JOBS:
                if job["id"] == job_id:
                    return job
            raise HTTPException(status_code=404, detail="Job not found")

    async def execute_job(self, job: dict):
        """Execute a job asynchronously"""
        await asyncio.sleep(1)  # Simulate work
        job["status"] = "completed"
        job["completed"] = datetime.now().isoformat()
        METRICS["jobs_completed"] += 1

    def setup_ui_routes(self):
        """Setup UI routes"""

        @self.app.get("/ui/{model_name}")
        async def model_ui(model_name: str):
            return HTMLResponse(self.render_model_ui(model_name))

    def render_home(self):
        """Render home page"""
        project_name = self.config.get("project", {}).get("name", "DBBasic App")

        models_html = ""
        for model_name in self.models:
            models_html += f"""
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">{model_name.title()}</h5>
                        <p class="card-text">Manage {model_name} records</p>
                        <a href="/ui/{model_name}" class="btn btn-primary">View</a>
                        <a href="/api/{model_name}" class="btn btn-outline-secondary">API</a>
                    </div>
                </div>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{project_name}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <nav class="navbar navbar-dark bg-dark mb-4">
                <div class="container">
                    <span class="navbar-brand mb-0 h1">{project_name}</span>
                </div>
            </nav>

            <div class="container">
                <h1>Welcome to {project_name}</h1>
                <p class="lead">Built with DBBasic - The crate engine for web apps</p>

                <div class="row mt-4">
                    <div class="col-md-3">
                        <div class="card text-white bg-primary mb-3">
                            <div class="card-body">
                                <h5 class="card-title">Models</h5>
                                <h2>{len(self.models)}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-success mb-3">
                            <div class="card-body">
                                <h5 class="card-title">API Calls</h5>
                                <h2>{sum(v for k,v in METRICS.items() if k.endswith('_get') or k.endswith('_list'))}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-info mb-3">
                            <div class="card-body">
                                <h5 class="card-title">Cache Hit Rate</h5>
                                <h2>{int(METRICS.get('cache_hits', 0) / max(1, METRICS.get('cache_hits', 0) + METRICS.get('cache_misses', 0)) * 100)}%</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-warning mb-3">
                            <div class="card-body">
                                <h5 class="card-title">Jobs</h5>
                                <h2>{METRICS.get('jobs_completed', 0)}/{METRICS.get('jobs_created', 0)}</h2>
                            </div>
                        </div>
                    </div>
                </div>

                <h2 class="mt-4">Models</h2>
                <div class="row">
                    {models_html}
                </div>

                <h2 class="mt-4">Stack Replacement</h2>
                <div class="row">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">🚀 Message Queue</h5>
                                <p class="card-text">Replaces Kafka/RabbitMQ</p>
                                <code>POST /api/queue/orders/publish</code>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">💾 Cache</h5>
                                <p class="card-text">Replaces Redis/Memcached</p>
                                <code>GET /api/cache/user:123</code>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">⚙️ Job Queue</h5>
                                <p class="card-text">Replaces Celery/Sidekiq</p>
                                <code>POST /api/jobs</code>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mt-4">
                    <a href="/docs" class="btn btn-outline-primary">API Documentation</a>
                    <a href="/api/metrics" class="btn btn-outline-secondary">Metrics</a>
                </div>
            </div>
        </body>
        </html>
        """

    def render_model_ui(self, model_name: str):
        """Render UI for a specific model"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{model_name.title()} - DBBasic</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <nav class="navbar navbar-dark bg-dark mb-4">
                <div class="container">
                    <a class="navbar-brand" href="/">DBBasic</a>
                </div>
            </nav>

            <div class="container">
                <h1>{model_name.title()}</h1>
                <table class="table" id="dataTable">
                    <thead>
                        <tr id="headerRow"></tr>
                    </thead>
                    <tbody id="dataBody"></tbody>
                </table>

                <button class="btn btn-primary" onclick="addNew()">Add New</button>
            </div>

            <script>
            // Load data
            fetch('/api/{model_name}')
                .then(r => r.json())
                .then(data => {{
                    if (data.length > 0) {{
                        // Build headers
                        const headers = Object.keys(data[0]);
                        document.getElementById('headerRow').innerHTML =
                            headers.map(h => `<th>${{h}}</th>`).join('');

                        // Build rows
                        document.getElementById('dataBody').innerHTML =
                            data.map(row =>
                                '<tr>' + headers.map(h => `<td>${{row[h]}}</td>`).join('') + '</tr>'
                            ).join('');
                    }}
                }});

            function addNew() {{
                alert('Add form would go here');
            }}
            </script>
        </body>
        </html>
        """


def create_app(config_file="dbbasic.yaml"):
    """Create FastAPI application from config"""
    engine = DBBasicEngine(config_file)
    return engine.app


if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)