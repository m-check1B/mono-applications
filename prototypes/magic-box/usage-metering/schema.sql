-- Magic Box Usage Metering Database Schema
-- Stores usage metrics for billing and monitoring

-- Tables are ordered by dependencies

-- Customers who have Magic Box VMs
CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    vm_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    billing_plan TEXT DEFAULT 'basic'  -- basic, pro, enterprise
);

-- AI API providers and their pricing
CREATE TABLE IF NOT EXISTS ai_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,  -- claude, openai, gemini
    model TEXT,
    input_token_price REAL DEFAULT 0.0,  -- price per 1M tokens
    output_token_price REAL DEFAULT 0.0,
    per_call_price REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API usage tracking
CREATE TABLE IF NOT EXISTS api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    provider_id INTEGER NOT NULL,
    model TEXT,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    estimated_cost REAL DEFAULT 0.0,
    endpoint TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (provider_id) REFERENCES ai_providers(id)
);

-- System resource snapshots (collected every 5 minutes)
CREATE TABLE IF NOT EXISTS resource_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    cpu_percent REAL NOT NULL,
    memory_percent REAL NOT NULL,
    memory_used_mb REAL NOT NULL,
    memory_total_mb REAL NOT NULL,
    disk_used_gb REAL NOT NULL,
    disk_total_gb REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Command usage tracking
CREATE TABLE IF NOT EXISTS command_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    command TEXT NOT NULL,
    args TEXT,
    exit_code INTEGER,
    duration_seconds REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Pattern usage (which prompt patterns were used)
CREATE TABLE IF NOT EXISTS pattern_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    pattern_name TEXT NOT NULL,
    ai_provider TEXT NOT NULL,  -- claude, gemini, codex
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Billing reports (generated monthly)
CREATE TABLE IF NOT EXISTS billing_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    report_month TEXT NOT NULL,  -- YYYY-MM
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_api_cost REAL DEFAULT 0.0,
    total_compute_hours REAL DEFAULT 0.0,
    total_commands INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',  -- pending, generated, sent, paid
    report_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    UNIQUE(customer_id, report_month)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_api_usage_customer_time ON api_usage(customer_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_api_usage_provider_time ON api_usage(provider_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_resource_usage_time ON resource_usage(timestamp);
CREATE INDEX IF NOT EXISTS idx_command_usage_time ON command_usage(timestamp);
CREATE INDEX IF NOT EXISTS idx_pattern_usage_time ON pattern_usage(timestamp);

-- Default AI providers (will be populated by service)
INSERT OR IGNORE INTO ai_providers (name, model, input_token_price, output_token_price) VALUES
('claude', 'claude-3-5-sonnet', 3.0, 15.0),
('claude', 'claude-3-opus', 15.0, 75.0),
('openai', 'gpt-4', 30.0, 60.0),
('openai', 'gpt-4-turbo', 10.0, 30.0),
('gemini', 'gemini-1.5-pro', 1.25, 5.0),
('gemini', 'gemini-1.5-flash', 0.075, 0.3);
