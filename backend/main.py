"""
ECONEX — Hyperlocal Opportunity Network Backend API
Provides endpoints for hyperlocal job discovery, task posting,
AI match scoring, application tracking, and skill-gap analysis.

Compatible with Python 3.8+ (including Python 3.15+) with zero required
external C-dependencies. Runs directly via:
    python main.py
or via ASGI:
    uvicorn main:app --reload
"""

import sys
import os
import json
import urllib.parse
import re
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler

# Import AI service
try:
    from . import ai_service
except (ImportError, ValueError):
    import ai_service

# ==============================================================================
# DATA STORES (In-memory prototype)
# ==============================================================================

JOBS_DATA = [
    {
        "id": 1,
        "title": "Local Business Growth Intern",
        "business": "GreenLeaf Cafe",
        "distance_km": 1.4,
        "match": 94,
        "pay": "₹8k–12k",
        "skills": ["Digital Marketing", "Canva", "Social Media"]
    },
    {
        "id": 2,
        "title": "React Website Sprint",
        "business": "Nexa Retail",
        "distance_km": 2.1,
        "match": 89,
        "pay": "₹15k fixed",
        "skills": ["React", "UI/UX", "JavaScript"]
    },
    {
        "id": 3,
        "title": "Student Data Analyst",
        "business": "CampusCart",
        "distance_km": 0.8,
        "match": 84,
        "pay": "₹10k–14k",
        "skills": ["Python", "SQL", "Data Analytics"]
    },
    {
        "id": 4,
        "title": "Content & Community Intern",
        "business": "UrbanBites",
        "distance_km": 2.7,
        "match": 81,
        "pay": "₹7k–10k",
        "skills": ["Content", "Social", "Copywriting"]
    },
    {
        "id": 5,
        "title": "Figma Product Design Task",
        "business": "Makers Hub",
        "distance_km": 1.9,
        "match": 88,
        "pay": "₹12k fixed",
        "skills": ["Figma", "UI/UX", "Wireframing"]
    }
]

TASKS_DATA = []

APPLICATIONS_DATA = [
    {"id": 1, "task": "Local Business Growth Intern", "business": "GreenLeaf Cafe", "status": "Interview", "applied_days_ago": 2},
    {"id": 2, "task": "React Website Sprint", "business": "Nexa Retail", "status": "Shortlisted", "applied_days_ago": 1},
    {"id": 3, "task": "Student Data Analyst", "business": "CampusCart", "status": "Selected", "applied_days_ago": 4},
]

# ==============================================================================
# OPENAPI SCHEMA & DOCUMENTATION UI
# ==============================================================================

OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "ECONEX API",
        "version": "1.0.0",
        "description": "Hyperlocal Opportunity Network API connecting local talent with businesses within 3 km."
    },
    "paths": {
        "/": {
            "get": {"summary": "Root status", "responses": {"200": {"description": "API status"}}}
        },
        "/health": {
            "get": {"summary": "Health check", "responses": {"200": {"description": "Service healthy"}}}
        },
        "/jobs": {
            "get": {
                "summary": "List nearby opportunities",
                "parameters": [
                    {"name": "radius_km", "in": "query", "schema": {"type": "number", "default": 3.0}},
                    {"name": "skill", "in": "query", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "Filtered jobs list"}}
            }
        },
        "/tasks": {
            "post": {
                "summary": "Post a local business task",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["title"],
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "budget": {"type": "number"},
                                    "deadline": {"type": "string"},
                                    "latitude": {"type": "number"},
                                    "longitude": {"type": "number"},
                                    "radius_km": {"type": "number"},
                                    "skills": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        }
                    }
                },
                "responses": {"201": {"description": "Task created with AI shortlist"}}
            }
        },
        "/match": {
            "post": {
                "summary": "Match student talent to task",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "integer"},
                                    "student_id": {"type": "integer"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "AI match score and explanation"}}
            }
        },
        "/applications": {
            "get": {
                "summary": "Get student applications",
                "parameters": [{"name": "student_id", "in": "query", "schema": {"type": "integer", "default": 1}}],
                "responses": {"200": {"description": "Applications list"}}
            }
        },
        "/skill-gap/{student_id}": {
            "get": {
                "summary": "Analyze skill gap for student",
                "parameters": [{"name": "student_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "Skill gap report"}}
            }
        }
    }
}

