DROP SCHEMA IF EXISTS rsa_math CASCADE;
CREATE SCHEMA rsa_math;

SET search_path = rsa_math, public;

-- PostgreSQL NUMERIC is used so the arithmetic does not depend on
-- machine-sized integer overflow. These functions model the mathematics;
-- they are not intended to replace a production cryptographic library.

CREATE TABLE key_parameters (
    key_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    p NUMERIC(1000, 0) NOT NULL CHECK (p > 1),
    q NUMERIC(1000, 0) NOT NULL CHECK (q > 1),
    n NUMERIC(2000, 0) NOT NULL CHECK (n > 1),
    phi_n NUMERIC(2000, 0) NOT NULL CHECK (phi_n > 1),
    public_exponent NUMERIC(2000, 0) NOT NULL CHECK (public_exponent > 1),
    private_exponent NUMERIC(2000, 0) NOT NULL CHECK (private_exponent > 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (n),
    CHECK (p <> q),
    CHECK (n = p * q),
    CHECK (phi_n = (p - 1) * (q - 1))
);

CREATE TABLE rsa_operations (
    operation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    key_id BIGINT NOT NULL REFERENCES key_parameters(key_id),
    operation_type TEXT NOT NULL CHECK (
        operation_type IN ('ENCRYPT', 'DECRYPT', 'VERIFY')
    ),
    input_value NUMERIC(2000, 0) NOT NULL CHECK (input_value >= 0),
    output_value NUMERIC(2000, 0) NOT NULL CHECK (output_value >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, branch_name)
);

CREATE TABLE commits (
    commit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    branch_id BIGINT REFERENCES branches(branch_id),
    commit_hash TEXT NOT NULL,
    parent_hash TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (repository_id, commit_hash)
);

CREATE TYPE pull_request_state AS ENUM (
    'DRAFT',
    'OPEN',
    'CHANGES_REQUESTED',
    'APPROVED',
    'CLOSED',
    'MERGED'
);

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    head_commit_id BIGINT REFERENCES commits(commit_id),
    base_commit_id BIGINT REFERENCES commits(commit_id),
    state pull_request_state NOT NULL DEFAULT 'OPEN',
    branch_synchronized BOOLEAN NOT NULL DEFAULT TRUE,
    merge_conflict BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMPTZ,
    merged_at TIMESTAMPTZ,
    CHECK (source_branch_id <> target_branch_id),
    CHECK (
        (state = 'CLOSED' AND closed_at IS NOT NULL)
        OR state <> 'CLOSED'
    ),
    CHECK (
        (state = 'MERGED' AND merged_at IS NOT NULL)
        OR state <> 'MERGED'
    )
);

CREATE TABLE reviewers (
    reviewer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    reviewer_name TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (repository_id, reviewer_name)
);

CREATE TYPE review_state AS ENUM (
    'COMMENTED',
    'APPROVED',
    'CHANGES_REQUESTED',
    'DISMISSED'
);

CREATE TABLE reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES reviewers(reviewer_id),
    state review_state NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (pull_request_id, reviewer_id, submitted_at)
);

CREATE TABLE review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id)
        ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER,
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (line_number IS NULL OR line_number > 0),
    CHECK (length(trim(body)) > 0)
);

CREATE TABLE conversations (
    conversation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    topic TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(topic)) > 0)
);

CREATE TABLE status_checks (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    required BOOLEAN NOT NULL DEFAULT FALSE,
    passed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, check_name)
);

