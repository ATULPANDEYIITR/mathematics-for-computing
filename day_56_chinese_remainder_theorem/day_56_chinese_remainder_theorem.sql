DROP SCHEMA IF EXISTS crt_lab CASCADE;
CREATE SCHEMA crt_lab;

SET search_path = crt_lab, public;

CREATE TABLE repositories (
    repository_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE repository_users (
    user_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE branches (
    branch_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    is_protected BOOLEAN NOT NULL DEFAULT FALSE,
    head_commit TEXT NOT NULL,
    UNIQUE (repository_id, branch_name)
);

CREATE TABLE commits (
    commit_id TEXT PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    parent_commit_id TEXT REFERENCES commits(commit_id),
    author_id BIGINT NOT NULL REFERENCES repository_users(user_id),
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pull_requests (
    pull_request_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    author_id BIGINT NOT NULL REFERENCES repository_users(user_id),
    head_commit_id TEXT NOT NULL REFERENCES commits(commit_id),
    title TEXT NOT NULL,
    state TEXT NOT NULL CHECK (
        state IN ('draft', 'open', 'merged', 'closed')
    ),
    has_conflicts BOOLEAN NOT NULL DEFAULT FALSE,
    linear_history BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    merged_at TIMESTAMPTZ,
    CHECK (source_branch_id <> target_branch_id)
);

CREATE TABLE reviews (
    review_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES repository_users(user_id),
    commit_id TEXT NOT NULL REFERENCES commits(commit_id),
    review_state TEXT NOT NULL CHECK (
        review_state IN (
            'commented',
            'approved',
            'changes_requested',
            'dismissed'
        )
    ),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE review_comments (
    comment_id BIGSERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id)
        ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER CHECK (line_number > 0),
    body TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE status_checks (
    status_check_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('pending', 'passed', 'failed')
    ),
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, check_name)
);

CREATE TABLE branch_protection_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    required_reviews INTEGER NOT NULL DEFAULT 0
        CHECK (required_reviews >= 0),
    require_status_checks BOOLEAN NOT NULL DEFAULT TRUE,
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT FALSE,
    restrict_direct_push BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_force_push BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_deletion BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    allow_administrator_bypass BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE approval_requirements (
    requirement_id BIGSERIAL PRIMARY KEY,
    policy_id BIGINT NOT NULL REFERENCES branch_protection_policies(policy_id)
        ON DELETE CASCADE,
    role_name TEXT NOT NULL,
    required_count INTEGER NOT NULL CHECK (required_count > 0),
    UNIQUE (policy_id, role_name)
);

CREATE TABLE reviewer_roles (
    reviewer_role_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES repository_users(user_id)
        ON DELETE CASCADE,
    role_name TEXT NOT NULL,
    UNIQUE (repository_id, user_id, role_name)
);

CREATE INDEX idx_pr_target_state
    ON pull_requests(target_branch_id, state);

CREATE INDEX idx_reviews_pr_state
    ON reviews(pull_request_id, review_state);

CREATE INDEX idx_status_checks_pr_status
    ON status_checks(pull_request_id, status);

CREATE INDEX idx_comments_review_resolution
    ON review_comments(review_id, is_resolved);

INSERT INTO repositories (name)
VALUES ('payment-service');

INSERT INTO repository_users (username)
VALUES
    ('alice'),
    ('bob'),
    ('carol'),
    ('david'),
    ('eve');

INSERT INTO branches (
    repository_id, branch_name, is_protected, head_commit
)
SELECT
    repository_id,
    'main',
    TRUE,
    'c100'
FROM repositories
WHERE name = 'payment-service';

INSERT INTO branches (
    repository_id, branch_name, is_protected, head_commit
)
SELECT
    repository_id,
    'feature/retry',
    FALSE,
    'c200'
FROM repositories
WHERE name = 'payment-service';

INSERT INTO branches (
    repository_id, branch_name, is_protected, head_commit
)
SELECT
    repository_id,
    'feature/audit',
    FALSE,
    'c300'
FROM repositories
WHERE name = 'payment-service';

INSERT INTO commits (
    commit_id, repository_id, parent_commit_id, author_id, message
)
SELECT
    'c100',
    r.repository_id,
    NULL,
    u.user_id,
    'Initial protected main commit'
FROM repositories r
JOIN repository_users u ON u.username = 'alice'
WHERE r.name = 'payment-service';

INSERT INTO commits (
    commit_id, repository_id, parent_commit_id, author_id, message
)
SELECT
    'c200',
    r.repository_id,
    'c100',
    u.user_id,
    'Implement payment retry'
FROM repositories r
JOIN repository_users u ON u.username = 'bob'
WHERE r.name = 'payment-service';

INSERT INTO commits (
    commit_id, repository_id, parent_commit_id, author_id, message
)
SELECT
    'c300',
    r.repository_id,
    'c100',
    u.user_id,
    'Add audit logging'
FROM repositories r
JOIN repository_users u ON u.username = 'carol'
WHERE r.name = 'payment-service';

UPDATE branches
SET head_commit = 'c100'
WHERE branch_name = 'main';

INSERT INTO pull_requests (
    repository_id,
    source_branch_id,
    target_branch_id,
    author_id,
    head_commit_id,
    title,
    state,
    has_conflicts,
    linear_history
)
SELECT
    r.repository_id,
    source.branch_id,
    target.branch_id,
    author.user_id,
    'c200',
    'Implement payment retry',
    'open',
    FALSE,
    TRUE
FROM repositories r
JOIN branches source
    ON source.repository_id = r.repository_id
   AND source.branch_name = 'feature/retry'
JOIN branches target
    ON target.repository_id = r.repository_id
   AND target.branch_name = 'main'
JOIN repository_users author
    ON author.username = 'bob'
WHERE r.name = 'payment-service';

INSERT INTO pull_requests (
    repository_id,
    source_branch_id,
    target_branch_id,
    author_id,
    head_commit_id,
    title,
    state,
    has_conflicts,
    linear_history
)
SELECT
    r.repository_id,
    source.branch_id,
    target.branch_id,
    author.user_id,
    'c300',
    'Add audit logging',
    'open',
    TRUE,
    TRUE
FROM repositories r
JOIN branches source
    ON source.repository_id = r.repository_id
   AND source.branch_name = 'feature/audit'
JOIN branches target
    ON target.repository_id = r.repository_id
   AND target.branch_name = 'main'
JOIN repository_users author
    ON author.username = 'carol'
WHERE r.name = 'payment-service';

INSERT INTO branch_protection_policies (
    branch_id,
    required_reviews,
    require_status_checks,
    require_conversation_resolution,
    restrict_direct_push,
    restrict_force_push,
    restrict_deletion,
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

INSERT INTO approval_requirements (
    policy_id, role_name, required_count
)
SELECT
    policy_id,
    'maintainer',
    2
FROM branch_protection_policies;

INSERT INTO reviewer_roles (
    repository_id, user_id, role_name
)
SELECT r.repository_id, u.user_id, 'maintainer'
FROM repositories r
JOIN repository_users u
    ON u.username IN ('alice', 'david')
WHERE r.name = 'payment-service';

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    commit_id,
    review_state
)
SELECT
    pr.pull_request_id,
    u.user_id,
    pr.head_commit_id,
    'approved'
FROM pull_requests pr
JOIN repository_users u
    ON u.username = 'alice'
WHERE pr.title = 'Implement payment retry';

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    commit_id,
    review_state
)
SELECT
    pr.pull_request_id,
    u.user_id,
    pr.head_commit_id,
    'approved'
FROM pull_requests pr
JOIN repository_users u
    ON u.username = 'david'
WHERE pr.title = 'Implement payment retry';

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    commit_id,
    review_state
)
SELECT
    pr.pull_request_id,
    u.user_id,
    'c100',
    'approved'
