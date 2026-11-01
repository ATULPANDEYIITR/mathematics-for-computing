/*
 * RAINBOW TABLES AND PASSWORD ATTACKS
 * PostgreSQL 15+
 *
 * Defensive password-security assessment database.
 *
 * Models:
 * - Repositories of synthetic password-security assessments
 * - Password credential metadata
 * - Unique salts and password-hash parameters
 * - Attack classifications
 * - Security policies
 * - Authentication attempts
 * - Security findings
 * - Account states
 * - Audit reports
 *
 * No plaintext passwords or real password hashes are stored.
 */

BEGIN;

CREATE SCHEMA IF NOT EXISTS password_security;

SET search_path TO password_security, public;

-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE attack_type AS ENUM (
    'dictionary',
    'brute_force',
    'rainbow_table',
    'password_spraying',
    'credential_stuffing',
    'phishing'
);

CREATE TYPE account_status AS ENUM (
    'active',
    'locked',
    'disabled'
);

CREATE TYPE assessment_status AS ENUM (
    'created',
    'running',
    'completed',
    'failed'
);

CREATE TYPE finding_severity AS ENUM (
    'informational',
    'low',
    'medium',
    'high',
    'critical'
);

CREATE TYPE authentication_result AS ENUM (
    'accepted',
    'rejected',
    'locked',
    'disabled'
);

-- ============================================================
-- 2. ORGANIZATIONS AND SECURITY ASSESSMENTS
-- ============================================================

CREATE TABLE organizations (
    organization_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_name VARCHAR(150) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE security_assessments (
    assessment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),
    assessment_name VARCHAR(150) NOT NULL,
    status assessment_status NOT NULL DEFAULT 'created',
    scope_description TEXT NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CHECK (
        completed_at IS NULL OR
        started_at IS NOT NULL
    ),

    CHECK (
        completed_at IS NULL OR
        completed_at >= started_at
    )
);

CREATE INDEX idx_assessments_organization
    ON security_assessments(organization_id, created_at DESC);

-- ============================================================
-- 3. ACCOUNTS AND CREDENTIAL METADATA
-- ============================================================

CREATE TABLE security_accounts (
    account_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),
    username VARCHAR(80) NOT NULL,
    status account_status NOT NULL DEFAULT 'active',
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (organization_id, username),

    CHECK (failed_attempts >= 0),

    CHECK (
        (status = 'locked' AND locked_at IS NOT NULL)
        OR
        (status <> 'locked')
    )
);

CREATE TABLE password_credentials (
    credential_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_id BIGINT NOT NULL UNIQUE
        REFERENCES security_accounts(account_id),
    algorithm VARCHAR(40) NOT NULL,
    salt BYTEA NOT NULL,
    password_hash BYTEA NOT NULL,
    iterations INTEGER,
    memory_kib INTEGER,
    parallelism INTEGER,
    key_length INTEGER NOT NULL DEFAULT 32,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    upgraded_at TIMESTAMPTZ,

    CHECK (octet_length(salt) >= 16),
    CHECK (octet_length(password_hash) >= 32),
    CHECK (key_length >= 32),

    CHECK (
        (algorithm = 'argon2id'
            AND memory_kib >= 19456
            AND iterations >= 2
            AND parallelism >= 1)
        OR
        (algorithm = 'pbkdf2-sha256'
            AND iterations >= 600000)
        OR
        (algorithm = 'scrypt'
            AND memory_kib IS NOT NULL)
    )
);

-- A salt must not be reused inside an organization.
CREATE TABLE organization_salts (
    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),
    salt_fingerprint BYTEA NOT NULL,
    credential_id BIGINT NOT NULL UNIQUE
        REFERENCES password_credentials(credential_id),

    PRIMARY KEY (organization_id, salt_fingerprint)
);

-- ============================================================
-- 4. PASSWORD POLICIES
-- ============================================================

