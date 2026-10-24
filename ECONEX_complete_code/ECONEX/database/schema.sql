CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS students (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    location GEOGRAPHY(POINT, 4326),
    availability_hours INTEGER DEFAULT 10,
    profile_embedding VECTOR
);

CREATE TABLE IF NOT EXISTS businesses (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    location GEOGRAPHY(POINT, 4326)
);

CREATE TABLE IF NOT EXISTS tasks (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT REFERENCES businesses(id),
    title TEXT NOT NULL,
    description TEXT,
    budget NUMERIC,
    deadline DATE,
    radius_km NUMERIC DEFAULT 3,
    location GEOGRAPHY(POINT, 4326),
    skills JSONB DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS applications (
    id BIGSERIAL PRIMARY KEY,
    task_id BIGINT REFERENCES tasks(id),
    student_id BIGINT REFERENCES students(id),
    status TEXT DEFAULT 'applied',
    match_score NUMERIC,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Example 3 km hyperlocal query:
-- SELECT *
-- FROM tasks
-- WHERE ST_DWithin(
--   location,
--   ST_SetSRID(ST_MakePoint(:lng,:lat),4326)::geography,
--   3000
-- );
