-- Campaign Automation Schema Additions
-- This migration adds complete campaign automation support

-- Campaign Lead table
CREATE TABLE IF NOT EXISTS campaign_leads (
    id VARCHAR(255) PRIMARY KEY,
    campaign_id VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    timezone VARCHAR(50),
    custom_fields JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    last_attempt_at TIMESTAMP,
    attempts INT DEFAULT 0,
    max_attempts INT DEFAULT 3,
    scheduled_for TIMESTAMP,
    completed_at TIMESTAMP,
    outcome VARCHAR(50),
    notes TEXT,
    dnc_checked BOOLEAN DEFAULT false,
    priority INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

-- Campaign Execution table
CREATE TABLE IF NOT EXISTS campaign_executions (
    id VARCHAR(255) PRIMARY KEY,
    campaign_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    total_leads INT DEFAULT 0,
    processed_leads INT DEFAULT 0,
    successful_calls INT DEFAULT 0,
    failed_calls INT DEFAULT 0,
    configuration JSONB,
    error_log JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

-- Do Not Call (DNC) list
CREATE TABLE IF NOT EXISTS dnc_list (
    id VARCHAR(255) PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    reason VARCHAR(255),
    added_by VARCHAR(255),
    added_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    organization_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Call Pacing Configuration
CREATE TABLE IF NOT EXISTS campaign_pacing (
    id VARCHAR(255) PRIMARY KEY,
    campaign_id VARCHAR(255) UNIQUE NOT NULL,
    calls_per_minute INT DEFAULT 10,
    max_concurrent_calls INT DEFAULT 5,
    call_interval_seconds INT DEFAULT 6,
    retry_delay_minutes INT DEFAULT 30,
    operating_hours JSONB,
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    respect_timezone BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_campaign_leads_campaign_status ON campaign_leads(campaign_id, status);
CREATE INDEX idx_campaign_leads_phone ON campaign_leads(phone_number);
CREATE INDEX idx_campaign_leads_scheduled ON campaign_leads(scheduled_for);
CREATE INDEX idx_campaign_executions_campaign ON campaign_executions(campaign_id);
CREATE INDEX idx_dnc_list_phone ON dnc_list(phone_number);
CREATE INDEX idx_campaign_pacing_campaign ON campaign_pacing(campaign_id);