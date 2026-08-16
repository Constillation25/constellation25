CREATE TABLE IF NOT EXISTS ai_skills_registry (
    id SERIAL PRIMARY KEY,
    skill_name VARCHAR(255) NOT NULL,
    repo_url VARCHAR(500) UNIQUE,
    author VARCHAR(255),
    stars INT DEFAULT 0,
    quality_tier VARCHAR(50),
    platforms JSONB,
    description TEXT,
    mcp_compatible BOOLEAN DEFAULT FALSE,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_skills_name ON ai_skills_registry(skill_name);
CREATE INDEX IF NOT EXISTS idx_skills_platforms ON ai_skills_registry USING GIN (platforms);
