-- ============================================================
-- ADVANCED PROBABILITY
-- PostgreSQL stochastic modeling and Markov-chain database
-- ============================================================
--
-- Implements:
-- 1. Probability model management
-- 2. Finite-state Markov chains
-- 3. Transition probability validation
-- 4. Stationary distribution computation
-- 5. Simulation trajectories
-- 6. Martingale difference observations
-- 7. Long-run reward evaluation
-- 8. Ergodicity metadata and reporting
--
-- PostgreSQL 14+
--
-- The stationary solver uses row-vector multiplication:
-- pi_next[j] = SUM(pi[i] * P[i,j]).
--
-- Power iteration can fail to converge for periodic chains.
-- A non-converged result is explicitly reported.

BEGIN;

DROP SCHEMA IF EXISTS advanced_probability CASCADE;

CREATE SCHEMA advanced_probability;

SET search_path TO advanced_probability, public;

-- ============================================================
-- 1. ENUMERATED DOMAIN TYPES
-- ============================================================

CREATE TYPE model_status AS ENUM (
    'draft',
    'validated',
    'active',
    'retired'
);

CREATE TYPE chain_classification AS ENUM (
    'ergodic',
    'irreducible_periodic',
    'reducible',
    'unclassified'
);

CREATE TYPE simulation_status AS ENUM (
    'created',
    'running',
    'completed',
    'failed'
);

-- ============================================================
-- 2. STOCHASTIC MODELS
-- ============================================================

CREATE TABLE stochastic_models (
    model_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    model_name VARCHAR(150) NOT NULL UNIQUE,

    description TEXT NOT NULL,

    status model_status NOT NULL DEFAULT 'draft',

    classification chain_classification
        NOT NULL DEFAULT 'unclassified',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (length(trim(model_name)) > 0)
);

-- ============================================================
-- 3. STATES
-- ============================================================

CREATE TABLE model_states (
    state_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    model_id BIGINT NOT NULL
        REFERENCES stochastic_models(model_id)
        ON DELETE CASCADE,

    state_code VARCHAR(40) NOT NULL,

    state_name VARCHAR(100) NOT NULL,

    state_reward NUMERIC(16,6) NOT NULL DEFAULT 0,

    is_absorbing BOOLEAN NOT NULL DEFAULT FALSE,

    UNIQUE (model_id, state_code),

    UNIQUE (model_id, state_id),

    CHECK (length(trim(state_code)) > 0),

    CHECK (length(trim(state_name)) > 0)
);

CREATE INDEX idx_model_states_model
    ON model_states(model_id);

-- ============================================================
-- 4. TRANSITION MATRIX
-- ============================================================

CREATE TABLE transitions (
    transition_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    model_id BIGINT NOT NULL,

    source_state_id BIGINT NOT NULL,

    destination_state_id BIGINT NOT NULL,

    probability NUMERIC(18,15) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    FOREIGN KEY (model_id, source_state_id)
        REFERENCES model_states(model_id, state_id)
        ON DELETE CASCADE,

    FOREIGN KEY (model_id, destination_state_id)
        REFERENCES model_states(model_id, state_id)
        ON DELETE CASCADE,

    UNIQUE (
        model_id,
        source_state_id,
        destination_state_id
    ),

    CHECK (probability >= 0 AND probability <= 1)
);

CREATE INDEX idx_transitions_source
    ON transitions(model_id, source_state_id);

CREATE INDEX idx_transitions_destination
    ON transitions(model_id, destination_state_id);

-- ============================================================
-- 5. SIMULATION RECORDS
-- ============================================================

CREATE TABLE simulations (
    simulation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    model_id BIGINT NOT NULL
        REFERENCES stochastic_models(model_id),

    initial_state_id BIGINT NOT NULL,

    random_seed BIGINT NOT NULL,

    requested_steps BIGINT NOT NULL,

    status simulation_status NOT NULL DEFAULT 'created',

    started_at TIMESTAMPTZ,

    completed_at TIMESTAMPTZ,

    failure_reason TEXT,

    FOREIGN KEY (model_id, initial_state_id)
        REFERENCES model_states(model_id, state_id),

    CHECK (requested_steps >= 0),

    CHECK (
        completed_at IS NULL
        OR started_at IS NULL
        OR completed_at >= started_at
    )
);

