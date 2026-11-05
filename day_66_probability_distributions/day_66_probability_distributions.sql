-- ============================================================
-- PROBABILITY DISTRIBUTIONS
-- Bernoulli, Binomial, Geometric, Negative Binomial
--
-- PostgreSQL 15+
--
-- Domain: Transaction reliability and operational analytics.
-- Includes:
--   1. Distribution metadata
--   2. Experiment configuration
--   3. Trial-level observations
--   4. Parameter validation
--   5. Probability calculation functions
--   6. Statistical reporting
--   7. Experiment evaluation
--   8. Transaction-safe sample processing
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS probability_lab;

SET search_path TO probability_lab, public;

-- ------------------------------------------------------------
-- 1. Distribution definitions
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS distribution_types (
    distribution_code VARCHAR(30) PRIMARY KEY,
    distribution_name VARCHAR(80) NOT NULL UNIQUE,
    support_description VARCHAR(150) NOT NULL,
    parameter_description TEXT NOT NULL
);

INSERT INTO distribution_types (
    distribution_code,
    distribution_name,
    support_description,
    parameter_description
)
VALUES
(
    'BERNOULLI',
    'Bernoulli Distribution',
    '0 or 1',
    'p: probability of success'
),
(
    'BINOMIAL',
    'Binomial Distribution',
    '0 through n',
    'n: number of trials; p: success probability'
),
(
    'GEOMETRIC',
    'Geometric Distribution',
    '1, 2, 3, ...',
    'p: probability of first success on each trial'
),
(
    'NEGATIVE_BINOMIAL',
    'Negative Binomial Distribution',
    'r, r+1, r+2, ...',
    'r: required successes; p: success probability'
)
ON CONFLICT (distribution_code) DO NOTHING;


-- ------------------------------------------------------------
-- 2. Experiment management
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_name VARCHAR(150) NOT NULL,

    distribution_code VARCHAR(30) NOT NULL
        REFERENCES distribution_types(distribution_code),

    success_probability NUMERIC(12, 10) NOT NULL,

    trial_count INTEGER,

    required_successes INTEGER,

    sample_size INTEGER NOT NULL DEFAULT 1000,

    experiment_status VARCHAR(20) NOT NULL DEFAULT 'CREATED',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMPTZ,

    CONSTRAINT valid_probability
        CHECK (
            success_probability >= 0
            AND success_probability <= 1
        ),

    CONSTRAINT valid_trial_count
        CHECK (trial_count IS NULL OR trial_count >= 0),

    CONSTRAINT valid_required_successes
        CHECK (
            required_successes IS NULL
            OR required_successes >= 1
        ),

    CONSTRAINT valid_sample_size
        CHECK (sample_size > 0),

    CONSTRAINT valid_experiment_status
        CHECK (
            experiment_status IN (
                'CREATED',
                'RUNNING',
                'COMPLETED',
                'FAILED'
            )
        ),

    CONSTRAINT valid_distribution_parameters
        CHECK (
            (
                distribution_code = 'BERNOULLI'
                AND trial_count IS NULL
                AND required_successes IS NULL
            )
            OR
            (
                distribution_code = 'BINOMIAL'
                AND trial_count IS NOT NULL
                AND required_successes IS NULL
            )
            OR
            (
                distribution_code = 'GEOMETRIC'
                AND trial_count IS NULL
                AND required_successes IS NULL
            )
            OR
            (
                distribution_code = 'NEGATIVE_BINOMIAL'
                AND trial_count IS NULL
                AND required_successes IS NOT NULL
            )
        )
);


-- ------------------------------------------------------------
-- 3. Trial observations
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,

    outcome INTEGER NOT NULL,

    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_observations_experiment
    ON observations(experiment_id);

CREATE INDEX IF NOT EXISTS idx_observations_outcome
    ON observations(experiment_id, outcome);

CREATE INDEX IF NOT EXISTS idx_experiments_status
    ON experiments(experiment_status, created_at);


-- ------------------------------------------------------------
-- 4. Experiment parameter validation
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_experiment_parameters()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.distribution_code = 'BERNOULLI'
       AND NEW.success_probability NOT IN (0, 1)
       AND NEW.sample_size < 1 THEN

        RAISE EXCEPTION 'Invalid Bernoulli experiment parameters.';
    END IF;

    IF NEW.distribution_code = 'BINOMIAL'
       AND NEW.trial_count IS NULL THEN

        RAISE EXCEPTION 'Binomial distribution requires n.';
    END IF;

    IF NEW.distribution_code = 'NEGATIVE_BINOMIAL'
       AND NEW.required_successes IS NULL THEN

        RAISE EXCEPTION
            'Negative binomial distribution requires r.';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_experiment
    ON experiments;