FROM pull_requests pr
JOIN repository_users u
    ON u.username = 'alice'
WHERE pr.title = 'Add audit logging';

INSERT INTO review_comments (
    review_id,
    file_path,
    line_number,
    body,
    is_resolved
)
SELECT
    review_id,
    'src/payment/retry.sql',
    42,
    'Retry policy needs an explicit maximum attempt count.',
    TRUE
FROM reviews
WHERE review_state = 'approved'
LIMIT 1;

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    status
)
SELECT
    pull_request_id,
    check_name,
    'passed'
FROM pull_requests
CROSS JOIN (
    VALUES ('unit-tests'), ('integration-tests'), ('security-scan')
) AS checks(check_name)
WHERE title = 'Implement payment retry';

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    status
)
SELECT
    pull_request_id,
    'unit-tests',
    'passed'
FROM pull_requests
WHERE title = 'Add audit logging';

CREATE OR REPLACE FUNCTION unresolved_conversation_count(
    p_pull_request_id BIGINT
)
RETURNS INTEGER
LANGUAGE SQL
STABLE
AS $$
    SELECT COUNT(*)::INTEGER
    FROM review_comments rc
    JOIN reviews r ON r.review_id = rc.review_id
    WHERE r.pull_request_id = p_pull_request_id
      AND rc.is_resolved = FALSE;
