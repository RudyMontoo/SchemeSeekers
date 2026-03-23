-- V1 Migration
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(30) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    state VARCHAR(255),
    language VARCHAR(10),
    phone_number VARCHAR(15),
    age INTEGER,
    category VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    last_login_at TIMESTAMP
);
CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_users_email ON users (email);

CREATE TABLE user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL REFERENCES users(id),
    district VARCHAR(100),
    annual_income_inr BIGINT,
    occupation VARCHAR(30),
    family_size INTEGER,
    has_bpl_card BOOLEAN,
    has_ration_card BOOLEAN,
    has_aadhaar BOOLEAN,
    has_bank_account BOOLEAN,
    has_disability BOOLEAN,
    disability_percentage INTEGER,
    is_farmer BOOLEAN,
    land_owned_acres DOUBLE PRECISION,
    gender VARCHAR(10),
    updated_at TIMESTAMP
);

CREATE TABLE schemes (
    id BIGSERIAL PRIMARY KEY,
    scheme_key VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    sector VARCHAR(50),
    description TEXT,
    eligibility TEXT,
    benefit VARCHAR(500),
    apply_url VARCHAR(300),
    helpline VARCHAR(20),
    min_age INTEGER,
    max_age INTEGER,
    target_gender VARCHAR(10),
    target_category VARCHAR(20),
    max_annual_income_inr BIGINT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX idx_schemes_key ON schemes (scheme_key);
CREATE INDEX idx_schemes_sector ON schemes (sector);

CREATE TABLE user_scheme_interactions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    scheme_id BIGINT NOT NULL REFERENCES schemes(id),
    interaction_type VARCHAR(20) NOT NULL,
    application_id VARCHAR(100),
    application_status VARCHAR(100),
    timestamp TIMESTAMP
);
CREATE INDEX idx_usi_user ON user_scheme_interactions (user_id);
CREATE INDEX idx_usi_scheme ON user_scheme_interactions (scheme_id);
CREATE INDEX idx_usi_type ON user_scheme_interactions (interaction_type);

CREATE TABLE chat_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id BIGINT REFERENCES users(id),
    language VARCHAR(10),
    state VARCHAR(50),
    session_type VARCHAR(20),
    started_at TIMESTAMP,
    last_activity_at TIMESTAMP
);
CREATE INDEX idx_chat_sessions_sid ON chat_sessions (session_id);
CREATE INDEX idx_chat_sessions_user ON chat_sessions (user_id);

CREATE TABLE chat_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES chat_sessions(id),
    role VARCHAR(15) NOT NULL,
    content TEXT NOT NULL,
    schemesmentioned TEXT,
    timestamp TIMESTAMP NOT NULL
);
CREATE INDEX idx_chat_messages_session ON chat_messages (session_id);
CREATE INDEX idx_chat_messages_ts ON chat_messages (timestamp);

CREATE TABLE status_check_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    scheme_key VARCHAR(50) NOT NULL,
    masked_identifier VARCHAR(50),
    result_stage VARCHAR(200),
    response_time_ms BIGINT,
    cached BOOLEAN DEFAULT FALSE,
    state_code VARCHAR(10),
    checked_at TIMESTAMP
);
CREATE INDEX idx_scl_user ON status_check_logs (user_id);
CREATE INDEX idx_scl_scheme ON status_check_logs (scheme_key);
CREATE INDEX idx_scl_ts ON status_check_logs (checked_at);

CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(30),
    resource_id VARCHAR(100),
    ip_address VARCHAR(20),
    details TEXT,
    timestamp TIMESTAMP NOT NULL
);
CREATE INDEX idx_audit_user ON audit_log (user_id);
CREATE INDEX idx_audit_action ON audit_log (action);
CREATE INDEX idx_audit_ts ON audit_log (timestamp);
