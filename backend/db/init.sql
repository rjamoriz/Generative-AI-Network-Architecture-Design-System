-- ============================================================================
-- PostgreSQL Initialization Script
-- Network Architecture Design System
-- ============================================================================

-- Create database (if running manually, not in Docker)
-- CREATE DATABASE network_designs;

-- Connect to database
\c network_designs;

-- ============================================================================
-- Extensions
-- ============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable full-text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- Tables
-- ============================================================================

-- Users table (for future authentication)
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API Keys table
CREATE TABLE IF NOT EXISTS api_keys (
    key_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 1000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP
);

-- Design metadata table (for quick queries)
CREATE TABLE IF NOT EXISTS design_metadata (
    design_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    network_type VARCHAR(100),
    topology_type VARCHAR(100),
    status VARCHAR(50),
    validation_score DECIMAL(3,2),
    component_count INTEGER,
    connection_count INTEGER,
    security_level VARCHAR(50),
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validated_at TIMESTAMP
);

-- Validation results table
CREATE TABLE IF NOT EXISTS validation_results (
    validation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    design_id VARCHAR(255) REFERENCES design_metadata(design_id) ON DELETE CASCADE,
    overall_score DECIMAL(3,2),
    passed BOOLEAN,
    critical_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    info_count INTEGER DEFAULT 0,
    validation_mode VARCHAR(50),
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validation_data JSONB
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Indexes
-- ============================================================================

-- Design metadata indexes
CREATE INDEX IF NOT EXISTS idx_design_network_type ON design_metadata(network_type);
CREATE INDEX IF NOT EXISTS idx_design_status ON design_metadata(status);
CREATE INDEX IF NOT EXISTS idx_design_validation_score ON design_metadata(validation_score);
CREATE INDEX IF NOT EXISTS idx_design_created_at ON design_metadata(created_at);
CREATE INDEX IF NOT EXISTS idx_design_created_by ON design_metadata(created_by);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_design_name_trgm ON design_metadata USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_design_description_trgm ON design_metadata USING gin(description gin_trgm_ops);

-- Validation results indexes
CREATE INDEX IF NOT EXISTS idx_validation_design_id ON validation_results(design_id);
CREATE INDEX IF NOT EXISTS idx_validation_score ON validation_results(overall_score);
CREATE INDEX IF NOT EXISTS idx_validation_passed ON validation_results(passed);
CREATE INDEX IF NOT EXISTS idx_validation_created_at ON validation_results(validated_at);

-- Audit log indexes
CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_log(created_at);

-- API keys indexes
CREATE INDEX IF NOT EXISTS idx_apikey_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_apikey_active ON api_keys(is_active);

-- ============================================================================
-- Functions
-- ============================================================================

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================================================
-- Triggers
-- ============================================================================

-- Auto-update updated_at on design_metadata
CREATE TRIGGER update_design_metadata_updated_at
    BEFORE UPDATE ON design_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-update updated_at on users
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Initial Data (Optional)
-- ============================================================================

-- Create default admin user (password: admin123 - CHANGE IN PRODUCTION!)
-- Password hash for 'admin123' using bcrypt
INSERT INTO users (username, email, hashed_password, is_superuser)
VALUES (
    'admin',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aeUkL/dEhbqK',
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- Grants (if needed)
-- ============================================================================

-- Grant permissions to application user
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE users IS 'User accounts for authentication';
COMMENT ON TABLE api_keys IS 'API keys for programmatic access';
COMMENT ON TABLE design_metadata IS 'Network design metadata for quick queries';
COMMENT ON TABLE validation_results IS 'Design validation results';
COMMENT ON TABLE audit_log IS 'Audit trail for all system actions';

-- ============================================================================
-- Completion
-- ============================================================================

SELECT 'Database initialization complete!' AS status;