CREATE TRIGGER trg_validate_experiment
BEFORE INSERT OR UPDATE ON experiments
FOR EACH ROW
EXECUTE FUNCTION validate_experiment_parameters();


-- ------------------------------------------------------------
-- 5. Logarithmic combination calculation
--
-- log(C(n,k)) avoids directly constructing very large
-- factorial values.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION log_combination(
    p_n INTEGER,
    p_k INTEGER
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_k INTEGER;
    v_result DOUBLE PRECISION := 0;
    i INTEGER;
BEGIN
    IF p_n < 0 OR p_k < 0 OR p_k > p_n THEN
        RETURN '-Infinity'::DOUBLE PRECISION;
    END IF;

    v_k := LEAST(p_k, p_n - p_k);

    FOR i IN 1..v_k LOOP
        v_result := v_result
            + LN((p_n - v_k + i)::DOUBLE PRECISION)
            - LN(i::DOUBLE PRECISION);
    END LOOP;

    RETURN v_result;
END;
$$;


-- ------------------------------------------------------------
-- 6. Bernoulli PMF
--
-- P(X=x) = p^x * (1-p)^(1-x)
-- x is either 0 or 1.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bernoulli_pmf(
    p_probability DOUBLE PRECISION,
    p_outcome INTEGER
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    IF p_probability IS NULL
       OR p_probability < 0
       OR p_probability > 1 THEN

        RAISE EXCEPTION 'Invalid probability.';
    END IF;

    IF p_outcome = 1 THEN
        RETURN p_probability;
    ELSIF p_outcome = 0 THEN
        RETURN 1 - p_probability;
    END IF;

    RETURN 0;
END;
$$;


-- ------------------------------------------------------------
-- 7. Binomial PMF
--
-- P(X=k) = C(n,k) * p^k * (1-p)^(n-k)
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION binomial_pmf(
    p_n INTEGER,
    p_probability DOUBLE PRECISION,
    p_k INTEGER
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_log_result DOUBLE PRECISION;
BEGIN
    IF p_n IS NULL OR p_n < 0 THEN
        RAISE EXCEPTION 'n must be non-negative.';
    END IF;

    IF p_probability IS NULL
       OR p_probability < 0
       OR p_probability > 1 THEN

        RAISE EXCEPTION 'Invalid probability.';
    END IF;

    IF p_k < 0 OR p_k > p_n THEN
        RETURN 0;
    END IF;

    IF p_probability = 0 THEN
        RETURN CASE WHEN p_k = 0 THEN 1 ELSE 0 END;
    END IF;

    IF p_probability = 1 THEN
        RETURN CASE WHEN p_k = p_n THEN 1 ELSE 0 END;
    END IF;

    v_log_result :=
        log_combination(p_n, p_k)
        + p_k * LN(p_probability)
        + (p_n - p_k) * LN(1 - p_probability);

    RETURN EXP(v_log_result);
END;
$$;


-- ------------------------------------------------------------
-- 8. Geometric PMF
--
-- P(X=k) = (1-p)^(k-1) * p
--
-- X counts trials through the first success.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION geometric_pmf(
    p_probability DOUBLE PRECISION,
    p_k INTEGER
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    IF p_probability IS NULL
       OR p_probability < 0
       OR p_probability > 1 THEN

        RAISE EXCEPTION 'Invalid probability.';
    END IF;

    IF p_k < 1 OR p_probability = 0 THEN
        RETURN 0;
    END IF;

    IF p_probability = 1 THEN
        RETURN CASE WHEN p_k = 1 THEN 1 ELSE 0 END;
    END IF;

    RETURN EXP(
        (p_k - 1) * LN(1 - p_probability)
        + LN(p_probability)
    );
END;
$$;


-- ------------------------------------------------------------
-- 9. Geometric CDF
--
-- P(X <= k) = 1 - (1-p)^k
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION geometric_cdf(
    p_probability DOUBLE PRECISION,
    p_k INTEGER
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    IF p_probability IS NULL
       OR p_probability < 0
       OR p_probability > 1 THEN

        RAISE EXCEPTION 'Invalid probability.';
    END IF;

    IF p_k < 1 OR p_probability = 0 THEN
        RETURN 0;
    END IF;

    IF p_probability = 1 THEN
        RETURN 1;
    END IF;

    RETURN 1 - EXP(p_k * LN(1 - p_probability));
END;
$$;


-- ------------------------------------------------------------
-- 10. Negative binomial PMF
--
-- P(X=k) = C(k-1,r-1) * p^r * (1-p)^(k-r)
--
-- X counts trials required for r successes.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION negative_binomial_pmf(
    p_r INTEGER,
    p_probability DOUBLE PRECISION,
    p_k INTEGER
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_log_result DOUBLE PRECISION;
BEGIN
    IF p_r IS NULL OR p_r < 1 THEN
        RAISE EXCEPTION 'r must be at least 1.';
    END IF;

    IF p_probability IS NULL
       OR p_probability < 0
       OR p_probability > 1 THEN

        RAISE EXCEPTION 'Invalid probability.';
    END IF;

    IF p_k < p_r OR p_probability = 0 THEN
        RETURN 0;
    END IF;

    IF p_probability = 1 THEN
        RETURN CASE WHEN p_k = p_r THEN 1 ELSE 0 END;
    END IF;

    v_log_result :=
        log_combination(p_k - 1, p_r - 1)
        + p_r * LN(p_probability)
        + (p_k - p_r) * LN(1 - p_probability);

    RETURN EXP(v_log_result);
END;
$$;


-- ------------------------------------------------------------
-- 11. Negative binomial CDF
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION negative_binomial_cdf(
    p_r INTEGER,
    p_probability DOUBLE PRECISION,
    p_k INTEGER
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_total DOUBLE PRECISION := 0;
    i INTEGER;
BEGIN
    IF p_r IS NULL OR p_r < 1 THEN
        RAISE EXCEPTION 'r must be at least 1.';
    END IF;

    IF p_probability IS NULL
       OR p_probability < 0
       OR p_probability > 1 THEN

        RAISE EXCEPTION 'Invalid probability.';
    END IF;

    IF p_k < p_r OR p_probability = 0 THEN
        RETURN 0;
    END IF;

    IF p_probability = 1 THEN
        RETURN 1;
    END IF;

    FOR i IN p_r..p_k LOOP
        v_total := v_total
            + negative_binomial_pmf(p_r, p_probability, i);
    END LOOP;

    RETURN LEAST(1, v_total);
END;
$$;


-- ------------------------------------------------------------
-- 12. Theoretical statistics
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION distribution_statistics(
    p_distribution VARCHAR,
    p_probability DOUBLE PRECISION,
    p_n INTEGER DEFAULT NULL,
    p_r INTEGER DEFAULT NULL
)
RETURNS TABLE (
    theoretical_mean DOUBLE PRECISION,
    theoretical_variance DOUBLE PRECISION,
    standard_deviation DOUBLE PRECISION
)
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    IF p_probability IS NULL
       OR p_probability < 0
       OR p_probability > 1 THEN

        RAISE EXCEPTION 'Invalid probability.';
    END IF;

    CASE p_distribution

        WHEN 'BERNOULLI' THEN

            theoretical_mean := p_probability;
            theoretical_variance :=
                p_probability * (1 - p_probability);

        WHEN 'BINOMIAL' THEN

            IF p_n IS NULL OR p_n < 0 THEN
                RAISE EXCEPTION 'Valid n is required.';
            END IF;

            theoretical_mean := p_n * p_probability;
            theoretical_variance :=
                p_n * p_probability * (1 - p_probability);

        WHEN 'GEOMETRIC' THEN

            IF p_probability = 0 THEN
                theoretical_mean := 'Infinity'::DOUBLE PRECISION;
                theoretical_variance := 'Infinity'::DOUBLE PRECISION;
            ELSE
                theoretical_mean := 1 / p_probability;
                theoretical_variance :=
                    (1 - p_probability) / POWER(p_probability, 2);
            END IF;

        WHEN 'NEGATIVE_BINOMIAL' THEN

            IF p_r IS NULL OR p_r < 1 THEN
                RAISE EXCEPTION 'Valid r is required.';
            END IF;

            IF p_probability = 0 THEN
                theoretical_mean := 'Infinity'::DOUBLE PRECISION;
                theoretical_variance := 'Infinity'::DOUBLE PRECISION;
            ELSE
                theoretical_mean := p_r / p_probability;
                theoretical_variance :=
                    p_r * (1 - p_probability)
                    / POWER(p_probability, 2);
            END IF;

        ELSE
            RAISE EXCEPTION 'Unknown distribution: %',
                p_distribution;

    END CASE;

    standard_deviation := SQRT(theoretical_variance);

    RETURN NEXT;
END;
$$;


-- ------------------------------------------------------------
-- 13. Observation validation trigger
--
-- Enforces each distribution's support before observations
-- enter the database.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_observation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_experiment experiments%ROWTYPE;
BEGIN
    SELECT *
    INTO v_experiment
    FROM experiments
    WHERE experiment_id = NEW.experiment_id
    FOR KEY SHARE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Experiment does not exist.';
    END IF;

    IF v_experiment.experiment_status IN ('COMPLETED', 'FAILED') THEN
        RAISE EXCEPTION
            'Observations cannot be added to a finalized experiment.';
    END IF;

    IF v_experiment.distribution_code = 'BERNOULLI'
       AND NEW.outcome NOT IN (0, 1) THEN

        RAISE EXCEPTION 'Bernoulli outcome must be 0 or 1.';
    END IF;

    IF v_experiment.distribution_code = 'BINOMIAL'
       AND (
           NEW.outcome < 0
           OR NEW.outcome > v_experiment.trial_count
       ) THEN

        RAISE EXCEPTION 'Binomial outcome is outside its support.';
    END IF;

    IF v_experiment.distribution_code = 'GEOMETRIC'
       AND NEW.outcome < 1 THEN

        RAISE EXCEPTION 'Geometric outcome must be at least 1.';
    END IF;

    IF v_experiment.distribution_code = 'NEGATIVE_BINOMIAL'
       AND NEW.outcome < v_experiment.required_successes THEN

        RAISE EXCEPTION
            'Negative binomial outcome must be at least r.';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_observation
    ON observations;

CREATE TRIGGER trg_validate_observation
BEFORE INSERT OR UPDATE ON observations
FOR EACH ROW
EXECUTE FUNCTION validate_observation();


-- ------------------------------------------------------------
-- 14. Observation recording procedure
--
-- A complete batch is inserted within a single transaction.
-- An invalid observation rolls back the entire batch.
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE record_observations(
    p_experiment_id BIGINT,
    p_outcomes INTEGER[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_experiment experiments%ROWTYPE;
    v_outcome INTEGER;
    v_count INTEGER;
BEGIN
    SELECT *
    INTO v_experiment
    FROM experiments
    WHERE experiment_id = p_experiment_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Experiment not found.';
    END IF;

    IF v_experiment.experiment_status IN ('COMPLETED', 'FAILED') THEN
        RAISE EXCEPTION 'Experiment is already finalized.';
    END IF;

    IF p_outcomes IS NULL
       OR CARDINALITY(p_outcomes) = 0 THEN

        RAISE EXCEPTION 'Observation batch cannot be empty.';
    END IF;

    SELECT COUNT(*)
    INTO v_count
    FROM observations
    WHERE experiment_id = p_experiment_id;

    IF v_count + CARDINALITY(p_outcomes) >
       v_experiment.sample_size THEN

        RAISE EXCEPTION 'Sample size limit exceeded.';
    END IF;

    UPDATE experiments
    SET experiment_status = 'RUNNING'
    WHERE experiment_id = p_experiment_id;

    FOREACH v_outcome IN ARRAY p_outcomes LOOP

        INSERT INTO observations (
            experiment_id,
            outcome
        )
        VALUES (
            p_experiment_id,
            v_outcome
        );

    END LOOP;
END;
$$;


-- ------------------------------------------------------------
-- 15. Empirical reporting view
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW empirical_distribution_report AS
SELECT
    e.experiment_id,
    e.experiment_name,
    e.distribution_code,
    e.success_probability,
    COUNT(o.observation_id) AS observations,
    AVG(o.outcome)::DOUBLE PRECISION AS empirical_mean,
    VAR_POP(o.outcome)::DOUBLE PRECISION AS empirical_variance,
    STDDEV_POP(o.outcome)::DOUBLE PRECISION AS empirical_stddev,
    MIN(o.outcome) AS minimum_outcome,
    MAX(o.outcome) AS maximum_outcome
FROM experiments e
LEFT JOIN observations o
    ON o.experiment_id = e.experiment_id
GROUP BY
    e.experiment_id,
    e.experiment_name,
    e.distribution_code,
    e.success_probability;


-- ------------------------------------------------------------
-- 16. Outcome frequency reporting
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW outcome_frequency_report AS
SELECT
    e.experiment_id,
    e.experiment_name,
    o.outcome,
    COUNT(*) AS frequency,
    COUNT(*)::DOUBLE PRECISION
        / NULLIF(
            SUM(COUNT(*)) OVER (PARTITION BY e.experiment_id),
            0
        ) AS empirical_probability
FROM experiments e
JOIN observations o
    ON o.experiment_id = e.experiment_id
GROUP BY
    e.experiment_id,
    e.experiment_name,
    o.outcome;


-- ------------------------------------------------------------
-- 17. Sample experiment configurations
-- ------------------------------------------------------------

INSERT INTO experiments (
    experiment_name,
    distribution_code,
    success_probability,
    trial_count,
    required_successes,
    sample_size
)
VALUES
(
    'Payment Success: Single Transaction',
    'BERNOULLI',
    0.9500000000,
    NULL,
    NULL,
    1000
),
(
    'Payment Success: Twenty Transactions',
    'BINOMIAL',
    0.9500000000,
    20,
    NULL,
    1000
),
(
    'Network Connection: First Successful Attempt',
    'GEOMETRIC',
    0.3000000000,
    NULL,
    NULL,
    1000
),
(
    'Customer Support: Five Resolved Cases',
    'NEGATIVE_BINOMIAL',
    0.6000000000,
    NULL,
    5,
    1000
),
(
    'Low Probability Network Failure',
    'GEOMETRIC',
    0.0000000000,
    NULL,
    NULL,
    1000
);


-- ------------------------------------------------------------
-- 18. Record meaningful observations
-- ------------------------------------------------------------

CALL record_observations(
    1,
    ARRAY[1, 1, 0, 1, 1, 1, 0, 1, 1, 1]
);

CALL record_observations(
    2,
    ARRAY[18, 19, 20, 17, 18, 19, 20, 16, 19, 18]
);

CALL record_observations(
    3,
    ARRAY[1, 2, 3, 1, 4, 2, 5, 3, 1, 2]
);

CALL record_observations(
    4,
    ARRAY[7, 8, 9, 6, 10, 8, 7, 11, 9, 8]
);


-- ------------------------------------------------------------
-- 19. Complete experiments
-- ------------------------------------------------------------

UPDATE experiments e
SET
    experiment_status = 'COMPLETED',
    completed_at = CURRENT_TIMESTAMP
WHERE e.experiment_id IN (1, 2, 3, 4)
AND (
    SELECT COUNT(*)
    FROM observations o
    WHERE o.experiment_id = e.experiment_id
) = 10;


COMMIT;


-- ============================================================
-- ANALYTICAL QUERIES
-- ============================================================

-- A. Retrieve distribution definitions.

SELECT *
FROM probability_lab.distribution_types
ORDER BY distribution_code;


-- B. Retrieve all experiment configurations.

SELECT
    experiment_id,
    experiment_name,
    distribution_code,
    success_probability,
    trial_count,
    required_successes,
    experiment_status
FROM probability_lab.experiments
ORDER BY experiment_id;


-- C. Bernoulli probability calculations.

SELECT
    probability_lab.bernoulli_pmf(0.8, 0) AS failure_probability,
    probability_lab.bernoulli_pmf(0.8, 1) AS success_probability;


-- D. Binomial PMF calculations.

SELECT
    k,
    probability_lab.binomial_pmf(10, 0.7, k) AS probability
FROM GENERATE_SERIES(0, 10) AS k
ORDER BY k;


-- E. Geometric PMF and CDF.

SELECT
    k,
    probability_lab.geometric_pmf(0.25, k) AS pmf,
    probability_lab.geometric_cdf(0.25, k) AS cdf
FROM GENERATE_SERIES(1, 10) AS k
ORDER BY k;


-- F. Negative binomial PMF and CDF.

SELECT
    k,
    probability_lab.negative_binomial_pmf(3, 0.5, k) AS pmf,
    probability_lab.negative_binomial_cdf(3, 0.5, k) AS cdf
FROM GENERATE_SERIES(3, 12) AS k
ORDER BY k;


-- G. Theoretical moments.

SELECT *
FROM probability_lab.distribution_statistics(
    'BINOMIAL',
    0.7,
    10,
    NULL
);


-- H. Empirical distribution reports.

SELECT *
FROM probability_lab.empirical_distribution_report
ORDER BY experiment_id;


-- I. Empirical frequency aggregation.

SELECT *
FROM probability_lab.outcome_frequency_report
ORDER BY experiment_id, outcome;


-- J. Compare theoretical and empirical means.

SELECT
    e.experiment_id,
    e.experiment_name,
    e.distribution_code,
    r.empirical_mean,
    s.theoretical_mean,
    r.empirical_mean - s.theoretical_mean AS mean_difference,
    r.empirical_variance,
    s.theoretical_variance
FROM probability_lab.experiments e
JOIN probability_lab.empirical_distribution_report r
    ON r.experiment_id = e.experiment_id
CROSS JOIN LATERAL
    probability_lab.distribution_statistics(
        e.distribution_code,
        e.success_probability,
        e.trial_count,
        e.required_successes
    ) s
WHERE r.observations > 0
ORDER BY e.experiment_id;


-- K. Calculate probability of meeting operational targets.

SELECT
    probability_lab.binomial_pmf(20, 0.95, 18)
    + probability_lab.binomial_pmf(20, 0.95, 19)
    + probability_lab.binomial_pmf(20, 0.95, 20)
    AS probability_at_least_18_successes;


-- L. Geometric probability of success within five attempts.

SELECT
    probability_lab.geometric_cdf(0.2, 5)
    AS probability_success_within_five_attempts;


-- M. Negative binomial probability of five successes
-- within eight attempts.

SELECT
    probability_lab.negative_binomial_cdf(5, 0.6, 8)
    AS probability_of_five_successes_within_eight_attempts;


-- N. Validate empirical frequency totals.

SELECT
    experiment_id,
    SUM(frequency) AS total_observations,
    SUM(empirical_probability) AS probability_sum
FROM probability_lab.outcome_frequency_report
GROUP BY experiment_id
ORDER BY experiment_id;


-- O. Identify experiments with incomplete observations.

SELECT
    e.experiment_id,
    e.experiment_name,
    e.sample_size,
    COUNT(o.observation_id) AS recorded_observations,
    e.experiment_status
FROM probability_lab.experiments e
LEFT JOIN probability_lab.observations o
    ON o.experiment_id = e.experiment_id
GROUP BY
    e.experiment_id,
    e.experiment_name,
    e.sample_size,
    e.experiment_status
HAVING COUNT(o.observation_id) < e.sample_size
ORDER BY e.experiment_id;


-- P. Operational reliability evaluation.
--
-- Example policy:
-- At least 25% success probability and no more than
-- four expected attempts for first success.

SELECT
    experiment_id,
    experiment_name,
    success_probability,
    CASE
        WHEN success_probability >= 0.25
         AND (
             1.0 / NULLIF(success_probability, 0)
         ) <= 4
        THEN 'ELIGIBLE'
        ELSE 'NOT_ELIGIBLE'
    END AS operational_decision
FROM probability_lab.experiments
WHERE distribution_code = 'GEOMETRIC';


-- Q. Distribution-specific probability mass validation.

SELECT
    'BERNOULLI' AS distribution,
    bernoulli_pmf(0.4, 0) + bernoulli_pmf(0.4, 1)
        AS probability_total

UNION ALL

SELECT
    'BINOMIAL',
    (
        SELECT SUM(binomial_pmf(5, 0.4, k))
        FROM GENERATE_SERIES(0, 5) AS k
    );


-- ============================================================
-- FAILURE TESTS
--
-- Execute separately when testing expected exceptions.
-- Each statement is intentionally invalid.
-- ============================================================

-- Invalid probability:
-- SELECT bernoulli_pmf(1.5, 1);

-- Invalid binomial trial count:
-- SELECT binomial_pmf(-1, 0.5, 1);

-- Invalid geometric support:
-- SELECT geometric_pmf(0.5, 0);

-- Invalid negative binomial parameter:
-- SELECT negative_binomial_pmf(0, 0.5, 2);

-- Invalid Bernoulli observation:
-- INSERT INTO observations (experiment_id, outcome)
-- VALUES (1, 5);

-- Attempt to insert observations into a completed experiment:
-- CALL record_observations(1, ARRAY[1, 0]);

-- Attempt to exceed the configured sample limit:
-- CALL record_observations(1, ARRAY[1, 1, 1]);


-- ============================================================
-- END OF PROBABILITY DISTRIBUTION WORKFLOW
-- ============================================================