CREATE INDEX idx_simulations_model_status
    ON simulations(model_id, status);

-- ============================================================
-- 6. OBSERVED TRAJECTORIES
-- ============================================================

CREATE TABLE trajectory_observations (
    simulation_id BIGINT NOT NULL
        REFERENCES simulations(simulation_id)
        ON DELETE CASCADE,

    step_number BIGINT NOT NULL,

    state_id BIGINT NOT NULL
        REFERENCES model_states(state_id),

    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (simulation_id, step_number),

    CHECK (step_number >= 0)
);

CREATE INDEX idx_trajectory_state
    ON trajectory_observations(state_id, simulation_id);

-- ============================================================
-- 7. MARTINGALE DIFFERENCE OBSERVATIONS
-- ============================================================

CREATE TABLE martingale_observations (
    simulation_id BIGINT NOT NULL,

    step_number BIGINT NOT NULL,

    source_state_id BIGINT NOT NULL
        REFERENCES model_states(state_id),

    destination_state_id BIGINT NOT NULL
        REFERENCES model_states(state_id),

    observed_reward NUMERIC(18,8) NOT NULL,

    conditional_expected_reward NUMERIC(18,8) NOT NULL,

    martingale_increment NUMERIC(18,8)
        GENERATED ALWAYS AS (
            observed_reward - conditional_expected_reward
        ) STORED,

    PRIMARY KEY (simulation_id, step_number),

    FOREIGN KEY (simulation_id, step_number)
        REFERENCES trajectory_observations(
            simulation_id,
            step_number
        )
        DEFERRABLE INITIALLY DEFERRED
);

