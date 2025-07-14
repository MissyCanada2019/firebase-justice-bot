-- PostgreSQL Schema Setup for SmartDispute.ai
-- This script sets up the database schema and inserts sample data

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (in reverse order to avoid foreign key constraints)
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS chat_sessions CASCADE;
DROP TABLE IF EXISTS case_merit_scores CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS disputes CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(50) DEFAULT 'user', -- user or admin
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    settings JSONB DEFAULT '{"notifications": true, "language": "en", "theme": "light", "high_contrast": false, "text_size": "medium"}'::JSONB
);

-- Create Disputes table
CREATE TABLE disputes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    case_type VARCHAR(100) NOT NULL, -- housing, credit, CAS, police, etc.
    status VARCHAR(50) DEFAULT 'draft', -- draft, submitted, closed
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    search_vector TSVECTOR
);

-- Create Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dispute_id UUID REFERENCES disputes(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_url TEXT NOT NULL,
    file_type VARCHAR(50), -- upload, generated_form
    extracted_text TEXT,
    doc_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    search_vector TSVECTOR
);

-- Create Payments table
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    payment_provider VARCHAR(50), -- PayPal, Stripe, etc.
    payment_id VARCHAR(255) UNIQUE, -- Provider's transaction ID
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'CAD',
    status VARCHAR(50) DEFAULT 'pending', -- pending, completed, failed
    payment_type VARCHAR(50), -- document, subscription, mailing
    service_details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create Case Merit Scores table
CREATE TABLE case_merit_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dispute_id UUID UNIQUE REFERENCES disputes(id) ON DELETE CASCADE,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    summary TEXT,
    legal_references TEXT,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create Chat Sessions table
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    dispute_id UUID REFERENCES disputes(id) ON DELETE CASCADE,
    title VARCHAR(200),
    session_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create Chat Messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    is_user BOOLEAN DEFAULT TRUE,
    message TEXT NOT NULL,
    message_data JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX ix_users_email ON users (email);
CREATE INDEX ix_users_role ON users (role);
CREATE INDEX ix_disputes_user_id ON disputes (user_id);
CREATE INDEX ix_disputes_case_type ON disputes (case_type);
CREATE INDEX ix_disputes_status ON disputes (status);
CREATE INDEX ix_documents_dispute_id ON documents (dispute_id);
CREATE INDEX ix_documents_file_type ON documents (file_type);
CREATE INDEX ix_payments_user_id ON payments (user_id);
CREATE INDEX ix_payments_status ON payments (status);
CREATE INDEX ix_case_merit_scores_dispute_id ON case_merit_scores (dispute_id);
CREATE INDEX ix_chat_sessions_user_id ON chat_sessions (user_id);
CREATE INDEX ix_chat_sessions_dispute_id ON chat_sessions (dispute_id);
CREATE INDEX ix_chat_messages_session_id ON chat_messages (session_id);
CREATE INDEX ix_chat_messages_is_user ON chat_messages (is_user);

-- Create indexes for full-text search
CREATE INDEX ix_disputes_search_vector ON disputes USING gin(search_vector);
CREATE INDEX ix_documents_search_vector ON documents USING gin(search_vector);

-- Insert sample users
INSERT INTO users (id, full_name, email, password_hash, role, created_at, last_login)
VALUES 
(gen_random_uuid(), 'Jane Doe', 'jane@example.com', 'scrypt$ln=16,p=1,r=8$QkKDZPmXqBhc9SCsZxJ2iQ$BG8/o3biw5NYtyXc3DpPofK6tXA0chW0SpgxRxAzuVE', 'user', NOW(), NOW()),
(gen_random_uuid(), 'Admin User', 'admin@example.com', 'scrypt$ln=16,p=1,r=8$UWmDy2AKN4F4Xl0G7O7ung$BWw8VWfbkLXaMq3msjUwVYg14j8QeUMXKZxCYeNnT3o', 'admin', NOW(), NOW() - INTERVAL '2 days');

-- Insert sample disputes
INSERT INTO disputes (id, user_id, case_type, status, title, created_at, updated_at)
VALUES 
(gen_random_uuid(), (SELECT id FROM users WHERE email = 'jane@example.com'), 'Housing', 'draft', 'Apartment Ceiling Leak', NOW(), NOW()),
(gen_random_uuid(), (SELECT id FROM users WHERE email = 'jane@example.com'), 'Credit Dispute', 'submitted', 'Wrong Collections Account', NOW(), NOW());

