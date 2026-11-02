DROP SCHEMA IF EXISTS bayes_repository_governance CASCADE;
CREATE SCHEMA bayes_repository_governance;
SET search_path = bayes_repository_governance, public;

CREATE TYPE pull_request_state AS ENUM
    ('draft', 'open', 'closed', 'merged');

CREATE TYPE review_state AS ENUM
    ('commented', 'changes_requested', 'approved', 'dismissed');

CREATE TYPE check_state AS ENUM
    ('pass', 'fail', 'pending');

CREATE TYPE merge_strategy AS ENUM
    ('merge_commit', 'squash', 'rebase');

CREATE TABLE repository (
    repository_id BIGSERIAL PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (length(trim(repository_name)) > 0)
);

CREATE TABLE repository_member (
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    username TEXT NOT NULL,
    role TEXT NOT NULL,
    PRIMARY KEY (repository_id, username),
    CHECK (role IN ('admin', 'maintainer', 'developer', 'reviewer'))
);

CREATE TABLE branch (
    branch_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    protected BOOLEAN NOT NULL DEFAULT false,
    UNIQUE (repository_id, branch_name),
    CHECK (length(trim(branch_name)) > 0)
);

CREATE TABLE commit_record (
    commit_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    sha TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, sha),
    CHECK (length(sha) BETWEEN 4 AND 64),
    CHECK (length(trim(message)) > 0)
);

CREATE TABLE pull_request (
    pull_request_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id)
        ON DELETE CASCADE,
    number INTEGER NOT NULL,
    source_branch_id BIGINT NOT NULL REFERENCES branch(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branch(branch_id),
    state pull_request_state NOT NULL DEFAULT 'draft',
    head_commit_id BIGINT REFERENCES commit_record(commit_id),
    base_commit_id BIGINT REFERENCES commit_record(commit_id),
    merge_strategy merge_strategy NOT NULL DEFAULT 'squash',
    open_conversations INTEGER NOT NULL DEFAULT 0,
    force_push_requested BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, number),
    CHECK (source_branch_id <> target_branch_id),
    CHECK (open_conversations >= 0)
);

CREATE TABLE pull_request_commit (
    pull_request_id BIGINT NOT NULL REFERENCES pull_request(pull_request_id)
        ON DELETE CASCADE,
    commit_id BIGINT NOT NULL REFERENCES commit_record(commit_id),
    sequence_number INTEGER NOT NULL,
    PRIMARY KEY (pull_request_id, commit_id),
    UNIQUE (pull_request_id, sequence_number),
    CHECK (sequence_number > 0)
);

