"""
ECONEX Database Engine (SQLite + Geospatial Haversine Engine)
Handles automatic schema creation, spatial radius filtering,
and CRUD operations for students, businesses, tasks, and applications.
"""

import sqlite3
import json
import math
import os
from pathlib import Path

# Database path: <workspace>/database/econex.db
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "econex.db"

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees).
    """
    try:
        if None in (lat1, lon1, lat2, lon2):
            return 9999.0
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
        r = 6371.0  # Earth radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(r * c, 2)
    except Exception:
        return 9999.0

def get_connection():
    """Returns a connection to the SQLite database with custom spatial functions."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.create_function("haversine_distance", 4, haversine)
    return conn

def init_db():
    """Initializes tables and seeds initial data if not already present."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        college TEXT DEFAULT 'Delhi University',
        major TEXT DEFAULT 'CSE',
        year TEXT DEFAULT '2nd year',
        latitude REAL DEFAULT 28.6139,
        longitude REAL DEFAULT 77.2090,
        availability_hours INTEGER DEFAULT 15,
        skills TEXT DEFAULT '["C++", "Python", "React", "SQL", "Figma", "Communication"]',
        portfolio TEXT DEFAULT '[{"title": "ECONEX Hackathon prototype", "status": "Verified"}, {"title": "React dashboard project", "status": "Verified"}]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Businesses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS businesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        latitude REAL,
        longitude REAL,
        category TEXT DEFAULT 'Local Business',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Tasks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER REFERENCES businesses(id),
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        budget REAL DEFAULT 0,
        pay TEXT DEFAULT 'Negotiable',
        deadline TEXT,
        radius_km REAL DEFAULT 3.0,
        latitude REAL,
        longitude REAL,
        skills TEXT DEFAULT '[]',
        status TEXT DEFAULT 'open',
        match_score INTEGER DEFAULT 88,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Applications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER REFERENCES tasks(id),
        student_id INTEGER REFERENCES students(id),
        status TEXT DEFAULT 'Applied',
        match_score INTEGER DEFAULT 90,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()

    # Seed initial data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        _seed_data(cursor, conn)

    conn.close()

def _seed_data(cursor, conn):
    """Seed initial student, businesses, tasks, and applications."""
    # Seed student
    cursor.execute("""
    INSERT INTO students (name, email, college, major, year, latitude, longitude, availability_hours, skills, portfolio)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Nakul Kumar",
        "nakul@econex.local",
        "Delhi Technological University",
        "Computer Science",
        "2nd year",
        28.6139,
        77.2090,
        15,
        json.dumps(["C++", "Python", "React", "SQL", "Figma", "Communication"]),
        json.dumps([
            {"title": "ECONEX Hackathon prototype", "status": "Verified"},
            {"title": "React dashboard project", "status": "Verified"}
        ])
    ))
    student_id = cursor.lastrowid

    # Seed businesses
    businesses = [
        ("GreenLeaf Cafe", "contact@greenleaf.local", 28.6220, 77.2180, "F&B / Hospitality"),
        ("Nexa Retail", "hiring@nexaretail.local", 28.6280, 77.2240, "E-Commerce & Retail"),
        ("CampusCart", "team@campuscart.local", 28.6100, 77.2030, "Campus Marketplace"),
        ("UrbanBites", "hello@urbanbites.local", 28.6320, 77.2290, "Restaurant Chain"),
        ("Makers Hub", "collaborate@makershub.local", 28.6190, 77.2210, "Design & Tech Studio"),
    ]
    biz_ids = {}
    for name, email, lat, lon, cat in businesses:
        cursor.execute("INSERT INTO businesses (name, email, latitude, longitude, category) VALUES (?, ?, ?, ?, ?)",
                       (name, email, lat, lon, cat))
        biz_ids[name] = cursor.lastrowid

    # Seed tasks
    initial_tasks = [
        (
            biz_ids["GreenLeaf Cafe"],
            "Local Business Growth Intern",
            "Grow social reach, manage local community engagement and design posters.",
            12000,
            "₹8k–12k",
            "2026-11-20",
            3.0,
            28.6220,
            77.2180,
            json.dumps(["Digital Marketing", "Canva", "Social Media"]),
            94
        ),
        (
            biz_ids["Nexa Retail"],
            "React Website Sprint",
            "Build responsive mobile-friendly checkout flows in React.",
            15000,
            "₹15k fixed",
            "2026-11-15",
            3.0,
            28.6280,
            77.2240,
            json.dumps(["React", "UI/UX", "JavaScript"]),
            89
        ),
        (
            biz_ids["CampusCart"],
            "Student Data Analyst",
            "Analyze order patterns, customer retention and deliver SQL reporting.",
            14000,
            "₹10k–14k",
            "2026-11-25",
            3.0,
            28.6100,
            77.2030,
            json.dumps(["Python", "SQL", "Data Analytics"]),
            84
        ),
        (
            biz_ids["UrbanBites"],
            "Content & Community Intern",
            "Create reels, manage weekend food promotions and track follower growth.",
            10000,
            "₹7k–10k",
            "2026-11-18",
            3.0,
            28.6320,
            77.2290,
            json.dumps(["Content", "Social", "Copywriting"]),
            81
        ),
        (
            biz_ids["Makers Hub"],
            "Figma Product Design Task",
            "Create modern design system components and wireframe student dashboard.",
            12000,
            "₹12k fixed",
            "2026-11-30",
            3.0,
            28.6190,
            77.2210,
            json.dumps(["Figma", "UI/UX", "Wireframing"]),
            88
        ),
    ]

    task_ids = []
    for t in initial_tasks:
        cursor.execute("""
        INSERT INTO tasks (business_id, title, description, budget, pay, deadline, radius_km, latitude, longitude, skills, match_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, t)
        task_ids.append(cursor.lastrowid)

    # Seed initial applications
    cursor.execute("INSERT INTO applications (task_id, student_id, status, match_score) VALUES (?, ?, 'Interview', 94)", (task_ids[0], student_id))
    cursor.execute("INSERT INTO applications (task_id, student_id, status, match_score) VALUES (?, ?, 'Shortlisted', 89)", (task_ids[1], student_id))
    cursor.execute("INSERT INTO applications (task_id, student_id, status, match_score) VALUES (?, ?, 'Selected', 84)", (task_ids[2], student_id))

    conn.commit()

# ==============================================================================
# QUERIES
# ==============================================================================

def get_jobs(radius_km=3.0, skill=None, student_lat=28.6139, student_lon=77.2090):
    """Query nearby jobs within radius using spatial Haversine SQL function."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT t.id, t.title, t.description, t.budget, t.pay, t.deadline, t.radius_km,
           t.latitude, t.longitude, t.skills, t.match_score, t.status, t.created_at,
           b.name AS business, b.category AS business_category,
           haversine_distance(?, ?, t.latitude, t.longitude) AS distance_km
    FROM tasks t
    JOIN businesses b ON t.business_id = b.id
    WHERE haversine_distance(?, ?, t.latitude, t.longitude) <= ?
    ORDER BY distance_km ASC
    """
    cursor.execute(query, (student_lat, student_lon, student_lat, student_lon, radius_km))
    rows = cursor.fetchall()

    items = []
    for r in rows:
        skills_raw = r["skills"]
        try:
            skills_list = json.loads(skills_raw) if isinstance(skills_raw, str) else skills_raw
        except Exception:
            skills_list = [skills_raw]

        # Skill filtering
        if skill:
            s = skill.lower()
            title_match = s in r["title"].lower()
            biz_match = s in r["business"].lower()
            skills_match = any(s in str(sk).lower() for sk in skills_list)
            if not (title_match or biz_match or skills_match):
                continue

        items.append({
            "id": r["id"],
            "title": r["title"],
            "business": r["business"],
            "business_category": r["business_category"],
            "description": r["description"],
            "pay": r["pay"],
            "budget": r["budget"],
            "deadline": r["deadline"],
            "distance_km": r["distance_km"],
            "match": r["match_score"],
            "skills": skills_list,
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "status": r["status"]
        })

    conn.close()
    return items

def create_task(title, description="", budget=0, deadline=None, radius_km=3.0,
                latitude=28.6150, longitude=77.2120, skills=None, business_name="Local Partner"):
    """Inserts a new business task into the database."""
    if skills is None:
        skills = ["General"]
    elif isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]

    conn = get_connection()
    cursor = conn.cursor()

    # Find or create business
    cursor.execute("SELECT id FROM businesses WHERE name = ?", (business_name,))
    biz = cursor.fetchone()
    if biz:
        biz_id = biz["id"]
    else:
        cursor.execute("INSERT INTO businesses (name, latitude, longitude) VALUES (?, ?, ?)",
                       (business_name, latitude, longitude))
        biz_id = cursor.lastrowid

    pay_display = f"₹{int(budget):,} fixed" if budget else "₹10k–15k"
    skills_json = json.dumps(skills)

    cursor.execute("""
    INSERT INTO tasks (business_id, title, description, budget, pay, deadline, radius_km, latitude, longitude, skills, match_score)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 92)
    """, (biz_id, title, description, budget, pay_display, deadline, radius_km, latitude, longitude, skills_json))

    task_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": task_id,
        "title": title,
        "business": business_name,
        "description": description,
        "budget": budget,
        "pay": pay_display,
        "deadline": deadline,
        "radius_km": radius_km,
        "latitude": latitude,
        "longitude": longitude,
        "skills": skills
    }

def apply_to_task(task_id, student_id=1, match_score=94):
    """Submits or updates an application in the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, status FROM applications WHERE task_id = ? AND student_id = ?",
                   (task_id, student_id))
    existing = cursor.fetchone()

    if existing:
        app_id = existing["id"]
        status = existing["status"]
    else:
        cursor.execute("""
        INSERT INTO applications (task_id, student_id, status, match_score)
        VALUES (?, ?, 'Shortlisted', ?)
        """, (task_id, student_id, match_score))
        app_id = cursor.lastrowid
        status = "Shortlisted"
        conn.commit()

    conn.close()
    return {"id": app_id, "task_id": task_id, "student_id": student_id, "status": status, "match_score": match_score}