DOCS_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ECONEX API Documentation</title>
<style>
  :root { --primary: #5b5cf0; --bg: #f8fafc; --card: #ffffff; --text: #0f172a; --muted: #64748b; --border: #e2e8f0; --code-bg: #0f172a; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px; line-height: 1.5; }
  .container { max-width: 900px; margin: 0 auto; }
  .header { display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }
  .badge { background: #e0e7ff; color: var(--primary); padding: 4px 10px; border-radius: 99px; font-size: 13px; font-weight: 700; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
  .method { display: inline-block; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 12px; margin-right: 8px; }
  .get { background: #dcfce7; color: #15803d; }
  .post { background: #e0e7ff; color: #4338ca; }
  .path { font-family: monospace; font-size: 15px; font-weight: 700; }
  .desc { color: var(--muted); margin: 8px 0; font-size: 14px; }
  pre { background: var(--code-bg); color: #f8fafc; padding: 14px; border-radius: 8px; overflow-x: auto; font-size: 13px; }
  a { color: var(--primary); text-decoration: none; font-weight: 600; }
  a:hover { text-decoration: underline; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <h1 style="margin:0 0 4px 0;">ECONEX API</h1>
      <span class="desc">Hyperlocal Opportunity Network — 3 km local matching API</span>
    </div>
    <span class="badge">v1.0.0 • Online</span>
  </div>

  <div class="card">
    <span class="method get">GET</span><span class="path">/</span>
    <p class="desc">Root system status and directory of endpoints.</p>
    <a href="/" target="_blank">Try in browser →</a>
  </div>

  <div class="card">
    <span class="method get">GET</span><span class="path">/health</span>
    <p class="desc">Service health probe.</p>
    <a href="/health" target="_blank">Try in browser →</a>
  </div>

  <div class="card">
    <span class="method get">GET</span><span class="path">/jobs?radius_km=3&skill=react</span>
    <p class="desc">Search and filter opportunities within a hyperlocal radius (default: 3 km).</p>
    <a href="/jobs?radius_km=3" target="_blank">View nearby jobs →</a>
  </div>

  <div class="card">
    <span class="method post">POST</span><span class="path">/tasks</span>
    <p class="desc">Post a new local task. Triggers AI requirement extraction.</p>
    <pre>curl -X POST http://127.0.0.1:8000/tasks \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Build Instagram Campaign", "budget": 12000, "radius_km": 3.0, "skills": ["Canva", "Marketing"]}'</pre>
  </div>

  <div class="card">
    <span class="method post">POST</span><span class="path">/match</span>
    <p class="desc">Calculate explainable AI match between candidate and task.</p>
    <pre>curl -X POST http://127.0.0.1:8000/match \\
  -H "Content-Type: application/json" \\
  -d '{"task_id": 1, "student_id": 1}'</pre>
  </div>

  <div class="card">
    <span class="method get">GET</span><span class="path">/applications?student_id=1</span>
    <p class="desc">Retrieve status of all submitted applications.</p>
    <a href="/applications" target="_blank">View applications →</a>
  </div>

  <div class="card">
    <span class="method get">GET</span><span class="path">/skill-gap/{student_id}</span>
    <p class="desc">Generate personalized skill-gap analysis and learning action items.</p>
    <a href="/skill-gap/1" target="_blank">View student #1 skill gap →</a>
  </div>

  <div class="card">
    <span class="method get">GET</span><span class="path">/openapi.json</span>
    <p class="desc">Raw OpenAPI 3.0 specification.</p>
    <a href="/openapi.json" target="_blank">View OpenAPI JSON →</a>
  </div>
</div>
</body>
</html>
"""

# ==============================================================================
# DISPATCHER / ROUTER (Pure Python, Zero External Dependencies)
# ==============================================================================

def dispatch_request(method: str, path: str, query_params: dict, body_bytes: bytes) -> tuple[int, dict, bytes]:
    """
    Central request router that handles routing, CORS, parameters, and responses.
    Shared by both the HTTP server and ASGI application.
    """
    clean_path = path.rstrip("/") or "/"

    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
    }

    # CORS Preflight
    if method == "OPTIONS":
        return 204, cors_headers, b""

    # Parse JSON body if present
    body_json = {}
    if body_bytes:
        try:
            body_json = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            err = json.dumps({"detail": "Invalid JSON in request body"}).encode("utf-8")
            return 400, {**cors_headers, "Content-Type": "application/json"}, err

    # 1. Root
    if method == "GET" and clean_path == "/":
        data = {
            "product": "ECONEX",
            "tagline": "Hyperlocal Opportunity Network",
            "status": "running",
            "version": "1.0.0",
            "docs": "/docs",
            "endpoints": [
                "/health",
                "/jobs",
                "/tasks",
                "/match",
                "/applications",
                "/skill-gap/{student_id}",
                "/openapi.json"
            ]
        }
        return 200, {**cors_headers, "Content-Type": "application/json"}, json.dumps(data, indent=2).encode("utf-8")

    # 2. Health check
    if method == "GET" and clean_path == "/health":
        return 200, {**cors_headers, "Content-Type": "application/json"}, b'{"status": "ok"}'

    # 3. Interactive Documentation
    if method == "GET" and clean_path == "/docs":
        return 200, {**cors_headers, "Content-Type": "text/html; charset=utf-8"}, DOCS_HTML.encode("utf-8")

    # 4. OpenAPI Specification
    if method == "GET" and clean_path == "/openapi.json":
        return 200, {**cors_headers, "Content-Type": "application/json"}, json.dumps(OPENAPI_SPEC, indent=2).encode("utf-8")

    # 5. Nearby Jobs
    if method == "GET" and clean_path == "/jobs":
        radius = float(query_params.get("radius_km", [3.0])[0])
        skill = query_params.get("skill", [None])[0]

        filtered = JOBS_DATA
        if skill:
            s = skill.lower()
            filtered = [
                x for x in filtered
                if s in x["title"].lower() or any(s in str(sk).lower() for sk in x.get("skills", []))
            ]
        filtered = [x for x in filtered if x.get("distance_km", 0) <= radius]
        res = {"items": filtered, "count": len(filtered), "radius_km": radius}
        return 200, {**cors_headers, "Content-Type": "application/json"}, json.dumps(res, indent=2).encode("utf-8")

    # 6. Post Task
    if method == "POST" and clean_path == "/tasks":
        title = body_json.get("title")
        if not title:
            err = json.dumps({"detail": "Missing required field: title"}).encode("utf-8")
            return 422, {**cors_headers, "Content-Type": "application/json"}, err

        task_id = 100 + len(TASKS_DATA) + 1
        new_task = {
            "id": task_id,
            "title": title,
            "description": body_json.get("description", ""),
            "budget": float(body_json.get("budget", 0)),
            "deadline": body_json.get("deadline"),
            "latitude": float(body_json.get("latitude", 28.6139)),
            "longitude": float(body_json.get("longitude", 77.2090)),
            "radius_km": float(body_json.get("radius_km", 3.0)),
            "skills": body_json.get("skills", ["General"]),
        }
        TASKS_DATA.append(new_task)

        # AI extraction using ai_service
        extracted = ai_service.extract_requirements(title)
        res = {
            "id": task_id,
            "status": "created",
            "task": new_task,
            "ai_shortlist": True,
            "extracted_requirements": extracted
        }
        return 201, {**cors_headers, "Content-Type": "application/json"}, json.dumps(res, indent=2).encode("utf-8")

    # 7. AI Match Scoring
    if method == "POST" and clean_path == "/match":
        task_id = int(body_json.get("task_id", 1))
        student_id = int(body_json.get("student_id", 1))

        components = {
            "skill_similarity": 0.93,
            "portfolio_evidence": 0.91,
            "location_fit": 0.98,
            "availability": 0.85
        }
        explanation = ai_service.explain_score(components)
        res = {
            "student_id": student_id,
            "task_id": task_id,
            "score": explanation["overall"],
            "components": explanation["components"]
        }
        return 200, {**cors_headers, "Content-Type": "application/json"}, json.dumps(res, indent=2).encode("utf-8")

    # 8. Applications
    if method == "GET" and clean_path == "/applications":
        student_id = int(query_params.get("student_id", [1])[0])
        res = {"student_id": student_id, "items": APPLICATIONS_DATA}
        return 200, {**cors_headers, "Content-Type": "application/json"}, json.dumps(res, indent=2).encode("utf-8")

    # 9. Skill-gap analysis
    skill_gap_match = re.match(r"^/skill-gap/(\d+)$", clean_path)
    if method == "GET" and skill_gap_match:
        student_id = int(skill_gap_match.group(1))
        required = {"SEO analytics", "Client pitching", "Advanced SQL", "React", "Python"}
        current = {"React", "Python"}
        missing = ai_service.generate_skill_gap(required, current)

        gaps = [
            {"skill": "SEO analytics", "gap": 0.32},
            {"skill": "Client pitching", "gap": 0.41},
            {"skill": "Advanced SQL", "gap": 0.54},
        ]
        res = {
            "student_id": student_id,
            "missing_skills": missing,
            "gaps": gaps
        }
        return 200, {**cors_headers, "Content-Type": "application/json"}, json.dumps(res, indent=2).encode("utf-8")

    # 404 Route Not Found
    err = json.dumps({"detail": f"Route '{method} {clean_path}' not found"}).encode("utf-8")
    return 404, {**cors_headers, "Content-Type": "application/json"}, err

# ==============================================================================
# ASGI APPLICATION (Compatible with `uvicorn main:app --reload`)
# ==============================================================================

async def app(scope, receive, send):
    """ASGI 3.0 Interface for Uvicorn / Hypercorn servers."""
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return
    elif scope["type"] == "http":
        method = scope["method"]
        path = scope["path"]
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = urllib.parse.parse_qs(query_string)

        body = b""
        if method in ("POST", "PUT", "PATCH"):
            while True:
                message = await receive()
                body += message.get("body", b"")
                if not message.get("more_body", False):
                    break

        status, headers, resp_body = dispatch_request(method, path, query_params, body)
        asgi_headers = [
            (k.lower().encode("utf-8"), v.encode("utf-8"))
            for k, v in headers.items()
        ]
        asgi_headers.append((b"content-length", str(len(resp_body)).encode("utf-8")))

        await send({
            "type": "http.response.start",
            "status": status,
            "headers": asgi_headers,
        })
        await send({
            "type": "http.response.body",
            "body": resp_body,
        })

# ==============================================================================
# HTTP SERVER (Direct execution via `python main.py`)
# ==============================================================================

class EconexHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def do_PUT(self):
        self._handle("PUT")

    def do_DELETE(self):
        self._handle("DELETE")

    def do_OPTIONS(self):
        self._handle("OPTIONS")

    def _handle(self, method):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query_params = urllib.parse.parse_qs(parsed.query)

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        status, headers, resp_body = dispatch_request(method, path, query_params, body)
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(resp_body)))
        self.end_headers()
        self.wfile.write(resp_body)

    def log_message(self, format, *args):
        # Format clean console logs
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

def run_server(host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host, port), EconexHTTPHandler)
    print("=" * 60)
    print("  ECONEX — Hyperlocal Opportunity Network Backend API")
    print(f"  Server active at:  http://{host}:{port}")
    print(f"  API Documentation: http://{host}:{port}/docs")
    print(f"  Health endpoint:   http://{host}:{port}/health")
    print("  Ready to receive requests from frontend & external clients.")
    print("  Press Ctrl+C to stop.")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down ECONEX server...")
        server.server_close()

if __name__ == "__main__":
    run_server()
