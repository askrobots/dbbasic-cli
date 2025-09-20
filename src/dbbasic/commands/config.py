"""
Service configuration and registry
"""

from pathlib import Path
from ..bootstrap import get_dbbasic_dir

# Base directory for DBBasic (auto-installs if needed)
DBBASIC_DIR = get_dbbasic_dir()

# Service registry
SERVICES = {
    "crud": {
        "name": "CRUD Engine",
        "module": "dbbasic_crud_engine",
        "port": 8005,
        "url": "http://localhost:8005",
        "description": "Data management interface"
    },
    "monitor": {
        "name": "Real-time Monitor",
        "module": "realtime_monitor",
        "port": 8004,
        "url": "http://localhost:8004",
        "description": "System dashboard"
    },
    "ai": {
        "name": "AI Service Builder",
        "module": "dbbasic_ai_service_builder",
        "port": 8003,
        "url": "http://localhost:8003",
        "description": "AI-powered service generator"
    },
    "event": {
        "name": "Event Store",
        "module": "dbbasic_event_store",
        "port": 8007,
        "url": "http://localhost:8007",
        "description": "Event sourcing system"
    },
}

# PID file location
PID_DIR = Path.home() / ".dbbasic" / "pids"
PID_DIR.mkdir(parents=True, exist_ok=True)

def get_pid_file(service_name):
    """Get PID file path for a service"""
    return PID_DIR / f"{service_name}.pid"

def save_pid(service_name, pid):
    """Save process PID"""
    pid_file = get_pid_file(service_name)
    pid_file.write_text(str(pid))

def get_pid(service_name):
    """Get saved PID for service"""
    pid_file = get_pid_file(service_name)
    if pid_file.exists():
        try:
            return int(pid_file.read_text().strip())
        except:
            return None
    return None

def remove_pid(service_name):
    """Remove PID file"""
    pid_file = get_pid_file(service_name)
    if pid_file.exists():
        pid_file.unlink()