def get_applications(student_id=1):
    """Retrieves all applications for a student with job details."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT a.id, a.status, a.match_score, a.applied_at,
           t.id AS task_id, t.title AS task_title, t.pay, t.deadline,
           b.name AS business_name
    FROM applications a
    JOIN tasks t ON a.task_id = t.id
    JOIN businesses b ON t.business_id = b.id
    WHERE a.student_id = ?
    ORDER BY a.applied_at DESC
    """, (student_id,))
    rows = cursor.fetchall()

    apps = []
    for r in rows:
        apps.append({
            "id": r["id"],
            "task_id": r["task_id"],
            "task": r["task_title"],
            "business": r["business_name"],
            "pay": r["pay"],
            "status": r["status"],
            "match_score": r["match_score"],
            "applied_at": r["applied_at"]
        })

    conn.close()
    return apps

def get_student_profile(student_id=1):
    """Fetches student details and portfolio from the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    try:
        skills = json.loads(row["skills"])
    except Exception:
        skills = []

    try:
        portfolio = json.loads(row["portfolio"])
    except Exception:
        portfolio = []

    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "college": row["college"],
        "major": row["major"],
        "year": row["year"],
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "availability_hours": row["availability_hours"],
        "skills": skills,
        "portfolio": portfolio
    }

def get_dashboard_stats(student_id=1):
    """Returns dynamic statistics aggregated from the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'open'")
    total_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications WHERE student_id = ?", (student_id,))
    active_apps = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications WHERE student_id = ? AND status = 'Interview'", (student_id,))
    interviews = cursor.fetchone()[0]

    conn.close()

    return {
        "match_readiness": 86,
        "nearby_opportunities": total_jobs,
        "active_applications": active_apps,
        "interviews": interviews,
        "gaps_closed": 4
    }

# Ensure database is initialized when module is loaded
init_db()
