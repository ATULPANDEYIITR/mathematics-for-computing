/*
 * ADVANCED DISTRIBUTIONS
 * PostgreSQL 14+
 *
 * Implements:
 * 1. Poisson PMF and CDF
 * 2. Gamma PDF and CDF
 * 3. Beta PDF and CDF
 * 4. Chi-square PDF and CDF
 * 5. Regularized incomplete gamma function
 * 6. Regularized incomplete beta function
 * 7. Bayesian Beta posterior updating
 * 8. Chi-square goodness-of-fit evaluation
 * 9. Simulation data storage and statistical reporting
 *
 * All calculations use PostgreSQL numeric types where practical.
 */

BEGIN;

CREATE SCHEMA IF NOT EXISTS advanced_stats;

SET search_path TO advanced_stats, public;

-- ============================================================
-- 1. Distribution configuration
-- ============================================================

CREATE TABLE IF NOT EXISTS distribution_registry (
    distribution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    distribution_name TEXT NOT NULL UNIQUE,
    distribution_category TEXT NOT NULL
        CHECK (distribution_category IN ('DISCRETE', 'CONTINUOUS')),
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO distribution_registry (
    distribution_name,
    distribution_category,
    description
)
VALUES
(
    'POISSON',
    'DISCRETE',
    'Models event counts over a fixed interval.'
),
(
    'GAMMA',
    'CONTINUOUS',
    'Models positive continuous waiting times and rates.'
),
(
    'BETA',
    'CONTINUOUS',
    'Models probabilities and bounded proportions.'
),
(
    'CHI_SQUARE',
    'CONTINUOUS',
    'Models sums of squared standard normal variables.'
)
ON CONFLICT (distribution_name) DO NOTHING;


-- ============================================================
-- 2. Log-gamma function
-- ============================================================

CREATE OR REPLACE FUNCTION log_gamma(p_z DOUBLE PRECISION)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    coefficients DOUBLE PRECISION[] := ARRAY[
        676.5203681218851,
        -1259.1392167224028,
        771.3234287776531,
        -176.6150291621406,
        12.507343278686905,
        -0.13857109526572012,
        0.000009984369578019572,
        0.00000015056327351493116
    ];

    z DOUBLE PRECISION;
    x DOUBLE PRECISION := 0.9999999999998099;
    t DOUBLE PRECISION;
    i INTEGER;
BEGIN
    IF NOT isfinite(p_z) OR p_z <= 0 THEN
        RAISE EXCEPTION 'Log-gamma requires positive finite input';
    END IF;

    IF p_z < 0.5 THEN
        RETURN LN(PI())
            - LN(SIN(PI() * p_z))
            - log_gamma(1 - p_z);
    END IF;

    z := p_z - 1;

    FOR i IN 1..8 LOOP
        x := x + coefficients[i] / (z + i);
    END LOOP;

    t := z + 7.5;

    RETURN 0.9189385332046727
        + (z + 0.5) * LN(t)
        - t
        + LN(x);
END;
$$;


-- ============================================================
-- 3. Regularized lower incomplete gamma function
-- ============================================================

CREATE OR REPLACE FUNCTION regularized_gamma_p(
    p_a DOUBLE PRECISION,
    p_x DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    epsilon CONSTANT DOUBLE PRECISION := 1e-12;
    tiny CONSTANT DOUBLE PRECISION := 1e-300;

    factor DOUBLE PRECISION;
    term DOUBLE PRECISION;
    total DOUBLE PRECISION;
    ap DOUBLE PRECISION;

    b DOUBLE PRECISION;
    c DOUBLE PRECISION;
    d DOUBLE PRECISION;
    h DOUBLE PRECISION;
    an DOUBLE PRECISION;
    delta DOUBLE PRECISION;

    i INTEGER;
BEGIN
    IF NOT isfinite(p_a) OR p_a <= 0 THEN
        RAISE EXCEPTION 'Shape must be positive and finite';
    END IF;

    IF NOT isfinite(p_x) OR p_x < 0 THEN
        RAISE EXCEPTION 'x must be finite and nonnegative';
    END IF;

    IF p_x = 0 THEN
        RETURN 0;
    END IF;

    factor := EXP(
        p_a * LN(p_x)
        - p_x
        - log_gamma(p_a)
    );

    IF p_x < p_a + 1 THEN
        term := 1 / p_a;
        total := term;
        ap := p_a;

        FOR i IN 1..10000 LOOP
            ap := ap + 1;
            term := term * p_x / ap;
            total := total + term;

            IF ABS(term) <= ABS(total) * epsilon THEN
                RETURN LEAST(
                    1.0,
                    GREATEST(0.0, factor * total)
                );
            END IF;
        END LOOP;

        RAISE EXCEPTION 'Gamma series failed to converge';
    END IF;

    b := p_x + 1 - p_a;
    c := 1 / tiny;
    d := 1 / b;
    h := d;

    FOR i IN 1..10000 LOOP
        an := -i * (i - p_a);
        b := b + 2;

        d := an * d + b;

        IF ABS(d) < tiny THEN
            d := tiny;
        END IF;

        c := b + an / c;

        IF ABS(c) < tiny THEN
            c := tiny;
        END IF;

        d := 1 / d;
        delta := d * c;
        h := h * delta;

        IF ABS(delta - 1) <= epsilon THEN
            RETURN LEAST(
                1.0,
                GREATEST(0.0, 1 - factor * h)
            );
        END IF;
    END LOOP;

    RAISE EXCEPTION 'Gamma continued fraction failed to converge';
END;
$$;


-- ============================================================
-- 4. Beta continued fraction
-- ============================================================

CREATE OR REPLACE FUNCTION beta_fraction(
    p_a DOUBLE PRECISION,
    p_b DOUBLE PRECISION,
    p_x DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    epsilon CONSTANT DOUBLE PRECISION := 1e-12;
    tiny CONSTANT DOUBLE PRECISION := 1e-300;

    qab DOUBLE PRECISION := p_a + p_b;
    qap DOUBLE PRECISION := p_a + 1;
    qam DOUBLE PRECISION := p_a - 1;

    c DOUBLE PRECISION := 1;
    d DOUBLE PRECISION;
    h DOUBLE PRECISION;
    term DOUBLE PRECISION;
    delta DOUBLE PRECISION;

    m INTEGER;
    m2 INTEGER;
BEGIN
    d := 1 - qab * p_x / qap;

    IF ABS(d) < tiny THEN
        d := tiny;
    END IF;

    d := 1 / d;
    h := d;

    FOR m IN 1..10000 LOOP
        m2 := 2 * m;

        term := m * (p_b - m) * p_x
            / ((qam + m2) * (p_a + m2));

        d := 1 + term * d;
        IF ABS(d) < tiny THEN d := tiny; END IF;

        c := 1 + term / c;
        IF ABS(c) < tiny THEN c := tiny; END IF;

        d := 1 / d;
        h := h * d * c;

        term := -(p_a + m) * (qab + m) * p_x
            / ((p_a + m2) * (qap + m2));

        d := 1 + term * d;
        IF ABS(d) < tiny THEN d := tiny; END IF;

        c := 1 + term / c;
        IF ABS(c) < tiny THEN c := tiny; END IF;

        d := 1 / d;

        delta := d * c;
        h := h * delta;

        IF ABS(delta - 1) <= epsilon THEN
            RETURN h;
        END IF;
    END LOOP;

    RAISE EXCEPTION 'Beta continued fraction failed';
END;
$$;


-- ============================================================
-- 5. Regularized incomplete beta function
-- ============================================================

CREATE OR REPLACE FUNCTION regularized_beta(
    p_x DOUBLE PRECISION,
    p_a DOUBLE PRECISION,
    p_b DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    factor DOUBLE PRECISION;
    result_value DOUBLE PRECISION;
BEGIN
    IF NOT isfinite(p_a) OR p_a <= 0
       OR NOT isfinite(p_b) OR p_b <= 0 THEN
        RAISE EXCEPTION 'Beta parameters must be positive and finite';
    END IF;

    IF NOT isfinite(p_x) OR p_x < 0 OR p_x > 1 THEN
        RAISE EXCEPTION 'x must be between zero and one';
    END IF;

    IF p_x = 0 THEN RETURN 0; END IF;
    IF p_x = 1 THEN RETURN 1; END IF;

    factor := EXP(
        log_gamma(p_a + p_b)
        - log_gamma(p_a)
        - log_gamma(p_b)
        + p_a * LN(p_x)
        + p_b * LN(1 - p_x)
    );

    IF p_x < (p_a + 1) / (p_a + p_b + 2) THEN
        result_value :=
            factor * beta_fraction(p_a, p_b, p_x) / p_a;
    ELSE
        result_value :=
            1 - factor * beta_fraction(p_b, p_a, 1 - p_x) / p_b;
    END IF;

    RETURN LEAST(1.0, GREATEST(0.0, result_value));
END;
$$;


-- ============================================================
-- 6. Poisson distribution
-- ============================================================

CREATE OR REPLACE FUNCTION poisson_pmf(
    p_k INTEGER,
    p_lambda DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF NOT isfinite(p_lambda) OR p_lambda <= 0 THEN
        RAISE EXCEPTION 'Lambda must be positive and finite';
    END IF;

    IF p_k < 0 THEN
        RETURN 0;
    END IF;

    RETURN EXP(
        p_k * LN(p_lambda)
        - p_lambda
        - log_gamma(p_k + 1)
    );
END;
$$;

CREATE OR REPLACE FUNCTION poisson_cdf(
    p_k INTEGER,
    p_lambda DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF NOT isfinite(p_lambda) OR p_lambda <= 0 THEN
        RAISE EXCEPTION 'Lambda must be positive and finite';
    END IF;

    IF p_k < 0 THEN
        RETURN 0;
    END IF;

    RETURN regularized_gamma_p(p_k + 1, p_lambda);
END;
$$;


-- ============================================================
-- 7. Gamma distribution
-- ============================================================

CREATE OR REPLACE FUNCTION gamma_pdf(
    p_x DOUBLE PRECISION,
    p_shape DOUBLE PRECISION,
    p_scale DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF NOT isfinite(p_shape) OR p_shape <= 0
       OR NOT isfinite(p_scale) OR p_scale <= 0 THEN
        RAISE EXCEPTION 'Gamma shape and scale must be positive';
    END IF;

    IF NOT isfinite(p_x) THEN
        RETURN 0;
    END IF;

    IF p_x < 0 THEN RETURN 0; END IF;

    IF p_x = 0 THEN
        IF p_shape < 1 THEN RETURN 'Infinity'::DOUBLE PRECISION; END IF;
        IF p_shape = 1 THEN RETURN 1 / p_scale; END IF;
        RETURN 0;
    END IF;

    RETURN EXP(
        (p_shape - 1) * LN(p_x)
        - p_x / p_scale
        - log_gamma(p_shape)
        - p_shape * LN(p_scale)
    );
END;
$$;

CREATE OR REPLACE FUNCTION gamma_cdf(
    p_x DOUBLE PRECISION,
    p_shape DOUBLE PRECISION,
    p_scale DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF NOT isfinite(p_shape) OR p_shape <= 0
       OR NOT isfinite(p_scale) OR p_scale <= 0 THEN
        RAISE EXCEPTION 'Gamma parameters must be positive';
    END IF;

    IF p_x <= 0 THEN RETURN 0; END IF;

    RETURN regularized_gamma_p(p_shape, p_x / p_scale);
END;
$$;


-- ============================================================
-- 8. Beta distribution
-- ============================================================

CREATE OR REPLACE FUNCTION beta_pdf(
    p_x DOUBLE PRECISION,
    p_alpha DOUBLE PRECISION,
    p_beta DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    log_normalizer DOUBLE PRECISION;
BEGIN
    IF NOT isfinite(p_alpha) OR p_alpha <= 0
       OR NOT isfinite(p_beta) OR p_beta <= 0 THEN
        RAISE EXCEPTION 'Beta parameters must be positive';
    END IF;

    IF NOT isfinite(p_x) OR p_x < 0 OR p_x > 1 THEN
        RETURN 0;
    END IF;

    log_normalizer :=
        log_gamma(p_alpha + p_beta)
        - log_gamma(p_alpha)
        - log_gamma(p_beta);

    IF p_x = 0 THEN
        IF p_alpha < 1 THEN RETURN 'Infinity'::DOUBLE PRECISION; END IF;
        IF p_alpha > 1 THEN RETURN 0; END IF;
        RETURN EXP(log_normalizer);
    END IF;

    IF p_x = 1 THEN
        IF p_beta < 1 THEN RETURN 'Infinity'::DOUBLE PRECISION; END IF;
        IF p_beta > 1 THEN RETURN 0; END IF;
        RETURN EXP(log_normalizer);
    END IF;

    RETURN EXP(
        (p_alpha - 1) * LN(p_x)
        + (p_beta - 1) * LN(1 - p_x)
        + log_normalizer
    );
END;
$$;

CREATE OR REPLACE FUNCTION beta_cdf(
    p_x DOUBLE PRECISION,
    p_alpha DOUBLE PRECISION,
    p_beta DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE sql
IMMUTABLE
STRICT
AS $$
    SELECT regularized_beta(p_x, p_alpha, p_beta);
$$;


-- ============================================================
-- 9. Chi-square distribution
-- ============================================================

CREATE OR REPLACE FUNCTION chi_square_pdf(
    p_x DOUBLE PRECISION,
    p_df DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF NOT isfinite(p_df) OR p_df <= 0 THEN
        RAISE EXCEPTION 'Degrees of freedom must be positive';
    END IF;

    IF NOT isfinite(p_x) THEN RETURN 0; END IF;
    IF p_x < 0 THEN RETURN 0; END IF;

    IF p_x = 0 THEN
        IF p_df < 2 THEN RETURN 'Infinity'::DOUBLE PRECISION; END IF;
        IF p_df = 2 THEN RETURN 0.5; END IF;
        RETURN 0;
    END IF;

    RETURN EXP(
        (p_df / 2 - 1) * LN(p_x)
        - p_x / 2
        - p_df / 2 * LN(2)
        - log_gamma(p_df / 2)
    );
END;
$$;

CREATE OR REPLACE FUNCTION chi_square_cdf(
    p_x DOUBLE PRECISION,
    p_df DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF NOT isfinite(p_df) OR p_df <= 0 THEN
        RAISE EXCEPTION 'Degrees of freedom must be positive';
    END IF;

    IF p_x <= 0 THEN RETURN 0; END IF;

    RETURN regularized_gamma_p(p_df / 2, p_x / 2);
END;
$$;


-- ============================================================
-- 10. Bayesian conversion-rate model
-- ============================================================

CREATE TABLE IF NOT EXISTS bayesian_experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_name TEXT NOT NULL,
    prior_alpha DOUBLE PRECISION NOT NULL CHECK (prior_alpha > 0),
    prior_beta DOUBLE PRECISION NOT NULL CHECK (prior_beta > 0),
    successes BIGINT NOT NULL DEFAULT 0 CHECK (successes >= 0),
    failures BIGINT NOT NULL DEFAULT 0 CHECK (failures >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE VIEW bayesian_posterior_report AS
SELECT
    experiment_id,
    experiment_name,
    prior_alpha,
    prior_beta,
    successes,
    failures,
    prior_alpha + successes AS posterior_alpha,
    prior_beta + failures AS posterior_beta,
    (prior_alpha + successes)
        / (prior_alpha + prior_beta + successes + failures)
        AS posterior_mean,
    (prior_alpha + successes)
        * (prior_beta + failures)
        / (
            POWER(
                prior_alpha + prior_beta + successes + failures,
                2
            )
            * (
                prior_alpha + prior_beta
                + successes + failures + 1
            )
        ) AS posterior_variance
FROM bayesian_experiments;


-- ============================================================
-- 11. Statistical simulation storage
-- ============================================================

CREATE TABLE IF NOT EXISTS simulation_runs (
    simulation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    distribution_name TEXT NOT NULL
        REFERENCES distribution_registry(distribution_name),
    sample_size INTEGER NOT NULL CHECK (sample_size > 0),
    theoretical_mean DOUBLE PRECISION NOT NULL,
    theoretical_variance DOUBLE PRECISION NOT NULL,
    empirical_mean DOUBLE PRECISION NOT NULL,
    empirical_variance DOUBLE PRECISION NOT NULL
        CHECK (empirical_variance >= 0),
    minimum_value DOUBLE PRECISION NOT NULL,
    maximum_value DOUBLE PRECISION NOT NULL,
    random_seed BIGINT,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (minimum_value <= maximum_value)
);

CREATE INDEX IF NOT EXISTS idx_simulation_distribution_time
ON simulation_runs(distribution_name, executed_at DESC);


-- ============================================================
-- 12. Chi-square goodness-of-fit workflow
-- ============================================================

CREATE TABLE IF NOT EXISTS goodness_of_fit_tests (
    test_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    test_name TEXT NOT NULL,
    significance_level DOUBLE PRECISION NOT NULL
        CHECK (significance_level > 0 AND significance_level < 1),
    test_statistic DOUBLE PRECISION NOT NULL CHECK (test_statistic >= 0),
    degrees_of_freedom INTEGER NOT NULL CHECK (degrees_of_freedom > 0),
    p_value DOUBLE PRECISION NOT NULL
        CHECK (p_value >= 0 AND p_value <= 1),
    reject_null BOOLEAN NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS goodness_of_fit_categories (
    category_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    test_id BIGINT NOT NULL
        REFERENCES goodness_of_fit_tests(test_id) ON DELETE CASCADE,
    category_name TEXT NOT NULL,
    observed_count BIGINT NOT NULL CHECK (observed_count >= 0),
    expected_count DOUBLE PRECISION NOT NULL CHECK (expected_count >= 5),
    UNIQUE(test_id, category_name)
);

CREATE INDEX IF NOT EXISTS idx_gof_test_categories
ON goodness_of_fit_categories(test_id);


-- ============================================================
-- 13. Goodness-of-fit calculation function
-- ============================================================

CREATE OR REPLACE FUNCTION evaluate_goodness_of_fit(
    p_test_name TEXT,
    p_observed BIGINT[],
    p_expected DOUBLE PRECISION[],
    p_alpha DOUBLE PRECISION DEFAULT 0.05
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    category_count INTEGER;
    observed_total NUMERIC := 0;
    expected_total NUMERIC := 0;
    statistic DOUBLE PRECISION := 0;
    degrees INTEGER;
    p_value DOUBLE PRECISION;
    reject_result BOOLEAN;
    test_identifier BIGINT;
    i INTEGER;
BEGIN
    IF p_test_name IS NULL OR length(trim(p_test_name)) = 0 THEN
        RAISE EXCEPTION 'Test name is required';
    END IF;

    IF p_observed IS NULL OR p_expected IS NULL THEN
        RAISE EXCEPTION 'Frequency arrays cannot be NULL';
    END IF;

    category_count := cardinality(p_observed);

    IF category_count < 2
       OR category_count <> cardinality(p_expected) THEN
        RAISE EXCEPTION 'Frequency arrays must have equal lengths >= 2';
    END IF;

    IF p_alpha <= 0 OR p_alpha >= 1 OR NOT isfinite(p_alpha) THEN
        RAISE EXCEPTION 'Significance level must be between zero and one';
    END IF;

    FOR i IN 1..category_count LOOP
        IF p_observed[i] IS NULL OR p_observed[i] < 0 THEN
            RAISE EXCEPTION 'Observed counts must be nonnegative';
        END IF;

        IF p_expected[i] IS NULL
           OR NOT isfinite(p_expected[i])
           OR p_expected[i] < 5 THEN
            RAISE EXCEPTION 'Expected counts must be at least five';
        END IF;

        observed_total := observed_total + p_observed[i];
        expected_total := expected_total + p_expected[i];

        statistic := statistic
            + POWER(p_observed[i] - p_expected[i], 2)
            / p_expected[i];
    END LOOP;

    IF ABS(observed_total - expected_total)
       > 0.000000001 * GREATEST(1, observed_total) THEN
        RAISE EXCEPTION 'Observed and expected totals must match';
    END IF;

    degrees := category_count - 1;

    p_value := 1 - regularized_gamma_p(
        degrees / 2.0,
        statistic / 2
    );

    p_value := LEAST(1.0, GREATEST(0.0, p_value));

    reject_result := p_value < p_alpha;

    INSERT INTO goodness_of_fit_tests (
        test_name,
        significance_level,
        test_statistic,
        degrees_of_freedom,
        p_value,
        reject_null
    )
    VALUES (
        p_test_name,
        p_alpha,
        statistic,
        degrees,
        p_value,
        reject_result
    )
    RETURNING test_id INTO test_identifier;

    FOR i IN 1..category_count LOOP
        INSERT INTO goodness_of_fit_categories (
            test_id,
            category_name,
            observed_count,
            expected_count
        )
        VALUES (
            test_identifier,
            'CATEGORY_' || i,
            p_observed[i],
            p_expected[i]
        );
    END LOOP;

    RETURN test_identifier;
END;
$$;


-- ============================================================
-- 14. Posterior update procedure
-- ============================================================

CREATE OR REPLACE PROCEDURE update_bayesian_experiment(
    p_experiment_id BIGINT,
    p_new_successes BIGINT,
    p_new_failures BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_new_successes < 0 OR p_new_failures < 0 THEN
        RAISE EXCEPTION 'New observations cannot be negative';
    END IF;

    UPDATE bayesian_experiments
    SET
        successes = successes + p_new_successes,
        failures = failures + p_new_failures
    WHERE experiment_id = p_experiment_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Experiment % does not exist', p_experiment_id;
    END IF;
END;
$$;


-- ============================================================
-- 15. Integrity trigger
-- ============================================================

CREATE OR REPLACE FUNCTION validate_simulation_record()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT isfinite(NEW.theoretical_mean)
       OR NOT isfinite(NEW.theoretical_variance)
       OR NOT isfinite(NEW.empirical_mean)
       OR NOT isfinite(NEW.empirical_variance)
       OR NOT isfinite(NEW.minimum_value)
       OR NOT isfinite(NEW.maximum_value) THEN
        RAISE EXCEPTION 'Simulation metrics must be finite';
    END IF;

    IF NEW.theoretical_variance < 0 THEN
        RAISE EXCEPTION 'Theoretical variance cannot be negative';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_simulation
ON simulation_runs;

CREATE TRIGGER trg_validate_simulation
BEFORE INSERT OR UPDATE ON simulation_runs
FOR EACH ROW
EXECUTE FUNCTION validate_simulation_record();


-- ============================================================
-- 16. Reporting view
-- ============================================================

CREATE OR REPLACE VIEW distribution_summary AS
SELECT
    distribution_name,
    COUNT(*) AS simulation_count,
    SUM(sample_size) AS total_observations,
    ROUND(AVG(theoretical_mean)::NUMERIC, 6)
        AS average_theoretical_mean,
    ROUND(AVG(empirical_mean)::NUMERIC, 6)
        AS average_empirical_mean,
    ROUND(AVG(theoretical_variance)::NUMERIC, 6)
        AS average_theoretical_variance,
    ROUND(AVG(empirical_variance)::NUMERIC, 6)
        AS average_empirical_variance
FROM simulation_runs
GROUP BY distribution_name;


-- ============================================================
-- 17. Sample Bayesian experiment
-- ============================================================

INSERT INTO bayesian_experiments (
    experiment_name,
    prior_alpha,
    prior_beta,
    successes,
    failures
)
VALUES (
    'Website conversion experiment',
    2,
    2,
    45,
    55
);


-- ============================================================
-- 18. Transactional workflow examples
-- ============================================================

DO $$
DECLARE
    experiment_identifier BIGINT;
    goodness_test_identifier BIGINT;
BEGIN
    SELECT experiment_id
    INTO experiment_identifier
    FROM bayesian_experiments
    WHERE experiment_name = 'Website conversion experiment'
    ORDER BY experiment_id DESC
    LIMIT 1;

    CALL update_bayesian_experiment(
        experiment_identifier,
        5,
        5
    );

    goodness_test_identifier := evaluate_goodness_of_fit(
        'Customer arrival distribution',
        ARRAY[48, 32, 15, 5]::BIGINT[],
        ARRAY[50, 30, 15, 5]::DOUBLE PRECISION[],
        0.05
    );

    RAISE NOTICE 'Created goodness-of-fit test: %',
        goodness_test_identifier;
END;
$$;


-- ============================================================
-- 19. Distribution retrieval and validation
-- ============================================================

SELECT
    poisson_pmf(3, 4.5) AS poisson_probability,
    poisson_cdf(5, 4.5) AS poisson_cumulative_probability;

SELECT
    gamma_pdf(5, 3, 2) AS gamma_density,
    gamma_cdf(5, 3, 2) AS gamma_cumulative_probability;

SELECT
    beta_pdf(0.4, 2, 5) AS beta_density,
    beta_cdf(0.4, 2, 5) AS beta_cumulative_probability;

SELECT
    chi_square_pdf(5, 4) AS chi_square_density,
    chi_square_cdf(5, 4) AS chi_square_cumulative_probability;


-- ============================================================
-- 20. Theoretical moments report
-- ============================================================

SELECT
    'POISSON' AS distribution,
    4.5 AS theoretical_mean,
    4.5 AS theoretical_variance

UNION ALL

SELECT
    'GAMMA',
    3.0 * 2.0,
    3.0 * POWER(2.0, 2)

UNION ALL

SELECT
    'BETA',
    2.0 / 7.0,
    2.0 * 5.0 / (POWER(7.0, 2) * 8.0)

UNION ALL

SELECT
    'CHI_SQUARE',
    4.0,
    8.0;


-- ============================================================
-- 21. Bayesian posterior retrieval
-- ============================================================

SELECT
    experiment_name,
    prior_alpha,
    prior_beta,
    successes,
    failures,
    posterior_alpha,
    posterior_beta,
    posterior_mean,
    posterior_variance
FROM bayesian_posterior_report
ORDER BY experiment_id;


-- ============================================================
-- 22. Goodness-of-fit reporting
-- ============================================================

SELECT
    test_id,
    test_name,
    test_statistic,
    degrees_of_freedom,
    p_value,
    significance_level,
    CASE
        WHEN reject_null THEN 'REJECT NULL'
        ELSE 'FAIL TO REJECT NULL'
    END AS statistical_decision,
    executed_at
FROM goodness_of_fit_tests
ORDER BY executed_at DESC;


-- ============================================================
-- 23. Category-level statistical evaluation
-- ============================================================

SELECT
    t.test_name,
    c.category_name,
    c.observed_count,
    c.expected_count,
    ROUND(
        POWER(c.observed_count - c.expected_count, 2)
        / c.expected_count::NUMERIC,
        6
    ) AS category_chi_square_contribution
FROM goodness_of_fit_categories c
JOIN goodness_of_fit_tests t
    ON t.test_id = c.test_id
ORDER BY t.test_id, c.category_id;


-- ============================================================
-- 24. Distribution registry retrieval
-- ============================================================

SELECT
    distribution_name,
    distribution_category,
    description
FROM distribution_registry
ORDER BY distribution_id;


COMMIT;
