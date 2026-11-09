CONDITIONAL DISTRIBUTIONS
PostgreSQL 14+

Implemented concepts:
    1. Joint probability mass functions.
    2. Marginal probability distributions.
    3. Conditional probability mass functions.
    4. Conditional expectation.
    5. Conditional variance.
    6. Conditional covariance.
    7. Conditional density of a bivariate normal distribution.
    8. Law of total expectation.
    9. Law of total variance.
   10. Data validation and reporting.
===============================================================================
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS conditional_stats;

SET search_path TO conditional_stats, public;


   1. DOMAIN MODEL

CREATE TABLE IF NOT EXISTS distribution_models (
    distribution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    distribution_name VARCHAR(150) NOT NULL UNIQUE,
    distribution_type VARCHAR(20) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_distribution_type
        CHECK (
            distribution_type IN (
                'DISCRETE',
                'CONTINUOUS'
            )
        )
);


CREATE TABLE IF NOT EXISTS joint_probability_observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    distribution_id BIGINT NOT NULL
        REFERENCES distribution_models(distribution_id)
        ON DELETE CASCADE,

    x_value NUMERIC(18, 6) NOT NULL,
    y_value NUMERIC(18, 6) NOT NULL,

    joint_probability NUMERIC(20, 12) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT nonnegative_joint_probability
        CHECK (
            joint_probability >= 0
            AND joint_probability <= 1
        ),

    CONSTRAINT unique_joint_outcome
        UNIQUE (distribution_id, x_value, y_value)
);


CREATE INDEX IF NOT EXISTS idx_joint_distribution_x
    ON joint_probability_observations (
        distribution_id,
        x_value
    );

CREATE INDEX IF NOT EXISTS idx_joint_distribution_y
    ON joint_probability_observations (
        distribution_id,
        y_value
    );


/* ============================================================================
   2. CONTINUOUS DISTRIBUTION PARAMETERS
============================================================================ */

CREATE TABLE IF NOT EXISTS bivariate_normal_parameters (
    distribution_id BIGINT PRIMARY KEY
        REFERENCES distribution_models(distribution_id)
        ON DELETE CASCADE,

    mu_x DOUBLE PRECISION NOT NULL,
    mu_y DOUBLE PRECISION NOT NULL,

    sigma_x DOUBLE PRECISION NOT NULL,
    sigma_y DOUBLE PRECISION NOT NULL,

    rho DOUBLE PRECISION NOT NULL,

    CONSTRAINT positive_sigma_x
        CHECK (
            sigma_x > 0
            AND sigma_x < 'Infinity'::DOUBLE PRECISION
        ),

    CONSTRAINT positive_sigma_y
        CHECK (
            sigma_y > 0
            AND sigma_y < 'Infinity'::DOUBLE PRECISION
        ),

    CONSTRAINT valid_correlation
        CHECK (rho > -1 AND rho < 1),

    CONSTRAINT finite_means
        CHECK (
            ABS(mu_x) < 'Infinity'::DOUBLE PRECISION
            AND ABS(mu_y) < 'Infinity'::DOUBLE PRECISION
        )
);


/* ============================================================================
   3. VALIDATE JOINT PROBABILITY DISTRIBUTIONS
============================================================================ */

