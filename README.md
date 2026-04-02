# PPWR Packaging Compliance Workspace

A practical web application for managing packaging data, suppliers, compliance evidence, requirements, gaps, and dossiers related to the EU Packaging and Packaging Waste Regulation (PPWR).

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Load demo data
python -m seeds.seed_data

# Run the application
python run.py
```

Open **http://localhost:5000** and log in with `admin` / `admin`.

## Features

- **Dashboard** — Overview of packaging portfolio with status counts, open gaps, and at-risk items
- **Packaging Register** — Create and manage packaging items (sales, grouped, transport, e-commerce)
- **Components** — Define packaging structure with materials, weights, recycled content, food-contact flags
- **Supplier Management** — Supplier records with contacts, linked components, and documents
- **Document Management** — Upload and track compliance documents with types, statuses, and validity dates
- **Requirement Library** — Configurable PPWR requirement matrix with applicability rules
- **Assessments** — Auto-assess which requirements apply based on packaging type, materials, and food-contact
- **Gap Detection** — Auto-generate gaps for missing data, documents, and supplier info
- **Task Tracking** — Create tasks from gaps, assign owners, track due dates
- **Packaging Dossier** — Full compliance dossier view and HTML export per packaging item
- **Audit Logging** — Track key actions on packaging items

## Demo Accounts

| Username | Password | Role  |
|----------|----------|-------|
| admin    | admin    | Admin |
| analyst  | analyst  | User  |

## Demo Data

The seed script loads realistic demo data:
- 5 suppliers with contacts
- 8 packaging items across all packaging types
- 18 components with varied materials
- 9 PPWR requirements across categories
- 10 documents in various statuses
- 6 gaps and 5 tasks

## Tech Stack

- **Backend:** Python 3.11+ / Flask
- **Database:** SQLite (designed for easy PostgreSQL migration)
- **ORM:** SQLAlchemy
- **Frontend:** Jinja2 templates + Bootstrap 5
- **Auth:** Flask-Login with session-based auth
- **Tests:** pytest

## Project Structure

```
app/
  __init__.py          # App factory
  models/              # SQLAlchemy models
  services/            # Business logic (assessment, gaps, audit)
  routes/              # Flask blueprints
  templates/           # Jinja2 HTML templates
  static/              # CSS/JS assets
seeds/
  seed_data.py         # Demo data loader
tests/                 # pytest test suite
uploads/               # Document upload storage
run.py                 # Development server entry point
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Key Workflows

### Assess a Packaging Item
1. Go to Packaging → select an item
2. Click **Run Assessment** — evaluates which requirements apply
3. Click **Generate Gaps** — detects missing data and documents
4. Review gaps and create tasks from them

### Export a Dossier
1. Go to Packaging → select an item → **View Dossier**
2. Click **Export HTML** for a standalone compliance summary

## Architecture Decisions

- **Modular monolith** with clear domain separation via Flask blueprints
- **Service layer** for business logic (assessment_service, gap_service, status_service)
- **Configurable requirements** via database, not hard-coded rules
- **Simple rule engine** for applicability based on packaging type, materials, and food-contact
- **SQLite** for local development simplicity (swap to PostgreSQL via `DATABASE_URL` env var)

## What's Not Included (Future Phases)

- AI/OCR features
- ERP/PLM integration
- Advanced workflow engine
- Full multi-country regulatory coverage
- Role-based permissions
- CSV import/export
- LCA calculations
- Multi-tenant billing
