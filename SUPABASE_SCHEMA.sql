-- ============================================================================
-- ASKLYTICS: Supabase PostgreSQL Schema with RLS (Row-Level Security)
-- ============================================================================
-- Run this entire script in Supabase SQL Editor to create all tables

-- 1. Profiles table (extends Supabase auth.users)
-- RLS: Users can only access their own profile
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    CONSTRAINT email_unique UNIQUE(email)
);

COMMENT ON TABLE profiles IS 'User profile information linked to Supabase Auth';

-- 2. Conversations table (groups queries by session/topic)
-- RLS: Users can only access their own conversations
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT,
    datasource_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    conversation_path TEXT
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);

COMMENT ON TABLE conversations IS 'Conversation groups - one conversation = multiple turns';
COMMENT ON COLUMN conversations.title IS 'Auto-generated from first query or user-provided';
COMMENT ON COLUMN conversations.datasource_id IS 'Default or custom CSV upload ID';

-- 3. Conversation turns table (ALL historical queries - NO LIMIT)
-- RLS: Inherited from parent conversation
CREATE TABLE IF NOT EXISTS conversation_turns (
    id BIGSERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    turn_number INTEGER NOT NULL,
    user_prompt TEXT NOT NULL,
    sql_generated TEXT,
    charts JSONB,
    insight_summary TEXT,
    data_limitations TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conversation_turns_conversation_id ON conversation_turns(conversation_id);
CREATE INDEX idx_conversation_turns_created_at ON conversation_turns(created_at DESC);

COMMENT ON TABLE conversation_turns IS 'All turns in a conversation with full history (no limit)';
COMMENT ON COLUMN conversation_turns.charts IS 'JSON array of chart specifications with actual data';
COMMENT ON COLUMN conversation_turns.sql_generated IS 'The SELECT statement that was executed';

-- 4. Sessions table (for API refresh tokens)
-- RLS: Users can only access their own sessions
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    refresh_token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

COMMENT ON TABLE sessions IS 'Active sessions with refresh tokens (7-day expiry)';

-- ============================================================================
-- ROW-LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_turns ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- ── PROFILES ──
-- Users can only read/update their own profile
CREATE POLICY "Users can read own profile"
  ON profiles FOR SELECT
  USING (id = auth.uid());

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (id = auth.uid());

CREATE POLICY "Users can insert their own profile"
  ON profiles FOR INSERT
  WITH CHECK (id = auth.uid());

-- ── CONVERSATIONS ──
-- Users can only access conversations they created
CREATE POLICY "Users can read own conversations"
  ON conversations FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "Users can create conversations"
  ON conversations FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own conversations"
  ON conversations FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY "Users can delete own conversations"
  ON conversations FOR DELETE
  USING (user_id = auth.uid());

-- ── CONVERSATION TURNS ──
-- Access controlled by parent conversation (inherited via FK)
-- Users can only read turns from conversations they own
CREATE POLICY "Users can read turns from own conversations"
  ON conversation_turns FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM conversations
      WHERE conversations.id = conversation_turns.conversation_id
      AND conversations.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert turns in own conversations"
  ON conversation_turns FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM conversations
      WHERE conversations.id = conversation_id
      AND conversations.user_id = auth.uid()
    )
  );

-- ── SESSIONS ──
-- Users can only access their own sessions
CREATE POLICY "Users can read own sessions"
  ON sessions FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "Users can create own sessions"
  ON sessions FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can delete own sessions"
  ON sessions FOR DELETE
  USING (user_id = auth.uid());

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to auto-update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update conversations.updated_at
CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to auto-update user last_login
CREATE OR REPLACE FUNCTION update_last_login()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE profiles SET last_login = NOW() WHERE id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update last_login on new conversation
CREATE TRIGGER update_profile_last_login
    AFTER INSERT ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_last_login();

-- ============================================================================
-- INSTRUCTIONS FOR USER
-- ============================================================================
-- 1. Go to Supabase SQL Editor: https://app.supabase.com/project/YOUR_PROJECT_ID/sql/new
-- 2. Paste this entire script
-- 3. Click "Run" (or press Ctrl+Enter)
-- 4. Verify all tables are created with no errors
-- 5. Check "Tables" in left sidebar - should see: profiles, conversations, conversation_turns, sessions
-- 6. Come back to continue with backend implementation
