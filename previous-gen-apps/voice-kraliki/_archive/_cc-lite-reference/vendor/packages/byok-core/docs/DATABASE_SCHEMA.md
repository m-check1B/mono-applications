# BYOK Database Schema

Complete database schema for the Bring Your Own Keys (BYOK) system.

## Overview

The BYOK system uses a secure, multi-tenant database design with the following key principles:

- **Multi-tenancy**: Complete isolation between users/organizations
- **Encryption**: All sensitive data encrypted at rest
- **Audit Trail**: Complete history of all key operations
- **Flexibility**: Support for various provider types and key formats
- **Performance**: Optimized for fast key retrieval and validation

## Core Tables

### 1. byok_users

Stores user/organization information for BYOK system.

```sql
CREATE TABLE byok_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL, -- External user ID from auth system
    organization_id VARCHAR(255), -- Optional organization grouping
    encryption_key_hash VARCHAR(255) NOT NULL, -- Derived encryption key for this user
    settings JSONB DEFAULT '{}', -- User preferences and settings
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id),
    INDEX(organization_id),
    INDEX(created_at)
);
```

### 2. byok_keys

Main table for storing encrypted API keys.

```sql
CREATE TABLE byok_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES byok_users(id) ON DELETE CASCADE,
    
    -- Provider Information
    provider_type VARCHAR(50) NOT NULL, -- openai, deepgram, twilio, etc.
    provider_service VARCHAR(50), -- specific service within provider
    
    -- Key Identification
    alias VARCHAR(255), -- User-friendly name
    description TEXT,
    environment VARCHAR(20) DEFAULT 'production', -- production, development, staging
    
    -- Encrypted Key Data
    encrypted_key_data TEXT NOT NULL, -- AES-256-GCM encrypted JSON
    encryption_nonce VARCHAR(255) NOT NULL, -- Unique nonce for this key
    key_hash VARCHAR(255) NOT NULL, -- Hash for duplicate detection
    
    -- Key Metadata (non-sensitive)
    metadata JSONB DEFAULT '{}', -- Provider-specific metadata
    capabilities JSONB DEFAULT '[]', -- What this key can do
    
    -- Status & Health
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, invalid, expired
    last_validated_at TIMESTAMP WITH TIME ZONE,
    validation_error TEXT,
    health_score INTEGER DEFAULT 100, -- 0-100 health rating
    
    -- Usage & Limits
    usage_tracking BOOLEAN DEFAULT true,
    rate_limit_config JSONB DEFAULT '{}',
    quota_config JSONB DEFAULT '{}',
    
    -- Timing
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, key_hash), -- Prevent duplicate keys
    INDEX(user_id, provider_type),
    INDEX(provider_type, status),
    INDEX(expires_at),
    INDEX(created_at)
);
```

### 3. byok_key_usage

Tracks API key usage for monitoring and billing.

```sql
CREATE TABLE byok_key_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_id UUID NOT NULL REFERENCES byok_keys(id) ON DELETE CASCADE,
    
    -- Usage Metrics
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    requests_count INTEGER DEFAULT 1,
    tokens_consumed BIGINT DEFAULT 0,
    cost_usd DECIMAL(10,4) DEFAULT 0,
    
    -- Request Details
    operation VARCHAR(100), -- completion, embedding, tts, stt, etc.
    model_used VARCHAR(100),
    success BOOLEAN DEFAULT true,
    error_code VARCHAR(50),
    
    -- Performance Metrics
    response_time_ms INTEGER,
    data_processed_bytes BIGINT,
    
    -- Partitioning by day for performance
    PARTITION BY RANGE (timestamp);
    
    INDEX(key_id, timestamp),
    INDEX(timestamp, success)
);

-- Create monthly partitions
CREATE TABLE byok_key_usage_202501 PARTITION OF byok_key_usage
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE byok_key_usage_202502 PARTITION OF byok_key_usage
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
-- ... continue for other months
```

### 4. byok_key_validations

Stores key validation results and health checks.

```sql
CREATE TABLE byok_key_validations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_id UUID NOT NULL REFERENCES byok_keys(id) ON DELETE CASCADE,
    
    -- Validation Details
    validated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    validation_type VARCHAR(50) NOT NULL, -- manual, automatic, scheduled
    is_valid BOOLEAN NOT NULL,
    
    -- Test Results
    test_results JSONB DEFAULT '{}', -- Detailed test results
    error_message TEXT,
    error_code VARCHAR(50),
    
    -- Performance Metrics
    response_time_ms INTEGER,
    tests_run JSONB DEFAULT '[]', -- List of tests performed
    
    -- Provider-specific data
    provider_response JSONB,
    
    INDEX(key_id, validated_at),
    INDEX(validated_at, is_valid)
);
```

### 5. byok_fallback_chains

Defines fallback sequences for when primary keys fail.

