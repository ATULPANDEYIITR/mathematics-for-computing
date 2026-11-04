/*
    EXPECTED VALUE AND MOMENTS
    PostgreSQL 14+

    Relational probability analytics system.

    Covers:
    - Discrete probability distributions
    - Outcomes and probabilities
    - Expected value
    - Variance
    - Standard deviation
    - Raw moments
    - Central moments
    - Skewness
    - Kurtosis
    - Conditional expectation
    - Joint distributions
    - Covariance and correlation
    - Monte Carlo-compatible empirical observations
    - Financial risk policies
    - Portfolio analytics
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS probability_lab;

SET search_path TO probability_lab, public;

-- ---------------------------------------------------------
-- 1. DOMAIN TYPES
-- ---------------------------------------------------------

DO $$
BEGIN
    CREATE TYPE probability_lab.distribution_kind AS ENUM (
        'DISCRETE',
        'JOINT'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END;
$$;

DO $$
BEGIN
    CREATE TYPE probability_lab.risk_category AS ENUM (
        'LOW',
        'MODERATE',
        'HIGH',
        'CRITICAL'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END;
$$;

-- ---------------------------------------------------------
-- 2. DISTRIBUTION MASTER
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS distributions (
    distribution_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    distribution_name VARCHAR(150) NOT NULL UNIQUE,

    distribution_type distribution_kind NOT NULL
        DEFAULT 'DISCRETE',

    description TEXT,

    probability_tolerance NUMERIC(18, 15) NOT NULL
        DEFAULT 0.000000001,

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_tolerance
        CHECK (
            probability_tolerance > 0
            AND probability_tolerance < 0.01
        )
);

-- ---------------------------------------------------------
-- 3. DISCRETE OUTCOMES
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS distribution_outcomes (
    outcome_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    distribution_id BIGINT NOT NULL
        REFERENCES distributions(distribution_id)
        ON DELETE CASCADE,

    outcome_value NUMERIC(24, 8) NOT NULL,

    probability NUMERIC(18, 15) NOT NULL,

    outcome_description VARCHAR(250),

    CONSTRAINT valid_probability
        CHECK (probability >= 0 AND probability <= 1),

    CONSTRAINT unique_distribution_outcome
        UNIQUE (distribution_id, outcome_value)
);

CREATE INDEX IF NOT EXISTS idx_outcomes_distribution
    ON distribution_outcomes(distribution_id);

CREATE INDEX IF NOT EXISTS idx_outcomes_value
    ON distribution_outcomes(distribution_id, outcome_value);

-- ---------------------------------------------------------
-- 4. JOINT DISTRIBUTION OUTCOMES
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS joint_outcomes (
    joint_outcome_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    distribution_id BIGINT NOT NULL
        REFERENCES distributions(distribution_id)
        ON DELETE CASCADE,

    x_value NUMERIC(24, 8) NOT NULL,

    y_value NUMERIC(24, 8) NOT NULL,

    probability NUMERIC(18, 15) NOT NULL,

    CONSTRAINT valid_joint_probability
        CHECK (probability >= 0 AND probability <= 1),

    CONSTRAINT unique_joint_outcome
        UNIQUE (distribution_id, x_value, y_value)
);

CREATE INDEX IF NOT EXISTS idx_joint_distribution
    ON joint_outcomes(distribution_id);

-- ---------------------------------------------------------
-- 5. EMPIRICAL OBSERVATIONS
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    distribution_id BIGINT NOT NULL
        REFERENCES distributions(distribution_id)
        ON DELETE CASCADE,

    observed_value NUMERIC(24, 8) NOT NULL,

    observed_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    source_identifier VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_observations_distribution
    ON observations(distribution_id, observed_at);

-- ---------------------------------------------------------
-- 6. RISK POLICIES
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS risk_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    policy_name VARCHAR(150) NOT NULL UNIQUE,

    maximum_standard_deviation NUMERIC(24, 8) NOT NULL,

    minimum_expected_value NUMERIC(24, 8) NOT NULL,

    enabled BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT nonnegative_risk_limit
        CHECK (maximum_standard_deviation >= 0)
);

-- ---------------------------------------------------------
-- 7. PORTFOLIO ASSETS
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS portfolio_assets (
    asset_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    asset_name VARCHAR(150) NOT NULL UNIQUE,

    expected_return NUMERIC(18, 8) NOT NULL,

    standard_deviation NUMERIC(18, 8) NOT NULL,

    portfolio_weight NUMERIC(12, 8) NOT NULL,

    CONSTRAINT valid_asset_deviation
        CHECK (standard_deviation >= 0),

    CONSTRAINT valid_portfolio_weight
        CHECK (portfolio_weight >= 0 AND portfolio_weight <= 1)
);

-- ---------------------------------------------------------
-- 8. PROBABILITY VALIDATION FUNCTION
-- ---------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_distribution(
    p_distribution_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_total NUMERIC;
    v_count BIGINT;
    v_tolerance NUMERIC;
    v_type distribution_kind;
BEGIN
    SELECT
        probability_tolerance,
        distribution_type
    INTO
        v_tolerance,
        v_type
    FROM distributions
    WHERE distribution_id = p_distribution_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Distribution % does not exist.',
            p_distribution_id;
    END IF;

    IF v_type = 'DISCRETE' THEN

        SELECT
            COUNT(*),
            COALESCE(SUM(probability), 0)
        INTO v_count, v_total
        FROM distribution_outcomes
        WHERE distribution_id = p_distribution_id;

    ELSE

        SELECT
            COUNT(*),
            COALESCE(SUM(probability), 0)
        INTO v_count, v_total
        FROM joint_outcomes
        WHERE distribution_id = p_distribution_id;

    END IF;

    IF v_count = 0 THEN
        RAISE EXCEPTION
            'Distribution % has no outcomes.',
            p_distribution_id;
    END IF;

    IF ABS(v_total - 1.0) > v_tolerance THEN
        RAISE EXCEPTION
            'Distribution % has probability total %, expected 1.',
            p_distribution_id,
            v_total;
    END IF;

    RETURN TRUE;
END;
$$;

-- ---------------------------------------------------------
-- 9. EXPECTED VALUE FUNCTION
-- ---------------------------------------------------------

CREATE OR REPLACE FUNCTION expected_value(
    p_distribution_id BIGINT
)
RETURNS NUMERIC
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_result NUMERIC;
BEGIN
    IF NOT validate_distribution(p_distribution_id) THEN
        RAISE EXCEPTION 'Invalid distribution.';
    END IF;

    IF (
        SELECT distribution_type
        FROM distributions
        WHERE distribution_id = p_distribution_id
    ) <> 'DISCRETE' THEN
        RAISE EXCEPTION
            'Expected value function requires a discrete distribution.';
    END IF;

    SELECT SUM(outcome_value * probability)
    INTO v_result
    FROM distribution_outcomes
    WHERE distribution_id = p_distribution_id;

    RETURN v_result;
END;
$$;

-- ---------------------------------------------------------
-- 10. RAW MOMENT FUNCTION
-- ---------------------------------------------------------

CREATE OR REPLACE FUNCTION raw_moment(
    p_distribution_id BIGINT,
    p_order INTEGER
)
RETURNS NUMERIC
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_result NUMERIC;
BEGIN
    IF p_order < 0 OR p_order > 20 THEN
        RAISE EXCEPTION
            'Moment order must be between 0 and 20.';
    END IF;

    IF NOT validate_distribution(p_distribution_id) THEN
        RAISE EXCEPTION 'Invalid distribution.';
    END IF;

    SELECT SUM(
        POWER(outcome_value, p_order) * probability
    )
    INTO v_result
    FROM distribution_outcomes
    WHERE distribution_id = p_distribution_id;

    RETURN v_result;
END;
$$;

-- ---------------------------------------------------------
-- 11. CENTRAL MOMENT FUNCTION
-- ---------------------------------------------------------

CREATE OR REPLACE FUNCTION central_moment(
    p_distribution_id BIGINT,
    p_order INTEGER
)
RETURNS NUMERIC
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_mean NUMERIC;
    v_result NUMERIC;
BEGIN
    IF p_order < 0 OR p_order > 20 THEN
        RAISE EXCEPTION
            'Moment order must be between 0 and 20.';
    END IF;

    v_mean := expected_value(p_distribution_id);

    SELECT SUM(
        POWER(outcome_value - v_mean, p_order)
        * probability
    )
    INTO v_result
    FROM distribution_outcomes
    WHERE distribution_id = p_distribution_id;

    RETURN v_result;
END;
$$;

-- ---------------------------------------------------------
-- 12. VARIANCE FUNCTION
-- ---------------------------------------------------------

CREATE OR REPLACE FUNCTION distribution_variance(
    p_distribution_id BIGINT
)
RETURNS NUMERIC
LANGUAGE sql
STABLE
AS $$
    SELECT GREATEST(
        0,
        central_moment(p_distribution_id, 2)
    );
$$;

-- ---------------------------------------------------------
-- 13. STANDARD DEVIATION FUNCTION
-- ---------------------------------------------------------

CREATE OR REPLACE FUNCTION distribution_stddev(
    p_distribution_id BIGINT
)
RETURNS NUMERIC
LANGUAGE sql
STABLE
AS $$
    SELECT SQRT(
        distribution_variance(p_distribution_id)
    );
$$;

-- ---------------------------------------------------------
-- 14. CONDITIONAL EXPECTATION
-- ---------------------------------------------------------

CREATE OR REPLACE FUNCTION conditional_expectation(
    p_distribution_id BIGINT,
    p_threshold NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_probability NUMERIC;
    v_result NUMERIC;
BEGIN
    PERFORM validate_distribution(p_distribution_id);

    SELECT SUM(probability)
    INTO v_probability
    FROM distribution_outcomes
    WHERE distribution_id = p_distribution_id
      AND outcome_value > p_threshold;

    IF COALESCE(v_probability, 0) <= 0 THEN
        RAISE EXCEPTION
            'Conditional event has zero probability.';
    END IF;

    SELECT SUM(outcome_value * probability)
           / v_probability
    INTO v_result
    FROM distribution_outcomes
    WHERE distribution_id = p_distribution_id
      AND outcome_value > p_threshold;

    RETURN v_result;
END;
$$;

-- ---------------------------------------------------------
-- 15. DISTRIBUTION STATISTICS VIEW
-- ---------------------------------------------------------

CREATE OR REPLACE VIEW distribution_statistics AS
WITH base AS (
    SELECT
        d.distribution_id,
        d.distribution_name,
        d.distribution_type,
        SUM(o.probability) AS total_probability,
        SUM(o.outcome_value * o.probability) AS mean_value
    FROM distributions d
    JOIN distribution_outcomes o
        ON o.distribution_id = d.distribution_id
    WHERE d.distribution_type = 'DISCRETE'
    GROUP BY
        d.distribution_id,
        d.distribution_name,
        d.distribution_type
),
moments AS (
    SELECT
        b.distribution_id,
        b.distribution_name,
        b.total_probability,
        b.mean_value,

        SUM(
            POWER(o.outcome_value - b.mean_value, 2)
            * o.probability
        ) AS variance,

        SUM(
            POWER(o.outcome_value - b.mean_value, 3)
            * o.probability
        ) AS third_central_moment,

        SUM(
            POWER(o.outcome_value - b.mean_value, 4)
            * o.probability
        ) AS fourth_central_moment

    FROM base b
    JOIN distribution_outcomes o
        ON o.distribution_id = b.distribution_id

    GROUP BY
        b.distribution_id,
        b.distribution_name,
        b.total_probability,
        b.mean_value
)
SELECT
    distribution_id,
    distribution_name,
    total_probability,
    mean_value AS expected_value,
    variance,
    SQRT(GREATEST(variance, 0)) AS standard_deviation,

    CASE
        WHEN variance = 0 THEN NULL
        ELSE third_central_moment
            / POWER(variance, 1.5)
    END AS skewness,

    CASE
        WHEN variance = 0 THEN NULL
        ELSE fourth_central_moment
            / POWER(variance, 2)
    END AS kurtosis

FROM moments;

-- ---------------------------------------------------------
-- 16. JOINT DISTRIBUTION ANALYSIS
-- ---------------------------------------------------------

CREATE OR REPLACE FUNCTION joint_statistics(
    p_distribution_id BIGINT
)
RETURNS TABLE (
    expected_x NUMERIC,
    expected_y NUMERIC,
    covariance_value NUMERIC,
    correlation_value NUMERIC
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_mean_x NUMERIC;
    v_mean_y NUMERIC;
    v_variance_x NUMERIC;
    v_variance_y NUMERIC;
    v_covariance NUMERIC;
    v_total NUMERIC;
BEGIN
    IF (
        SELECT distribution_type
        FROM distributions
        WHERE distribution_id = p_distribution_id
    ) IS DISTINCT FROM 'JOINT' THEN
        RAISE EXCEPTION
            'Distribution must have JOINT type.';
    END IF;

    SELECT SUM(probability)
    INTO v_total
    FROM joint_outcomes
    WHERE distribution_id = p_distribution_id;

    IF v_total IS NULL OR ABS(v_total - 1) > 0.000000001 THEN
        RAISE EXCEPTION
            'Joint probabilities must sum to 1.';
    END IF;

    SELECT
        SUM(x_value * probability),
        SUM(y_value * probability)
    INTO v_mean_x, v_mean_y
    FROM joint_outcomes
    WHERE distribution_id = p_distribution_id;

    SELECT
        SUM(POWER(x_value - v_mean_x, 2) * probability),
        SUM(POWER(y_value - v_mean_y, 2) * probability),
        SUM(
            (x_value - v_mean_x)
            * (y_value - v_mean_y)
            * probability
        )
    INTO
        v_variance_x,
        v_variance_y,
        v_covariance
    FROM joint_outcomes
    WHERE distribution_id = p_distribution_id;

    RETURN QUERY
    SELECT
        v_mean_x,
        v_mean_y,
        v_covariance,

        CASE
            WHEN v_variance_x = 0 OR v_variance_y = 0
                THEN NULL
            ELSE v_covariance
                / SQRT(v_variance_x * v_variance_y)
        END;
END;
$$;

-- ---------------------------------------------------------
-- 17. EMPIRICAL STATISTICS VIEW
-- ---------------------------------------------------------

CREATE OR REPLACE VIEW empirical_statistics AS
SELECT
    distribution_id,
    COUNT(*) AS observation_count,
    AVG(observed_value) AS empirical_mean,
    VAR_POP(observed_value) AS population_variance,
    STDDEV_POP(observed_value) AS population_standard_deviation,
    VAR_SAMP(observed_value) AS sample_variance,
    STDDEV_SAMP(observed_value) AS sample_standard_deviation
FROM observations
GROUP BY distribution_id;

-- ---------------------------------------------------------
-- 18. RISK EVALUATION FUNCTION
-- ---------------------------------------------------------

CREATE OR REPLACE FUNCTION evaluate_risk_policy(
    p_distribution_id BIGINT,
    p_policy_id BIGINT
)
RETURNS TABLE (
    distribution_name VARCHAR,
    expected_return NUMERIC,
    standard_deviation NUMERIC,
    category risk_category,
    accepted BOOLEAN,
    decision_reason TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_mean NUMERIC;
    v_sd NUMERIC;
    v_max_sd NUMERIC;
    v_min_mean NUMERIC;
    v_enabled BOOLEAN;
    v_name VARCHAR(150);
    v_category risk_category;
    v_accepted BOOLEAN;
BEGIN
    SELECT
        d.distribution_name,
        s.expected_value,
        s.standard_deviation,
        p.maximum_standard_deviation,
        p.minimum_expected_value,
        p.enabled
    INTO
        v_name,
        v_mean,
        v_sd,
        v_max_sd,
        v_min_mean,
        v_enabled
    FROM distribution_statistics s
    JOIN distributions d
        ON d.distribution_id = s.distribution_id
    JOIN risk_policies p
        ON p.policy_id = p_policy_id
    WHERE s.distribution_id = p_distribution_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Distribution or risk policy not found.';
    END IF;

    IF NOT v_enabled THEN
        RAISE EXCEPTION
            'Risk policy is disabled.';
    END IF;

    v_category := CASE
        WHEN v_sd <= v_max_sd * 0.25 THEN 'LOW'
        WHEN v_sd <= v_max_sd * 0.50 THEN 'MODERATE'
        WHEN v_sd <= v_max_sd THEN 'HIGH'
        ELSE 'CRITICAL'
    END;

    v_accepted :=
        v_sd <= v_max_sd
        AND v_mean >= v_min_mean;

    RETURN QUERY
    SELECT
        v_name,
        v_mean,
        v_sd,
        v_category,
        v_accepted,
        CASE
            WHEN v_accepted
                THEN 'Distribution satisfies the risk policy.'
            ELSE 'Risk or expected return violates the policy.'
        END::TEXT;
END;
$$;

-- ---------------------------------------------------------
-- 19. PORTFOLIO ANALYTICS VIEW
-- ---------------------------------------------------------

CREATE OR REPLACE VIEW portfolio_statistics AS
SELECT
    SUM(portfolio_weight * expected_return)
        AS expected_portfolio_return,

    SUM(
        POWER(
            portfolio_weight * standard_deviation,
            2
        )
    ) AS variance_assuming_independence,

    SQRT(
        SUM(
            POWER(
                portfolio_weight * standard_deviation,
                2
            )
        )
    ) AS standard_deviation_assuming_independence,

    SUM(portfolio_weight) AS total_weight

FROM portfolio_assets;

-- This variance assumes independent asset returns.
-- A full portfolio covariance matrix is required when
-- asset returns are correlated.

-- ---------------------------------------------------------
-- 20. SAMPLE DISTRIBUTIONS
-- ---------------------------------------------------------

INSERT INTO distributions (
    distribution_name,
    distribution_type,
    description
)
VALUES
(
    'Fair Six-Sided Die',
    'DISCRETE',
    'Uniform distribution over six outcomes.'
),
(
    'Investment Returns',
    'DISCRETE',
    'Probability-weighted investment profit and loss.'
),
(
    'Joint Financial Variables',
    'JOINT',
    'Joint distribution of two financial variables.'
),
(
    'Deterministic Outcome',
    'DISCRETE',
    'A single outcome with probability one.'
)
ON CONFLICT (distribution_name) DO NOTHING;

-- ---------------------------------------------------------
-- 21. SAMPLE OUTCOME RECORDS
-- ---------------------------------------------------------

INSERT INTO distribution_outcomes (
    distribution_id,
    outcome_value,
    probability,
    outcome_description
)
SELECT
    d.distribution_id,
    x.value,
    x.probability,
    x.description
FROM distributions d
CROSS JOIN (
    VALUES
        (1::NUMERIC, 1.0 / 6, 'Face 1'),
        (2::NUMERIC, 1.0 / 6, 'Face 2'),
        (3::NUMERIC, 1.0 / 6, 'Face 3'),
        (4::NUMERIC, 1.0 / 6, 'Face 4'),
        (5::NUMERIC, 1.0 / 6, 'Face 5'),
        (6::NUMERIC, 1.0 / 6, 'Face 6')
) AS x(value, probability, description)
WHERE d.distribution_name = 'Fair Six-Sided Die'
ON CONFLICT (distribution_id, outcome_value) DO NOTHING;

INSERT INTO distribution_outcomes (
    distribution_id,
    outcome_value,
    probability,
    outcome_description
)
SELECT
    d.distribution_id,
    x.value,
    x.probability,
    x.description
FROM distributions d
CROSS JOIN (
    VALUES
        (-1000::NUMERIC, 0.10::NUMERIC, 'Major loss'),
        (-200::NUMERIC, 0.20::NUMERIC, 'Minor loss'),
        (300::NUMERIC, 0.40::NUMERIC, 'Moderate profit'),
        (1000::NUMERIC, 0.20::NUMERIC, 'High profit'),
        (2500::NUMERIC, 0.10::NUMERIC, 'Exceptional profit')
) AS x(value, probability, description)
WHERE d.distribution_name = 'Investment Returns'
ON CONFLICT (distribution_id, outcome_value) DO NOTHING;

INSERT INTO distribution_outcomes (
    distribution_id,
    outcome_value,
    probability,
    outcome_description
)
SELECT
    d.distribution_id,
    50,
    1,
    'Certain outcome'
FROM distributions d
WHERE d.distribution_name = 'Deterministic Outcome'
ON CONFLICT (distribution_id, outcome_value) DO NOTHING;

-- ---------------------------------------------------------
-- 22. JOINT DISTRIBUTION SAMPLE DATA
-- ---------------------------------------------------------

INSERT INTO joint_outcomes (
    distribution_id,
    x_value,
    y_value,
    probability
)
SELECT
    d.distribution_id,
    x.x,
    x.y,
    x.probability
FROM distributions d
CROSS JOIN (
    VALUES
        (10::NUMERIC, 20::NUMERIC, 0.20::NUMERIC),
        (20::NUMERIC, 30::NUMERIC, 0.30::NUMERIC),
        (30::NUMERIC, 20::NUMERIC, 0.10::NUMERIC),
        (40::NUMERIC, 50::NUMERIC, 0.40::NUMERIC)
) AS x(x, y, probability)
WHERE d.distribution_name = 'Joint Financial Variables'
ON CONFLICT (distribution_id, x_value, y_value) DO NOTHING;

-- ---------------------------------------------------------
-- 23. RISK POLICY DATA
-- ---------------------------------------------------------

INSERT INTO risk_policies (
    policy_name,
    maximum_standard_deviation,
    minimum_expected_value
)
VALUES
(
    'Standard Investment Policy',
    1200,
    100
),
(
    'Conservative Investment Policy',
    500,
    200
)
ON CONFLICT (policy_name) DO NOTHING;

-- ---------------------------------------------------------
-- 24. PORTFOLIO DATA
-- ---------------------------------------------------------

INSERT INTO portfolio_assets (
    asset_name,
    expected_return,
    standard_deviation,
    portfolio_weight
)
VALUES
    ('Equity', 0.12, 0.20, 0.60),
    ('Bonds', 0.05, 0.06, 0.30),
    ('Cash', 0.03, 0.01, 0.10)
ON CONFLICT (asset_name) DO NOTHING;

-- ---------------------------------------------------------
-- 25. EMPIRICAL OBSERVATION DATA
-- ---------------------------------------------------------

INSERT INTO observations (
    distribution_id,
    observed_value,
    source_identifier
)
SELECT
    d.distribution_id,
    x.value,
    'DEMO_SAMPLE'
FROM distributions d
CROSS JOIN (
    VALUES
        (12::NUMERIC),
        (15::NUMERIC),
        (18::NUMERIC),
        (20::NUMERIC),
        (22::NUMERIC),
        (25::NUMERIC),
        (28::NUMERIC)
) AS x(value)
WHERE d.distribution_name = 'Fair Six-Sided Die'
  AND NOT EXISTS (
      SELECT 1
      FROM observations o
      WHERE o.distribution_id = d.distribution_id
        AND o.source_identifier = 'DEMO_SAMPLE'
  );

-- ---------------------------------------------------------
-- 26. DISTRIBUTION VALIDATION REPORT
-- ---------------------------------------------------------

SELECT
    distribution_name,
    distribution_type,
    CASE
        WHEN distribution_type = 'DISCRETE'
            THEN validate_distribution(distribution_id)
        ELSE (
            SELECT ABS(SUM(j.probability) - 1)
                <= 0.000000001
            FROM joint_outcomes j
            WHERE j.distribution_id = distributions.distribution_id
        )
    END AS is_valid
FROM distributions;

-- ---------------------------------------------------------
-- 27. EXPECTATION AND MOMENT RETRIEVAL
-- ---------------------------------------------------------

SELECT *
FROM distribution_statistics
ORDER BY distribution_name;

SELECT
    distribution_name,
    raw_moment(distribution_id, 1) AS first_raw_moment,
    raw_moment(distribution_id, 2) AS second_raw_moment,
    raw_moment(distribution_id, 3) AS third_raw_moment,
    raw_moment(distribution_id, 4) AS fourth_raw_moment
FROM distributions
WHERE distribution_type = 'DISCRETE';

SELECT
    distribution_name,
    central_moment(distribution_id, 2) AS variance,
    central_moment(distribution_id, 3) AS third_central_moment,
    central_moment(distribution_id, 4) AS fourth_central_moment
FROM distributions
WHERE distribution_type = 'DISCRETE';

-- ---------------------------------------------------------
-- 28. CONDITIONAL EXPECTATION REPORT
-- ---------------------------------------------------------

SELECT
    distribution_name,
    expected_value(distribution_id) AS unconditional_expectation,
    conditional_expectation(distribution_id, 0)
        AS expected_positive_outcome
FROM distributions
WHERE distribution_name = 'Investment Returns';

-- ---------------------------------------------------------
-- 29. JOINT COVARIANCE AND CORRELATION
-- ---------------------------------------------------------

SELECT
    d.distribution_name,
    j.*
FROM distributions d
CROSS JOIN LATERAL joint_statistics(d.distribution_id) j
WHERE d.distribution_type = 'JOINT';

-- ---------------------------------------------------------
-- 30. RISK POLICY EVALUATION
-- ---------------------------------------------------------

SELECT *
FROM evaluate_risk_policy(
    (
        SELECT distribution_id
        FROM distributions
        WHERE distribution_name = 'Investment Returns'
    ),
    (
        SELECT policy_id
        FROM risk_policies
        WHERE policy_name = 'Standard Investment Policy'
    )
);

-- ---------------------------------------------------------
-- 31. EMPIRICAL REPORTING
-- ---------------------------------------------------------

SELECT
    d.distribution_name,
    e.observation_count,
    e.empirical_mean,
    e.population_variance,
    e.population_standard_deviation,
    e.sample_variance,
    e.sample_standard_deviation
FROM empirical_statistics e
JOIN distributions d
    ON d.distribution_id = e.distribution_id;

-- ---------------------------------------------------------
-- 32. PORTFOLIO REPORT
-- ---------------------------------------------------------

SELECT
    *,
    CASE
        WHEN ABS(total_weight - 1) <= 0.000000001
            THEN 'VALID'
        ELSE 'INVALID'
    END AS portfolio_status
FROM portfolio_statistics;

-- ---------------------------------------------------------
-- 33. VALIDATION FAILURE DEMONSTRATION
-- ---------------------------------------------------------

DO $$
BEGIN
    BEGIN
        INSERT INTO distribution_outcomes (
            distribution_id,
            outcome_value,
            probability
        )
        SELECT
            distribution_id,
            9999,
            1.50
        FROM distributions
        WHERE distribution_name = 'Fair Six-Sided Die';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Invalid probability rejected by CHECK constraint.';
    END;

    BEGIN
        PERFORM conditional_expectation(
            (
                SELECT distribution_id
                FROM distributions
                WHERE distribution_name = 'Investment Returns'
            ),
            10000
        );

    EXCEPTION
        WHEN raise_exception THEN
            RAISE NOTICE
                'Zero-probability conditional event handled.';
    END;
END;
$$;

-- ---------------------------------------------------------
-- 34. TRANSACTIONAL WORKFLOW
-- ---------------------------------------------------------

SAVEPOINT probability_report_checkpoint;

-- A valid distribution is validated before reporting.
DO $$
DECLARE
    v_id BIGINT;
BEGIN
    SELECT distribution_id
    INTO v_id
    FROM distributions
    WHERE distribution_name = 'Investment Returns';

    IF NOT validate_distribution(v_id) THEN
        RAISE EXCEPTION 'Distribution validation failed.';
    END IF;

    RAISE NOTICE
        'Investment distribution is eligible for analysis.';
END;
$$;

RELEASE SAVEPOINT probability_report_checkpoint;

COMMIT;
