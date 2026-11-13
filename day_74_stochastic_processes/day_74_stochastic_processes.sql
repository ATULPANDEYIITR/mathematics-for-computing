/*
 * STOCHASTIC PROCESSES
 * PostgreSQL 15+
 *
 * Relational stochastic simulation and analytical workflow.
 *
 * Models:
 *   - Discrete-time Markov chains
 *   - Random walks
 *   - Transition probabilities
 *   - Simulation runs
 *   - State observations
 *   - Monte Carlo experiments
 *   - Absorbing states
 *   - Statistical reporting
 */

CREATE SCHEMA IF NOT EXISTS stochastic_lab;

SET search_path TO stochastic_lab, public;

-- ============================================================
-- 1. DOMAIN TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS stochastic_process (
    process_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    process_name VARCHAR(150) NOT NULL UNIQUE,
    process_type VARCHAR(30) NOT NULL
        CHECK (
            process_type IN (
                'MARKOV_CHAIN',
                'RANDOM_WALK'
            )
        ),
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS process_state (
    state_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    process_id BIGINT NOT NULL
        REFERENCES stochastic_process(process_id)
        ON DELETE CASCADE,
    state_code VARCHAR(80) NOT NULL,
    state_description TEXT,
    is_absorbing BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (process_id, state_code)
);

CREATE TABLE IF NOT EXISTS transition_rule (
    transition_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    process_id BIGINT NOT NULL
        REFERENCES stochastic_process(process_id)
        ON DELETE CASCADE,
    source_state_id BIGINT NOT NULL
        REFERENCES process_state(state_id),
    destination_state_id BIGINT NOT NULL
        REFERENCES process_state(state_id),
    probability NUMERIC(15,12) NOT NULL
        CHECK (probability >= 0 AND probability <= 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (
        process_id,
        source_state_id,
        destination_state_id
    ),
    CHECK (source_state_id <> destination_state_id OR probability <= 1)
);

CREATE INDEX IF NOT EXISTS idx_transition_source
    ON transition_rule(process_id, source_state_id);

CREATE INDEX IF NOT EXISTS idx_transition_destination
    ON transition_rule(destination_state_id);

CREATE TABLE IF NOT EXISTS simulation_run (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    process_id BIGINT NOT NULL
        REFERENCES stochastic_process(process_id),
    run_reference UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    initial_state_id BIGINT NOT NULL
        REFERENCES process_state(state_id),
    final_state_id BIGINT
        REFERENCES process_state(state_id),
    random_seed BIGINT NOT NULL,
    maximum_steps INTEGER NOT NULL
        CHECK (maximum_steps >= 0),
    executed_steps INTEGER NOT NULL DEFAULT 0
        CHECK (executed_steps >= 0),
    run_status VARCHAR(20) NOT NULL DEFAULT 'CREATED'
        CHECK (
            run_status IN (
                'CREATED',
                'RUNNING',
                'COMPLETED',
                'ABSORBED',
                'FAILED'
            )
        ),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (executed_steps <= maximum_steps),
    CHECK (
        completed_at IS NULL
        OR started_at IS NULL
        OR completed_at >= started_at
    )
);

CREATE INDEX IF NOT EXISTS idx_simulation_process_status
    ON simulation_run(process_id, run_status, created_at DESC);

CREATE TABLE IF NOT EXISTS state_observation (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id BIGINT NOT NULL
        REFERENCES simulation_run(run_id)
        ON DELETE CASCADE,
    step_number INTEGER NOT NULL
        CHECK (step_number >= 0),
    state_id BIGINT NOT NULL
        REFERENCES process_state(state_id),
    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (run_id, step_number)
);

CREATE INDEX IF NOT EXISTS idx_observation_run_step
    ON state_observation(run_id, step_number);

CREATE INDEX IF NOT EXISTS idx_observation_state
    ON state_observation(state_id, observed_at);

CREATE TABLE IF NOT EXISTS experiment_batch (
    batch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    process_id BIGINT NOT NULL
        REFERENCES stochastic_process(process_id),
    batch_name VARCHAR(150) NOT NULL,
    target_state_id BIGINT NOT NULL
        REFERENCES process_state(state_id),
    experiment_count INTEGER NOT NULL
        CHECK (experiment_count > 0),
    maximum_steps INTEGER NOT NULL
        CHECK (maximum_steps >= 0),
    random_seed BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (process_id, batch_name)
);

CREATE TABLE IF NOT EXISTS experiment_result (
    result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    batch_id BIGINT NOT NULL
        REFERENCES experiment_batch(batch_id)
        ON DELETE CASCADE,
    run_id BIGINT NOT NULL UNIQUE
        REFERENCES simulation_run(run_id),
    reached_target BOOLEAN NOT NULL,
    absorption_time INTEGER,
    CHECK (
        absorption_time IS NULL
        OR absorption_time >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_experiment_batch_target
    ON experiment_result(batch_id, reached_target);

-- ============================================================
-- 2. DATA INTEGRITY TRIGGERS
-- ============================================================

CREATE OR REPLACE FUNCTION validate_transition_process()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    source_process BIGINT;
    destination_process BIGINT;
BEGIN
    SELECT process_id
    INTO source_process
    FROM process_state
    WHERE state_id = NEW.source_state_id;

    SELECT process_id
    INTO destination_process
    FROM process_state
    WHERE state_id = NEW.destination_state_id;

    IF source_process IS NULL OR destination_process IS NULL THEN
        RAISE EXCEPTION 'Transition states must exist.';
    END IF;

    IF source_process <> NEW.process_id
       OR destination_process <> NEW.process_id THEN
        RAISE EXCEPTION
            'Both transition states must belong to the specified process.';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_transition_process
ON transition_rule;

CREATE TRIGGER trg_validate_transition_process
BEFORE INSERT OR UPDATE ON transition_rule
FOR EACH ROW
EXECUTE FUNCTION validate_transition_process();


CREATE OR REPLACE FUNCTION validate_state_absorption()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    outgoing_count INTEGER;
    self_probability NUMERIC;
BEGIN
    IF NEW.is_absorbing THEN
        SELECT
            COUNT(*),
            COALESCE(
                SUM(probability) FILTER (
                    WHERE source_state_id = NEW.state_id
                      AND destination_state_id = NEW.state_id
                ),
                0
            )
        INTO outgoing_count, self_probability
        FROM transition_rule
        WHERE source_state_id = NEW.state_id;

        IF outgoing_count > 0
           AND (
               outgoing_count <> 1
               OR self_probability <> 1
           ) THEN
            RAISE EXCEPTION
                'An absorbing state must have exactly one self-transition with probability 1.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_state_absorption
ON process_state;

CREATE TRIGGER trg_validate_state_absorption
BEFORE INSERT OR UPDATE OF is_absorbing ON process_state
FOR EACH ROW
EXECUTE FUNCTION validate_state_absorption();


-- ============================================================
-- 3. TRANSITION PROBABILITY VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_transition_distribution(
    p_process_id BIGINT
)
RETURNS TABLE (
    source_state VARCHAR,
    probability_total NUMERIC,
    is_valid BOOLEAN
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        s.state_code,
        COALESCE(SUM(t.probability), 0)::NUMERIC,
        ABS(COALESCE(SUM(t.probability), 0) - 1) <= 0.000000001
    FROM process_state s
    LEFT JOIN transition_rule t
        ON t.source_state_id = s.state_id
       AND t.process_id = s.process_id
    WHERE s.process_id = p_process_id
    GROUP BY s.state_id, s.state_code
    ORDER BY s.state_code;
$$;


CREATE OR REPLACE FUNCTION enforce_transition_distribution()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    affected_process BIGINT;
    invalid_count INTEGER;
BEGIN
    affected_process := COALESCE(NEW.process_id, OLD.process_id);

    SELECT COUNT(*)
    INTO invalid_count
    FROM validate_transition_distribution(affected_process)
    WHERE NOT is_valid;

    IF invalid_count > 0 THEN
        RAISE EXCEPTION
            'Invalid transition distribution for process %.',
            affected_process;
    END IF;

    RETURN NULL;
END;
$$;

-- Constraint triggers validate complete source-state distributions
-- at transaction commit, allowing multiple transition rows per transaction.

DROP TRIGGER IF EXISTS trg_enforce_transition_distribution
ON transition_rule;

CREATE CONSTRAINT TRIGGER trg_enforce_transition_distribution
AFTER INSERT OR UPDATE OR DELETE ON transition_rule
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION enforce_transition_distribution();


-- ============================================================
-- 4. PROCESS REGISTRATION
-- ============================================================

INSERT INTO stochastic_process (
    process_name,
    process_type,
    description
)
VALUES
(
    'WEATHER_MODEL',
    'MARKOV_CHAIN',
    'Three-state discrete-time weather model.'
),
(
    'SYSTEM_RELIABILITY',
    'MARKOV_CHAIN',
    'Operational degradation and absorbing failure model.'
),
(
    'BOUNDED_RANDOM_WALK',
    'RANDOM_WALK',
    'One-dimensional random walk with absorbing boundaries.'
)
ON CONFLICT (process_name) DO NOTHING;


-- ============================================================
-- 5. WEATHER MODEL
-- ============================================================

INSERT INTO process_state (
    process_id,
    state_code,
    state_description,
    is_absorbing
)
SELECT
    p.process_id,
    states.state_code,
    states.description,
    FALSE
FROM stochastic_process p
CROSS JOIN (
    VALUES
        ('SUNNY', 'Clear atmospheric conditions'),
        ('CLOUDY', 'Cloud coverage'),
        ('RAINY', 'Rainfall conditions')
) AS states(state_code, description)
WHERE p.process_name = 'WEATHER_MODEL'
ON CONFLICT (process_id, state_code) DO NOTHING;


INSERT INTO transition_rule (
    process_id,
    source_state_id,
    destination_state_id,
    probability
)
SELECT
    p.process_id,
    source.state_id,
    destination.state_id,
    matrix.probability
FROM stochastic_process p
JOIN (
    VALUES
        ('SUNNY', 'SUNNY', 0.70::NUMERIC),
        ('SUNNY', 'CLOUDY', 0.20::NUMERIC),
        ('SUNNY', 'RAINY', 0.10::NUMERIC),
        ('CLOUDY', 'SUNNY', 0.30::NUMERIC),
        ('CLOUDY', 'CLOUDY', 0.40::NUMERIC),
        ('CLOUDY', 'RAINY', 0.30::NUMERIC),
        ('RAINY', 'SUNNY', 0.20::NUMERIC),
        ('RAINY', 'CLOUDY', 0.30::NUMERIC),
        ('RAINY', 'RAINY', 0.50::NUMERIC)
) AS matrix(source_code, destination_code, probability)
    ON TRUE
JOIN process_state source
    ON source.process_id = p.process_id
   AND source.state_code = matrix.source_code
JOIN process_state destination
    ON destination.process_id = p.process_id
   AND destination.state_code = matrix.destination_code
WHERE p.process_name = 'WEATHER_MODEL'
ON CONFLICT (
    process_id,
    source_state_id,
    destination_state_id
) DO NOTHING;


-- ============================================================
-- 6. RELIABILITY MODEL
-- ============================================================

INSERT INTO process_state (
    process_id,
    state_code,
    state_description,
    is_absorbing
)
SELECT
    p.process_id,
    states.state_code,
    states.description,
    states.is_absorbing
FROM stochastic_process p
CROSS JOIN (
    VALUES
        ('OPERATIONAL', 'System operating normally', FALSE),
        ('DEGRADED', 'System operating with reduced performance', FALSE),
        ('FAILED', 'Terminal system failure', TRUE)
) AS states(state_code, description, is_absorbing)
WHERE p.process_name = 'SYSTEM_RELIABILITY'
ON CONFLICT (process_id, state_code)
DO UPDATE SET
    state_description = EXCLUDED.state_description,
    is_absorbing = EXCLUDED.is_absorbing;


INSERT INTO transition_rule (
    process_id,
    source_state_id,
    destination_state_id,
    probability
)
SELECT
    p.process_id,
    source.state_id,
    destination.state_id,
    matrix.probability
FROM stochastic_process p
JOIN (
    VALUES
        ('OPERATIONAL', 'OPERATIONAL', 0.65::NUMERIC),
        ('OPERATIONAL', 'DEGRADED', 0.25::NUMERIC),
        ('OPERATIONAL', 'FAILED', 0.10::NUMERIC),
        ('DEGRADED', 'OPERATIONAL', 0.30::NUMERIC),
        ('DEGRADED', 'DEGRADED', 0.40::NUMERIC),
        ('DEGRADED', 'FAILED', 0.30::NUMERIC),
        ('FAILED', 'FAILED', 1.00::NUMERIC)
) AS matrix(source_code, destination_code, probability)
    ON TRUE
JOIN process_state source
    ON source.process_id = p.process_id
   AND source.state_code = matrix.source_code
JOIN process_state destination
    ON destination.process_id = p.process_id
   AND destination.state_code = matrix.destination_code
WHERE p.process_name = 'SYSTEM_RELIABILITY'
ON CONFLICT (
    process_id,
    source_state_id,
    destination_state_id
) DO NOTHING;


-- ============================================================
-- 7. BOUNDED RANDOM WALK STATES
-- ============================================================

INSERT INTO process_state (
    process_id,
    state_code,
    state_description,
    is_absorbing
)
SELECT
    p.process_id,
    'POSITION_' || position_value,
    'Random walk position ' || position_value,
    position_value IN (-5, 5)
FROM stochastic_process p
CROSS JOIN generate_series(-5, 5) AS position_value
WHERE p.process_name = 'BOUNDED_RANDOM_WALK'
ON CONFLICT (process_id, state_code) DO NOTHING;


INSERT INTO transition_rule (
    process_id,
    source_state_id,
    destination_state_id,
    probability
)
SELECT
    p.process_id,
    source.state_id,
    destination.state_id,
    CASE
        WHEN source.state_code = 'POSITION_-5'
            OR source.state_code = 'POSITION_5'
        THEN 1.0
        ELSE 0.5
    END
FROM stochastic_process p
JOIN process_state source
    ON source.process_id = p.process_id
JOIN process_state destination
    ON destination.process_id = p.process_id
WHERE p.process_name = 'BOUNDED_RANDOM_WALK'
AND (
    (
        source.state_code IN ('POSITION_-5', 'POSITION_5')
        AND destination.state_id = source.state_id
    )
    OR
    (
        source.state_code NOT IN ('POSITION_-5', 'POSITION_5')
        AND destination.state_code IN (
            'POSITION_' || (
                substring(source.state_code FROM 'POSITION_(-?[0-9]+)')::INTEGER - 1
            ),
            'POSITION_' || (
                substring(source.state_code FROM 'POSITION_(-?[0-9]+)')::INTEGER + 1
            )
        )
    )
)
ON CONFLICT (
    process_id,
    source_state_id,
    destination_state_id
) DO NOTHING;


-- ============================================================
-- 8. SIMULATION WORKFLOW
-- ============================================================

CREATE OR REPLACE FUNCTION simulate_markov_chain(
    p_process_id BIGINT,
    p_initial_state_id BIGINT,
    p_maximum_steps INTEGER,
    p_seed BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_run_id BIGINT;
    v_current_state BIGINT;
    v_next_state BIGINT;
    v_total NUMERIC;
    v_random NUMERIC;
    v_cumulative NUMERIC;
    v_step INTEGER := 0;
    v_absorbing BOOLEAN;
    v_status VARCHAR(20);
    v_probability NUMERIC;
BEGIN
    IF p_maximum_steps < 0 THEN
        RAISE EXCEPTION 'Maximum steps cannot be negative.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM process_state
        WHERE state_id = p_initial_state_id
          AND process_id = p_process_id
    ) THEN
        RAISE EXCEPTION 'Initial state does not belong to process.';
    END IF;

    -- Serialize simulations for a process while transition definitions
    -- are being consumed. This prevents concurrent policy changes.
    PERFORM pg_advisory_xact_lock(p_process_id);

    IF EXISTS (
        SELECT 1
        FROM validate_transition_distribution(p_process_id)
        WHERE NOT is_valid
    ) THEN
        RAISE EXCEPTION 'Process has invalid transition distributions.';
    END IF;

    INSERT INTO simulation_run (
        process_id,
        initial_state_id,
        random_seed,
        maximum_steps,
        run_status,
        started_at
    )
    VALUES (
        p_process_id,
        p_initial_state_id,
        p_seed,
        p_maximum_steps,
        'RUNNING',
        clock_timestamp()
    )
    RETURNING run_id INTO v_run_id;

    v_current_state := p_initial_state_id;

    INSERT INTO state_observation (
        run_id,
        step_number,
        state_id
    )
    VALUES (
        v_run_id,
        0,
        v_current_state
    );

    -- setseed is session-scoped. The run is deterministic only within
    -- the same PostgreSQL random implementation and execution context.
    PERFORM setseed(
        ((abs(p_seed::NUMERIC) % 1000000) / 1000000.0)::DOUBLE PRECISION
    );

    FOR v_step IN 1..p_maximum_steps LOOP

        SELECT is_absorbing
        INTO v_absorbing
        FROM process_state
        WHERE state_id = v_current_state;

        IF v_absorbing THEN
            EXIT;
        END IF;

        v_random := random();

        v_cumulative := 0;
        v_next_state := NULL;

        FOR v_next_state, v_probability IN
            SELECT
                destination_state_id,
                probability
            FROM transition_rule
            WHERE process_id = p_process_id
              AND source_state_id = v_current_state
            ORDER BY destination_state_id
        LOOP
            v_cumulative := v_cumulative + v_probability;

            IF v_random < v_cumulative THEN
                EXIT;
            END IF;
        END LOOP;

        IF v_next_state IS NULL THEN
            RAISE EXCEPTION
                'No transition available from state %.',
                v_current_state;
        END IF;

        v_current_state := v_next_state;

        INSERT INTO state_observation (
            run_id,
            step_number,
            state_id
        )
        VALUES (
            v_run_id,
            v_step,
            v_current_state
        );

        SELECT is_absorbing
        INTO v_absorbing
        FROM process_state
        WHERE state_id = v_current_state;

        IF v_absorbing THEN
            EXIT;
        END IF;
    END LOOP;

    SELECT is_absorbing
    INTO v_absorbing
    FROM process_state
    WHERE state_id = v_current_state;

    v_status := CASE
        WHEN v_absorbing THEN 'ABSORBED'
        ELSE 'COMPLETED'
    END;

    UPDATE simulation_run
    SET
        final_state_id = v_current_state,
        executed_steps = v_step,
        run_status = v_status,
        completed_at = clock_timestamp()
    WHERE run_id = v_run_id;

    RETURN v_run_id;

EXCEPTION
    WHEN OTHERS THEN
        -- The exception is propagated. The surrounding transaction
        -- determines whether the run and observations are rolled back.
        RAISE;
END;
$$;


-- ============================================================
-- 9. BATCH MONTE CARLO EXPERIMENTS
-- ============================================================

CREATE OR REPLACE PROCEDURE execute_experiment_batch(
    p_batch_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_batch experiment_batch%ROWTYPE;
    v_initial_state BIGINT;
    v_run_id BIGINT;
    v_index INTEGER;
    v_final_state BIGINT;
    v_executed_steps INTEGER;
    v_success BOOLEAN;
BEGIN
    SELECT *
    INTO v_batch
    FROM experiment_batch
    WHERE batch_id = p_batch_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Experiment batch does not exist.';
    END IF;

    SELECT state_id
    INTO v_initial_state
    FROM process_state
    WHERE process_id = v_batch.process_id
      AND is_absorbing = FALSE
    ORDER BY state_id
    LIMIT 1;

    IF v_initial_state IS NULL THEN
        RAISE EXCEPTION 'No non-absorbing initial state is available.';
    END IF;

    FOR v_index IN 1..v_batch.experiment_count LOOP

        v_run_id := simulate_markov_chain(
            v_batch.process_id,
            v_initial_state,
            v_batch.maximum_steps,
            v_batch.random_seed + v_index
        );

        SELECT final_state_id, executed_steps
        INTO v_final_state, v_executed_steps
        FROM simulation_run
        WHERE run_id = v_run_id;

        v_success := (
            v_final_state = v_batch.target_state_id
        );

        INSERT INTO experiment_result (
            batch_id,
            run_id,
            reached_target,
            absorption_time
        )
        VALUES (
            p_batch_id,
            v_run_id,
            v_success,
            CASE
                WHEN v_success THEN v_executed_steps
                ELSE NULL
            END
        );
    END LOOP;
END;
$$;


-- ============================================================
-- 10. ANALYTICAL VIEWS
-- ============================================================

CREATE OR REPLACE VIEW v_transition_distribution AS
SELECT
    p.process_name,
    source.state_code AS source_state,
    destination.state_code AS destination_state,
    t.probability
FROM transition_rule t
JOIN stochastic_process p
    ON p.process_id = t.process_id
JOIN process_state source
    ON source.state_id = t.source_state_id
JOIN process_state destination
    ON destination.state_id = t.destination_state_id;


CREATE OR REPLACE VIEW v_simulation_summary AS
SELECT
    r.run_id,
    r.run_reference,
    p.process_name,
    initial_state.state_code AS initial_state,
    final_state.state_code AS final_state,
    r.executed_steps,
    r.run_status,
    r.random_seed,
    r.created_at,
    r.completed_at
FROM simulation_run r
JOIN stochastic_process p
    ON p.process_id = r.process_id
JOIN process_state initial_state
    ON initial_state.state_id = r.initial_state_id
LEFT JOIN process_state final_state
    ON final_state.state_id = r.final_state_id;


CREATE OR REPLACE VIEW v_empirical_state_frequency AS
SELECT
    p.process_name,
    s.state_code,
    COUNT(o.observation_id) AS observation_count,
    ROUND(
        COUNT(o.observation_id)::NUMERIC /
        NULLIF(
            SUM(COUNT(o.observation_id)) OVER (
                PARTITION BY p.process_id
            ),
            0
        ),
        6
    ) AS empirical_frequency
FROM state_observation o
JOIN simulation_run r
    ON r.run_id = o.run_id
JOIN stochastic_process p
    ON p.process_id = r.process_id
JOIN process_state s
    ON s.state_id = o.state_id
GROUP BY p.process_id, p.process_name, s.state_code;


-- ============================================================
-- 11. SAMPLE SIMULATIONS
-- ============================================================

DO $$
DECLARE
    v_weather_id BIGINT;
    v_reliability_id BIGINT;
    v_walk_id BIGINT;
    v_initial BIGINT;
    v_run BIGINT;
BEGIN
    SELECT process_id
    INTO v_weather_id
    FROM stochastic_process
    WHERE process_name = 'WEATHER_MODEL';

    SELECT process_id
    INTO v_reliability_id
    FROM stochastic_process
    WHERE process_name = 'SYSTEM_RELIABILITY';

    SELECT process_id
    INTO v_walk_id
    FROM stochastic_process
    WHERE process_name = 'BOUNDED_RANDOM_WALK';

    SELECT state_id
    INTO v_initial
    FROM process_state
    WHERE process_id = v_weather_id
      AND state_code = 'SUNNY';

    v_run := simulate_markov_chain(
        v_weather_id,
        v_initial,
        20,
        42
    );

    SELECT state_id
    INTO v_initial
    FROM process_state
    WHERE process_id = v_reliability_id
      AND state_code = 'OPERATIONAL';

    v_run := simulate_markov_chain(
        v_reliability_id,
        v_initial,
        100,
        1001
    );

    SELECT state_id
    INTO v_initial
    FROM process_state
    WHERE process_id = v_walk_id
      AND state_code = 'POSITION_0';

    v_run := simulate_markov_chain(
        v_walk_id,
        v_initial,
        100,
        2001
    );
END;
$$;


-- ============================================================
-- 12. MONTE CARLO BATCH
-- ============================================================

INSERT INTO experiment_batch (
    process_id,
    batch_name,
    target_state_id,
    experiment_count,
    maximum_steps,
    random_seed
)
SELECT
    p.process_id,
    'FAILURE_PROBABILITY_1000',
    target.state_id,
    1000,
    100,
    5000
FROM stochastic_process p
JOIN process_state target
    ON target.process_id = p.process_id
   AND target.state_code = 'FAILED'
WHERE p.process_name = 'SYSTEM_RELIABILITY'
ON CONFLICT (process_id, batch_name) DO NOTHING;


-- Execute only when the batch has not already produced results.
DO $$
DECLARE
    v_batch_id BIGINT;
BEGIN
    SELECT batch_id
    INTO v_batch_id
    FROM experiment_batch
    WHERE batch_name = 'FAILURE_PROBABILITY_1000';

    IF NOT EXISTS (
        SELECT 1
        FROM experiment_result
        WHERE batch_id = v_batch_id
    ) THEN
        CALL execute_experiment_batch(v_batch_id);
    END IF;
END;
$$;


-- ============================================================
-- 13. RETRIEVAL AND VALIDATION QUERIES
-- ============================================================

-- Retrieve transition probabilities.
SELECT *
FROM v_transition_distribution
ORDER BY process_name, source_state, destination_state;


-- Validate all transition distributions.
SELECT
    p.process_name,
    validation.source_state,
    validation.probability_total,
    validation.is_valid
FROM stochastic_process p
CROSS JOIN LATERAL
    validate_transition_distribution(p.process_id) validation
ORDER BY p.process_name, validation.source_state;


-- Retrieve simulation execution details.
SELECT *
FROM v_simulation_summary
ORDER BY created_at DESC;


-- Retrieve chronological state paths.
SELECT
    r.run_id,
    r.process_id,
    o.step_number,
    s.state_code,
    o.observed_at
FROM state_observation o
JOIN simulation_run r
    ON r.run_id = o.run_id
JOIN process_state s
    ON s.state_id = o.state_id
ORDER BY r.run_id, o.step_number;


-- ============================================================
-- 14. AGGREGATION AND REPORTING
-- ============================================================

-- State frequency across simulations.
SELECT *
FROM v_empirical_state_frequency
ORDER BY process_name, state_code;


-- Mean execution length by process.
SELECT
    p.process_name,
    COUNT(*) AS total_runs,
    ROUND(AVG(r.executed_steps), 3) AS mean_steps,
    MIN(r.executed_steps) AS minimum_steps,
    MAX(r.executed_steps) AS maximum_steps
FROM simulation_run r
JOIN stochastic_process p
    ON p.process_id = r.process_id
GROUP BY p.process_name
ORDER BY p.process_name;


-- Failure probability estimate.
SELECT
    b.batch_name,
    COUNT(*) AS experiments,
    COUNT(*) FILTER (
        WHERE result.reached_target
    ) AS target_hits,
    ROUND(
        COUNT(*) FILTER (
            WHERE result.reached_target
        )::NUMERIC / NULLIF(COUNT(*), 0),
        6
    ) AS estimated_probability,
    ROUND(
        AVG(result.absorption_time),
        3
    ) AS mean_target_time
FROM experiment_result result
JOIN experiment_batch b
    ON b.batch_id = result.batch_id
GROUP BY b.batch_id, b.batch_name;


-- ============================================================
-- 15. EMPIRICAL TRANSITION FREQUENCIES
-- ============================================================

WITH ordered_observations AS (
    SELECT
        r.process_id,
        o.run_id,
        o.step_number,
        o.state_id,
        LEAD(o.state_id) OVER (
            PARTITION BY o.run_id
            ORDER BY o.step_number
        ) AS next_state_id
    FROM state_observation o
    JOIN simulation_run r
        ON r.run_id = o.run_id
),
transition_counts AS (
    SELECT
        process_id,
        state_id,
        next_state_id,
        COUNT(*) AS transition_count
    FROM ordered_observations
    WHERE next_state_id IS NOT NULL
    GROUP BY process_id, state_id, next_state_id
)
SELECT
    p.process_name,
    source.state_code AS source_state,
    destination.state_code AS destination_state,
    transition_counts.transition_count,
    ROUND(
        transition_counts.transition_count::NUMERIC /
        SUM(transition_counts.transition_count) OVER (
            PARTITION BY
                transition_counts.process_id,
                transition_counts.state_id
        ),
        6
    ) AS empirical_transition_probability
FROM transition_counts
JOIN stochastic_process p
    ON p.process_id = transition_counts.process_id
JOIN process_state source
    ON source.state_id = transition_counts.state_id
JOIN process_state destination
    ON destination.state_id = transition_counts.next_state_id
ORDER BY p.process_name, source_state, destination_state;


-- ============================================================
-- 16. ABSORPTION REPORT
-- ============================================================

SELECT
    p.process_name,
    final_state.state_code AS terminal_state,
    COUNT(*) AS completed_runs,
    ROUND(
        COUNT(*)::NUMERIC /
        NULLIF(
            SUM(COUNT(*)) OVER (
                PARTITION BY p.process_id
            ),
            0
        ),
        6
    ) AS terminal_state_frequency,
    ROUND(
        AVG(r.executed_steps),
        3
    ) AS average_steps
FROM simulation_run r
JOIN stochastic_process p
    ON p.process_id = r.process_id
JOIN process_state final_state
    ON final_state.state_id = r.final_state_id
WHERE r.run_status IN ('COMPLETED', 'ABSORBED')
GROUP BY
    p.process_id,
    p.process_name,
    final_state.state_code
ORDER BY p.process_name, terminal_state;


-- ============================================================
-- 17. FAILURE CASE VALIDATION
-- ============================================================

-- The following query identifies any missing transition distribution.
SELECT
    p.process_name,
    validation.source_state,
    validation.probability_total
FROM stochastic_process p
CROSS JOIN LATERAL
    validate_transition_distribution(p.process_id) validation
WHERE NOT validation.is_valid;


-- Detect observations exceeding a run's configured limit.
SELECT
    r.run_id,
    r.maximum_steps,
    MAX(o.step_number) AS observed_maximum_step
FROM simulation_run r
JOIN state_observation o
    ON o.run_id = r.run_id
GROUP BY r.run_id, r.maximum_steps
HAVING MAX(o.step_number) > r.maximum_steps;


-- ============================================================
-- 18. TRANSACTION EXAMPLE
-- ============================================================

BEGIN;

-- A read-only inspection of a selected reliability process.
SELECT
    p.process_name,
    s.state_code,
    s.is_absorbing
FROM stochastic_process p
JOIN process_state s
    ON s.process_id = p.process_id
WHERE p.process_name = 'SYSTEM_RELIABILITY'
ORDER BY s.state_code;

-- The transaction can be committed after inspection.
COMMIT;


-- ============================================================
-- END OF STOCHASTIC PROCESS DATABASE
-- ============================================================
