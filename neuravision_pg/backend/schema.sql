-- ============================================================
--  NEURAVISION — PostgreSQL Schema
--  Run this once to set up your database
-- ============================================================

-- Create database (run this separately if needed):
-- CREATE DATABASE neuravision;

-- Connect to neuravision database then run the rest:

-- Subjects (registered faces)
CREATE TABLE IF NOT EXISTS subjects (
    id              SERIAL PRIMARY KEY,
    subject_id      VARCHAR(30)  NOT NULL UNIQUE,
    name            VARCHAR(100) NOT NULL,
    department      VARCHAR(100) DEFAULT NULL,
    email           VARCHAR(150) DEFAULT NULL,
    role            VARCHAR(20)  DEFAULT 'student',
    encoding        BYTEA        DEFAULT NULL,
    registered_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    is_active       BOOLEAN      DEFAULT TRUE
);

-- Attendance (one row per subject per day)
CREATE TABLE IF NOT EXISTS attendance (
    id           SERIAL PRIMARY KEY,
    subject_id   VARCHAR(30)  NOT NULL,
    date         DATE         NOT NULL,
    first_seen   TIMESTAMP    NOT NULL,
    last_seen    TIMESTAMP    NOT NULL,
    scan_count   INT          DEFAULT 1,
    confidence   FLOAT        DEFAULT 0,
    emotion      VARCHAR(20)  DEFAULT NULL,
    status       VARCHAR(20)  DEFAULT 'present',
    UNIQUE (subject_id, date),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
);

-- Detection log (every face seen)
CREATE TABLE IF NOT EXISTS detection_log (
    id          BIGSERIAL PRIMARY KEY,
    subject_id  VARCHAR(30)  DEFAULT 'UNKNOWN',
    detected_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    confidence  FLOAT        DEFAULT 0,
    emotion     VARCHAR(20)  DEFAULT NULL,
    age_est     FLOAT        DEFAULT NULL,
    gender_est  VARCHAR(10)  DEFAULT NULL,
    liveness    FLOAT        DEFAULT NULL,
    cam_id      VARCHAR(20)  DEFAULT 'CAM-01'
);

-- System events
CREATE TABLE IF NOT EXISTS system_log (
    id          SERIAL PRIMARY KEY,
    event_type  VARCHAR(50),
    message     TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_att_date    ON attendance(date);
CREATE INDEX IF NOT EXISTS idx_att_sub     ON attendance(subject_id);
CREATE INDEX IF NOT EXISTS idx_det_sub     ON detection_log(subject_id);
CREATE INDEX IF NOT EXISTS idx_det_time    ON detection_log(detected_at);

-- Verify
SELECT 'NEURAVISION PostgreSQL database ready!' AS status;
