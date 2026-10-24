"""
ECONEX AI matching service.
Replace the placeholder embedding/LLM functions with your provider of choice.
"""

def extract_requirements(task_text: str) -> dict:
    # Production: call an LLM and return normalized skills/constraints.
    return {
        "skills": ["react", "ui/ux"],
        "budget": None,
        "deadline": None,
        "location_required": True,
    }

def calculate_match(skill_similarity: float,
                    evidence: float,
                    location_fit: float,
                    availability: float) -> float:
    weights = {
        "skills": 0.40,
        "evidence": 0.25,
        "location": 0.20,
        "availability": 0.15,
    }
    return round(
        skill_similarity * weights["skills"] +
        evidence * weights["evidence"] +
        location_fit * weights["location"] +
        availability * weights["availability"], 4
    )

def generate_skill_gap(required: set[str], current: set[str]) -> list[str]:
    return sorted(required - current)

def explain_score(scores: dict) -> dict:
    evidence = scores.get("evidence", scores.get("portfolio_evidence", 0.0))
    skill_sim = scores.get("skill_similarity", 0.0)
    loc_fit = scores.get("location_fit", 0.0)
    avail = scores.get("availability", 0.0)
    total = calculate_match(
        skill_sim,
        evidence,
        loc_fit,
        avail,
    )
    return {"overall": total, "components": scores}
