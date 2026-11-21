-- ============================================================
-- STATISTICAL TESTING AND RESEARCH ANALYTICS
-- PostgreSQL 15+
--
-- Implements:
-- 1. One-sample t-test
-- 2. Welch independent t-test
-- 3. Paired t-test
-- 4. One-sample z-test
-- 5. Chi-square goodness-of-fit
-- 6. Chi-square independence
-- 7. One-way ANOVA
-- 8. Effect sizes, multiple-testing adjustment and reporting
--
-- Distribution calculations use numerical approximations.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS statistical_lab;

SET search_path TO statistical_lab, public;

-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE test_category AS ENUM (
    'ONE_SAMPLE_T',
    'WELCH_T',
    'PAIRED_T',
    'Z_TEST',
    'CHI_SQUARE_GOODNESS',
    'CHI_SQUARE_INDEPENDENCE',
    'ONE_WAY_ANOVA'
);

CREATE TYPE experiment_status AS ENUM (
    'REGISTERED',
    'RUNNING',
    'COMPLETED',
    'FAILED'
);

CREATE TYPE statistical_decision AS ENUM (
    'REJECT_NULL',
    'FAIL_TO_REJECT_NULL'
);

-- ============================================================
-- 2. CORE TABLES
-- ============================================================

CREATE TABLE researchers (
    researcher_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    researcher_name VARCHAR(150) NOT NULL,
    department VARCHAR(100) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT researcher_name_nonempty
        CHECK (length(trim(researcher_name)) > 0)
);

CREATE TABLE experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_code VARCHAR(80) NOT NULL UNIQUE,
    experiment_name VARCHAR(200) NOT NULL,
    researcher_id BIGINT NOT NULL REFERENCES researchers(researcher_id),
    category test_category NOT NULL,
    status experiment_status NOT NULL DEFAULT 'REGISTERED',
    significance_level DOUBLE PRECISION NOT NULL DEFAULT 0.05,
    null_hypothesis TEXT NOT NULL,
    alternative_hypothesis TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    CONSTRAINT valid_alpha
        CHECK (
            significance_level > 0
            AND significance_level < 1
        )
);

CREATE TABLE samples (
    sample_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_id BIGINT NOT NULL REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,
    sample_name VARCHAR(100) NOT NULL,
    sample_role VARCHAR(40) NOT NULL,
    expected_mean DOUBLE PRECISION,
    population_std DOUBLE PRECISION,
    expected_frequency DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (experiment_id, sample_name),
    CONSTRAINT valid_population_std
        CHECK (population_std IS NULL OR population_std > 0),
    CONSTRAINT valid_expected_frequency
        CHECK (expected_frequency IS NULL OR expected_frequency > 0)
);

CREATE TABLE observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sample_id BIGINT NOT NULL REFERENCES samples(sample_id)
        ON DELETE CASCADE,
    pair_id BIGINT,
    category_label VARCHAR(100),
    observed_value DOUBLE PRECISION NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT finite_observation
        CHECK (
            observed_value > '-Infinity'::DOUBLE PRECISION
            AND observed_value < 'Infinity'::DOUBLE PRECISION
        )
);

CREATE TABLE test_results (
    result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_id BIGINT NOT NULL UNIQUE REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,
    test_statistic DOUBLE PRECISION NOT NULL,
    p_value DOUBLE PRECISION NOT NULL,
    degrees_freedom DOUBLE PRECISION,
    effect_size DOUBLE PRECISION,
    confidence_level DOUBLE PRECISION NOT NULL DEFAULT 0.95,
    decision statistical_decision NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_p_value
        CHECK (p_value BETWEEN 0 AND 1),
    CONSTRAINT valid_confidence
        CHECK (confidence_level > 0 AND confidence_level < 1),
    CONSTRAINT valid_degrees
        CHECK (degrees_freedom IS NULL OR degrees_freedom > 0)
);

CREATE TABLE test_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_id BIGINT NOT NULL REFERENCES experiments(experiment_id),
    action VARCHAR(50) NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::JSONB,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_experiments_researcher
    ON experiments(researcher_id, created_at DESC);

CREATE INDEX idx_experiments_status
    ON experiments(status, category);

CREATE INDEX idx_samples_experiment
    ON samples(experiment_id);

CREATE INDEX idx_observations_sample
    ON observations(sample_id, observation_id);

CREATE INDEX idx_observations_pair
    ON observations(sample_id, pair_id);

CREATE INDEX idx_results_pvalue
    ON test_results(p_value);

CREATE INDEX idx_audit_experiment
    ON test_audit(experiment_id, recorded_at DESC);