-- Insert sample documents
INSERT INTO documents (id, dispute_id, file_name, file_url, file_type, extracted_text, doc_metadata, created_at)
VALUES 
(
    gen_random_uuid(), 
    (SELECT id FROM disputes WHERE case_type = 'Housing' AND user_id = (SELECT id FROM users WHERE email = 'jane@example.com')), 
    'leak_photos.zip', 
    '/uploads/leak_photos.zip', 
    'upload', 
    'Photos showing water damage from ceiling leak in apartment.',
    '{"page_count": 3, "size_kb": 1250}'::JSONB,
    NOW()
),
(
    gen_random_uuid(), 
    (SELECT id FROM disputes WHERE case_type = 'Credit Dispute' AND user_id = (SELECT id FROM users WHERE email = 'jane@example.com')), 
    'credit_dispute_letter.docx', 
    '/generated/credit_dispute_letter.docx', 
    'generated_form',
    'Formal dispute letter for Equifax regarding incorrect collections account.',
    '{"page_count": 2, "size_kb": 124}'::JSONB,
    NOW()
);

-- Insert a sample payment
INSERT INTO payments (id, user_id, payment_provider, payment_id, amount, currency, status, payment_type, service_details, created_at)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM users WHERE email = 'jane@example.com'),
    'PayPal',
    'PAY-1234567890',
    5.99,
    'CAD',
    'completed',
    'document',
    '{"document_id": "' || (SELECT id FROM documents WHERE file_name = 'credit_dispute_letter.docx')::text || '", "service_type": "document_generation"}'::JSONB,
    NOW()
);

-- Insert a merit score for the Credit Dispute
INSERT INTO case_merit_scores (id, dispute_id, score, summary, legal_references, details, created_at)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM disputes WHERE case_type = 'Credit Dispute' AND user_id = (SELECT id FROM users WHERE email = 'jane@example.com')), 
    85, 
    'Strong case based on violation of FCRA reporting rules.', 
    'Refer to FCRA 609(b) - right to dispute inaccuracies.',
    '{
        "strengths": ["Clear documentation of error", "Multiple attempts to contact creditor", "Statutory protections apply"],
        "weaknesses": ["Delayed response to initial notice"],
        "relevant_cases": ["Smith v. Experian (2020)", "Jones v. TransUnion (2019)"]
    }'::JSONB,
    NOW()
);

-- Insert a chat session and messages
INSERT INTO chat_sessions (id, user_id, dispute_id, title, session_data, created_at)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM users WHERE email = 'jane@example.com'),
    (SELECT id FROM disputes WHERE case_type = 'Housing' AND user_id = (SELECT id FROM users WHERE email = 'jane@example.com')),
    'Housing Dispute Assistance',
    '{"opened_from": "dispute_page", "related_docs": ["' || (SELECT id FROM documents WHERE file_name = 'leak_photos.zip')::text || '"]}'::JSONB,
    NOW()
);

-- Insert chat messages
INSERT INTO chat_messages (id, session_id, is_user, message, message_data, timestamp)
VALUES 
(
    gen_random_uuid(),
    (SELECT id FROM chat_sessions WHERE title = 'Housing Dispute Assistance'),
    TRUE,
    'I have a water leak in my apartment ceiling. What rights do I have?',
    NULL,
    NOW() - INTERVAL '5 minutes'
),
(
    gen_random_uuid(),
    (SELECT id FROM chat_sessions WHERE title = 'Housing Dispute Assistance'),
    FALSE,
    'In Ontario, your landlord is responsible for maintaining your unit in a good state of repair. This includes fixing leaks and water damage. You should notify your landlord in writing about the issue and keep a copy for your records. If the landlord fails to fix the issue within a reasonable time, you can file a T6 maintenance application with the Landlord and Tenant Board.',
    '{"references": ["Residential Tenancies Act, 2006, S.O. 2006, c. 17, s. 20", "Ontario Landlord and Tenant Board Form T6"], "analysis": "Clear case of landlord responsibility for unit maintenance"}'::JSONB,
    NOW() - INTERVAL '4 minutes'
);

-- Update search vectors
UPDATE disputes
SET search_vector = 
    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(case_type, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(status, '')), 'C');

UPDATE documents
SET search_vector = 
    setweight(to_tsvector('english', COALESCE(file_name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(file_type, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(extracted_text, '')), 'C');

-- Create trigger functions for search vector updates
CREATE OR REPLACE FUNCTION disputes_search_vector_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.case_type, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.status, '')), 'C');
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION documents_search_vector_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.file_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.file_type, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.extracted_text, '')), 'C');
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

-- Create triggers for search vector updates
CREATE TRIGGER disputes_search_update
BEFORE INSERT OR UPDATE OF title, case_type, status
ON disputes
FOR EACH ROW
EXECUTE FUNCTION disputes_search_vector_update();

CREATE TRIGGER documents_search_update
BEFORE INSERT OR UPDATE OF file_name, file_type, extracted_text
ON documents
FOR EACH ROW
EXECUTE FUNCTION documents_search_vector_update();

-- Display success message
DO $$
BEGIN
    RAISE NOTICE 'Database setup completed successfully!';
END $$;