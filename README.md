# DBBasic CLI

**The crate engine for web apps** - Zero to running app in 30 seconds.

Replace your entire web development stack with a single command. DBBasic gives you the power of PostgreSQL, Redis, Kafka, Celery, Elasticsearch, and more - all in one process.

## Installation

```bash
pip install dbbasic-cli
```

Or run directly without installing:
```bash
pipx run dbbasic-cli crm
```

## Quick Start

### Create instant applications

```bash
# Create a complete CRM in 30 seconds
dbbasic crm

# Create an e-commerce shop
dbbasic shop

# Create a blog
dbbasic blog
```

Each command creates a **complete, running application** with:
- Database with sample data
- API with documentation
- Admin interface
- User interface
- Real-time features
- AI services

### Manage services

```bash
# Start all DBBasic services
dbbasic start

# Check status
dbbasic status

# View logs
dbbasic logs -f

# Stop services
dbbasic stop
```

### Development workflow

```bash
# Check system health
dbbasic doctor

# Open dashboard in browser
dbbasic open

# View port usage
dbbasic ports
```

## What's Included

### 🚀 Instant Apps
- **CRM**: Contacts, deals, pipeline, lead scoring
- **Shop**: Products, cart, checkout, inventory
- **Blog**: Posts, comments, SEO, social sharing

### 🔧 Built-in Stack
- **Database**: DuckDB with 402M rows/sec performance
- **Queue**: Message queue (replaces Kafka)
- **Jobs**: Background processing (replaces Celery)
- **Cache**: In-memory cache (replaces Redis)
- **Search**: Full-text search (replaces Elasticsearch)
- **Monitoring**: Real-time metrics (replaces Grafana)

### 🎯 Zero Configuration
- No YAML files to write
- No Docker to configure
- No services to orchestrate
- Just run and go

## Examples

### Create and run a CRM

```bash
# Create the CRM
dbbasic crm my-crm

# Navigate to the project
cd my-crm

# Start the application
python run.py

# Open in browser
open http://localhost:8000
```

### Start existing DBBasic project

```bash
# In a DBBasic project directory
dbbasic start

# Check what's running
dbbasic status
✅ Real-time Monitor    [8004] Running
✅ CRUD Engine         [8005] Running
✅ AI Service Builder  [8003] Running
✅ Event Store         [8007] Running

# Open the dashboard
dbbasic open
```

## Philosophy

DBBasic follows the Unix philosophy:
- **Do one thing well**: Each command has a clear purpose
- **Compose freely**: Commands work together
- **Text interface**: Everything is pipeable
- **No surprises**: Smart defaults, no wizards

## Why DBBasic?

**Traditional stack:**
- 12+ services to configure
- 8GB RAM minimum
- DevOps team required
- Days to set up

**DBBasic:**
- 1 command
- 200MB RAM
- Works instantly
- 30 seconds to running app

## Requirements

- Python 3.8+
- DuckDB
- FastAPI

## License

MIT

## Contributing

DBBasic is open source. Contribute at:
https://github.com/askrobots/dbbasic

---

**"We replaced your entire infrastructure with a single command"**