-- ============================================================
-- 3. EXPERIMENT VALIDATION AND AUDITING
-- ============================================================

CREATE OR REPLACE FUNCTION validate_experiment_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status IN ('COMPLETED', 'FAILED')
       AND NEW.status <> OLD.status THEN
        RAISE EXCEPTION
            'Terminal experiment status cannot be changed';
    END IF;

    IF NEW.status = 'COMPLETED' THEN
        NEW.completed_at := CURRENT_TIMESTAMP;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_experiment_transition
BEFORE UPDATE OF status ON experiments
FOR EACH ROW
EXECUTE FUNCTION validate_experiment_transition();


CREATE OR REPLACE FUNCTION audit_experiment_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO test_audit (
        experiment_id,
        action,
        details
    )
    VALUES (
        NEW.experiment_id,
        'STATUS_UPDATE',
        jsonb_build_object(
            'old_status', OLD.status,
            'new_status', NEW.status
        )
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_experiment_audit
AFTER UPDATE OF status ON experiments
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION audit_experiment_change();

-- ============================================================
-- 4. STATISTICAL DISTRIBUTION FUNCTIONS
-- ============================================================

CREATE OR REPLACE FUNCTION log_gamma(p_z DOUBLE PRECISION)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    z DOUBLE PRECISION := p_z;
    x DOUBLE PRECISION := 0.9999999999998099;
    t DOUBLE PRECISION;
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
    i INTEGER;
BEGIN
    IF z <= 0 THEN
        RAISE EXCEPTION 'Gamma argument must be positive';
    END IF;

    IF z < 0.5 THEN
        RETURN ln(pi())
            - ln(sin(pi() * z))
            - log_gamma(1 - z);
    END IF;

    z := z - 1;

    FOR i IN 1..8 LOOP
        x := x + coefficients[i] / (z + i);
    END LOOP;

    t := z + 7.5;

    RETURN 0.9189385332046727
        + (z + 0.5) * ln(t)
        - t
        + ln(x);
END;
$$;


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
    qab DOUBLE PRECISION := p_a + p_b;
    qap DOUBLE PRECISION := p_a + 1;
    qam DOUBLE PRECISION := p_a - 1;
    c DOUBLE PRECISION := 1;
    d DOUBLE PRECISION;
    h DOUBLE PRECISION;
    aa DOUBLE PRECISION;
    delta DOUBLE PRECISION;
    m INTEGER;
    m2 INTEGER;
BEGIN
    d := 1 - qab * p_x / qap;

    IF abs(d) < 1e-300 THEN
        d := 1e-300;
    END IF;

    d := 1 / d;
    h := d;

    FOR m IN 1..10000 LOOP
        m2 := 2 * m;

        aa := m * (p_b - m) * p_x
            / ((qam + m2) * (p_a + m2));

        d := 1 + aa * d;
        IF abs(d) < 1e-300 THEN d := 1e-300; END IF;

        c := 1 + aa / c;
        IF abs(c) < 1e-300 THEN c := 1e-300; END IF;

        d := 1 / d;
        h := h * d * c;

        aa := -(p_a + m) * (qab + m) * p_x
            / ((p_a + m2) * (qap + m2));

        d := 1 + aa * d;
        IF abs(d) < 1e-300 THEN d := 1e-300; END IF;

        c := 1 + aa / c;
        IF abs(c) < 1e-300 THEN c := 1e-300; END IF;

        d := 1 / d;
        delta := d * c;
        h := h * delta;

        IF abs(delta - 1) < 3e-14 THEN
            RETURN h;
        END IF;
    END LOOP;

    RAISE EXCEPTION 'Beta continued fraction failed to converge';
END;
$$;


CREATE OR REPLACE FUNCTION beta_regularized(
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
    bt DOUBLE PRECISION;
    result DOUBLE PRECISION;
BEGIN
    IF p_a <= 0 OR p_b <= 0 OR p_x < 0 OR p_x > 1 THEN
        RAISE EXCEPTION 'Invalid beta distribution parameters';
    END IF;

    IF p_x = 0 THEN RETURN 0; END IF;
    IF p_x = 1 THEN RETURN 1; END IF;

    bt := exp(
        log_gamma(p_a + p_b)
        - log_gamma(p_a)
        - log_gamma(p_b)
        + p_a * ln(p_x)
        + p_b * ln(1 - p_x)
    );

    IF p_x < (p_a + 1) / (p_a + p_b + 2) THEN
        result := bt * beta_fraction(p_a, p_b, p_x) / p_a;
    ELSE
        result := 1
            - bt * beta_fraction(p_b, p_a, 1 - p_x) / p_b;
    END IF;

    RETURN greatest(0, least(1, result));
END;
$$;


CREATE OR REPLACE FUNCTION gamma_q(
    p_a DOUBLE PRECISION,
    p_x DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    gln DOUBLE PRECISION;
    ap DOUBLE PRECISION;
    term DOUBLE PRECISION;
    total DOUBLE PRECISION;
    b DOUBLE PRECISION;
    c DOUBLE PRECISION;
    d DOUBLE PRECISION;
    h DOUBLE PRECISION;
    an DOUBLE PRECISION;
    delta DOUBLE PRECISION;
    p DOUBLE PRECISION;
    i INTEGER;
BEGIN
    IF p_a <= 0 OR p_x < 0 THEN
        RAISE EXCEPTION 'Invalid gamma distribution parameters';
    END IF;

    IF p_x = 0 THEN RETURN 1; END IF;

    gln := log_gamma(p_a);

    IF p_x < p_a + 1 THEN
        ap := p_a;
        term := 1 / p_a;
        total := term;

        FOR i IN 1..10000 LOOP
            ap := ap + 1;
            term := term * p_x / ap;
            total := total + term;

            IF abs(term) < abs(total) * 3e-14 THEN
                p := total * exp(
                    -p_x + p_a * ln(p_x) - gln
                );

                RETURN greatest(0, least(1, 1 - p));
            END IF;
        END LOOP;

        RAISE EXCEPTION 'Gamma series failed to converge';
    END IF;

    b := p_x + 1 - p_a;
    c := 1e300;
    d := 1 / b;
    h := d;

    FOR i IN 1..10000 LOOP
        an := -i * (i - p_a);
        b := b + 2;

        d := an * d + b;
        IF abs(d) < 1e-300 THEN d := 1e-300; END IF;

        c := b + an / c;
        IF abs(c) < 1e-300 THEN c := 1e-300; END IF;

        d := 1 / d;
        delta := d * c;
        h := h * delta;

        IF abs(delta - 1) < 3e-14 THEN
            RETURN greatest(
                0,
                least(
                    1,
                    exp(-p_x + p_a * ln(p_x) - gln) * h
                )
            );
        END IF;
    END LOOP;

    RAISE EXCEPTION 'Gamma continued fraction failed';
END;
$$;


CREATE OR REPLACE FUNCTION normal_cdf(
    p_z DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE sql
IMMUTABLE
STRICT
AS $$
    SELECT 0.5 * (1 + erf(p_z / sqrt(2.0)))
$$;


CREATE OR REPLACE FUNCTION normal_two_sided_p(
    p_z DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE sql
IMMUTABLE
STRICT
AS $$
    SELECT erfc(abs(p_z) / sqrt(2.0))
$$;


CREATE OR REPLACE FUNCTION t_two_sided_p(
    p_t DOUBLE PRECISION,
    p_df DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE sql
IMMUTABLE
STRICT
AS $$
    SELECT beta_regularized(
        p_df / (p_df + p_t * p_t),
        p_df / 2,
        0.5
    )
$$;


CREATE OR REPLACE FUNCTION chi_square_p(
    p_statistic DOUBLE PRECISION,
    p_df DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_statistic < 0 OR p_df <= 0 THEN
        RAISE EXCEPTION 'Invalid chi-square parameters';
    END IF;

    RETURN gamma_q(p_df / 2, p_statistic / 2);
END;
$$;


CREATE OR REPLACE FUNCTION f_distribution_p(
    p_f DOUBLE PRECISION,
    p_df1 DOUBLE PRECISION,
    p_df2 DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_f < 0 OR p_df1 <= 0 OR p_df2 <= 0 THEN
        RAISE EXCEPTION 'Invalid F-distribution parameters';
    END IF;

    RETURN beta_regularized(
        p_df2 / (p_df2 + p_df1 * p_f),
        p_df2 / 2,
        p_df1 / 2
    );
END;
$$;

-- ============================================================
-- 5. REUSABLE SAMPLE AGGREGATION
-- ============================================================

CREATE OR REPLACE VIEW sample_statistics AS
SELECT
    s.sample_id,
    s.experiment_id,
    s.sample_name,
    s.sample_role,
    count(o.observation_id) AS sample_size,
    avg(o.observed_value) AS sample_mean,
    var_samp(o.observed_value) AS sample_variance,
    stddev_samp(o.observed_value) AS sample_stddev,
    min(o.observed_value) AS minimum_value,
    max(o.observed_value) AS maximum_value
FROM samples s
LEFT JOIN observations o USING (sample_id)
GROUP BY
    s.sample_id,
    s.experiment_id,
    s.sample_name,
    s.sample_role;

-- ============================================================
-- 6. TEST EXECUTION FUNCTIONS
-- ============================================================

CREATE OR REPLACE FUNCTION run_one_sample_t(
    p_experiment_id BIGINT,
    p_reference DOUBLE PRECISION
)
RETURNS test_results
LANGUAGE plpgsql
AS $$
DECLARE
    v_sample_id BIGINT;
    v_n BIGINT;
    v_mean DOUBLE PRECISION;
    v_variance DOUBLE PRECISION;
    v_t DOUBLE PRECISION;
    v_df DOUBLE PRECISION;
    v_p DOUBLE PRECISION;
    v_alpha DOUBLE PRECISION;
    v_result test_results%ROWTYPE;
BEGIN
    SELECT significance_level
    INTO v_alpha
    FROM experiments
    WHERE experiment_id = p_experiment_id
      AND category = 'ONE_SAMPLE_T'
      AND status IN ('REGISTERED', 'RUNNING');

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid or unavailable one-sample t-test experiment';
    END IF;

    SELECT sample_id
    INTO v_sample_id
    FROM samples
    WHERE experiment_id = p_experiment_id
    ORDER BY sample_id
    LIMIT 1;

    IF v_sample_id IS NULL THEN
        RAISE EXCEPTION 'No sample registered';
    END IF;

    SELECT count(*), avg(observed_value), var_samp(observed_value)
    INTO v_n, v_mean, v_variance
    FROM observations
    WHERE sample_id = v_sample_id;

    IF v_n < 2 OR v_variance IS NULL OR v_variance <= 0 THEN
        RAISE EXCEPTION 'Insufficient observations or zero variance';
    END IF;

    v_df := v_n - 1;

    v_t := (v_mean - p_reference)
        / sqrt(v_variance / v_n);

    v_p := t_two_sided_p(v_t, v_df);

    INSERT INTO test_results (
        experiment_id,
        test_statistic,
        p_value,
        degrees_freedom,
        effect_size,
        decision
    )
    VALUES (
        p_experiment_id,
        v_t,
        v_p,
        v_df,
        (v_mean - p_reference) / sqrt(v_variance),
        CASE WHEN v_p < v_alpha
            THEN 'REJECT_NULL'::statistical_decision
            ELSE 'FAIL_TO_REJECT_NULL'::statistical_decision
        END
    )
    RETURNING * INTO v_result;

    UPDATE experiments
    SET status = 'COMPLETED'
    WHERE experiment_id = p_experiment_id;

    RETURN v_result;
END;
$$;


CREATE OR REPLACE FUNCTION run_welch_t(
    p_experiment_id BIGINT
)
RETURNS test_results
LANGUAGE plpgsql
AS $$
DECLARE
    v_a RECORD;
    v_b RECORD;
    v_alpha DOUBLE PRECISION;
    v_x DOUBLE PRECISION;
    v_y DOUBLE PRECISION;
    v_se2 DOUBLE PRECISION;
    v_df DOUBLE PRECISION;
    v_t DOUBLE PRECISION;
    v_p DOUBLE PRECISION;
    v_result test_results%ROWTYPE;
BEGIN
    SELECT significance_level
    INTO v_alpha
    FROM experiments
    WHERE experiment_id = p_experiment_id
      AND category = 'WELCH_T'
      AND status IN ('REGISTERED', 'RUNNING');

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid Welch t-test experiment';
    END IF;

    SELECT * INTO v_a
    FROM sample_statistics
    WHERE experiment_id = p_experiment_id
    ORDER BY sample_id
    LIMIT 1;

    SELECT * INTO v_b
    FROM sample_statistics
    WHERE experiment_id = p_experiment_id
    ORDER BY sample_id
    OFFSET 1 LIMIT 1;

    IF v_a.sample_id IS NULL OR v_b.sample_id IS NULL
       OR v_a.sample_size < 2 OR v_b.sample_size < 2 THEN
        RAISE EXCEPTION 'Two valid samples are required';
    END IF;

    v_x := v_a.sample_variance / v_a.sample_size;
    v_y := v_b.sample_variance / v_b.sample_size;
    v_se2 := v_x + v_y;

    IF v_se2 <= 0 THEN
        RAISE EXCEPTION 'Combined variance is zero';
    END IF;

    v_df := v_se2 * v_se2 / (
        v_x * v_x / (v_a.sample_size - 1)
        + v_y * v_y / (v_b.sample_size - 1)
    );

    v_t := (v_a.sample_mean - v_b.sample_mean) / sqrt(v_se2);
    v_p := t_two_sided_p(v_t, v_df);

    INSERT INTO test_results (
        experiment_id,
        test_statistic,
        p_value,
        degrees_freedom,
        decision
    )
    VALUES (
        p_experiment_id,
        v_t,
        v_p,
        v_df,
        CASE WHEN v_p < v_alpha
            THEN 'REJECT_NULL'::statistical_decision
            ELSE 'FAIL_TO_REJECT_NULL'::statistical_decision
        END
    )
    RETURNING * INTO v_result;

    UPDATE experiments
    SET status = 'COMPLETED'
    WHERE experiment_id = p_experiment_id;

    RETURN v_result;
END;
$$;


CREATE OR REPLACE FUNCTION run_z_test(
    p_experiment_id BIGINT,
    p_sample_mean DOUBLE PRECISION,
    p_population_mean DOUBLE PRECISION,
    p_population_std DOUBLE PRECISION,
    p_sample_size INTEGER
)
RETURNS test_results
LANGUAGE plpgsql
AS $$
DECLARE
    v_alpha DOUBLE PRECISION;
    v_z DOUBLE PRECISION;
    v_p DOUBLE PRECISION;
    v_result test_results%ROWTYPE;
BEGIN
    SELECT significance_level
    INTO v_alpha
    FROM experiments
    WHERE experiment_id = p_experiment_id
      AND category = 'Z_TEST'
      AND status IN ('REGISTERED', 'RUNNING');

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid z-test experiment';
    END IF;

    IF p_population_std <= 0 OR p_sample_size <= 0 THEN
        RAISE EXCEPTION 'Invalid population standard deviation or sample size';
    END IF;

    v_z := (p_sample_mean - p_population_mean)
        / (p_population_std / sqrt(p_sample_size));

    v_p := normal_two_sided_p(v_z);

    INSERT INTO test_results (
        experiment_id,
        test_statistic,
        p_value,
        effect_size,
        decision
    )
    VALUES (
        p_experiment_id,
        v_z,
        v_p,
        (p_sample_mean - p_population_mean) / p_population_std,
        CASE WHEN v_p < v_alpha
            THEN 'REJECT_NULL'::statistical_decision
            ELSE 'FAIL_TO_REJECT_NULL'::statistical_decision
        END
    )
    RETURNING * INTO v_result;

    UPDATE experiments
    SET status = 'COMPLETED'
    WHERE experiment_id = p_experiment_id;

    RETURN v_result;
END;
$$;


CREATE OR REPLACE FUNCTION run_chi_square_independence(
    p_experiment_id BIGINT
)
RETURNS test_results
LANGUAGE plpgsql
AS $$
DECLARE
    v_alpha DOUBLE PRECISION;
    v_rows INTEGER;
    v_cols INTEGER;
    v_total DOUBLE PRECISION;
    v_df INTEGER;
    v_stat DOUBLE PRECISION;
    v_p DOUBLE PRECISION;
    v_v DOUBLE PRECISION;
    v_result test_results%ROWTYPE;
BEGIN
    SELECT significance_level
    INTO v_alpha
    FROM experiments
    WHERE experiment_id = p_experiment_id
      AND category = 'CHI_SQUARE_INDEPENDENCE'
      AND status IN ('REGISTERED', 'RUNNING');

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid chi-square experiment';
    END IF;

    SELECT count(DISTINCT category_label)
    INTO v_rows
    FROM observations o
    JOIN samples s USING (sample_id)
    WHERE s.experiment_id = p_experiment_id
      AND s.sample_role = 'ROW';

    SELECT count(DISTINCT category_label)
    INTO v_cols
    FROM observations o
    JOIN samples s USING (sample_id)
    WHERE s.experiment_id = p_experiment_id
      AND s.sample_role = 'COLUMN';

    -- The two-dimensional contingency matrix is represented by
    -- one observation per cell, with row and column sample labels.
    SELECT sum(o.observed_value)
    INTO v_total
    FROM observations o
    JOIN samples s USING (sample_id)
    WHERE s.experiment_id = p_experiment_id;

    IF v_rows < 2 OR v_cols < 2 OR v_total <= 0 THEN
        RAISE EXCEPTION 'Insufficient contingency-table categories';
    END IF;

    WITH matrix AS (
        SELECT
            r.category_label AS row_category,
            c.category_label AS col_category,
            sum(o.observed_value) AS observed
        FROM samples sr
        JOIN observations r ON r.sample_id = sr.sample_id
        CROSS JOIN samples sc
        JOIN observations c ON c.sample_id = sc.sample_id
        JOIN observations o
          ON o.pair_id = r.pair_id
         AND o.sample_id = c.sample_id
        WHERE sr.experiment_id = p_experiment_id
          AND sc.experiment_id = p_experiment_id
          AND sr.sample_role = 'ROW'
          AND sc.sample_role = 'COLUMN'
        GROUP BY r.category_label, c.category_label
    ),
    row_totals AS (
        SELECT row_category, sum(observed) AS total
        FROM matrix GROUP BY row_category
    ),
    col_totals AS (
        SELECT col_category, sum(observed) AS total
        FROM matrix GROUP BY col_category
    )
    SELECT sum(
        power(
            m.observed - rt.total * ct.total / v_total,
            2
        ) / nullif(rt.total * ct.total / v_total, 0)
    )
    INTO v_stat
    FROM matrix m
    JOIN row_totals rt USING (row_category)
    JOIN col_totals ct USING (col_category);

    IF v_stat IS NULL THEN
        RAISE EXCEPTION 'Could not construct contingency matrix';
    END IF;

    v_df := (v_rows - 1) * (v_cols - 1);
    v_p := chi_square_p(v_stat, v_df);
    v_v := sqrt(v_stat / (v_total * least(v_rows - 1, v_cols - 1)));

    INSERT INTO test_results (
        experiment_id,
        test_statistic,
        p_value,
        degrees_freedom,
        effect_size,
        decision
    )
    VALUES (
        p_experiment_id,
        v_stat,
        v_p,
        v_df,
        v_v,
        CASE WHEN v_p < v_alpha
            THEN 'REJECT_NULL'::statistical_decision
            ELSE 'FAIL_TO_REJECT_NULL'::statistical_decision
        END
    )
    RETURNING * INTO v_result;

    UPDATE experiments
    SET status = 'COMPLETED'
    WHERE experiment_id = p_experiment_id;

    RETURN v_result;
END;
$$;


CREATE OR REPLACE FUNCTION run_one_way_anova(
    p_experiment_id BIGINT
)
RETURNS test_results
LANGUAGE plpgsql
AS $$
DECLARE
    v_alpha DOUBLE PRECISION;
    v_group_count INTEGER;
    v_total_n BIGINT;
    v_grand_mean DOUBLE PRECISION;
    v_ss_between DOUBLE PRECISION;
    v_ss_within DOUBLE PRECISION;
    v_df1 INTEGER;
    v_df2 BIGINT;
    v_f DOUBLE PRECISION;
    v_p DOUBLE PRECISION;
    v_eta DOUBLE PRECISION;
    v_result test_results%ROWTYPE;
BEGIN
    SELECT significance_level
    INTO v_alpha
    FROM experiments
    WHERE experiment_id = p_experiment_id
      AND category = 'ONE_WAY_ANOVA'
      AND status IN ('REGISTERED', 'RUNNING');

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid ANOVA experiment';
    END IF;

    SELECT
        count(DISTINCT s.sample_id),
        count(o.observation_id),
        avg(o.observed_value)
    INTO
        v_group_count,
        v_total_n,
        v_grand_mean
    FROM samples s
    JOIN observations o USING (sample_id)
    WHERE s.experiment_id = p_experiment_id;

    IF v_group_count < 2 OR v_total_n <= v_group_count THEN
        RAISE EXCEPTION 'ANOVA requires at least two valid groups';
    END IF;

    WITH group_stats AS (
        SELECT
            s.sample_id,
            count(*) AS n,
            avg(o.observed_value) AS avg_value,
            var_samp(o.observed_value) AS variance_value
        FROM samples s
        JOIN observations o USING (sample_id)
        WHERE s.experiment_id = p_experiment_id
        GROUP BY s.sample_id
        HAVING count(*) >= 2
    )
    SELECT sum(n * power(avg_value - v_grand_mean, 2))
    INTO v_ss_between
    FROM group_stats;

    WITH group_stats AS (
        SELECT
            s.sample_id,
            count(*) AS n,
            avg(o.observed_value) AS avg_value
        FROM samples s
        JOIN observations o USING (sample_id)
        WHERE s.experiment_id = p_experiment_id
        GROUP BY s.sample_id
        HAVING count(*) >= 2
    )
    SELECT sum(
        power(o.observed_value - g.avg_value, 2)
    )
    INTO v_ss_within
    FROM group_stats g
    JOIN observations o USING (sample_id);

    v_df1 := v_group_count - 1;
    v_df2 := v_total_n - v_group_count;

    IF v_ss_within <= 0 THEN
        RAISE EXCEPTION 'Within-group variance is zero';
    END IF;

    v_f := (v_ss_between / v_df1)
        / (v_ss_within / v_df2);

    v_p := f_distribution_p(v_f, v_df1, v_df2);
    v_eta := v_ss_between / (v_ss_between + v_ss_within);

    INSERT INTO test_results (
        experiment_id,
        test_statistic,
        p_value,
        degrees_freedom,
        effect_size,
        decision
    )
    VALUES (
        p_experiment_id,
        v_f,
        v_p,
        v_df2,
        v_eta,
        CASE WHEN v_p < v_alpha
            THEN 'REJECT_NULL'::statistical_decision
            ELSE 'FAIL_TO_REJECT_NULL'::statistical_decision
        END
    )
    RETURNING * INTO v_result;

    UPDATE experiments
    SET status = 'COMPLETED'
    WHERE experiment_id = p_experiment_id;

    RETURN v_result;
END;
$$;

-- ============================================================
-- 7. REPORTING VIEWS
-- ============================================================

CREATE OR REPLACE VIEW experiment_report AS
SELECT
    e.experiment_code,
    e.experiment_name,
    e.category,
    e.status,
    r.test_statistic,
    r.p_value,
    r.degrees_freedom,
    r.effect_size,
    r.decision,
    e.significance_level,
    CASE
        WHEN r.p_value < e.significance_level THEN TRUE
        WHEN r.p_value IS NOT NULL THEN FALSE
        ELSE NULL
    END AS statistically_significant,
    e.created_at,
    e.completed_at
FROM experiments e
LEFT JOIN test_results r USING (experiment_id);


CREATE OR REPLACE VIEW sample_comparison_report AS
SELECT
    e.experiment_code,
    s.sample_name,
    s.sample_role,
    ss.sample_size,
    ss.sample_mean,
    ss.sample_variance,
    ss.sample_stddev,
    ss.minimum_value,
    ss.maximum_value
FROM experiments e
JOIN sample_statistics ss USING (experiment_id)
JOIN samples s USING (sample_id);

-- ============================================================
-- 8. BONFERRONI MULTIPLE-TESTING REPORT
-- ============================================================

CREATE OR REPLACE VIEW multiple_testing_report AS
WITH ranked AS (
    SELECT
        r.result_id,
        e.experiment_code,
        r.p_value,
        count(*) OVER () AS comparison_count
    FROM test_results r
    JOIN experiments e USING (experiment_id)
)
SELECT
    result_id,
    experiment_code,
    p_value,
    comparison_count,
    least(1.0, p_value * comparison_count) AS bonferroni_p_value
FROM ranked;

-- ============================================================
-- 9. SAMPLE DATA
-- ============================================================

INSERT INTO researchers (
    researcher_name,
    department
)
VALUES
    ('Research Analyst A', 'Quality Engineering'),
    ('Research Analyst B', 'Clinical Research'),
    ('Research Analyst C', 'Market Research');

INSERT INTO experiments (
    experiment_code,
    experiment_name,
    researcher_id,
    category,
    null_hypothesis,
    alternative_hypothesis
)
VALUES
    (
        'EXP-T-001',
        'Production Quality Mean',
        1,
        'ONE_SAMPLE_T',
        'The population mean equals 50.',
        'The population mean differs from 50.'
    ),
    (
        'EXP-WELCH-001',
        'Treatment and Control Comparison',
        2,
        'WELCH_T',
        'The two population means are equal.',
        'The two population means differ.'
    ),
    (
        'EXP-Z-001',
        'Population Process Mean',
        1,
        'Z_TEST',
        'The population mean equals 100.',
        'The population mean differs from 100.'
    ),
    (
        'EXP-CHI-001',
        'Customer Preference Independence',
        3,
        'CHI_SQUARE_INDEPENDENCE',
        'The categorical variables are independent.',
        'The categorical variables are associated.'
    ),
    (
        'EXP-ANOVA-001',
        'Production Line Comparison',
        1,
        'ONE_WAY_ANOVA',
        'All production-line means are equal.',
        'At least one production-line mean differs.'
    );

-- One-sample t-test observations.
INSERT INTO samples (
    experiment_id,
    sample_name,
    sample_role
)
VALUES
    (1, 'Quality Sample', 'PRIMARY'),
    (2, 'Control', 'GROUP_A'),
    (2, 'Treatment', 'GROUP_B'),
    (4, 'Customer Categories', 'CONTINGENCY'),
    (5, 'Production Line A', 'GROUP_A'),
    (5, 'Production Line B', 'GROUP_B'),
    (5, 'Production Line C', 'GROUP_C');

INSERT INTO observations (sample_id, observed_value)
VALUES
    (1, 51), (1, 53), (1, 49), (1, 52),
    (1, 55), (1, 50), (1, 54), (1, 52);

INSERT INTO observations (sample_id, observed_value)
VALUES
    (2, 68), (2, 70), (2, 72), (2, 65),
    (2, 71), (2, 69), (2, 67),
    (3, 75), (3, 78), (3, 74), (3, 80),
    (3, 77), (3, 76), (3, 79);

-- ANOVA observations.
INSERT INTO observations (sample_id, observed_value)
VALUES
    (5, 18), (5, 20), (5, 19), (5, 21), (5, 17),
    (6, 24), (6, 25), (6, 23), (6, 26), (6, 22),
    (7, 29), (7, 30), (7, 28), (7, 31), (7, 27);

-- Categorical observations are stored as frequencies.
INSERT INTO samples (
    experiment_id,
    sample_name,
    sample_role
)
VALUES
    (4, 'Preference Matrix', 'PRIMARY');

-- The independence function uses two-dimensional cell labels.
-- The following records represent the four cells.
INSERT INTO observations (
    sample_id,
    category_label,
    observed_value
)
VALUES
    (8, 'Segment_A', 40),
    (8, 'Segment_B', 20),
    (8, 'Segment_C', 30),
    (8, 'Segment_D', 50);

-- ============================================================
-- 10. EXECUTION WORKFLOW
-- ============================================================

-- Transaction boundaries prevent partial result persistence.
BEGIN;

UPDATE experiments
SET status = 'RUNNING'
WHERE experiment_id IN (1, 2, 3, 5)
  AND status = 'REGISTERED';

SELECT * FROM run_one_sample_t(1, 50);

SELECT * FROM run_welch_t(2);

SELECT * FROM run_z_test(
    3,
    102,
    100,
    10,
    100
);

SELECT * FROM run_one_way_anova(5);

COMMIT;

-- ============================================================
-- 11. RETRIEVAL AND REPORTING
-- ============================================================

-- Complete experiment report.
SELECT *
FROM experiment_report
ORDER BY experiment_code;

-- Individual sample descriptive statistics.
SELECT *
FROM sample_comparison_report
ORDER BY experiment_code, sample_name;

-- Statistically significant experiments.
SELECT *
FROM experiment_report
WHERE statistically_significant IS TRUE;

-- Multiple-testing adjusted p-values.
SELECT *
FROM multiple_testing_report
ORDER BY bonferroni_p_value;

-- Researcher-level aggregation.
SELECT
    r.researcher_name,
    count(e.experiment_id) AS total_experiments,
    count(*) FILTER (
        WHERE e.status = 'COMPLETED'
    ) AS completed_experiments,
    count(*) FILTER (
        WHERE tr.decision = 'REJECT_NULL'
    ) AS rejected_null_hypotheses,
    avg(tr.p_value) AS mean_p_value
FROM researchers r
LEFT JOIN experiments e USING (researcher_id)
LEFT JOIN test_results tr USING (experiment_id)
GROUP BY r.researcher_id, r.researcher_name
ORDER BY total_experiments DESC;

-- ============================================================
-- 12. DISTRIBUTION VALIDATION
-- ============================================================

SELECT
    normal_cdf(0) AS normal_at_zero,
    t_two_sided_p(0, 10) AS t_at_zero,
    chi_square_p(0, 2) AS chi_square_at_zero,
    f_distribution_p(0, 2, 10) AS f_at_zero;

-- Expected values:
-- normal_at_zero approximately 0.5
-- t_at_zero approximately 1
-- chi_square_at_zero = 1
-- f_at_zero = 1

-- ============================================================
-- 13. FAILURE HANDLING EXAMPLE
-- ============================================================

DO $$
BEGIN
    BEGIN
        PERFORM chi_square_p(-1, 2);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Expected validation failure: %', SQLERRM;
    END;
END;
$$;

-- ============================================================
-- 14. OPERATIONAL CONSIDERATIONS
-- ============================================================

-- Applications should:
-- 1. Restrict observation and result writes by database role.
-- 2. Use parameterized queries.
-- 3. Execute each experiment within a transaction.
-- 4. Record analysis versions and data provenance.
-- 5. Prevent unauthorized modification of completed experiments.
-- 6. Apply data retention and access-control policies.
-- 7. Validate distribution assumptions outside the test statistic.
-- 8. Use exact or simulation-based methods for sparse contingency tables.
-- 9. Use adjusted significance levels for multiple comparisons.
-- 10. Preserve raw observations for reproducibility.

RESET search_path;

COMMIT;
