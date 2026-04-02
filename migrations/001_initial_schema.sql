-- Migration: 001_initial_schema
-- Date: 2026-03-27
-- Description: Initial schema for Constellation25 Agent Registry

CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    designation VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES agents(id),
    description TEXT,
    completed BOOLEAN DEFAULT FALSE
);
