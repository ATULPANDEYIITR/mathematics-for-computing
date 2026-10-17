-- PostgreSQL 15+
-- Graph matching for repository review allocation.
-- The graph is stored relationally as reviewer, request, and eligibility edges.

BEGIN;

DROP VIEW IF EXISTS review_matching_candidates;
DROP TABLE IF EXISTS review_assignments;
DROP TABLE IF EXISTS reviewer_eligibility;
DROP TABLE IF EXISTS pull_requests;
DROP TABLE IF EXISTS reviewers;
DROP TABLE IF EXISTS repositories;

CREATE TABLE repositories (
    repository_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name text NOT NULL UNIQUE
);

CREATE TABLE reviewers (
    reviewer_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reviewer_name text NOT NULL UNIQUE,
    review_role text NOT NULL CHECK (
        review_role IN ('CODE_OWNER', 'SECURITY', 'GENERAL')
    ),
    active boolean NOT NULL DEFAULT true
);

CREATE TABLE pull_requests (
    pull_request_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id bigint NOT NULL REFERENCES repositories(repository_id),
    external_key text NOT NULL UNIQUE,
    target_branch text NOT NULL,
    state text NOT NULL CHECK (state IN ('OPEN', 'CLOSED', 'MERGED'))
);

-- An eligibility row is an edge in the bipartite graph.
CREATE TABLE reviewer_eligibility (
    reviewer_id bigint NOT NULL REFERENCES reviewers(reviewer_id),
    pull_request_id bigint NOT NULL REFERENCES pull_requests(pull_request_id),
    reason text NOT NULL,
    PRIMARY KEY (reviewer_id, pull_request_id)
);

-- This table stores a selected matching, not every possible eligible edge.
CREATE TABLE review_assignments (
    pull_request_id bigint PRIMARY KEY REFERENCES pull_requests(pull_request_id),
    reviewer_id bigint NOT NULL REFERENCES reviewers(reviewer_id),
    assigned_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (reviewer_id, pull_request_id)
);

CREATE INDEX idx_eligibility_request
    ON reviewer_eligibility (pull_request_id, reviewer_id);

CREATE INDEX idx_open_pull_requests
    ON pull_requests (state, repository_id)
    WHERE state = 'OPEN';

INSERT INTO repositories (repository_name)
VALUES ('payments'), ('identity'), ('platform');

INSERT INTO reviewers (reviewer_name, review_role)
VALUES
    ('Reviewer-A', 'SECURITY'),
    ('Reviewer-B', 'CODE_OWNER'),
    ('Reviewer-C', 'GENERAL'),
    ('Reviewer-D', 'GENERAL');

INSERT INTO pull_requests (
    repository_id, external_key, target_branch, state
)
SELECT r.repository_id, v.external_key, v.target_branch, 'OPEN'
FROM (
    VALUES
        ('payments', 'PR-601', 'main'),
        ('identity', 'PR-602', 'main'),
        ('payments', 'PR-603', 'release'),
        ('platform', 'PR-604', 'main')
) AS v(repository_name, external_key, target_branch)
JOIN repositories r USING (repository_name);

INSERT INTO reviewer_eligibility (reviewer_id, pull_request_id, reason)
SELECT rv.reviewer_id, pr.pull_request_id, v.reason
FROM (
    VALUES
        ('Reviewer-A', 'PR-601', 'Security expertise'),
        ('Reviewer-A', 'PR-602', 'Identity security'),
        ('Reviewer-B', 'PR-601', 'Payments code ownership'),
        ('Reviewer-B', 'PR-603', 'Release ownership'),
        ('Reviewer-C', 'PR-602', 'General review'),
        ('Reviewer-C', 'PR-601', 'Cross-team review'),
        ('Reviewer-D', 'PR-604', 'Platform expertise')
) AS v(reviewer_name, external_key, reason)
JOIN reviewers rv USING (reviewer_name)
JOIN pull_requests pr USING (external_key);

-- A candidate report lists active eligible reviewers for open requests.
-- Candidate rows are edges, not yet a matching: a reviewer can appear
-- against several requests until an allocation algorithm selects edges.
CREATE VIEW review_matching_candidates AS
SELECT
    pr.external_key,
    r.repository_name,
    pr.target_branch,
    rv.reviewer_name,
    rv.review_role,
    e.reason
FROM reviewer_eligibility e
JOIN reviewers rv USING (reviewer_id)
JOIN pull_requests pr USING (pull_request_id)
JOIN repositories r USING (repository_id)
WHERE rv.active
  AND pr.state = 'OPEN';

SELECT *
FROM review_matching_candidates
ORDER BY external_key, reviewer_name;

-- Greedy allocation is useful for a quick feasible matching, but it does
-- not guarantee maximum cardinality. Exact maximum matching requires an
-- augmenting-path or equivalent graph algorithm in an application/service.
-- This deterministic query chooses at most one eligible reviewer per PR
-- and at most one PR per reviewer, but can leave feasible assignments unused.
WITH ranked_edges AS (
    SELECT
        e.reviewer_id,
        e.pull_request_id,
        row_number() OVER (
            PARTITION BY e.pull_request_id
            ORDER BY e.reviewer_id
        ) AS request_rank
    FROM reviewer_eligibility e
    JOIN reviewers rv USING (reviewer_id)
    JOIN pull_requests pr USING (pull_request_id)
    WHERE rv.active AND pr.state = 'OPEN'
),
greedy_edges AS (
    SELECT reviewer_id, pull_request_id
    FROM ranked_edges
    WHERE request_rank = 1
),
deduplicated AS (
    SELECT
        reviewer_id,
        pull_request_id,
        row_number() OVER (
            PARTITION BY reviewer_id
            ORDER BY pull_request_id
        ) AS reviewer_rank
    FROM greedy_edges
)
INSERT INTO review_assignments (reviewer_id, pull_request_id)
SELECT reviewer_id, pull_request_id
FROM deduplicated
WHERE reviewer_rank = 1
ON CONFLICT DO NOTHING;

-- The assignment table's primary key and foreign keys enforce uniqueness
-- and referential integrity, but cannot by themselves prove maximality.
SELECT
    rv.reviewer_name,
    pr.external_key,
    r.repository_name,
    pr.target_branch
FROM review_assignments a
JOIN reviewers rv USING (reviewer_id)
JOIN pull_requests pr USING (pull_request_id)
JOIN repositories r USING (repository_id)
ORDER BY pr.external_key;

-- Diagnose open requests that have no assigned reviewer.
SELECT pr.external_key, r.repository_name
FROM pull_requests pr
JOIN repositories r USING (repository_id)
LEFT JOIN review_assignments a USING (pull_request_id)
WHERE pr.state = 'OPEN'
  AND a.pull_request_id IS NULL
ORDER BY pr.external_key;

-- Diagnose active reviewers who have eligible requests but no assignment.
SELECT rv.reviewer_name
FROM reviewers rv
WHERE rv.active
  AND EXISTS (
      SELECT 1
      FROM reviewer_eligibility e
      JOIN pull_requests pr USING (pull_request_id)
      WHERE e.reviewer_id = rv.reviewer_id
        AND pr.state = 'OPEN'
  )
  AND NOT EXISTS (
      SELECT 1
      FROM review_assignments a
      WHERE a.reviewer_id = rv.reviewer_id
  )
ORDER BY rv.reviewer_name;

ROLLBACK;
