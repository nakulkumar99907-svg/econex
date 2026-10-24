# ECONEX — Hyperlocal Opportunity Network

This package contains the complete working prototype plus a FastAPI backend scaffold.

## Included

### Student
- Dashboard
- Nearby jobs
- Search/filter
- 3 km hyperlocal opportunity map
- Profile
- Skills/portfolio
- AI match score
- Skill-gap analysis
- Learn → Apply
- Applications
- Premium

### Business
- Business workspace
- Post local task
- Budget/deadline/radius
- AI shortlist UI
- Candidate match scores
- Evidence workflow

### AI / platform
- Demand → extraction → match → gap → action
- FastAPI API
- PostgreSQL/PostGIS schema
- Matching service
- Hyperlocal query
- Revenue/scaling architecture

## Run frontend

Open `frontend/index.html` directly in a browser.

## Run backend

You can run the backend directly with Python (no extra installations needed):

```bash
cd backend
python main.py
```

Or using uvicorn (ASGI mode):

```bash
cd backend
uvicorn main:app --reload
```

API docs: http://127.0.0.1:8000/docs
Health check: http://127.0.0.1:8000/health

## Production next steps

1. Connect PostgreSQL/PostGIS.
2. Add authentication and role-based access.
3. Replace demo jobs with database queries.
4. Add real geocoding/maps.
5. Add LLM requirement extraction.
6. Add embeddings/vector search.
7. Add verified portfolio evidence storage.
8. Connect TinyFish/Fetch/Search ingestion.
9. Add Redis caching and background workers.
10. Deploy frontend and API separately.