CREATE TABLE password_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),
    policy_name VARCHAR(120) NOT NULL,
    minimum_length INTEGER NOT NULL DEFAULT 14,
    maximum_length INTEGER NOT NULL DEFAULT 128,
    reject_common_passwords BOOLEAN NOT NULL DEFAULT TRUE,
    require_mfa BOOLEAN NOT NULL DEFAULT TRUE,
    require_phishing_resistant_mfa BOOLEAN NOT NULL DEFAULT FALSE,
    maximum_failed_attempts INTEGER NOT NULL DEFAULT 5,
    require_password_hashing BOOLEAN NOT NULL DEFAULT TRUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,

    UNIQUE (organization_id, policy_name),

    CHECK (minimum_length >= 8),
    CHECK (maximum_length >= minimum_length),
    CHECK (maximum_length <= 1024),
    CHECK (maximum_failed_attempts BETWEEN 1 AND 100)
);

CREATE UNIQUE INDEX idx_one_active_policy_per_org
    ON password_policies(organization_id)
    WHERE active = TRUE;

-- ============================================================
-- 5. ATTACK CLASSIFICATION
-- ============================================================

CREATE TABLE attack_catalog (
    attack_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    attack attack_type NOT NULL UNIQUE,
    description TEXT NOT NULL,
    defensive_control TEXT NOT NULL
);

INSERT INTO attack_catalog (
    attack,
    description,
    defensive_control
)
VALUES
(
    'dictionary',
    'Tests candidate passwords against password hashes.',
    'Password hashing, compromised-password screening and MFA.'
),
(
    'brute_force',
    'Searches a defined password search space.',
    'Strong password storage and authentication rate limiting.'
),
(
    'rainbow_table',
    'Uses precomputed hash chains for repeated hash lookups.',
    'Unique random salts and slow password hashing.'
),
(
    'password_spraying',
    'Attempts a small password set across multiple accounts.',
    'Cross-account detection and MFA.'
),
(
    'credential_stuffing',
    'Reuses previously exposed authentication combinations.',
    'Credential monitoring, MFA and anomaly detection.'
),
(
    'phishing',
    'Uses deceptive communication to obtain authentication secrets.',
    'Phishing-resistant authentication and user verification.'
);

-- ============================================================
-- 6. ASSESSMENT ATTACK EXECUTIONS
-- ============================================================

CREATE TABLE attack_executions (
    execution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    assessment_id BIGINT NOT NULL
        REFERENCES security_assessments(assessment_id),
    attack_id BIGINT NOT NULL
        REFERENCES attack_catalog(attack_id),
    status assessment_status NOT NULL DEFAULT 'created',
    synthetic_data_only BOOLEAN NOT NULL DEFAULT TRUE,
    candidates_tested BIGINT NOT NULL DEFAULT 0,
    successful_matches INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    execution_notes TEXT,

    CHECK (candidates_tested >= 0),
    CHECK (successful_matches >= 0),
    CHECK (successful_matches <= candidates_tested),
    CHECK (synthetic_data_only = TRUE),

    CHECK (
        completed_at IS NULL OR
        started_at IS NOT NULL
    )
);

CREATE INDEX idx_attack_execution_assessment
    ON attack_executions(assessment_id, status);

-- ============================================================
-- 7. SECURITY FINDINGS
-- ============================================================

CREATE TABLE security_findings (
    finding_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    execution_id BIGINT NOT NULL
        REFERENCES attack_executions(execution_id),
    severity finding_severity NOT NULL,
    finding_title VARCHAR(180) NOT NULL,
    finding_description TEXT NOT NULL,
    remediation TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,

    CHECK (
        (resolved = TRUE AND resolved_at IS NOT NULL)
        OR
        (resolved = FALSE AND resolved_at IS NULL)
    )
);

CREATE INDEX idx_findings_open_severity
    ON security_findings(severity, created_at DESC)
    WHERE resolved = FALSE;

-- ============================================================
-- 8. AUTHENTICATION EVENTS
-- ============================================================

CREATE TABLE authentication_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_id BIGINT NOT NULL
        REFERENCES security_accounts(account_id),
    result authentication_result NOT NULL,
    source_identifier VARCHAR(100),
    authentication_method VARCHAR(60) NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Never store passwords, tokens or raw authentication secrets.
    CHECK (length(authentication_method) > 0)
);

CREATE INDEX idx_authentication_account_time
    ON authentication_events(account_id, occurred_at DESC);