```sql
CREATE TABLE byok_fallback_chains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES byok_users(id) ON DELETE CASCADE,
    
    -- Chain Configuration
    provider_type VARCHAR(50) NOT NULL,
    environment VARCHAR(20) DEFAULT 'production',
    chain_name VARCHAR(255),
    
    -- Fallback Sequence
    primary_key_id UUID REFERENCES byok_keys(id) ON DELETE SET NULL,
    fallback_sequence JSONB NOT NULL, -- Array of key IDs in order
    
    -- System Fallback
    use_system_fallback BOOLEAN DEFAULT true,
    system_fallback_priority INTEGER DEFAULT 999,
    
    -- Configuration
    max_retries INTEGER DEFAULT 3,
    retry_delay_ms INTEGER DEFAULT 1000,
    circuit_breaker_config JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, provider_type, environment),
    INDEX(provider_type)
);
```

### 6. byok_usage_alerts

User-defined usage alerts and notifications.

```sql
CREATE TABLE byok_usage_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES byok_users(id) ON DELETE CASCADE,
    key_id UUID REFERENCES byok_keys(id) ON DELETE CASCADE, -- NULL for all keys
    
    -- Alert Configuration
    alert_name VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) NOT NULL, -- cost, requests, tokens, quota
    threshold_value DECIMAL(12,4) NOT NULL,
    threshold_period VARCHAR(20) NOT NULL, -- daily, weekly, monthly
    
    -- Notification Settings
    notification_channels JSONB DEFAULT '[]', -- email, webhook, in-app
    is_active BOOLEAN DEFAULT true,
    
    -- Tracking
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    trigger_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX(user_id, is_active),
    INDEX(alert_type)
);
```

### 7. byok_audit_log

Complete audit trail for all BYOK operations.

```sql
CREATE TABLE byok_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES byok_users(id) ON DELETE SET NULL,
    key_id UUID REFERENCES byok_keys(id) ON DELETE SET NULL,
    
    -- Event Details
    event_type VARCHAR(50) NOT NULL, -- create, update, delete, validate, use
    event_action VARCHAR(100) NOT NULL, -- specific action taken
    event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    request_id VARCHAR(255),
    
    -- Changes (for update events)
    old_values JSONB,
    new_values JSONB,
    
    -- Metadata
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    additional_data JSONB DEFAULT '{}',
    
    -- Partitioning by month for performance
    PARTITION BY RANGE (event_timestamp);
    
    INDEX(user_id, event_timestamp),
    INDEX(key_id, event_timestamp),
    INDEX(event_type, event_timestamp)
);
```

### 8. byok_provider_configs

Store provider-specific configuration templates and validation rules.

```sql
CREATE TABLE byok_provider_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Provider Information
    provider_type VARCHAR(50) NOT NULL,
    provider_service VARCHAR(50),
    provider_version VARCHAR(20),
    
    -- Configuration Schema
    key_schema JSONB NOT NULL, -- JSON schema for key validation
    metadata_schema JSONB DEFAULT '{}',
    capabilities JSONB DEFAULT '[]',
    
    -- Validation Rules
    validation_config JSONB DEFAULT '{}',
    test_endpoints JSONB DEFAULT '[]',
    rate_limits JSONB DEFAULT '{}',
    
    -- Documentation
    description TEXT,
    setup_instructions TEXT,
    example_config JSONB,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_beta BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(provider_type, provider_service, provider_version),
    INDEX(provider_type, is_active)
);
```

## Indexes and Performance

### Additional Indexes

```sql
-- Performance indexes for common queries
CREATE INDEX idx_byok_keys_user_provider_active 
    ON byok_keys(user_id, provider_type) 
    WHERE status = 'active';

CREATE INDEX idx_byok_keys_expiring_soon 
    ON byok_keys(expires_at) 
    WHERE expires_at IS NOT NULL AND status = 'active';

CREATE INDEX idx_byok_usage_daily_aggregation 
    ON byok_key_usage(key_id, DATE(timestamp), success);

CREATE INDEX idx_byok_audit_log_security 
    ON byok_audit_log(ip_address, event_timestamp) 
    WHERE event_type IN ('create', 'delete', 'validate');
```

## Data Types and Encryption

### Provider Type Enum

```sql
CREATE TYPE provider_type_enum AS ENUM (
    'openai',
    'anthropic', 
    'google_vertex',
    'google_gemini',
    'deepgram',
    'twilio',
    'telnyx',
    'openrouter',
    'huggingface'
);
```

### Status Enum

```sql
CREATE TYPE key_status_enum AS ENUM (
    'active',
    'inactive', 
    'invalid',
    'expired',
    'rate_limited',
    'suspended'
);
```

### Environment Enum

```sql
CREATE TYPE environment_enum AS ENUM (
    'development',
    'staging', 
    'production'
);
```

## Encryption Strategy

### Key Encryption

1. **User Master Key**: Derived from user ID + global secret using PBKDF2
2. **Key-Specific Nonce**: Unique nonce generated for each key
3. **Encryption**: AES-256-GCM with authenticated encryption
4. **Storage**: Only encrypted data and nonce stored in database

