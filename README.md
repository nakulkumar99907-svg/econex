# ECONEX — Hyperlocal Opportunity Network (Full-Stack)

ECONEX connects local student talent with businesses using verified skills, portfolio evidence, AI matching, and a 3 km hyperlocal geospatial database.

This repository contains the complete unified full-stack application:
- **Frontend**: Responsive single-page application with Dashboard, Hyperlocal Opportunity Map, Live Job Search & Filters, Student Profile, Real Applications Tracker, and Post Task Modal.
- **Backend API**: Pure-Python REST & ASGI server with AI requirement extraction and explainable scoring.
- **Database Engine**: Persistent SQLite database with real Haversine spatial calculations (`haversine_distance`), pre-seeded with local opportunities, students, and businesses.

---

## Quick Start (Run the Full Stack)

Run a single command from the project root:

```bash
python run.py
```

Or from the `backend/` directory:

```bash
cd backend
python main.py
```

Once running:
- **Web Application**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Features & Integration

1. **Integrated Web App Serving**:
   The backend automatically serves the frontend at the root URL `http://127.0.0.1:8000/`. No separate web server is required.

2. **Geospatial Database (`database/econex.db`)**:
   - Real PostGIS-style distance queries via SQLite custom `haversine_distance()` function.
   - Live filtering by radius (1 km, 3 km, 5 km, 10 km) and skills.
   - Persistent storage for tasks posted by businesses and applications submitted by students.

3. **AI Matching & Sourcing Layer**:
   - `extract_requirements()`: AI extraction of normalized skills, budgets, and constraints from task postings.
   - `explain_score()`: Explainable match breakdown across skills, portfolio evidence, location fit, and availability.
   - `generate_skill_gap()`: Missing skills converted into actionable student learning pathways.

4. **REST Endpoints**:
   - `GET /` — Serves the interactive ECONEX web frontend.
   - `GET /api/jobs?radius_km=3&skill=react` — Nearby opportunities from SQLite.
   - `POST /api/tasks` — Post a local business task into SQLite.
   - `POST /api/applications` — Submit application with AI match scoring.
   - `GET /api/applications` — Real student applications list.
   - `GET /api/stats` — Live aggregated dashboard statistics.
   - `GET /api/profile` — Student profile and portfolio evidence.
   - `GET /api/skill-gap/{id}` — Personalized skill gap report.
   - `GET /docs` — Interactive API explorer.

---

## Project Structure

```
econex/
├── frontend/
│   └── index.html          # Interactive web application UI
├── backend/
│   ├── main.py             # Unified server & request dispatcher
│   ├── db.py               # SQLite geospatial database engine
│   ├── ai_service.py       # AI matching & requirement extraction
│   └── requirements.txt    # Optional dependencies
├── database/
│   ├── schema.sql          # SQL schema reference
│   └── econex.db           # Persistent SQLite database
├── run.py                  # Single-command launcher
└── README.md
```