-- ============================================================
-- 9. ACCOUNT STATE TRANSITION TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION enforce_account_state()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.failed_attempts < 0 THEN
        RAISE EXCEPTION 'Failed attempts cannot be negative';
    END IF;

    IF OLD.status = 'disabled' AND NEW.status <> 'disabled' THEN
        RAISE EXCEPTION
            'Disabled accounts cannot be reactivated through this operation';
    END IF;

    IF NEW.status = 'locked' AND NEW.locked_at IS NULL THEN
        NEW.locked_at := now();
    END IF;

    IF NEW.status <> 'locked' THEN
        NEW.locked_at := NULL;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_enforce_account_state
BEFORE UPDATE ON security_accounts
FOR EACH ROW
EXECUTE FUNCTION enforce_account_state();

-- ============================================================
-- 10. CREDENTIAL SALT REGISTRATION
-- ============================================================

CREATE OR REPLACE FUNCTION register_credential_salt()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_organization_id BIGINT;
BEGIN
    SELECT organization_id
    INTO v_organization_id
    FROM security_accounts
    WHERE account_id = NEW.account_id;

    IF v_organization_id IS NULL THEN
        RAISE EXCEPTION 'Credential account does not exist';
    END IF;

    INSERT INTO organization_salts (
        organization_id,
        salt_fingerprint,
        credential_id
    )
    VALUES (
        v_organization_id,
        NEW.salt,
        NEW.credential_id
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_register_credential_salt
AFTER INSERT ON password_credentials
FOR EACH ROW
EXECUTE FUNCTION register_credential_salt();

-- ============================================================
-- 11. FAILED LOGIN ACCOUNT LOCKING
-- ============================================================

CREATE OR REPLACE FUNCTION record_authentication_attempt(
    p_account_id BIGINT,
    p_success BOOLEAN,
    p_method VARCHAR DEFAULT 'password'
)
RETURNS authentication_result
LANGUAGE plpgsql
AS $$
DECLARE
    v_status account_status;
    v_failed INTEGER;
    v_maximum INTEGER;
    v_result authentication_result;
BEGIN
    SELECT a.status, a.failed_attempts,
           p.maximum_failed_attempts
    INTO v_status, v_failed, v_maximum
    FROM security_accounts a
    JOIN password_policies p
      ON p.organization_id = a.organization_id
     AND p.active = TRUE
    WHERE a.account_id = p_account_id
    FOR UPDATE OF a;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account or active policy not found';
    END IF;

    IF v_status = 'disabled' THEN
        v_result := 'disabled';

    ELSIF v_status = 'locked' THEN
        v_result := 'locked';

    ELSIF p_success THEN
        UPDATE security_accounts
        SET failed_attempts = 0
        WHERE account_id = p_account_id;

        v_result := 'accepted';

    ELSE
        v_failed := v_failed + 1;

        IF v_failed >= v_maximum THEN
            UPDATE security_accounts
            SET failed_attempts = v_failed,
                status = 'locked',
                locked_at = now()
            WHERE account_id = p_account_id;

            v_result := 'locked';
        ELSE
            UPDATE security_accounts
            SET failed_attempts = v_failed
            WHERE account_id = p_account_id;

            v_result := 'rejected';
        END IF;
    END IF;

    INSERT INTO authentication_events (
        account_id,
        result,
        authentication_method
    )
    VALUES (
        p_account_id,
        v_result,
        p_method
    );

    RETURN v_result;
END;
$$;

-- ============================================================
-- 12. ASSESSMENT LIFECYCLE
-- ============================================================

CREATE OR REPLACE FUNCTION validate_assessment_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status = 'completed'
       AND NEW.status <> 'completed' THEN
        RAISE EXCEPTION 'Completed assessments are immutable';
    END IF;

    IF OLD.status = 'failed'
       AND NEW.status <> 'failed' THEN
        RAISE EXCEPTION 'Failed assessments cannot be reopened';
    END IF;

    IF NEW.status = 'running'
       AND NEW.started_at IS NULL THEN
        NEW.started_at := now();
    END IF;

    IF NEW.status IN ('completed', 'failed') THEN
        IF NEW.completed_at IS NULL THEN
            NEW.completed_at := now();
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_assessment_transition
BEFORE UPDATE ON security_assessments
FOR EACH ROW
EXECUTE FUNCTION validate_assessment_transition();

-- ============================================================
-- 13. REPORTING VIEW
-- ============================================================

CREATE OR REPLACE VIEW assessment_security_report AS
SELECT
    sa.assessment_id,
    o.organization_name,
    sa.assessment_name,
    sa.status AS assessment_status,
    COUNT(DISTINCT ae.execution_id) AS attack_executions,
    COALESCE(SUM(ae.candidates_tested), 0) AS candidates_tested,
    COALESCE(SUM(ae.successful_matches), 0) AS successful_matches,
    COUNT(DISTINCT sf.finding_id) AS findings,
    COUNT(DISTINCT sf.finding_id)
        FILTER (WHERE sf.resolved = FALSE) AS open_findings
FROM security_assessments sa
JOIN organizations o
    ON o.organization_id = sa.organization_id
LEFT JOIN attack_executions ae
    ON ae.assessment_id = sa.assessment_id
LEFT JOIN security_findings sf
    ON sf.execution_id = ae.execution_id
GROUP BY
    sa.assessment_id,
    o.organization_name,
    sa.assessment_name,
    sa.status;

-- ============================================================
-- 14. SAMPLE ORGANIZATION AND POLICIES
-- ============================================================

INSERT INTO organizations(organization_name)
VALUES ('Synthetic Security Research Unit');

INSERT INTO password_policies (
    organization_id,
    policy_name,
    minimum_length,
    maximum_length,
    reject_common_passwords,
    require_mfa,
    maximum_failed_attempts
)
SELECT
    organization_id,
    'Enterprise Password Policy',
    14,
    128,
    TRUE,
    TRUE,
    3
FROM organizations
WHERE organization_name = 'Synthetic Security Research Unit';

INSERT INTO security_assessments (
    organization_id,
    assessment_name,
    scope_description
)
SELECT
    organization_id,
    'Rainbow Table Resistance Assessment',
    'Controlled synthetic password-storage and authentication evaluation.'
FROM organizations
WHERE organization_name = 'Synthetic Security Research Unit';

-- ============================================================
-- 15. SAMPLE ACCOUNTS
-- ============================================================

INSERT INTO security_accounts (
    organization_id,
    username
)
SELECT
    organization_id,
    username
FROM organizations
CROSS JOIN (
    VALUES
        ('security_admin'),
        ('security_analyst'),
        ('security_auditor'),
        ('security_locked')
) AS accounts(username)
WHERE organization_name = 'Synthetic Security Research Unit';

-- ============================================================
-- 16. SAMPLE CREDENTIAL METADATA
-- ============================================================

/*
 * These are synthetic byte sequences, not usable password hashes.
 * Production credentials must be generated by an approved
 * Argon2id, scrypt or PBKDF2 implementation.
 */

INSERT INTO password_credentials (
    account_id,
    algorithm,
    salt,
    password_hash,
    iterations,
    key_length
)
SELECT
    account_id,
    'pbkdf2-sha256',
    decode(
        lpad(to_hex(account_id), 32, '0'),
        'hex'
    ),
    decode(
        repeat('ab', 32),
        'hex'
    ),
    600000,
    32
FROM security_accounts
WHERE organization_id = (
    SELECT organization_id
    FROM organizations
    WHERE organization_name = 'Synthetic Security Research Unit'
);

-- ============================================================
-- 17. SAMPLE ATTACK EXECUTIONS
-- ============================================================

INSERT INTO attack_executions (
    assessment_id,
    attack_id,
    status,
    candidates_tested,
    successful_matches,
    started_at,
    completed_at,
    execution_notes
)
SELECT
    sa.assessment_id,
    ac.attack_id,
    'completed',
    sample.tested,
    sample.matches,
    now() - interval '10 minutes',
    now(),
    sample.notes
FROM security_assessments sa
CROSS JOIN (
    VALUES
    (
        'dictionary'::attack_type,
        4::BIGINT,
        1,
        'Synthetic candidate-list audit.'
    ),
    (
        'rainbow_table'::attack_type,
        64::BIGINT,
        1,
        'Synthetic precomputed chain experiment.'
    ),
    (
        'brute_force'::attack_type,
        16::BIGINT,
        0,
        'Restricted synthetic search-space experiment.'
    ),
    (
        'password_spraying'::attack_type,
        0::BIGINT,
        0,
        'Detection-policy review without live authentication attempts.'
    ),
    (
        'credential_stuffing'::attack_type,
        0::BIGINT,
        0,
        'Synthetic detection scenario.'
    ),
    (
        'phishing'::attack_type,
        0::BIGINT,
        0,
        'Authentication-awareness control review.'
    )
) AS sample(attack, tested, matches, notes)
JOIN attack_catalog ac ON ac.attack = sample.attack
WHERE sa.assessment_name = 'Rainbow Table Resistance Assessment';

-- ============================================================
-- 18. SECURITY FINDINGS
-- ============================================================

INSERT INTO security_findings (
    execution_id,
    severity,
    finding_title,
    finding_description,
    remediation
)
SELECT
    execution_id,
    'high',
    'Unsalted fast-hash exposure',
    'Synthetic legacy configuration illustrates repeated unsalted hash exposure.',
    'Use unique salts and an approved adaptive password hashing scheme.'
FROM attack_executions ae
JOIN attack_catalog ac ON ac.attack_id = ae.attack_id
WHERE ac.attack = 'rainbow_table'
LIMIT 1;

INSERT INTO security_findings (
    execution_id,
    severity,
    finding_title,
    finding_description,
    remediation
)
SELECT
    execution_id,
    'medium',
    'Weak password candidate detected',
    'A synthetic dictionary candidate matched the demonstration hash.',
    'Reject compromised passwords and enforce appropriate password storage.'
FROM attack_executions ae
JOIN attack_catalog ac ON ac.attack_id = ae.attack_id
WHERE ac.attack = 'dictionary'
LIMIT 1;

-- ============================================================
-- 19. AUTHENTICATION WORKFLOW DEMONSTRATION
-- ============================================================

DO $$
DECLARE
    v_account_id BIGINT;
    v_result authentication_result;
BEGIN
    SELECT account_id
    INTO v_account_id
    FROM security_accounts
    WHERE username = 'security_analyst';

    -- Three consecutive failures trigger the configured lock.
    FOR i IN 1..3 LOOP
        v_result := record_authentication_attempt(
            v_account_id,
            FALSE,
            'password'
        );

        RAISE NOTICE 'Authentication attempt %: %', i, v_result;
    END LOOP;
END;
$$;

-- ============================================================
-- 20. ASSESSMENT COMPLETION
-- ============================================================

UPDATE security_assessments
SET status = 'completed',
    started_at = COALESCE(started_at, now()),
    completed_at = now()
WHERE assessment_name = 'Rainbow Table Resistance Assessment'
  AND status = 'created';

-- ============================================================
-- 21. RETRIEVAL QUERIES
-- ============================================================

-- Attack taxonomy and associated defensive controls.
SELECT
    attack,
    description,
    defensive_control
FROM attack_catalog
ORDER BY attack;

-- Organization accounts and current state.
SELECT
    username,
    status,
    failed_attempts,
    locked_at
FROM security_accounts
ORDER BY username;

-- ============================================================
-- 22. HASHING CONFIGURATION VALIDATION
-- ============================================================

SELECT
    sa.username,
    pc.algorithm,
    octet_length(pc.salt) AS salt_bytes,
    octet_length(pc.password_hash) AS hash_bytes,
    pc.iterations,
    CASE
        WHEN pc.algorithm = 'argon2id'
             AND pc.iterations >= 2
             AND pc.memory_kib >= 19456
            THEN 'VALID'
        WHEN pc.algorithm = 'pbkdf2-sha256'
             AND pc.iterations >= 600000
            THEN 'VALID'
        WHEN pc.algorithm = 'scrypt'
             AND pc.memory_kib IS NOT NULL
            THEN 'CONFIGURATION_REQUIRES_REVIEW'
        ELSE 'INVALID'
    END AS configuration_status
FROM security_accounts sa
JOIN password_credentials pc
    ON pc.account_id = sa.account_id;

-- ============================================================
-- 23. AGGREGATION AND ASSESSMENT REPORT
-- ============================================================

SELECT *
FROM assessment_security_report
ORDER BY assessment_id;

-- Attack execution success rate.
SELECT
    ac.attack,
    COUNT(ae.execution_id) AS executions,
    COALESCE(SUM(ae.candidates_tested), 0) AS candidates_tested,
    COALESCE(SUM(ae.successful_matches), 0) AS matches,
    CASE
        WHEN SUM(ae.candidates_tested) = 0 THEN 0
        ELSE ROUND(
            100.0 * SUM(ae.successful_matches)
            / SUM(ae.candidates_tested),
            2
        )
    END AS match_percentage
FROM attack_catalog ac
LEFT JOIN attack_executions ae
    ON ae.attack_id = ac.attack_id
GROUP BY ac.attack_id, ac.attack
ORDER BY ac.attack;

-- ============================================================
-- 24. SECURITY FINDINGS REPORT
-- ============================================================

SELECT
    sf.finding_title,
    sf.severity,
    ac.attack,
    sf.resolved,
    sf.remediation
FROM security_findings sf
JOIN attack_executions ae
    ON ae.execution_id = sf.execution_id
JOIN attack_catalog ac
    ON ac.attack_id = ae.attack_id
ORDER BY
    CASE sf.severity
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
        ELSE 5
    END;

-- ============================================================
-- 25. AUTHENTICATION FAILURE ANALYSIS
-- ============================================================

SELECT
    sa.username,
    COUNT(*) FILTER (
        WHERE ae.result = 'rejected'
    ) AS rejected_attempts,
    COUNT(*) FILTER (
        WHERE ae.result = 'accepted'
    ) AS successful_attempts,
    COUNT(*) FILTER (
        WHERE ae.result = 'locked'
    ) AS locked_events
FROM security_accounts sa
LEFT JOIN authentication_events ae
    ON ae.account_id = sa.account_id
GROUP BY sa.account_id, sa.username
ORDER BY sa.username;

-- ============================================================
-- 26. CTE: OPEN FINDINGS PRIORITIZATION
-- ============================================================

WITH open_findings AS (
    SELECT
        ac.attack,
        sf.severity,
        COUNT(*) AS finding_count
    FROM security_findings sf
    JOIN attack_executions ae
        ON ae.execution_id = sf.execution_id
    JOIN attack_catalog ac
        ON ac.attack_id = ae.attack_id
    WHERE sf.resolved = FALSE
    GROUP BY ac.attack, sf.severity
),
prioritized AS (
    SELECT
        attack,
        severity,
        finding_count,
        SUM(finding_count) OVER (
            PARTITION BY attack
        ) AS attack_total
    FROM open_findings
)
SELECT *
FROM prioritized
ORDER BY finding_count DESC, attack;

-- ============================================================
-- 27. TRANSACTIONAL ACCOUNT STATE VALIDATION
-- ============================================================

SAVEPOINT before_security_validation;

DO $$
DECLARE
    v_locked_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_locked_count
    FROM security_accounts
    WHERE status = 'locked';

    IF v_locked_count < 1 THEN
        RAISE NOTICE 'No locked accounts detected in this dataset.';
    ELSE
        RAISE NOTICE 'Locked accounts detected: %', v_locked_count;
    END IF;
END;
$$;

RELEASE SAVEPOINT before_security_validation;

-- ============================================================
-- 28. PRODUCTION SECURITY DESIGN NOTES
-- ============================================================

COMMENT ON TABLE password_credentials IS
'Stores adaptive password-hash metadata only. Plaintext passwords must never be stored.';

COMMENT ON COLUMN password_credentials.salt IS
'Unique cryptographically random per-credential salt.';

COMMENT ON COLUMN password_credentials.password_hash IS
'Derived password hash generated by an approved password hashing library.';

COMMENT ON TABLE attack_executions IS
'Stores controlled synthetic assessment executions, not live credential attacks.';

COMMENT ON TABLE authentication_events IS
'Records authentication outcomes without retaining password values or authentication secrets.';

COMMENT ON FUNCTION record_authentication_attempt(
    BIGINT,
    BOOLEAN,
    VARCHAR
) IS
'Serializes account failure-counter updates and applies configured account locking.';

COMMIT;