-- ============================================================
-- 8. MODEL VALIDATION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_transition_matrix(
    p_model_id BIGINT,
    p_tolerance NUMERIC DEFAULT 0.000000000001
)
RETURNS TABLE (
    source_state_id BIGINT,
    probability_sum NUMERIC,
    is_valid BOOLEAN
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        s.state_id,
        COALESCE(SUM(t.probability), 0)::NUMERIC,
        ABS(COALESCE(SUM(t.probability), 0) - 1)
            <= p_tolerance
    FROM model_states s
    LEFT JOIN transitions t
        ON t.model_id = s.model_id
       AND t.source_state_id = s.state_id
    WHERE s.model_id = p_model_id
    GROUP BY s.state_id
    ORDER BY s.state_id;
$$;

-- ============================================================
-- 9. MODEL ACTIVATION PROCEDURE
-- ============================================================

CREATE OR REPLACE PROCEDURE activate_model(
    p_model_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_state_count BIGINT;
    v_invalid_count BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_state_count
    FROM model_states
    WHERE model_id = p_model_id;

    IF v_state_count = 0 THEN
        RAISE EXCEPTION
            'Cannot activate a model without states: %',
            p_model_id;
    END IF;

    SELECT COUNT(*)
    INTO v_invalid_count
    FROM validate_transition_matrix(p_model_id)
    WHERE NOT is_valid;

    IF v_invalid_count > 0 THEN
        RAISE EXCEPTION
            'Transition matrix has % invalid rows.',
            v_invalid_count;
    END IF;

    UPDATE stochastic_models
    SET status = 'active'
    WHERE model_id = p_model_id
      AND status IN ('draft', 'validated');

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Model cannot be activated from its current state.';
    END IF;
END;
$$;

-- ============================================================
-- 10. STATIONARY DISTRIBUTION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_stationary_distribution(
    p_model_id BIGINT,
    p_tolerance DOUBLE PRECISION DEFAULT 1e-12,
    p_max_iterations INTEGER DEFAULT 100000
)
RETURNS TABLE (
    state_id BIGINT,
    state_code VARCHAR,
    stationary_probability DOUBLE PRECISION,
    converged BOOLEAN,
    iterations INTEGER,
    residual DOUBLE PRECISION
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_ids BIGINT[];
    v_codes VARCHAR[];
    v_n INTEGER;

    v_current DOUBLE PRECISION[];
    v_next DOUBLE PRECISION[];

    v_i INTEGER;
    v_j INTEGER;
    v_iteration INTEGER;

    v_sum DOUBLE PRECISION;
    v_error DOUBLE PRECISION;
    v_residual DOUBLE PRECISION;

    v_converged BOOLEAN := FALSE;
BEGIN
    IF p_tolerance <= 0 OR NOT isfinite(p_tolerance) THEN
        RAISE EXCEPTION 'Tolerance must be finite and positive.';
    END IF;

    IF p_max_iterations <= 0 THEN
        RAISE EXCEPTION 'Iteration limit must be positive.';
    END IF;

    SELECT
        array_agg(state_id ORDER BY state_id),
        array_agg(state_code ORDER BY state_id)
    INTO v_ids, v_codes
    FROM model_states
    WHERE model_id = p_model_id;

    v_n := COALESCE(array_length(v_ids, 1), 0);

    IF v_n = 0 THEN
        RAISE EXCEPTION 'Model has no states.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM validate_transition_matrix(p_model_id)
        WHERE NOT is_valid
    ) THEN
        RAISE EXCEPTION 'Invalid transition matrix.';
    END IF;

    v_current := array_fill(1.0 / v_n, ARRAY[v_n]);

    FOR v_iteration IN 1..p_max_iterations LOOP
        v_next := array_fill(0.0, ARRAY[v_n]);

        FOR v_i IN 1..v_n LOOP
            FOR v_j IN 1..v_n LOOP

                SELECT COALESCE(SUM(t.probability), 0)::DOUBLE PRECISION
                INTO v_sum
                FROM transitions t
                WHERE t.model_id = p_model_id
                  AND t.source_state_id = v_ids[v_i]
                  AND t.destination_state_id = v_ids[v_j];

                v_next[v_j] := v_next[v_j]
                    + v_current[v_i] * v_sum;
            END LOOP;
        END LOOP;

        v_error := 0;

        FOR v_i IN 1..v_n LOOP
            v_error := GREATEST(
                v_error,
                ABS(v_next[v_i] - v_current[v_i])
            );
        END LOOP;

        v_current := v_next;

        IF v_error < p_tolerance THEN
            v_converged := TRUE;
            EXIT;
        END IF;
    END LOOP;

    v_residual := 0;

    -- Independently verify pi P = pi.
    FOR v_j IN 1..v_n LOOP
        v_sum := 0;

        FOR v_i IN 1..v_n LOOP
            SELECT COALESCE(SUM(t.probability), 0)::DOUBLE PRECISION
            INTO STRICT v_error
            FROM transitions t
            WHERE t.model_id = p_model_id
              AND t.source_state_id = v_ids[v_i]
              AND t.destination_state_id = v_ids[v_j];

            v_sum := v_sum + v_current[v_i] * v_error;
        END LOOP;

        v_residual := GREATEST(
            v_residual,
            ABS(v_sum - v_current[v_j])
        );
    END LOOP;

    FOR v_i IN 1..v_n LOOP
        state_id := v_ids[v_i];
        state_code := v_codes[v_i];
        stationary_probability := v_current[v_i];
        converged := v_converged;
        iterations := v_iteration;
        residual := v_residual;

        RETURN NEXT;
    END LOOP;
END;
$$;

-- ============================================================
-- 11. STATIONARY REWARD EVALUATION
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_long_run_reward(
    p_model_id BIGINT,
    p_tolerance DOUBLE PRECISION DEFAULT 1e-12,
    p_max_iterations INTEGER DEFAULT 100000
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_reward DOUBLE PRECISION;
BEGIN
    SELECT SUM(
        stationary_probability * s.state_reward
    )
    INTO v_reward
    FROM calculate_stationary_distribution(
        p_model_id,
        p_tolerance,
        p_max_iterations
    ) d
    JOIN model_states s
      ON s.state_id = d.state_id
    WHERE d.converged;

    IF v_reward IS NULL THEN
        RAISE EXCEPTION
            'Stationary distribution did not converge.';
    END IF;

    RETURN v_reward;
END;
$$;

-- ============================================================
-- 12. TRAJECTORY VALIDATION TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION validate_trajectory_observation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_model_id BIGINT;
    v_previous_state BIGINT;
    v_probability NUMERIC;
BEGIN
    SELECT model_id
    INTO STRICT v_model_id
    FROM simulations
    WHERE simulation_id = NEW.simulation_id;

    IF NOT EXISTS (
        SELECT 1
        FROM model_states
        WHERE state_id = NEW.state_id
          AND model_id = v_model_id
    ) THEN
        RAISE EXCEPTION
            'Trajectory state does not belong to the simulation model.';
    END IF;

    IF NEW.step_number = 0 THEN
        RETURN NEW;
    END IF;

    SELECT state_id
    INTO v_previous_state
    FROM trajectory_observations
    WHERE simulation_id = NEW.simulation_id
      AND step_number = NEW.step_number - 1;

    IF v_previous_state IS NULL THEN
        RAISE EXCEPTION
            'Previous trajectory observation is missing.';
    END IF;

    SELECT probability
    INTO v_probability
    FROM transitions
    WHERE model_id = v_model_id
      AND source_state_id = v_previous_state
      AND destination_state_id = NEW.state_id;

    IF v_probability IS NULL OR v_probability <= 0 THEN
        RAISE EXCEPTION
            'Observed transition is impossible under the model.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_trajectory
BEFORE INSERT ON trajectory_observations
FOR EACH ROW
EXECUTE FUNCTION validate_trajectory_observation();

-- ============================================================
-- 13. SIMULATION COMPLETION PROCEDURE
-- ============================================================

CREATE OR REPLACE PROCEDURE complete_simulation(
    p_simulation_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_expected BIGINT;
    v_actual BIGINT;
BEGIN
    SELECT requested_steps
    INTO STRICT v_expected
    FROM simulations
    WHERE simulation_id = p_simulation_id
      AND status = 'running'
    FOR UPDATE;

    SELECT COUNT(*)
    INTO v_actual
    FROM trajectory_observations
    WHERE simulation_id = p_simulation_id;

    IF v_actual <> v_expected + 1 THEN
        RAISE EXCEPTION
            'Expected % observations, found %.',
            v_expected + 1,
            v_actual;
    END IF;

    UPDATE simulations
    SET status = 'completed',
        completed_at = NOW()
    WHERE simulation_id = p_simulation_id;
END;
$$;

-- ============================================================
-- 14. REPORTING VIEW
-- ============================================================

CREATE VIEW model_state_reporting AS
SELECT
    m.model_id,
    m.model_name,
    m.status,
    s.state_id,
    s.state_code,
    s.state_name,
    s.state_reward,
    s.is_absorbing,
    COALESCE(
        SUM(t.probability),
        0
    ) AS outgoing_probability
FROM stochastic_models m
JOIN model_states s
    ON s.model_id = m.model_id
LEFT JOIN transitions t
    ON t.model_id = s.model_id
   AND t.source_state_id = s.state_id
GROUP BY
    m.model_id,
    m.model_name,
    m.status,
    s.state_id,
    s.state_code,
    s.state_name,
    s.state_reward,
    s.is_absorbing;

-- ============================================================
-- 15. SAMPLE WEATHER MODEL
-- ============================================================

INSERT INTO stochastic_models (
    model_name,
    description,
    status,
    classification
)
VALUES (
    'Weather-Markov-Model',
    'Three-state stochastic weather process.',
    'draft',
    'ergodic'
);

INSERT INTO model_states (
    model_id,
    state_code,
    state_name,
    state_reward,
    is_absorbing
)
SELECT
    model_id,
    sample.state_code,
    sample.state_name,
    sample.state_reward,
    FALSE
FROM stochastic_models m
CROSS JOIN (
    VALUES
        ('SUN', 'Sunny', 100.0::NUMERIC),
        ('CLD', 'Cloudy', 60.0::NUMERIC),
        ('RAN', 'Rainy', 20.0::NUMERIC)
) AS sample(
    state_code,
    state_name,
    state_reward
)
WHERE m.model_name = 'Weather-Markov-Model';

INSERT INTO transitions (
    model_id,
    source_state_id,
    destination_state_id,
    probability
)
SELECT
    m.model_id,
    source.state_id,
    destination.state_id,
    sample.probability
FROM stochastic_models m
JOIN (
    VALUES
        ('SUN', 'SUN', 0.70::NUMERIC),
        ('SUN', 'CLD', 0.20::NUMERIC),
        ('SUN', 'RAN', 0.10::NUMERIC),

        ('CLD', 'SUN', 0.25::NUMERIC),
        ('CLD', 'CLD', 0.50::NUMERIC),
        ('CLD', 'RAN', 0.25::NUMERIC),

        ('RAN', 'SUN', 0.20::NUMERIC),
        ('RAN', 'CLD', 0.30::NUMERIC),
        ('RAN', 'RAN', 0.50::NUMERIC)
) AS sample(source_code, destination_code, probability)
    ON TRUE
JOIN model_states source
    ON source.model_id = m.model_id
   AND source.state_code = sample.source_code
JOIN model_states destination
    ON destination.model_id = m.model_id
   AND destination.state_code = sample.destination_code
WHERE m.model_name = 'Weather-Markov-Model';

-- ============================================================
-- 16. PERIODIC MODEL
-- ============================================================

INSERT INTO stochastic_models (
    model_name,
    description,
    status,
    classification
)
VALUES (
    'Alternating-Periodic-Model',
    'Two-state deterministic alternating process.',
    'draft',
    'irreducible_periodic'
);

INSERT INTO model_states (
    model_id,
    state_code,
    state_name
)
SELECT
    model_id,
    sample.state_code,
    sample.state_name
FROM stochastic_models m
CROSS JOIN (
    VALUES
        ('A', 'State A'),
        ('B', 'State B')
) AS sample(state_code, state_name)
WHERE m.model_name = 'Alternating-Periodic-Model';

INSERT INTO transitions (
    model_id,
    source_state_id,
    destination_state_id,
    probability
)
SELECT
    m.model_id,
    source.state_id,
    destination.state_id,
    1.0
FROM stochastic_models m
JOIN model_states source
    ON source.model_id = m.model_id
JOIN model_states destination
    ON destination.model_id = m.model_id
WHERE m.model_name = 'Alternating-Periodic-Model'
  AND (
      (source.state_code = 'A' AND destination.state_code = 'B')
      OR
      (source.state_code = 'B' AND destination.state_code = 'A')
  );

-- ============================================================
-- 17. REDUCIBLE MODEL
-- ============================================================

INSERT INTO stochastic_models (
    model_name,
    description,
    status,
    classification
)
VALUES (
    'Absorbing-Model',
    'Transient state leading to an absorbing state.',
    'draft',
    'reducible'
);

INSERT INTO model_states (
    model_id,
    state_code,
    state_name,
    is_absorbing
)
SELECT
    model_id,
    sample.state_code,
    sample.state_name,
    sample.is_absorbing
FROM stochastic_models m
CROSS JOIN (
    VALUES
        ('T', 'Transient', FALSE),
        ('ABS', 'Absorbing', TRUE)
) AS sample(state_code, state_name, is_absorbing)
WHERE m.model_name = 'Absorbing-Model';

INSERT INTO transitions (
    model_id,
    source_state_id,
    destination_state_id,
    probability
)
SELECT
    m.model_id,
    source.state_id,
    destination.state_id,
    sample.probability
FROM stochastic_models m
JOIN (
    VALUES
        ('T', 'T', 0.8::NUMERIC),
        ('T', 'ABS', 0.2::NUMERIC),
        ('ABS', 'T', 0.0::NUMERIC),
        ('ABS', 'ABS', 1.0::NUMERIC)
) AS sample(source_code, destination_code, probability)
    ON TRUE
JOIN model_states source
    ON source.model_id = m.model_id
   AND source.state_code = sample.source_code
JOIN model_states destination
    ON destination.model_id = m.model_id
   AND destination.state_code = sample.destination_code
WHERE m.model_name = 'Absorbing-Model';

-- ============================================================
-- 18. ACTIVATE VALID MODELS
-- ============================================================

CALL activate_model(
    (SELECT model_id
     FROM stochastic_models
     WHERE model_name = 'Weather-Markov-Model')
);

CALL activate_model(
    (SELECT model_id
     FROM stochastic_models
     WHERE model_name = 'Alternating-Periodic-Model')
);

CALL activate_model(
    (SELECT model_id
     FROM stochastic_models
     WHERE model_name = 'Absorbing-Model')
);

COMMIT;

-- ============================================================
-- 19. TRANSITION MATRIX VALIDATION
-- ============================================================

SELECT
    m.model_name,
    s.state_code,
    validation.probability_sum,
    validation.is_valid
FROM stochastic_models m
CROSS JOIN LATERAL
    validate_transition_matrix(m.model_id) validation
JOIN model_states s
    ON s.state_id = validation.source_state_id
ORDER BY m.model_name, s.state_code;

-- ============================================================
-- 20. MODEL RETRIEVAL
-- ============================================================

SELECT *
FROM model_state_reporting
ORDER BY model_name, state_id;

-- ============================================================
-- 21. STATIONARY DISTRIBUTION
-- ============================================================

SELECT
    m.model_name,
    d.state_code,
    ROUND(d.stationary_probability::NUMERIC, 8)
        AS stationary_probability,
    d.converged,
    d.iterations,
    d.residual
FROM stochastic_models m
CROSS JOIN LATERAL
    calculate_stationary_distribution(m.model_id) d
WHERE m.model_name = 'Weather-Markov-Model'
ORDER BY d.state_id;

-- ============================================================
-- 22. LONG-RUN EXPECTED REWARD
-- ============================================================

SELECT
    model_name,
    calculate_long_run_reward(model_id)
        AS expected_long_run_reward
FROM stochastic_models
WHERE model_name = 'Weather-Markov-Model';

-- ============================================================
-- 23. SIMULATION WORKFLOW
-- ============================================================

BEGIN;

INSERT INTO simulations (
    model_id,
    initial_state_id,
    random_seed,
    requested_steps,
    status,
    started_at
)
SELECT
    m.model_id,
    s.state_id,
    2026,
    5,
    'running',
    NOW()
FROM stochastic_models m
JOIN model_states s
    ON s.model_id = m.model_id
WHERE m.model_name = 'Weather-Markov-Model'
  AND s.state_code = 'SUN';

-- Capture the generated simulation identifier.
CREATE TEMP TABLE current_simulation
ON COMMIT DROP
AS
SELECT MAX(simulation_id) AS simulation_id
FROM simulations;

-- First observation.
INSERT INTO trajectory_observations (
    simulation_id,
    step_number,
    state_id
)
SELECT
    cs.simulation_id,
    0,
    s.state_id
FROM current_simulation cs
JOIN simulations sim
    ON sim.simulation_id = cs.simulation_id
JOIN model_states s
    ON s.state_id = sim.initial_state_id;

-- Valid transitions for the example trajectory:
-- SUN -> CLD -> RAN -> CLD -> SUN -> SUN

INSERT INTO trajectory_observations (
    simulation_id,
    step_number,
    state_id
)
SELECT
    cs.simulation_id,
    sample.step_number,
    s.state_id
FROM current_simulation cs
CROSS JOIN (
    VALUES
        (1, 'CLD'),
        (2, 'RAN'),
        (3, 'CLD'),
        (4, 'SUN'),
        (5, 'SUN')
) AS sample(step_number, state_code)
JOIN current_simulation sim
    ON TRUE
JOIN simulations model
    ON model.simulation_id = sim.simulation_id
JOIN model_states s
    ON s.model_id = model.model_id
   AND s.state_code = sample.state_code;

CALL complete_simulation(
    (SELECT simulation_id FROM current_simulation)
);

COMMIT;

-- ============================================================
-- 24. TRAJECTORY RETRIEVAL
-- ============================================================

SELECT
    sim.simulation_id,
    observation.step_number,
    state.state_code,
    state.state_name,
    observation.observed_at
FROM simulations sim
JOIN trajectory_observations observation
    ON observation.simulation_id = sim.simulation_id
JOIN model_states state
    ON state.state_id = observation.state_id
ORDER BY sim.simulation_id, observation.step_number;

-- ============================================================
-- 25. EMPIRICAL STATE DISTRIBUTION
-- ============================================================

SELECT
    state.state_code,
    COUNT(*) AS visits,
    ROUND(
        COUNT(*)::NUMERIC /
        SUM(COUNT(*)) OVER (),
        6
    ) AS empirical_probability
FROM trajectory_observations observation
JOIN model_states state
    ON state.state_id = observation.state_id
GROUP BY state.state_code
ORDER BY state.state_code;

-- ============================================================
-- 26. MARTINGALE DIFFERENCE RECORDING
-- ============================================================

-- Reward is the difference between destination and source
-- state index. Conditional expectation is computed from
-- the transition matrix.

INSERT INTO martingale_observations (
    simulation_id,
    step_number,
    source_state_id,
    destination_state_id,
    observed_reward,
    conditional_expected_reward
)
SELECT
    current.simulation_id,
    destination_observation.step_number,
    source_observation.state_id,
    destination_observation.state_id,

    destination_state.state_id::NUMERIC -
        source_state.state_id::NUMERIC,

    SUM(
        transition.probability *
        (
            expected_state.state_id::NUMERIC -
            source_state.state_id::NUMERIC
        )
    )

FROM current_simulation current
JOIN trajectory_observations source_observation
    ON source_observation.simulation_id =
       current.simulation_id
JOIN trajectory_observations destination_observation
    ON destination_observation.simulation_id =
       source_observation.simulation_id
   AND destination_observation.step_number =
       source_observation.step_number + 1

JOIN source_state
    ON source_state.state_id = source_observation.state_id
JOIN destination_state
    ON destination_state.state_id =
       destination_observation.state_id

JOIN simulations simulation
    ON simulation.simulation_id =
       current.simulation_id

JOIN transitions transition
    ON transition.model_id = simulation.model_id
   AND transition.source_state_id =
       source_state.state_id

JOIN model_states expected_state
    ON expected_state.state_id =
       transition.destination_state_id

GROUP BY
    current.simulation_id,
    destination_observation.step_number,
    source_observation.state_id,
    destination_observation.state_id;

-- ============================================================
-- 27. MARTINGALE REPORT
-- ============================================================

SELECT
    simulation_id,
    step_number,
    observed_reward,
    conditional_expected_reward,
    martingale_increment,
    SUM(martingale_increment) OVER (
        PARTITION BY simulation_id
        ORDER BY step_number
        ROWS BETWEEN UNBOUNDED PRECEDING
        AND CURRENT ROW
    ) AS cumulative_martingale
FROM martingale_observations
ORDER BY simulation_id, step_number;

-- ============================================================
-- 28. AGGREGATE MARTINGALE DIAGNOSTICS
-- ============================================================

SELECT
    simulation_id,
    COUNT(*) AS observation_count,
    AVG(martingale_increment) AS average_increment,
    VAR_POP(martingale_increment) AS increment_variance,
    MIN(martingale_increment) AS minimum_increment,
    MAX(martingale_increment) AS maximum_increment
FROM martingale_observations
GROUP BY simulation_id;

-- ============================================================
-- 29. FAILURE CASE: INVALID PROBABILITY ROW
-- ============================================================

-- This query identifies incomplete or invalid matrix rows.
-- It does not modify the active model.

SELECT
    model_id,
    source_state_id,
    probability_sum,
    is_valid
FROM (
    SELECT
        model_id,
        source_state_id,
        SUM(probability) AS probability_sum,
        ABS(SUM(probability) - 1) <= 0.000000000001
            AS is_valid
    FROM transitions
    GROUP BY model_id, source_state_id
) validation
WHERE NOT is_valid;

-- ============================================================
-- 30. FINAL MODEL STATUS REPORT
-- ============================================================

SELECT
    m.model_name,
    m.status,
    m.classification,
    COUNT(DISTINCT s.state_id) AS number_of_states,
    COUNT(DISTINCT t.transition_id) AS number_of_transitions,
    COUNT(DISTINCT sim.simulation_id) AS number_of_simulations
FROM stochastic_models m
LEFT JOIN model_states s
    ON s.model_id = m.model_id
LEFT JOIN transitions t
    ON t.model_id = m.model_id
LEFT JOIN simulations sim
    ON sim.model_id = m.model_id
GROUP BY
    m.model_id,
    m.model_name,
    m.status,
    m.classification
ORDER BY m.model_name;