CREATE TABLE branch_protection_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 0
        CHECK (required_approvals >= 0),
    require_passing_checks BOOLEAN NOT NULL DEFAULT TRUE,
    require_resolved_conversations BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_direct_push BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_force_push BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_branch_deletion BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    allow_administrator_bypass BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE required_status_checks (
    policy_id BIGINT NOT NULL REFERENCES branch_protection_policies(policy_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (policy_id, check_name)
);

CREATE TABLE approval_requirements (
    requirement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    policy_id BIGINT NOT NULL REFERENCES branch_protection_policies(policy_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT REFERENCES reviewers(reviewer_id),
    minimum_approvals INTEGER NOT NULL CHECK (minimum_approvals > 0),
    UNIQUE (policy_id, reviewer_id)
);

CREATE TABLE merge_events (
    merge_event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL UNIQUE
        REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    merge_method TEXT NOT NULL CHECK (
        merge_method IN ('MERGE_COMMIT', 'SQUASH', 'REBASE')
    ),
    merged_by TEXT NOT NULL,
    merged_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pr_repository_state
    ON pull_requests(repository_id, state);

CREATE INDEX idx_reviews_pr_state
    ON reviews(pull_request_id, state);

CREATE INDEX idx_status_checks_pr_required
    ON status_checks(pull_request_id, required, passed);

CREATE INDEX idx_conversations_pr_resolved
    ON conversations(pull_request_id, resolved);

CREATE OR REPLACE FUNCTION modular_pow(
    p_base NUMERIC,
    p_exponent NUMERIC,
    p_modulus NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    result NUMERIC := 1;
    base_value NUMERIC := p_base % p_modulus;
    exponent_value NUMERIC := p_exponent;
BEGIN
    IF p_modulus <= 0 OR p_exponent < 0 THEN
        RAISE EXCEPTION 'Invalid modular exponentiation arguments';
    END IF;

    result := result % p_modulus;

    WHILE exponent_value > 0 LOOP
        IF mod(exponent_value, 2) = 1 THEN
            result := mod(result * base_value, p_modulus);
        END IF;

        base_value := mod(base_value * base_value, p_modulus);
        exponent_value := trunc(exponent_value / 2);
    END LOOP;

    RETURN result;
END;
$$;

CREATE OR REPLACE FUNCTION extended_gcd(
    p_a NUMERIC,
    p_b NUMERIC
)
RETURNS TABLE(g NUMERIC, x NUMERIC, y NUMERIC)
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    old_r NUMERIC := p_a;
    r NUMERIC := p_b;
    old_x NUMERIC := 1;
    x_value NUMERIC := 0;
    old_y NUMERIC := 0;
    y_value NUMERIC := 1;
    quotient NUMERIC;
    temp NUMERIC;
BEGIN
    WHILE r <> 0 LOOP
        quotient := trunc(old_r / r);

        temp := old_r - quotient * r;
        old_r := r;
        r := temp;

        temp := old_x - quotient * x_value;
        old_x := x_value;
        x_value := temp;

        temp := old_y - quotient * y_value;
        old_y := y_value;
        y_value := temp;
    END LOOP;

    RETURN QUERY SELECT old_r, old_x, old_y;
END;
$$;

CREATE OR REPLACE FUNCTION modular_inverse(
    p_value NUMERIC,
    p_modulus NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    result RECORD;
BEGIN
    SELECT * INTO result
    FROM extended_gcd(mod(p_value, p_modulus), p_modulus);

    IF result.g <> 1 THEN
        RAISE EXCEPTION 'No modular inverse exists';
    END IF;

    RETURN mod(result.x + p_modulus, p_modulus);
END;
$$;

CREATE OR REPLACE FUNCTION validate_rsa_key(
    p_key_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    key_row key_parameters%ROWTYPE;
BEGIN
    SELECT *
    INTO key_row
    FROM key_parameters
    WHERE key_id = p_key_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    RETURN key_row.n = key_row.p * key_row.q
       AND key_row.phi_n = (key_row.p - 1) * (key_row.q - 1)
       AND modular_pow(
            key_row.public_exponent * key_row.private_exponent,
            1,
            key_row.phi_n
          ) = 1;
END;
$$;

CREATE OR REPLACE FUNCTION check_pull_request_consistency()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.source_branch_id = NEW.target_branch_id THEN
        RAISE EXCEPTION 'A Pull Request cannot target its source branch';
    END IF;

    IF NEW.state = 'MERGED' AND NEW.merged_at IS NULL THEN
        NEW.merged_at := CURRENT_TIMESTAMP;
    END IF;

    IF NEW.state = 'CLOSED' AND NEW.closed_at IS NULL THEN
        NEW.closed_at := CURRENT_TIMESTAMP;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_pr_consistency
BEFORE INSERT OR UPDATE ON pull_requests
FOR EACH ROW
EXECUTE FUNCTION check_pull_request_consistency();

CREATE OR REPLACE VIEW merge_eligibility AS
WITH effective_approvals AS (
    SELECT
        pr.pull_request_id,
        COUNT(*) FILTER (
            WHERE r.state = 'APPROVED'
              AND r.state <> 'DISMISSED'
              AND rev.active
        ) AS approval_count
    FROM pull_requests pr
    LEFT JOIN reviews r
        ON r.pull_request_id = pr.pull_request_id
    LEFT JOIN reviewers rev
        ON rev.reviewer_id = r.reviewer_id
    GROUP BY pr.pull_request_id
),
required_checks AS (
    SELECT
        pr.pull_request_id,
        COUNT(*) FILTER (
            WHERE rsp.check_name IS NOT NULL
              AND sc.passed = TRUE
        ) AS passed_required,
        COUNT(rsp.check_name) AS total_required
    FROM pull_requests pr
    LEFT JOIN branches b
        ON b.branch_id = pr.target_branch_id
    LEFT JOIN branch_protection_policies bp
        ON bp.branch_id = b.branch_id
    LEFT JOIN required_status_checks rsp
        ON rsp.policy_id = bp.policy_id
    LEFT JOIN status_checks sc
        ON sc.pull_request_id = pr.pull_request_id
       AND sc.check_name = rsp.check_name
    GROUP BY pr.pull_request_id
),
unresolved AS (
    SELECT
        pull_request_id,
        COUNT(*) FILTER (WHERE resolved = FALSE) AS unresolved_count
    FROM conversations
    GROUP BY pull_request_id
)
SELECT
    pr.pull_request_id,
    pr.state,
    pr.branch_synchronized,
    pr.merge_conflict,
    COALESCE(ea.approval_count, 0) AS approval_count,
    COALESCE(rc.passed_required, 0) AS passed_required_checks,
    COALESCE(rc.total_required, 0) AS total_required_checks,
    COALESCE(u.unresolved_count, 0) AS unresolved_conversations,
    bp.required_approvals,
    (
        pr.state IN ('OPEN', 'APPROVED')
        AND pr.branch_synchronized
        AND NOT pr.merge_conflict
        AND COALESCE(ea.approval_count, 0) >= COALESCE(bp.required_approvals, 0)
        AND (
            COALESCE(bp.require_passing_checks, TRUE) = FALSE
            OR COALESCE(rc.passed_required, 0) = COALESCE(rc.total_required, 0)
        )
        AND (
            COALESCE(bp.require_resolved_conversations, TRUE) = FALSE
            OR COALESCE(u.unresolved_count, 0) = 0
        )
    ) AS eligible
FROM pull_requests pr
LEFT JOIN effective_approvals ea
    ON ea.pull_request_id = pr.pull_request_id
LEFT JOIN required_checks rc
    ON rc.pull_request_id = pr.pull_request_id
LEFT JOIN unresolved u
    ON u.pull_request_id = pr.pull_request_id
LEFT JOIN branch_protection_policies bp
    ON bp.branch_id = pr.target_branch_id;

BEGIN;

INSERT INTO key_parameters (
    p, q, n, phi_n, public_exponent, private_exponent
)
VALUES (
    61,
    53,
    3233,
    3120,
    17,
    2753
);

INSERT INTO repositories (repository_name, default_branch)
VALUES ('cryptographic-math-service', 'main');

INSERT INTO branches (repository_id, branch_name, protected)
SELECT repository_id, branch_name, protected
FROM (
    SELECT repository_id, 'main' AS branch_name, TRUE AS protected
    FROM repositories
    WHERE repository_name = 'cryptographic-math-service'
    UNION ALL
    SELECT repository_id, 'feature/rsa-review' AS branch_name, FALSE
    FROM repositories
    WHERE repository_name = 'cryptographic-math-service'
) AS source_rows;

INSERT INTO commits (
    repository_id,
    branch_id,
    commit_hash,
    parent_hash
)
SELECT
    r.repository_id,
    b.branch_id,
    'a1b2c3d4',
    NULL
FROM repositories r
JOIN branches b
    ON b.repository_id = r.repository_id
WHERE r.repository_name = 'cryptographic-math-service'
  AND b.branch_name = 'main';

INSERT INTO commits (
    repository_id,
    branch_id,
    commit_hash,
    parent_hash
)
SELECT
    r.repository_id,
    b.branch_id,
    'e5f6a7b8',
    'a1b2c3d4'
FROM repositories r
JOIN branches b
    ON b.repository_id = r.repository_id
WHERE r.repository_name = 'cryptographic-math-service'
  AND b.branch_name = 'feature/rsa-review';

INSERT INTO pull_requests (
    repository_id,
    source_branch_id,
    target_branch_id,
    head_commit_id,
    base_commit_id,
    state,
    branch_synchronized,
    merge_conflict
)
SELECT
    r.repository_id,
    source_branch.branch_id,
    target_branch.branch_id,
    head.commit_id,
    base.commit_id,
    'APPROVED',
    TRUE,
    FALSE
FROM repositories r
JOIN branches source_branch
    ON source_branch.repository_id = r.repository_id
   AND source_branch.branch_name = 'feature/rsa-review'
JOIN branches target_branch
    ON target_branch.repository_id = r.repository_id
   AND target_branch.branch_name = 'main'
JOIN commits head
    ON head.commit_hash = 'e5f6a7b8'
JOIN commits base
    ON base.commit_hash = 'a1b2c3d4'
WHERE r.repository_name = 'cryptographic-math-service';

INSERT INTO reviewers (repository_id, reviewer_name)
SELECT repository_id, reviewer_name
FROM repositories
CROSS JOIN (
    VALUES
        ('security-reviewer'),
        ('platform-reviewer')
) AS names(reviewer_name)
WHERE repository_name = 'cryptographic-math-service';

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    state
)
SELECT
    pr.pull_request_id,
    rv.reviewer_id,
    'APPROVED'
FROM pull_requests pr
JOIN repositories repo
    ON repo.repository_id = pr.repository_id
JOIN reviewers rv
    ON rv.repository_id = repo.repository_id
WHERE repo.repository_name = 'cryptographic-math-service'
  AND rv.reviewer_name IN ('security-reviewer', 'platform-reviewer');

INSERT INTO review_comments (
    review_id,
    file_path,
    line_number,
    body,
    resolved
)
SELECT
    review_id,
    'rsa_math.sql',
    42,
    'Verify that the modular inverse exists before storing the private exponent.',
    TRUE
FROM reviews
WHERE state = 'APPROVED';

INSERT INTO conversations (
    pull_request_id,
    topic,
    resolved
)
SELECT
    pull_request_id,
    'Confirm that the educational modulus is not presented as production RSA.',
    TRUE
FROM pull_requests;

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    required,
    passed,
    completed_at
)
SELECT
    pull_request_id,
    check_name,
    TRUE,
    TRUE,
    CURRENT_TIMESTAMP
FROM pull_requests
CROSS JOIN (
    VALUES ('unit-tests'), ('security-scan')
) AS checks(check_name);

INSERT INTO branch_protection_policies (
    branch_id,
    required_approvals,
    require_passing_checks,
    require_resolved_conversations,
    prohibit_direct_push,
    prohibit_force_push,
    prohibit_branch_deletion,
    require_linear_history,
    allow_administrator_bypass
)
SELECT
    branch_id,
    2,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    FALSE
FROM branches
WHERE branch_name = 'main';

INSERT INTO required_status_checks (policy_id, check_name)
SELECT policy_id, check_name
FROM branch_protection_policies
CROSS JOIN (
    VALUES ('unit-tests'), ('security-scan')
) AS checks(check_name);

INSERT INTO approval_requirements (
    policy_id,
    reviewer_id,
    minimum_approvals
)
SELECT
    bp.policy_id,
    NULL,
    2
FROM branch_protection_policies bp;

COMMIT;

-- Mathematical validation.
SELECT
    key_id,
    p,
    q,
    n,
    phi_n,
    public_exponent,
    private_exponent,
    validate_rsa_key(key_id) AS key_is_valid
FROM key_parameters;

-- Encryption: 65^17 mod 3233 = 2790.
INSERT INTO rsa_operations (
    key_id,
    operation_type,
    input_value,
    output_value
)
SELECT
    key_id,
    'ENCRYPT',
    65,
    modular_pow(65, public_exponent, n)
FROM key_parameters
WHERE n = 3233;

-- Decryption: 2790^2753 mod 3233 = 65.
INSERT INTO rsa_operations (
    key_id,
    operation_type,
    input_value,
    output_value
)
SELECT
    key_id,
    'DECRYPT',
    2790,
    modular_pow(2790, private_exponent, n)
FROM key_parameters
WHERE n = 3233;

SELECT
    operation_id,
    operation_type,
    input_value,
    output_value
FROM rsa_operations
ORDER BY operation_id;

-- CTE-based review and approval report.
WITH review_summary AS (
    SELECT
        pr.pull_request_id,
        COUNT(*) FILTER (WHERE r.state = 'APPROVED') AS approvals,
        COUNT(*) FILTER (WHERE r.state = 'CHANGES_REQUESTED') AS changes_requested
    FROM pull_requests pr
    LEFT JOIN reviews r
        ON r.pull_request_id = pr.pull_request_id
    GROUP BY pr.pull_request_id
)
SELECT
    pr.pull_request_id,
    pr.state,
    rs.approvals,
    rs.changes_requested,
    pr.branch_synchronized,
    pr.merge_conflict
FROM pull_requests pr
JOIN review_summary rs
    ON rs.pull_request_id = pr.pull_request_id;

-- Final merge-eligibility evaluation.
SELECT *
FROM merge_eligibility
ORDER BY pull_request_id;

-- Demonstrate a failure condition: make a required check fail.
BEGIN;

UPDATE status_checks
SET passed = FALSE
WHERE check_name = 'security-scan';

SELECT
    pull_request_id,
    eligible
FROM merge_eligibility;

ROLLBACK;

-- Transactional integrity restores the successful check state.
SELECT
    pull_request_id,
    check_name,
    required,
    passed
FROM status_checks
ORDER BY pull_request_id, check_name;

-- Relationship report showing repository -> branch -> Pull Request.
SELECT
    r.repository_name,
    source_branch.branch_name AS source_branch,
    target_branch.branch_name AS target_branch,
    pr.pull_request_id,
    pr.state,
    pr.branch_synchronized,
    pr.merge_conflict
FROM repositories r
JOIN branches source_branch
    ON source_branch.repository_id = r.repository_id
JOIN pull_requests pr
    ON pr.source_branch_id = source_branch.branch_id
JOIN branches target_branch
    ON target_branch.branch_id = pr.target_branch_id
ORDER BY pr.pull_request_id;