CREATE TABLE review (
    review_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_request(pull_request_id)
        ON DELETE CASCADE,
    reviewer_username TEXT NOT NULL,
    state review_state NOT NULL,
    commit_id BIGINT REFERENCES commit_record(commit_id),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE review_comment (
    comment_id BIGSERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES review(review_id)
        ON DELETE CASCADE,
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (length(trim(body)) > 0)
);

CREATE TABLE status_check (
    status_check_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_request(pull_request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    state check_state NOT NULL,
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, check_name)
);

CREATE TABLE branch_protection (
    branch_id BIGINT PRIMARY KEY REFERENCES branch(branch_id)
        ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 0,
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT false,
    require_linear_history BOOLEAN NOT NULL DEFAULT false,
    allow_direct_push BOOLEAN NOT NULL DEFAULT false,
    allow_force_push BOOLEAN NOT NULL DEFAULT false,
    bayes_prior_safe NUMERIC(8,7) NOT NULL DEFAULT 0.8500000,
    bayes_threshold NUMERIC(8,7) NOT NULL DEFAULT 0.9000000,
    CHECK (required_approvals >= 0),
    CHECK (bayes_prior_safe > 0 AND bayes_prior_safe < 1),
    CHECK (bayes_threshold > 0 AND bayes_threshold < 1)
);

CREATE TABLE required_status_check (
    branch_id BIGINT NOT NULL REFERENCES branch_protection(branch_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    PRIMARY KEY (branch_id, check_name),
    CHECK (length(trim(check_name)) > 0)
);

CREATE TABLE bayes_evidence (
    evidence_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_request(pull_request_id)
        ON DELETE CASCADE,
    evidence_name TEXT NOT NULL,
    likelihood_safe NUMERIC(12,10) NOT NULL,
    likelihood_unsafe NUMERIC(12,10) NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (likelihood_safe > 0 AND likelihood_safe <= 1),
    CHECK (likelihood_unsafe > 0 AND likelihood_unsafe <= 1)
);

CREATE INDEX idx_pr_target_state
    ON pull_request(target_branch_id, state);

CREATE INDEX idx_review_pr_commit_state
    ON review(pull_request_id, commit_id, state);

CREATE INDEX idx_status_check_pr_state
    ON status_check(pull_request_id, state);

CREATE INDEX idx_pr_commit_sequence
    ON pull_request_commit(pull_request_id, sequence_number);

CREATE OR REPLACE FUNCTION validate_pull_request_commit()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    pr_repo BIGINT;
    commit_repo BIGINT;
BEGIN
    SELECT repository_id
    INTO pr_repo
    FROM pull_request
    WHERE pull_request_id = NEW.pull_request_id;

    SELECT repository_id
    INTO commit_repo
    FROM commit_record
    WHERE commit_id = NEW.commit_id;

    IF pr_repo IS NULL OR commit_repo IS NULL OR pr_repo <> commit_repo THEN
        RAISE EXCEPTION
            'Pull Request and commit must belong to the same repository';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_pr_commit
BEFORE INSERT OR UPDATE ON pull_request_commit
FOR EACH ROW
EXECUTE FUNCTION validate_pull_request_commit();

CREATE OR REPLACE FUNCTION bayes_posterior(
    prior_safe NUMERIC,
    evidence_safe NUMERIC,
    evidence_unsafe NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    safe_weight NUMERIC;
    unsafe_weight NUMERIC;
BEGIN
    IF prior_safe <= 0 OR prior_safe >= 1 THEN
        RAISE EXCEPTION 'Prior must be between zero and one';
    END IF;

    IF evidence_safe <= 0 OR evidence_safe > 1
       OR evidence_unsafe <= 0 OR evidence_unsafe > 1 THEN
        RAISE EXCEPTION 'Likelihoods must be in (0, 1]';
    END IF;

    safe_weight := prior_safe * evidence_safe;
    unsafe_weight := (1 - prior_safe) * evidence_unsafe;

    RETURN safe_weight / NULLIF(safe_weight + unsafe_weight, 0);
END;
$$;

CREATE OR REPLACE FUNCTION refresh_head_commit()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    latest_commit BIGINT;
BEGIN
    SELECT commit_id
    INTO latest_commit
    FROM pull_request_commit
    WHERE pull_request_id = NEW.pull_request_id
    ORDER BY sequence_number DESC
    LIMIT 1;

    UPDATE pull_request
    SET head_commit_id = latest_commit
    WHERE pull_request_id = NEW.pull_request_id;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_refresh_head_commit
AFTER INSERT OR UPDATE OR DELETE ON pull_request_commit
FOR EACH ROW
EXECUTE FUNCTION refresh_head_commit();

INSERT INTO repository(repository_name)
VALUES ('payments-service');

INSERT INTO repository_member(repository_id, username, role)
SELECT repository_id, username, role
FROM (
    VALUES
        ('alice', 'reviewer'),
        ('bob', 'reviewer'),
        ('carol', 'developer'),
        ('diana', 'maintainer')
) AS members(username, role)
CROSS JOIN repository
WHERE repository_name = 'payments-service';

INSERT INTO branch(repository_id, branch_name, protected)
SELECT repository_id, branch_name, protected
FROM (
    VALUES
        ('main', true),
        ('feature/payment-validation', false)
) AS branches(branch_name, protected)
CROSS JOIN repository
WHERE repository_name = 'payments-service';

INSERT INTO branch_protection (
    branch_id,
    required_approvals,
    require_conversation_resolution,
    require_linear_history,
    allow_direct_push,
    allow_force_push,
    bayes_prior_safe,
    bayes_threshold
)
SELECT
    branch_id,
    2,
    true,
    true,
    false,
    false,
    0.8500000,
    0.9000000
FROM branch
WHERE branch_name = 'main';

INSERT INTO required_status_check(branch_id, check_name)
SELECT branch_id, check_name
FROM branch_protection
CROSS JOIN (
    VALUES ('unit-tests'), ('security-scan')
) AS checks(check_name);

INSERT INTO commit_record(repository_id, sha, message)
SELECT repository_id, sha, message
FROM repository
CROSS JOIN (
    VALUES
        ('a100', 'Add payment validation'),
        ('a101', 'Fix boundary validation'),
        ('m500', 'Current main branch')
) AS commits(sha, message)
WHERE repository_name = 'payments-service';

INSERT INTO pull_request (
    repository_id,
    number,
    source_branch_id,
    target_branch_id,
    state,
    head_commit_id,
    base_commit_id,
    merge_strategy,
    open_conversations
)
SELECT
    r.repository_id,
    42,
    source.branch_id,
    target.branch_id,
    'open',
    head.commit_id,
    base.commit_id,
    'squash',
    0
FROM repository r
JOIN branch source
    ON source.repository_id = r.repository_id
   AND source.branch_name = 'feature/payment-validation'
JOIN branch target
    ON target.repository_id = r.repository_id
   AND target.branch_name = 'main'
JOIN commit_record head
    ON head.repository_id = r.repository_id
   AND head.sha = 'a101'
JOIN commit_record base
    ON base.repository_id = r.repository_id
   AND base.sha = 'm500'
WHERE r.repository_name = 'payments-service';

INSERT INTO pull_request_commit(pull_request_id, commit_id, sequence_number)
SELECT pr.pull_request_id, c.commit_id, v.sequence_number
FROM pull_request pr
JOIN repository r ON r.repository_id = pr.repository_id
JOIN (
    VALUES
        ('a100', 1),
        ('a101', 2)
) AS v(sha, sequence_number) ON true
JOIN commit_record c
    ON c.repository_id = r.repository_id
   AND c.sha = v.sha
WHERE r.repository_name = 'payments-service'
  AND pr.number = 42;

INSERT INTO review(
    pull_request_id,
    reviewer_username,
    state,
    commit_id
)
SELECT
    pr.pull_request_id,
    v.reviewer,
    v.state::review_state,
    c.commit_id
FROM pull_request pr
JOIN repository r ON r.repository_id = pr.repository_id
CROSS JOIN (
    VALUES
        ('alice', 'approved', 'a101'),
        ('bob', 'approved', 'a101'),
        ('carol', 'commented', 'a101')
) AS v(reviewer, state, sha)
JOIN commit_record c
    ON c.repository_id = r.repository_id
   AND c.sha = v.sha
WHERE r.repository_name = 'payments-service'
  AND pr.number = 42;

INSERT INTO review_comment(review_id, body, resolved)
SELECT review_id, 'Validate the maximum transaction amount.', true
FROM review
WHERE reviewer_username = 'carol'
  AND pull_request_id = (
      SELECT pull_request_id
      FROM pull_request
      WHERE number = 42
  );

INSERT INTO status_check(
    pull_request_id,
    check_name,
    state,
    completed_at
)
SELECT
    pr.pull_request_id,
    v.check_name,
    v.state::check_state,
    CASE WHEN v.state = 'pass' THEN now() ELSE NULL END
FROM pull_request pr
CROSS JOIN (
    VALUES
        ('unit-tests', 'pass'),
        ('security-scan', 'pass'),
        ('integration-tests', 'pass')
) AS v(check_name, state)
WHERE pr.number = 42;

INSERT INTO bayes_evidence(
    pull_request_id,
    evidence_name,
    likelihood_safe,
    likelihood_unsafe
)
SELECT
    pull_request_id,
    evidence_name,
    likelihood_safe,
    likelihood_unsafe
FROM pull_request
CROSS JOIN (
    VALUES
        ('current-head-approval', 0.92, 0.08),
        ('required-status-checks', 0.97, 0.03),
        ('failed-checks', 0.98, 0.02),
        ('pending-checks', 0.94, 0.06),
        ('resolved-conversations', 0.96, 0.04),
        ('requested-changes', 0.95, 0.05)
) AS e(evidence_name, likelihood_safe, likelihood_unsafe)
WHERE number = 42;

CREATE OR REPLACE VIEW pull_request_governance_report AS
WITH approval_counts AS (
    SELECT
        pr.pull_request_id,
        count(DISTINCT r.reviewer_username)
            FILTER (
                WHERE r.state = 'approved'
                  AND r.commit_id = pr.head_commit_id
            ) AS current_approvals
    FROM pull_request pr
    LEFT JOIN review r
        ON r.pull_request_id = pr.pull_request_id
    GROUP BY pr.pull_request_id
),
check_status AS (
    SELECT
        pr.pull_request_id,
        bool_and(sc.state = 'pass') AS all_checks_pass,
        bool_or(sc.state = 'fail') AS has_failed_check,
        bool_or(sc.state = 'pending') AS has_pending_check
    FROM pull_request pr
    LEFT JOIN status_check sc
        ON sc.pull_request_id = pr.pull_request_id
    GROUP BY pr.pull_request_id
),
bayes AS (
    SELECT
        pr.pull_request_id,
        bp.bayes_threshold,
        bp.bayes_prior_safe,
        exp(
            sum(
                ln(
                    CASE
                        WHEN be.likelihood_safe > 0
                        THEN be.likelihood_safe
                        ELSE 0.0000001
                    END
                )
            )
        ) * bp.bayes_prior_safe AS safe_weight,
        exp(
            sum(
                ln(
                    CASE
                        WHEN be.likelihood_unsafe > 0
                        THEN be.likelihood_unsafe
                        ELSE 0.0000001
                    END
                )
            )
        ) * (1 - bp.bayes_prior_safe) AS unsafe_weight
    FROM pull_request pr
    JOIN branch_protection bp
        ON bp.branch_id = pr.target_branch_id
    JOIN bayes_evidence be
        ON be.pull_request_id = pr.pull_request_id
    GROUP BY
        pr.pull_request_id,
        bp.bayes_threshold,
        bp.bayes_prior_safe
)
SELECT
    r.repository_name,
    pr.number AS pull_request_number,
    source.branch_name AS source_branch,
    target.branch_name AS target_branch,
    pr.state,
    ac.current_approvals,
    bp.required_approvals,
    cs.all_checks_pass,
    cs.has_failed_check,
    cs.has_pending_check,
    pr.open_conversations,
    bp.require_conversation_resolution,
    pr.merge_strategy,
    bp.require_linear_history,
    CASE
        WHEN bayes.safe_weight + bayes.unsafe_weight = 0
        THEN 0
        ELSE bayes.safe_weight /
             (bayes.safe_weight + bayes.unsafe_weight)
    END AS posterior_merge_safety,
    bayes.bayes_threshold,
    (
        pr.state = 'open'
        AND ac.current_approvals >= bp.required_approvals
        AND cs.all_checks_pass
        AND NOT cs.has_failed_check
        AND NOT cs.has_pending_check
        AND (
            NOT bp.require_conversation_resolution
            OR pr.open_conversations = 0
        )
        AND (
            NOT bp.require_linear_history
            OR pr.merge_strategy <> 'merge_commit'
        )
        AND (
            CASE
                WHEN bayes.safe_weight + bayes.unsafe_weight = 0
                THEN 0
                ELSE bayes.safe_weight /
                     (bayes.safe_weight + bayes.unsafe_weight)
            END
        ) >= bayes.bayes_threshold
    ) AS merge_eligible
FROM pull_request pr
JOIN repository r
    ON r.repository_id = pr.repository_id
JOIN branch source
    ON source.branch_id = pr.source_branch_id
JOIN branch target
    ON target.branch_id = pr.target_branch_id
JOIN branch_protection bp
    ON bp.branch_id = target.branch_id
JOIN approval_counts ac
    ON ac.pull_request_id = pr.pull_request_id
JOIN check_status cs
    ON cs.pull_request_id = pr.pull_request_id
JOIN bayes
    ON bayes.pull_request_id = pr.pull_request_id;

-- Retrieval and governance reporting.
SELECT *
FROM pull_request_governance_report
ORDER BY pull_request_number;

-- Approval validation at the current Pull Request head.
SELECT
    pr.number,
    COUNT(DISTINCT r.reviewer_username) AS current_head_approvals,
    bp.required_approvals,
    COUNT(DISTINCT r.reviewer_username) >= bp.required_approvals
        AS approval_requirement_satisfied
FROM pull_request pr
JOIN review r
    ON r.pull_request_id = pr.pull_request_id
   AND r.commit_id = pr.head_commit_id
   AND r.state = 'approved'
JOIN branch_protection bp
    ON bp.branch_id = pr.target_branch_id
WHERE pr.number = 42
GROUP BY pr.number, bp.required_approvals;

-- Status-check evaluation.
SELECT
    pr.number,
    sc.check_name,
    sc.state,
    required_status_check.check_name IS NOT NULL AS required_check
FROM pull_request pr
JOIN status_check sc
    ON sc.pull_request_id = pr.pull_request_id
LEFT JOIN required_status_check
    ON required_status_check.branch_id = pr.target_branch_id
   AND required_status_check.check_name = sc.check_name
WHERE pr.number = 42
ORDER BY sc.check_name;

-- Bayesian posterior from multiple independent evidence observations.
WITH weights AS (
    SELECT
        pr.pull_request_id,
        bp.bayes_prior_safe,
        bp.bayes_threshold,
        bp.bayes_prior_safe *
            exp(sum(ln(be.likelihood_safe))) AS safe_weight,
        (1 - bp.bayes_prior_safe) *
            exp(sum(ln(be.likelihood_unsafe))) AS unsafe_weight
    FROM pull_request pr
    JOIN branch_protection bp
        ON bp.branch_id = pr.target_branch_id
    JOIN bayes_evidence be
        ON be.pull_request_id = pr.pull_request_id
    WHERE pr.number = 42
    GROUP BY
        pr.pull_request_id,
        bp.bayes_prior_safe,
        bp.bayes_threshold
)
SELECT
    pull_request_id,
    safe_weight / NULLIF(safe_weight + unsafe_weight, 0)
        AS posterior_probability,
    bayes_threshold,
    safe_weight / NULLIF(safe_weight + unsafe_weight, 0)
        >= bayes_threshold AS probability_gate_passed
FROM weights;

-- Failure analysis: open conversations, failed checks, and requested changes.
SELECT
    pr.number,
    pr.open_conversations,
    COUNT(*) FILTER (
        WHERE sc.state = 'fail'
    ) AS failed_checks,
    COUNT(*) FILTER (
        WHERE r.state = 'changes_requested'
          AND r.commit_id = pr.head_commit_id
    ) AS current_head_change_requests
FROM pull_request pr
LEFT JOIN status_check sc
    ON sc.pull_request_id = pr.pull_request_id
LEFT JOIN review r
    ON r.pull_request_id = pr.pull_request_id
WHERE pr.number = 42
GROUP BY pr.number, pr.open_conversations;

-- Transactional governance update: resolving a conversation and recording
-- the resulting state as one atomic operation.
BEGIN;

UPDATE pull_request
SET open_conversations = 0
WHERE number = 42;

INSERT INTO bayes_evidence(
    pull_request_id,
    evidence_name,
    likelihood_safe,
    likelihood_unsafe
)
SELECT
    pull_request_id,
    'post-resolution-conversation-state',
    0.96,
    0.04
FROM pull_request
WHERE number = 42;

COMMIT;

-- Re-read final eligibility after the transaction.
SELECT
    pull_request_number,
    posterior_merge_safety,
    bayes_threshold,
    merge_eligible
FROM pull_request_governance_report
WHERE pull_request_number = 42;

-- Demonstrate the stale-approval condition without corrupting the main
-- demonstration data by using a transaction that is rolled back.
BEGIN;

INSERT INTO commit_record(repository_id, sha, message)
SELECT repository_id, 'a102', 'Address reviewer findings'
FROM repository
WHERE repository_name = 'payments-service';

INSERT INTO pull_request_commit(
    pull_request_id,
    commit_id,
    sequence_number
)
SELECT
    pr.pull_request_id,
    c.commit_id,
    3
FROM pull_request pr
JOIN commit_record c
    ON c.repository_id = pr.repository_id
   AND c.sha = 'a102'
WHERE pr.number = 42;

UPDATE pull_request
SET head_commit_id = (
    SELECT commit_id
    FROM commit_record
    WHERE sha = 'a102'
      AND repository_id = pull_request.repository_id
)
WHERE number = 42;

-- Existing approvals point to a101 and are therefore stale.
SELECT
    pr.number,
    pr.head_commit_id,
    COUNT(r.review_id) FILTER (
        WHERE r.state = 'approved'
          AND r.commit_id = pr.head_commit_id
    ) AS current_head_approvals
FROM pull_request pr
LEFT JOIN review r
    ON r.pull_request_id = pr.pull_request_id
WHERE pr.number = 42
GROUP BY pr.number, pr.head_commit_id;

ROLLBACK;

-- A compact audit query suitable for operational reporting.
SELECT
    repository_name,
    pull_request_number,
    source_branch,
    target_branch,
    current_approvals,
    required_approvals,
    posterior_merge_safety,
    bayes_threshold,
    merge_eligible
FROM pull_request_governance_report;
