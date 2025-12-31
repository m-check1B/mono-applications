-- Create database if it doesn't exist (run as superuser)
-- CREATE DATABASE operator_demo;

-- Connect to operator_demo database
\c operator_demo;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    organization VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider_type VARCHAR(50) NOT NULL,
    provider_model VARCHAR(100),
    telephony_provider VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE
);

-- Create provider_settings table
CREATE TABLE IF NOT EXISTS provider_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider_type VARCHAR(50) NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, provider_type)
);

-- Create telephony_calls table
CREATE TABLE IF NOT EXISTS telephony_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    call_sid VARCHAR(255) UNIQUE,
    provider VARCHAR(50) NOT NULL,
    from_number VARCHAR(50),
    to_number VARCHAR(50),
    direction VARCHAR(20),
    status VARCHAR(50),
    duration INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE
);

-- Create companies table
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    description TEXT,
    industry VARCHAR(100),
    size VARCHAR(50),
    phone_number VARCHAR(32),
    email VARCHAR(255),
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    website TEXT,
    logo_url TEXT,
    settings JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    user_count INTEGER DEFAULT 0,
    call_count INTEGER DEFAULT 0,
    script_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create call_dispositions table
CREATE TABLE IF NOT EXISTS call_dispositions (
    id SERIAL PRIMARY KEY,
    call_id TEXT NOT NULL,
    disposition_type TEXT NOT NULL,
    notes TEXT,
    agent_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    script_id INTEGER,
    customer_satisfaction INTEGER,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    follow_up_notes TEXT,
    sale_amount NUMERIC,
    sale_currency VARCHAR(3) DEFAULT 'USD',
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create refresh_tokens table for JWT refresh tokens
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_telephony_calls_session_id ON telephony_calls(session_id);
CREATE INDEX IF NOT EXISTS idx_telephony_calls_call_sid ON telephony_calls(call_sid);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_companies_active ON companies(is_active);
CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry);
CREATE INDEX IF NOT EXISTS idx_companies_size ON companies(size);
CREATE INDEX IF NOT EXISTS idx_call_dispositions_company_id ON call_dispositions(company_id);
CREATE INDEX IF NOT EXISTS idx_call_dispositions_call_id ON call_dispositions(call_id);
CREATE INDEX IF NOT EXISTS idx_call_dispositions_follow_up ON call_dispositions(follow_up_required, follow_up_date);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE
    ON users FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE
    ON sessions FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_provider_settings_updated_at BEFORE UPDATE
    ON provider_settings FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE
    ON companies FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_call_dispositions_updated_at BEFORE UPDATE
    ON call_dispositions FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Create a default test user (optional - remove in production)
-- Password is 'test123' hashed with bcrypt
INSERT INTO users (email, password_hash, full_name, organization, role, is_active)
VALUES ('test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY3/iD5mQMwGY8u', 'Test User', NULL, 'user', TRUE)
ON CONFLICT (email) DO NOTHING;

-- Grant permissions (adjust as needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO postgres;

-- Show created tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
