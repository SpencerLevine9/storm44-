-- User account table for Storm44 app.
-- Store only a hash of the password (e.g. bcrypt); never store plain text.

CREATE TABLE IF NOT EXISTS user_account (
    id         SERIAL PRIMARY KEY,
    username   VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_user_account_username ON user_account (username);
