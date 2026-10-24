from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(title="ECONEX API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Task(BaseModel):
    title: str
    description: str = ""
    budget: float = 0
    deadline: Optional[str] = None
    latitude: float
    longitude: float
    radius_km: float = 3
    skills: List[str] = []

class MatchRequest(BaseModel):
    task_id: int
    student_id: int

@app.get("/")
def root():
    return {"product": "ECONEX", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/jobs")
def jobs(radius_km: float = 3, skill: Optional[str] = None):
    # Replace this demo response with a PostGIS query in production.
    data = [
        {"id": 1, "title": "Local Business Growth Intern", "business": "GreenLeaf Cafe", "distance_km": 1.4, "match": 94},
        {"id": 2, "title": "React Website Sprint", "business": "Nexa Retail", "distance_km": 2.1, "match": 89},
        {"id": 3, "title": "Student Data Analyst", "business": "CampusCart", "distance_km": 0.8, "match": 84},
    ]
    if skill:
        data = [x for x in data if skill.lower() in x["title"].lower()]
    return {"items": [x for x in data if x["distance_km"] <= radius_km]}

@app.post("/tasks")
def create_task(task: Task):
    return {"id": 101, "status": "created", "task": task, "ai_shortlist": True}

@app.post("/match")
def match(req: MatchRequest):
    return {
        "student_id": req.student_id,
        "task_id": req.task_id,
        "score": 0.96,
        "components": {
            "skill_similarity": 0.93,
            "portfolio_evidence": 0.91,
            "location_fit": 0.98,
            "availability": 0.85
        }
    }

@app.get("/applications")
def applications(student_id: int = 1):
    return {"items": [
        {"task": "Local Business Growth Intern", "status": "Interview"},
        {"task": "React Website Sprint", "status": "Shortlisted"},
        {"task": "Student Data Analyst", "status": "Selected"},
    ]}

@app.get("/skill-gap/{student_id}")
def skill_gap(student_id: int):
    return {"student_id": student_id, "gaps": [
        {"skill": "SEO analytics", "gap": 0.32},
        {"skill": "Client pitching", "gap": 0.41},
        {"skill": "Advanced SQL", "gap": 0.54},
    ]}
