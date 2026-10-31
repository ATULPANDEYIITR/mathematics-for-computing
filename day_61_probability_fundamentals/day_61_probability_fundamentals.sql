DROP SCHEMA IF EXISTS probability_fundamentals CASCADE;
CREATE SCHEMA probability_fundamentals;
SET search_path TO probability_fundamentals;

-- A finite probability model stores each outcome exactly once.
CREATE TABLE sample_spaces (
    sample_space_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE outcomes (
    outcome_id BIGSERIAL PRIMARY KEY,
    sample_space_id BIGINT NOT NULL
        REFERENCES sample_spaces(sample_space_id)
        ON DELETE CASCADE,
    outcome_value INTEGER NOT NULL,
    probability NUMERIC(18,12) NOT NULL,
    UNIQUE (sample_space_id, outcome_value),
    CHECK (probability >= 0 AND probability <= 1)
);

CREATE TABLE events (
    event_id BIGSERIAL PRIMARY KEY,
    sample_space_id BIGINT NOT NULL
        REFERENCES sample_spaces(sample_space_id)
        ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    UNIQUE (sample_space_id, name)
);

CREATE TABLE event_outcomes (
    event_id BIGINT NOT NULL
        REFERENCES events(event_id)
        ON DELETE CASCADE,
    outcome_id BIGINT NOT NULL
        REFERENCES outcomes(outcome_id)
        ON DELETE CASCADE,
    PRIMARY KEY (event_id, outcome_id)
);

CREATE TABLE experiments (
    experiment_id BIGSERIAL PRIMARY KEY,
    sample_space_id BIGINT NOT NULL
        REFERENCES sample_spaces(sample_space_id),
    name TEXT NOT NULL,
    trials INTEGER NOT NULL CHECK (trials > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE experiment_results (
    result_id BIGSERIAL PRIMARY KEY,
    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,
    outcome_id BIGINT NOT NULL
        REFERENCES outcomes(outcome_id),
    observed_count INTEGER NOT NULL CHECK (observed_count >= 0),
    UNIQUE (experiment_id, outcome_id)
);

CREATE TABLE probability_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    max_absolute_error NUMERIC(18,12) NOT NULL,
    CHECK (max_absolute_error > 0)
);

CREATE INDEX idx_outcomes_sample_space
    ON outcomes(sample_space_id);

CREATE INDEX idx_events_sample_space
    ON events(sample_space_id);

CREATE INDEX idx_event_outcomes_outcome
    ON event_outcomes(outcome_id);

CREATE INDEX idx_results_experiment
    ON experiment_results(experiment_id);

CREATE OR REPLACE FUNCTION validate_sample_space_probabilities(
    p_sample_space_id BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    outcome_count INTEGER;
    probability_sum NUMERIC(30,15);
BEGIN
    SELECT COUNT(*), COALESCE(SUM(probability), 0)
    INTO outcome_count, probability_sum
    FROM outcomes
    WHERE sample_space_id = p_sample_space_id;

    IF outcome_count = 0 THEN
        RAISE EXCEPTION
            'Sample space % has no outcomes',
            p_sample_space_id;
    END IF;

    IF ABS(probability_sum - 1) > 0.000000000001 THEN
        RAISE EXCEPTION
            'Sample space % has probability total %, expected 1',
            p_sample_space_id,
            probability_sum;
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION event_probability(
    p_event_id BIGINT
)
RETURNS NUMERIC(18,12)
LANGUAGE sql
STABLE
AS $$
    SELECT COALESCE(SUM(o.probability), 0)::NUMERIC(18,12)
    FROM event_outcomes eo
    JOIN outcomes o
      ON o.outcome_id = eo.outcome_id
    WHERE eo.event_id = p_event_id;
$$;

CREATE OR REPLACE FUNCTION validate_event_sample_space()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    event_space BIGINT;
    outcome_space BIGINT;
BEGIN
    SELECT sample_space_id
    INTO event_space
    FROM events
    WHERE event_id = NEW.event_id;

    SELECT sample_space_id
    INTO outcome_space
    FROM outcomes
    WHERE outcome_id = NEW.outcome_id;

    IF event_space IS NULL OR outcome_space IS NULL THEN
        RAISE EXCEPTION 'Event and outcome must exist';
    END IF;

    IF event_space <> outcome_space THEN
        RAISE EXCEPTION
            'Event % and outcome % belong to different sample spaces',
            NEW.event_id,
            NEW.outcome_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_event_sample_space
BEFORE INSERT OR UPDATE ON event_outcomes
FOR EACH ROW
EXECUTE FUNCTION validate_event_sample_space();

CREATE OR REPLACE VIEW event_probability_report AS
SELECT
    e.event_id,
    ss.name AS sample_space,
    e.name AS event_name,
    COUNT(eo.outcome_id) AS outcome_count,
    COALESCE(SUM(o.probability), 0)::NUMERIC(18,12) AS event_probability
FROM events e
JOIN sample_spaces ss
  ON ss.sample_space_id = e.sample_space_id
LEFT JOIN event_outcomes eo
  ON eo.event_id = e.event_id
LEFT JOIN outcomes o
  ON o.outcome_id = eo.outcome_id
GROUP BY e.event_id, ss.name, e.name;

CREATE OR REPLACE VIEW experiment_distribution_report AS
SELECT
    e.experiment_id,
    e.name AS experiment_name,
    o.outcome_value,
    o.probability AS theoretical_probability,
    er.observed_count,
    ROUND(
        er.observed_count::NUMERIC / e.trials,
        6
    ) AS empirical_probability,
    ROUND(
        (er.observed_count::NUMERIC / e.trials) - o.probability,
        6
    ) AS empirical_minus_theoretical
FROM experiments e
JOIN experiment_results er
  ON er.experiment_id = e.experiment_id
JOIN outcomes o
  ON o.outcome_id = er.outcome_id;

INSERT INTO sample_spaces (name, description)
VALUES (
    'fair_six_sided_die',
    'One roll of a fair six-sided die.'
);

INSERT INTO outcomes (
    sample_space_id,
    outcome_value,
    probability
)
SELECT
    sample_space_id,
    value,
    1.0 / 6.0
FROM sample_spaces
CROSS JOIN generate_series(1, 6) AS value
WHERE name = 'fair_six_sided_die';

INSERT INTO events (sample_space_id, name, description)
SELECT
    sample_space_id,
    'even',
    'The die result is divisible by two.'
FROM sample_spaces
WHERE name = 'fair_six_sided_die';

INSERT INTO events (sample_space_id, name, description)
SELECT
    sample_space_id,
    'prime',
    'The die result is prime.'
FROM sample_spaces
WHERE name = 'fair_six_sided_die';

INSERT INTO events (sample_space_id, name, description)
SELECT
    sample_space_id,
    'greater_than_three',
    'The die result is greater than three.'
FROM sample_spaces
WHERE name = 'fair_six_sided_die';

INSERT INTO event_outcomes (event_id, outcome_id)
SELECT
    e.event_id,
    o.outcome_id
FROM events e
JOIN outcomes o
  ON o.sample_space_id = e.sample_space_id
WHERE e.name = 'even'
  AND o.outcome_value IN (2, 4, 6);

INSERT INTO event_outcomes (event_id, outcome_id)
SELECT
    e.event_id,
    o.outcome_id
FROM events e
JOIN outcomes o
  ON o.sample_space_id = e.sample_space_id
WHERE e.name = 'prime'
  AND o.outcome_value IN (2, 3, 5);

INSERT INTO event_outcomes (event_id, outcome_id)
SELECT
    e.event_id,
    o.outcome_id
FROM events e
JOIN outcomes o
  ON o.sample_space_id = e.sample_space_id
WHERE e.name = 'greater_than_three'
  AND o.outcome_value IN (4, 5, 6);

INSERT INTO experiments (sample_space_id, name, trials)
SELECT
    sample_space_id,
    'die_simulation_100000',
    100000
FROM sample_spaces
WHERE name = 'fair_six_sided_die';

-- Deterministic demonstration counts representing one recorded experiment.
INSERT INTO experiment_results (
    experiment_id,
    outcome_id,
    observed_count
)
SELECT
    e.experiment_id,
    o.outcome_id,
    counts.observed_count
FROM experiments e
JOIN sample_spaces ss
  ON ss.sample_space_id = e.sample_space_id
JOIN outcomes o
  ON o.sample_space_id = ss.sample_space_id
JOIN (
    VALUES
        (1, 16704),
        (2, 16591),
        (3, 16644),
        (4, 16703),
        (5, 16696),
        (6, 16662)
) AS counts(outcome_value, observed_count)
  ON counts.outcome_value = o.outcome_value
WHERE e.name = 'die_simulation_100000';

INSERT INTO probability_policies (
    name,
    description,
    max_absolute_error
)
VALUES (
    'simulation_accuracy_2_percent',
    'A simulation estimate is accepted when its absolute error is at most two percentage points.',
    0.02
);

-- Transactional validation of the probability model.
BEGIN;

SELECT validate_sample_space_probabilities(
    sample_space_id
)
FROM sample_spaces
WHERE name = 'fair_six_sided_die';

COMMIT;

-- Retrieval: probabilities of all defined events.
SELECT *
FROM event_probability_report
ORDER BY event_id;

-- Validation: the sample-space axiom P(Omega) = 1.
SELECT
    ss.name,
    SUM(o.probability)::NUMERIC(18,12) AS total_probability,
    ABS(SUM(o.probability) - 1)::NUMERIC(18,12) AS distance_from_one
FROM sample_spaces ss
JOIN outcomes o
  ON o.sample_space_id = ss.sample_space_id
GROUP BY ss.sample_space_id, ss.name;

-- Evaluation: complement of an event.
WITH even_event AS (
    SELECT event_id
    FROM events
    WHERE name = 'even'
),
all_outcomes AS (
    SELECT
        o.outcome_id,
        o.probability
    FROM outcomes o
    JOIN sample_spaces ss
      ON ss.sample_space_id = o.sample_space_id
    WHERE ss.name = 'fair_six_sided_die'
)
SELECT
    SUM(ao.probability)::NUMERIC(18,12) AS complement_probability
FROM all_outcomes ao
WHERE ao.outcome_id NOT IN (
    SELECT outcome_id
    FROM event_outcomes
    WHERE event_id = (SELECT event_id FROM even_event)
);

-- Evaluation: addition rule for even OR prime.
WITH event_probabilities AS (
    SELECT
        e.name,
        event_probability(e.event_id) AS probability
    FROM events e
    WHERE e.name IN ('even', 'prime')
),
intersection_probability AS (
    SELECT COALESCE(SUM(o.probability), 0) AS probability
    FROM outcomes o
    JOIN event_outcomes eo1
      ON eo1.outcome_id = o.outcome_id
    JOIN event_outcomes eo2
      ON eo2.outcome_id = o.outcome_id
    JOIN events e1
      ON e1.event_id = eo1.event_id
    JOIN events e2
      ON e2.event_id = eo2.event_id
    WHERE e1.name = 'even'
      AND e2.name = 'prime'
)
SELECT
    (SELECT probability
     FROM event_probabilities
     WHERE name = 'even')
    +
    (SELECT probability
     FROM event_probabilities
     WHERE name = 'prime')
    -
    (SELECT probability FROM intersection_probability)
    AS probability_even_or_prime;

-- Conditional probability P(prime | even).
WITH even_probability AS (
    SELECT event_probability(event_id) AS p
    FROM events
    WHERE name = 'even'
),
intersection_probability AS (
    SELECT COALESCE(SUM(o.probability), 0) AS p
    FROM outcomes o
    JOIN event_outcomes eo1
      ON eo1.outcome_id = o.outcome_id
    JOIN event_outcomes eo2
      ON eo2.outcome_id = o.outcome_id
    JOIN events e1
      ON e1.event_id = eo1.event_id
    JOIN events e2
      ON e2.event_id = eo2.event_id
    WHERE e1.name = 'prime'
      AND e2.name = 'even'
)
SELECT
    intersection_probability.p / even_probability.p
        AS probability_prime_given_even
FROM intersection_probability, even_probability;

-- Experiment reporting compares empirical and theoretical distributions.
SELECT *
FROM experiment_distribution_report
ORDER BY outcome_value;

-- Aggregation: total observed trials must equal the experiment trial count.
SELECT
    e.name,
    e.trials,
    SUM(er.observed_count) AS recorded_trials,
    e.trials = SUM(er.observed_count) AS trial_count_valid
FROM experiments e
JOIN experiment_results er
  ON er.experiment_id = e.experiment_id
GROUP BY e.experiment_id, e.name, e.trials;

-- Eligibility evaluation for a simulation-accuracy policy.
SELECT
    edr.experiment_name,
    pp.name AS policy,
    MAX(ABS(edr.empirical_minus_theoretical)) AS maximum_absolute_error,
    MAX(ABS(edr.empirical_minus_theoretical))
        <= pp.max_absolute_error AS eligible_under_policy
FROM experiment_distribution_report edr
CROSS JOIN probability_policies pp
WHERE pp.name = 'simulation_accuracy_2_percent'
GROUP BY edr.experiment_name, pp.name, pp.max_absolute_error;
