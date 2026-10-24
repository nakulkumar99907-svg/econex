def calculate_match(student_skills, job_skills):
    if not job_skills:
        return 0

    student_skills = {s.lower() for s in student_skills}
    job_skills = {s.lower() for s in job_skills}

    matched = student_skills.intersection(job_skills)

    return round((len(matched) / len(job_skills)) * 100)


def get_skill_gap(student_skills, job_skills):
    student_skills = {s.lower() for s in student_skills}
    return [skill for skill in job_skills if skill.lower() not in student_skills]
