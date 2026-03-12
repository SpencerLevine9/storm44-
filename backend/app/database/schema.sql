CREATE EXTENSION IF NOT EXISTS vector;

-- 1. user_account
CREATE TABLE IF NOT EXISTS user_account (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. source
CREATE TABLE IF NOT EXISTS source (
    id                SERIAL PRIMARY KEY,
    user_id           INTEGER      NOT NULL REFERENCES user_account(id) ON DELETE CASCADE,
    title             VARCHAR(512) NOT NULL,
    source_type       VARCHAR(32)  NOT NULL,
    source_path       TEXT,
    output_text_path  TEXT,
    num_pages         INTEGER,
    video_id          VARCHAR(32),
    video_url         TEXT,
    transcript_source VARCHAR(64),
    num_segments      INTEGER,
    status            VARCHAR(32)  NOT NULL DEFAULT 'processing',
    error_message     TEXT,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- 3. chunk
CREATE TABLE IF NOT EXISTS chunk (
    id            SERIAL PRIMARY KEY,
    source_id     INTEGER NOT NULL REFERENCES source(id) ON DELETE CASCADE,
    chunk_index   INTEGER NOT NULL,
    start_page    INTEGER,
    end_page      INTEGER,
    start_time    REAL,
    end_time      REAL,
    approx_words  INTEGER,
    text          TEXT    NOT NULL,
    preview       VARCHAR(256),
    UNIQUE (source_id, chunk_index)
);

-- 4. video_segment
CREATE TABLE IF NOT EXISTS video_segment (
    id          SERIAL PRIMARY KEY,
    source_id   INTEGER NOT NULL REFERENCES source(id) ON DELETE CASCADE,
    text        TEXT    NOT NULL,
    start_time  REAL    NOT NULL,
    duration    REAL,
    seg_index   INTEGER NOT NULL,
    UNIQUE (source_id, seg_index)
);

-- 5. embedding (pgvector)
CREATE TABLE IF NOT EXISTS embedding (
    id              SERIAL PRIMARY KEY,
    chunk_id        INTEGER      NOT NULL REFERENCES chunk(id) ON DELETE CASCADE UNIQUE,
    embedding       vector(384)  NOT NULL,
    embedding_model VARCHAR(128) NOT NULL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_account_username ON user_account (username);
CREATE INDEX IF NOT EXISTS idx_source_user_id        ON source (user_id);
CREATE INDEX IF NOT EXISTS idx_source_status          ON source (status);
CREATE INDEX IF NOT EXISTS idx_chunk_source_id        ON chunk (source_id);
CREATE INDEX IF NOT EXISTS idx_vseg_source_id         ON video_segment (source_id);
CREATE INDEX IF NOT EXISTS idx_embedding_cosine
    ON embedding USING hnsw (embedding vector_cosine_ops);