$$;

CREATE OR REPLACE FUNCTION merge_eligibility(
    p_pull_request_id BIGINT
)
RETURNS TABLE (
    pull_request_id BIGINT,
    eligible BOOLEAN,
    reason TEXT,
    valid_approvals BIGINT,
    failed_checks BIGINT,
    unresolved_comments INTEGER
)
LANGUAGE SQL
STABLE
AS $$
    WITH pr AS (
        SELECT
            p.*,
            b.branch_id AS target_branch_id
        FROM pull_requests p
        JOIN branches b ON b.branch_id = p.target_branch_id
        WHERE p.pull_request_id = p_pull_request_id
    ),
    policy AS (
        SELECT bp.*
        FROM branch_protection_policies bp
        JOIN pr ON pr.target_branch_id = bp.branch_id
    ),
    approvals AS (
        SELECT COUNT(*)::BIGINT AS count
        FROM reviews r
        JOIN reviewer_roles rr
          ON rr.user_id = r.reviewer_id
         AND rr.repository_id = (SELECT repository_id FROM pr)
         AND rr.role_name = 'maintainer'
        WHERE r.pull_request_id = p_pull_request_id
          AND r.review_state = 'approved'
          AND r.commit_id = (SELECT head_commit_id FROM pr)
    ),
    checks AS (
        SELECT COUNT(*)::BIGINT AS failed
        FROM status_checks sc
        WHERE sc.pull_request_id = p_pull_request_id
          AND sc.status <> 'passed'
    ),
    comments AS (
        SELECT unresolved_conversation_count(p_pull_request_id) AS count
    )
    SELECT
        pr.pull_request_id,
        (
            pr.state = 'open'
            AND NOT pr.has_conflicts
            AND pr.linear_history = policy.require_linear_history
                OR (
                    pr.state = 'open'
                    AND NOT pr.has_conflicts
                    AND (
                        NOT policy.require_linear_history
                        OR pr.linear_history
                    )
                )
        )
        AND approvals.count >= policy.required_reviews
        AND (
            NOT policy.require_status_checks
            OR checks.failed = 0
        )
        AND (
            NOT policy.require_conversation_resolution
            OR comments.count = 0
        ) AS eligible,
        CASE
            WHEN pr.state <> 'open'
                THEN 'Pull Request is not open'
            WHEN pr.has_conflicts
                THEN 'Merge conflicts must be resolved'
            WHEN policy.require_linear_history
                 AND NOT pr.linear_history
                THEN 'Linear history is required'
            WHEN approvals.count < policy.required_reviews
                THEN 'Required approvals are missing or stale'
            WHEN policy.require_status_checks
                 AND checks.failed > 0
                THEN 'Required status checks are not all passing'
            WHEN policy.require_conversation_resolution
                 AND comments.count > 0
                THEN 'Unresolved review conversations remain'
            ELSE 'Merge eligible'
        END,
        approvals.count,
        checks.failed,
        comments.count
    FROM pr, policy, approvals, checks, comments;