```typescript
// Encryption process (conceptual)
const userMasterKey = deriveKey(userId, globalSecret);
const nonce = generateSecureNonce();
const encrypted = aes256gcm.encrypt(keyData, userMasterKey, nonce);

// Store in database
{
  encrypted_key_data: encrypted.data,
  encryption_nonce: encrypted.nonce,
  key_hash: sha256(keyData) // For duplicate detection
}
```

## Sample Provider Configurations

### OpenAI Key Schema

```json
{
  "type": "object",
  "required": ["apiKey"],
  "properties": {
    "apiKey": {
      "type": "string",
      "pattern": "^sk-[a-zA-Z0-9]{48}$"
    },
    "organization": {
      "type": "string",
      "pattern": "^org-[a-zA-Z0-9]{24}$"
    },
    "project": {
      "type": "string", 
      "pattern": "^proj_[a-zA-Z0-9]{24}$"
    }
  }
}
```

### Deepgram Key Schema

```json
{
  "type": "object",
  "required": ["apiKey"],
  "properties": {
    "apiKey": {
      "type": "string",
      "minLength": 40
    },
    "projectId": {
      "type": "string",
      "pattern": "^[a-fA-F0-9-]{36}$"
    }
  }
}
```

### Twilio Key Schema

```json
{
  "type": "object",
  "required": ["accountSid", "authToken"],
  "properties": {
    "accountSid": {
      "type": "string",
      "pattern": "^AC[a-fA-F0-9]{32}$"
    },
    "authToken": {
      "type": "string",
      "minLength": 32
    },
    "apiKeySid": {
      "type": "string",
      "pattern": "^SK[a-fA-F0-9]{32}$"
    }
  }
}
```

## Migration Considerations

### From Environment Variables

1. **Detection**: Scan existing environment variables
2. **Validation**: Test each key before migration
3. **Encryption**: Encrypt and store in BYOK system
4. **Fallback**: Keep environment variables as system fallback
5. **Cleanup**: Optional removal of environment variables

### Zero-Downtime Migration

1. **Gradual Rollout**: Migrate users in batches
2. **Dual Reading**: Read from both systems during transition
3. **Validation**: Continuous validation during migration
4. **Rollback**: Ability to rollback to environment variables

## Backup and Recovery

### Encryption Key Management

- Store encryption keys separately from database
- Use key management service (AWS KMS, Azure Key Vault)
- Regular key rotation with backward compatibility
- Secure backup of master keys

### Database Backup

- Regular encrypted backups
- Point-in-time recovery capability
- Cross-region replication for disaster recovery
- Automated backup validation

## Compliance and Security

### Data Protection

- GDPR compliant with right to deletion
- SOC 2 Type II compatible logging
- Encrypted at rest and in transit
- Zero-knowledge architecture

### Audit Requirements

- Complete audit trail for all operations
- Immutable log entries
- Regular security audits
- Compliance reporting capabilities

## Performance Optimization

### Caching Strategy

```sql
-- Redis cache keys
byok:user:{user_id}:keys:{provider_type}
byok:key:{key_id}:decrypted (TTL: 5 minutes)
byok:validation:{key_id}:status (TTL: 1 hour)
byok:usage:{key_id}:daily:{date}
```

### Query Optimization

- Partitioned tables for high-volume data
- Proper indexing for common access patterns
- Connection pooling for database connections
- Read replicas for analytics queries

## Monitoring Queries

### Key Health Dashboard

```sql
-- Active keys per provider
SELECT provider_type, COUNT(*) as active_keys
FROM byok_keys 
WHERE status = 'active' 
GROUP BY provider_type;

-- Keys expiring in next 7 days
SELECT user_id, provider_type, alias, expires_at
FROM byok_keys
WHERE expires_at BETWEEN NOW() AND NOW() + INTERVAL '7 days'
  AND status = 'active';

-- Failed validations in last 24 hours
SELECT key_id, COUNT(*) as failures
FROM byok_key_validations
WHERE validated_at > NOW() - INTERVAL '24 hours'
  AND is_valid = false
GROUP BY key_id
HAVING COUNT(*) > 3;
```

### Usage Analytics

```sql
-- Daily usage by provider
SELECT 
    DATE(timestamp) as date,
    provider_type,
    SUM(requests_count) as total_requests,
    SUM(cost_usd) as total_cost
FROM byok_key_usage u
JOIN byok_keys k ON u.key_id = k.id
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY DATE(timestamp), provider_type
ORDER BY date DESC;

-- Top consuming users
SELECT 
    u.user_id,
    COUNT(DISTINCT k.id) as key_count,
    SUM(usage.requests_count) as total_requests,
    SUM(usage.cost_usd) as total_cost
FROM byok_users u
JOIN byok_keys k ON u.id = k.user_id
JOIN byok_key_usage usage ON k.id = usage.key_id
WHERE usage.timestamp > NOW() - INTERVAL '7 days'
GROUP BY u.user_id
ORDER BY total_cost DESC
LIMIT 10;
```