CREATE OR REPLACE FUNCTION validate_joint_distribution(
    p_distribution_id BIGINT
)
RETURNS TABLE (
    total_probability NUMERIC,
    outcome_count BIGINT,
    is_valid BOOLEAN
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        COALESCE(SUM(joint_probability), 0),
        COUNT(*),
        (
            COUNT(*) > 0
            AND ABS(
                COALESCE(SUM(joint_probability), 0) - 1
            ) <= 0.0000000001
        )
    FROM joint_probability_observations
    WHERE distribution_id = p_distribution_id;
$$;


/* ============================================================================
   4. MARGINAL DISTRIBUTIONS
============================================================================ */

CREATE OR REPLACE VIEW marginal_x_distribution AS
SELECT
    distribution_id,
    x_value,
    SUM(joint_probability) AS marginal_probability
FROM joint_probability_observations
GROUP BY distribution_id, x_value;


CREATE OR REPLACE VIEW marginal_y_distribution AS
SELECT
    distribution_id,
    y_value,
    SUM(joint_probability) AS marginal_probability
FROM joint_probability_observations
GROUP BY distribution_id, y_value;


/* ============================================================================
   5. CONDITIONAL PROBABILITY MASS FUNCTION

   P(Y=y | X=x) = P(X=x,Y=y) / P(X=x)

   A zero-probability conditioning event is rejected.
============================================================================ */

CREATE OR REPLACE FUNCTION conditional_pmf_y_given_x(
    p_distribution_id BIGINT,
    p_x NUMERIC
)
RETURNS TABLE (
    y_value NUMERIC,
    joint_probability NUMERIC,
    marginal_probability NUMERIC,
    conditional_probability NUMERIC
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_denominator NUMERIC;
BEGIN
    SELECT SUM(joint_probability)
    INTO v_denominator
    FROM joint_probability_observations
    WHERE distribution_id = p_distribution_id
      AND x_value = p_x;

    IF v_denominator IS NULL OR v_denominator <= 0 THEN
        RAISE EXCEPTION
            'P(X=%) is zero or undefined for distribution %',
            p_x,
            p_distribution_id;
    END IF;

    RETURN QUERY
    SELECT
        observation.y_value,
        observation.joint_probability,
        v_denominator,
        observation.joint_probability / v_denominator
    FROM joint_probability_observations observation
    WHERE observation.distribution_id = p_distribution_id
      AND observation.x_value = p_x
    ORDER BY observation.y_value;
END;
$$;


/* ============================================================================
   6. CONDITIONAL EXPECTATION AND VARIANCE
============================================================================ */

CREATE OR REPLACE FUNCTION conditional_statistics(
    p_distribution_id BIGINT,
    p_x NUMERIC
)
RETURNS TABLE (
    conditioning_probability NUMERIC,
    conditional_expectation NUMERIC,
    conditional_variance NUMERIC
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_probability NUMERIC;
    v_mean NUMERIC;
    v_variance NUMERIC;
BEGIN
    SELECT SUM(joint_probability)
    INTO v_probability
    FROM joint_probability_observations
    WHERE distribution_id = p_distribution_id
      AND x_value = p_x;

    IF v_probability IS NULL OR v_probability <= 0 THEN
        RAISE EXCEPTION
            'Conditional statistics undefined for X=%',
            p_x;
    END IF;

    SELECT
        SUM(
            y_value * joint_probability / v_probability
        ),
        SUM(
            POWER(y_value, 2)
            * joint_probability / v_probability
        )
    INTO v_mean, v_variance
    FROM joint_probability_observations
    WHERE distribution_id = p_distribution_id
      AND x_value = p_x;

    v_variance := v_variance - POWER(v_mean, 2);

    RETURN QUERY
    SELECT
        v_probability,
        v_mean,
        GREATEST(v_variance, 0);
END;
$$;


/* ============================================================================
   7. CONDITIONAL COVARIANCE
============================================================================ */

CREATE OR REPLACE FUNCTION joint_covariance(
    p_distribution_id BIGINT
)
RETURNS NUMERIC
LANGUAGE SQL
STABLE
AS $$
    WITH means AS (
        SELECT
            SUM(x_value * joint_probability) AS mean_x,
            SUM(y_value * joint_probability) AS mean_y
        FROM joint_probability_observations
        WHERE distribution_id = p_distribution_id
    )
    SELECT
        SUM(
            (
                observation.x_value - means.mean_x
            ) *
            (
                observation.y_value - means.mean_y
            ) *
            observation.joint_probability
        )
    FROM joint_probability_observations observation
    CROSS JOIN means
    WHERE observation.distribution_id = p_distribution_id;
$$;


/* ============================================================================
   8. LAW OF TOTAL EXPECTATION

   E[Y] = E[E[Y|X]]
============================================================================ */

CREATE OR REPLACE FUNCTION total_expectation_y(
    p_distribution_id BIGINT
)
RETURNS NUMERIC
LANGUAGE SQL
STABLE
AS $$
    SELECT
        SUM(
            x_marginal.marginal_probability
            * conditional.conditional_mean
        )
    FROM marginal_x_distribution x_marginal
    CROSS JOIN LATERAL (
        SELECT
            SUM(
                observation.y_value
                * observation.joint_probability
                / x_marginal.marginal_probability
            ) AS conditional_mean
        FROM joint_probability_observations observation
        WHERE observation.distribution_id =
            x_marginal.distribution_id
          AND observation.x_value = x_marginal.x_value
    ) conditional
    WHERE x_marginal.distribution_id = p_distribution_id
      AND x_marginal.marginal_probability > 0;
$$;


/* ============================================================================
   9. LAW OF TOTAL VARIANCE

   Var(Y) = E[Var(Y|X)] + Var(E[Y|X])
============================================================================ */

CREATE OR REPLACE FUNCTION total_variance_y(
    p_distribution_id BIGINT
)
RETURNS TABLE (
    expected_conditional_variance NUMERIC,
    variance_of_conditional_means NUMERIC,
    total_variance NUMERIC
)
LANGUAGE SQL
STABLE
AS $$
    WITH conditional_values AS (
        SELECT
            x_marginal.x_value,
            x_marginal.marginal_probability,

            SUM(
                observation.y_value
                * observation.joint_probability
                / x_marginal.marginal_probability
            ) AS conditional_mean,

            SUM(
                POWER(observation.y_value, 2)
                * observation.joint_probability
                / x_marginal.marginal_probability
            )
            -
            POWER(
                SUM(
                    observation.y_value
                    * observation.joint_probability
                    / x_marginal.marginal_probability
                ),
                2
            ) AS conditional_variance

        FROM marginal_x_distribution x_marginal

        JOIN joint_probability_observations observation
          ON observation.distribution_id =
                x_marginal.distribution_id
         AND observation.x_value = x_marginal.x_value

        WHERE x_marginal.distribution_id = p_distribution_id
          AND x_marginal.marginal_probability > 0

        GROUP BY
            x_marginal.x_value,
            x_marginal.marginal_probability
    ),
    aggregate_values AS (
        SELECT
            SUM(
                marginal_probability
                * GREATEST(conditional_variance, 0)
            ) AS expected_variance,

            SUM(
                marginal_probability * conditional_mean
            ) AS overall_mean

        FROM conditional_values
    )
    SELECT
        aggregate_values.expected_variance,

        SUM(
            conditional_values.marginal_probability
            * POWER(
                conditional_values.conditional_mean
                - aggregate_values.overall_mean,
                2
            )
        ),

        aggregate_values.expected_variance
        +
        SUM(
            conditional_values.marginal_probability
            * POWER(
                conditional_values.conditional_mean
                - aggregate_values.overall_mean,
                2
            )
        )

    FROM conditional_values
    CROSS JOIN aggregate_values
    GROUP BY aggregate_values.expected_variance;
$$;


/* ============================================================================
   10. BIVARIATE NORMAL CONDITIONAL DENSITY

   Y | X=x ~ Normal(
       mu_y + rho * sigma_y/sigma_x * (x-mu_x),
       sigma_y^2 * (1-rho^2)
   )
============================================================================ */

CREATE OR REPLACE FUNCTION normal_conditional_density(
    p_distribution_id BIGINT,
    p_x DOUBLE PRECISION,
    p_y DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_mu_y DOUBLE PRECISION;
    v_sigma_x DOUBLE PRECISION;
    v_sigma_y DOUBLE PRECISION;
    v_rho DOUBLE PRECISION;

    v_conditional_mean DOUBLE PRECISION;
    v_conditional_variance DOUBLE PRECISION;
BEGIN
    IF p_x IS NULL OR p_y IS NULL
       OR ABS(p_x) = 'Infinity'::DOUBLE PRECISION
       OR ABS(p_y) = 'Infinity'::DOUBLE PRECISION
       OR p_x = 'NaN'::DOUBLE PRECISION
       OR p_y = 'NaN'::DOUBLE PRECISION THEN

        RAISE EXCEPTION 'Evaluation points must be finite.';
    END IF;

    SELECT
        mu_y,
        sigma_x,
        sigma_y,
        rho
    INTO
        v_mu_y,
        v_sigma_x,
        v_sigma_y,
        v_rho
    FROM bivariate_normal_parameters
    WHERE distribution_id = p_distribution_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Continuous distribution parameters not found.';
    END IF;

    SELECT
        mu_y
        + v_rho * v_sigma_y / v_sigma_x
          * (p_x - mu_x)
    INTO v_conditional_mean
    FROM bivariate_normal_parameters
    WHERE distribution_id = p_distribution_id;

    v_conditional_variance :=
        POWER(v_sigma_y, 2) * (1 - POWER(v_rho, 2));

    RETURN EXP(
        -POWER(p_y - v_conditional_mean, 2)
        / (2 * v_conditional_variance)
    )
    /
    SQRT(
        2 * PI() * v_conditional_variance
    );
END;
$$;


/* ============================================================================
   11. SAMPLE DISCRETE DISTRIBUTION
============================================================================ */

INSERT INTO distribution_models (
    distribution_name,
    distribution_type,
    description
)
VALUES (
    'study_performance',
    'DISCRETE',
    'Joint distribution of study category and examination outcome.'
)
ON CONFLICT (distribution_name) DO NOTHING;


INSERT INTO joint_probability_observations (
    distribution_id,
    x_value,
    y_value,
    joint_probability
)
SELECT
    model.distribution_id,
    sample.x_value,
    sample.y_value,
    sample.joint_probability
FROM distribution_models model
CROSS JOIN (
    VALUES
        (0::NUMERIC, 0::NUMERIC, 0.10::NUMERIC),
        (0::NUMERIC, 1::NUMERIC, 0.10::NUMERIC),
        (0::NUMERIC, 2::NUMERIC, 0.05::NUMERIC),
        (1::NUMERIC, 0::NUMERIC, 0.05::NUMERIC),
        (1::NUMERIC, 1::NUMERIC, 0.20::NUMERIC),
        (1::NUMERIC, 2::NUMERIC, 0.15::NUMERIC),
        (2::NUMERIC, 0::NUMERIC, 0.05::NUMERIC),
        (2::NUMERIC, 1::NUMERIC, 0.10::NUMERIC),
        (2::NUMERIC, 2::NUMERIC, 0.20::NUMERIC)
) AS sample(x_value, y_value, joint_probability)
WHERE model.distribution_name = 'study_performance'
ON CONFLICT (distribution_id, x_value, y_value)
DO UPDATE SET
    joint_probability = EXCLUDED.joint_probability;


/* ============================================================================
   12. SAMPLE CONTINUOUS DISTRIBUTION
============================================================================ */

INSERT INTO distribution_models (
    distribution_name,
    distribution_type,
    description
)
VALUES (
    'bivariate_normal_example',
    'CONTINUOUS',
    'Bivariate normal model for conditional density calculations.'
)
ON CONFLICT (distribution_name) DO NOTHING;


INSERT INTO bivariate_normal_parameters (
    distribution_id,
    mu_x,
    mu_y,
    sigma_x,
    sigma_y,
    rho
)
SELECT
    distribution_id,
    10.0,
    50.0,
    2.0,
    8.0,
    0.75
FROM distribution_models
WHERE distribution_name = 'bivariate_normal_example'
ON CONFLICT (distribution_id)
DO UPDATE SET
    mu_x = EXCLUDED.mu_x,
    mu_y = EXCLUDED.mu_y,
    sigma_x = EXCLUDED.sigma_x,
    sigma_y = EXCLUDED.sigma_y,
    rho = EXCLUDED.rho;


/* ============================================================================
   13. REPORTING VIEW
============================================================================ */

CREATE OR REPLACE VIEW conditional_statistics_report AS
SELECT
    x_marginal.distribution_id,
    x_marginal.x_value,
    x_marginal.marginal_probability,

    SUM(
        observation.y_value
        * observation.joint_probability
        / x_marginal.marginal_probability
    ) AS conditional_expectation,

    GREATEST(
        SUM(
            POWER(observation.y_value, 2)
            * observation.joint_probability
            / x_marginal.marginal_probability
        )
        -
        POWER(
            SUM(
                observation.y_value
                * observation.joint_probability
                / x_marginal.marginal_probability
            ),
            2
        ),
        0
    ) AS conditional_variance

FROM marginal_x_distribution x_marginal

JOIN joint_probability_observations observation
  ON observation.distribution_id = x_marginal.distribution_id
 AND observation.x_value = x_marginal.x_value

WHERE x_marginal.marginal_probability > 0

GROUP BY
    x_marginal.distribution_id,
    x_marginal.x_value,
    x_marginal.marginal_probability;


/* ============================================================================
   14. EXECUTABLE ANALYSIS QUERIES
============================================================================ */

/* Identify the sample distribution. */

SELECT
    distribution_id,
    distribution_name,
    distribution_type
FROM distribution_models
ORDER BY distribution_id;


/* Validate joint probability normalization. */

SELECT *
FROM validate_joint_distribution(
    (
        SELECT distribution_id
        FROM distribution_models
        WHERE distribution_name = 'study_performance'
    )
);


/* Retrieve marginal distribution of X. */

SELECT *
FROM marginal_x_distribution
WHERE distribution_id = (
    SELECT distribution_id
    FROM distribution_models
    WHERE distribution_name = 'study_performance'
)
ORDER BY x_value;


/* Retrieve marginal distribution of Y. */

SELECT *
FROM marginal_y_distribution
WHERE distribution_id = (
    SELECT distribution_id
    FROM distribution_models
    WHERE distribution_name = 'study_performance'
)
ORDER BY y_value;


/* Calculate P(Y=y | X=1). */

SELECT *
FROM conditional_pmf_y_given_x(
    (
        SELECT distribution_id
        FROM distribution_models
        WHERE distribution_name = 'study_performance'
    ),
    1
);


/* Calculate conditional expectation and variance. */

SELECT *
FROM conditional_statistics(
    (
        SELECT distribution_id
        FROM distribution_models
        WHERE distribution_name = 'study_performance'
    ),
    1
);


/* Retrieve conditional statistics for every X. */

SELECT *
FROM conditional_statistics_report
WHERE distribution_id = (
    SELECT distribution_id
    FROM distribution_models
    WHERE distribution_name = 'study_performance'
)
ORDER BY x_value;


/* Calculate conditional covariance. */

SELECT joint_covariance(
    (
        SELECT distribution_id
        FROM distribution_models
        WHERE distribution_name = 'study_performance'
    )
) AS covariance;


/* Verify the law of total expectation. */

SELECT
    total_expectation_y(
        (
            SELECT distribution_id
            FROM distribution_models
            WHERE distribution_name = 'study_performance'
        )
    ) AS expected_value;


/* Verify the law of total variance. */

SELECT *
FROM total_variance_y(
    (
        SELECT distribution_id
        FROM distribution_models
        WHERE distribution_name = 'study_performance'
    )
);


/* Evaluate continuous conditional density. */

SELECT normal_conditional_density(
    (
        SELECT distribution_id
        FROM distribution_models
        WHERE distribution_name = 'bivariate_normal_example'
    ),
    12.0,
    58.0
) AS conditional_density;


/* ============================================================================
   15. VALIDATION AND FAILURE SCENARIOS
============================================================================ */

/*
The following block demonstrates zero-probability conditioning.
The exception is caught so the complete script can continue.
*/

DO $$
DECLARE
    v_distribution_id BIGINT;
BEGIN
    SELECT distribution_id
    INTO v_distribution_id
    FROM distribution_models
    WHERE distribution_name = 'study_performance';

    BEGIN
        PERFORM *
        FROM conditional_statistics(v_distribution_id, 99);

        RAISE EXCEPTION
            'Expected zero-probability conditioning failure.';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Conditioning validation handled: %',
                SQLERRM;
    END;
END;
$$;


/* ============================================================================
   16. TRANSACTIONAL DATA VALIDATION
============================================================================ */

/*
The transaction verifies that the discrete distribution is normalized.
Invalid data causes rollback rather than publishing an incorrect model.
*/

DO $$
DECLARE
    v_distribution_id BIGINT;
    v_valid BOOLEAN;
BEGIN
    SELECT distribution_id
    INTO v_distribution_id
    FROM distribution_models
    WHERE distribution_name = 'study_performance';

    SELECT is_valid
    INTO v_valid
    FROM validate_joint_distribution(v_distribution_id);

    IF NOT v_valid THEN
        RAISE EXCEPTION
            'Joint probability distribution failed normalization.';
    END IF;

    RAISE NOTICE
        'Joint probability distribution validated successfully.';
END;
$$;


COMMIT;


/* ============================================================================
   17. PERFORMANCE AND OPERATIONAL NOTES

   - Composite indexes support conditional filtering.
   - Aggregate queries calculate conditional moments without
     materializing intermediate probability tables.
   - Views provide reusable reporting structures.
   - SQL functions reject zero-probability conditioning events.
   - NUMERIC is used for discrete probability storage to reduce
     decimal representation errors.
   - DOUBLE PRECISION is used for continuous density calculations.
   - Large-scale models should validate normalization during
     controlled publication rather than on every analytical query.
   - Access to probability records should be restricted where
     the underlying observations contain confidential information.
============================================================================ */