$$;

CREATE OR REPLACE FUNCTION prevent_direct_push()
RETURNS TRIGGER
LANGUAGE PLPGSQL
AS $$
DECLARE
    protected BOOLEAN;
BEGIN
    SELECT is_protected
    INTO protected
    FROM branches
    WHERE branch_id = NEW.target_branch_id;

    IF protected AND NEW.source_branch_id = NEW.target_branch_id THEN
        RAISE EXCEPTION
            'Direct changes to protected branches are not permitted.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prevent_direct_push
BEFORE INSERT OR UPDATE ON pull_requests
FOR EACH ROW
EXECUTE FUNCTION prevent_direct_push();

CREATE VIEW merge_eligibility_report AS
SELECT *
FROM pull_requests p
CROSS JOIN LATERAL merge_eligibility(p.pull_request_id);

-- Retrieval: complete Pull Request workflow state.
SELECT
    pr.pull_request_id,
    pr.title,
    source.branch_name AS source_branch,
    target.branch_name AS target_branch,
    pr.state,
    pr.head_commit_id,
    pr.has_conflicts
FROM pull_requests pr
JOIN branches source ON source.branch_id = pr.source_branch_id
JOIN branches target ON target.branch_id = pr.target_branch_id
ORDER BY pr.pull_request_id;

-- Review aggregation and approval validation.
SELECT
    pr.pull_request_id,
    pr.title,
    COUNT(r.review_id) FILTER (
        WHERE r.review_state = 'approved'
    ) AS all_approvals,
    COUNT(r.review_id) FILTER (
        WHERE r.review_state = 'approved'
          AND r.commit_id = pr.head_commit_id
    ) AS current_commit_approvals
FROM pull_requests pr
LEFT JOIN reviews r
    ON r.pull_request_id = pr.pull_request_id
GROUP BY pr.pull_request_id, pr.title
ORDER BY pr.pull_request_id;

-- Status-check reporting.
SELECT
    pr.pull_request_id,
    pr.title,
    COUNT(sc.status_check_id) AS checks,
    COUNT(sc.status_check_id) FILTER (
        WHERE sc.status = 'passed'
    ) AS passed_checks,
    COUNT(sc.status_check_id) FILTER (
        WHERE sc.status <> 'passed'
    ) AS blocking_checks
FROM pull_requests pr
LEFT JOIN status_checks sc
    ON sc.pull_request_id = pr.pull_request_id
GROUP BY pr.pull_request_id, pr.title
ORDER BY pr.pull_request_id;

-- Final merge-eligibility evaluation.
SELECT
    pull_request_id,
    eligible,
    reason,
    valid_approvals,
    failed_checks,
    unresolved_comments
FROM merge_eligibility_report
ORDER BY pull_request_id;

-- Transactional merge example. The eligibility row is locked before state change.
BEGIN;

SELECT *
FROM merge_eligibility(1)
FOR UPDATE;

UPDATE pull_requests
SET state = 'merged',
    merged_at = CURRENT_TIMESTAMP
WHERE pull_request_id = 1
  AND (SELECT eligible FROM merge_eligibility(1));

UPDATE branches b
SET head_commit = pr.head_commit_id
FROM pull_requests pr
WHERE pr.pull_request_id = 1
  AND b.branch_id = pr.target_branch_id
  AND pr.state = 'merged';

COMMIT;

-- Re-check the resulting repository state.
SELECT
    pr.pull_request_id,
    pr.title,
    pr.state,
    b.branch_name AS target_branch,
    b.head_commit
FROM pull_requests pr
JOIN branches b
    ON b.branch_id = pr.target_branch_id
WHERE pr.pull_request_id = 1;
