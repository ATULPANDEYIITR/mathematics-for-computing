DROP SCHEMA IF EXISTS graph_optimization CASCADE;
CREATE SCHEMA graph_optimization;
SET search_path = graph_optimization;

-- PostgreSQL model for a transportation and network-planning workload.
-- Route cost, infrastructure cost, capacity, and connectivity are separate
-- database facts because they represent different optimization objectives.

CREATE TABLE network_node (
    node_id      BIGSERIAL PRIMARY KEY,
    node_code    TEXT NOT NULL UNIQUE,
    node_name    TEXT NOT NULL,
    node_type    TEXT NOT NULL CHECK (
        node_type IN (
            'data_center',
            'regional_hub',
            'service_site',
            'backup_site'
        )
    )
);

CREATE TABLE network_edge (
    edge_id          BIGSERIAL PRIMARY KEY,
    source_node_id   BIGINT NOT NULL REFERENCES network_node(node_id),
    target_node_id   BIGINT NOT NULL REFERENCES network_node(node_id),
    distance_cost    NUMERIC(12, 2) NOT NULL CHECK (distance_cost >= 0),
    capacity_units   INTEGER NOT NULL CHECK (capacity_units >= 0),
    directed         BOOLEAN NOT NULL DEFAULT FALSE,
    active           BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (source_node_id, target_node_id)
);

CREATE INDEX idx_network_edge_source
    ON network_edge(source_node_id)
    WHERE active;

CREATE INDEX idx_network_edge_target
    ON network_edge(target_node_id)
    WHERE active;

CREATE TABLE routing_demand (
    demand_id        BIGSERIAL PRIMARY KEY,
    source_node_id   BIGINT NOT NULL REFERENCES network_node(node_id),
    target_node_id   BIGINT NOT NULL REFERENCES network_node(node_id),
    demand_units     INTEGER NOT NULL CHECK (demand_units > 0),
    priority         INTEGER NOT NULL CHECK (priority BETWEEN 1 AND 5),
    status           TEXT NOT NULL CHECK (
        status IN ('open', 'planned', 'fulfilled', 'cancelled')
    )
);

CREATE TABLE optimization_run (
    run_id             BIGSERIAL PRIMARY KEY,
    objective           TEXT NOT NULL CHECK (
        objective IN (
            'shortest_path',
            'minimum_spanning_tree',
            'maximum_flow'
        )
    ),
    source_node_id     BIGINT REFERENCES network_node(node_id),
    target_node_id     BIGINT REFERENCES network_node(node_id),
    started_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at       TIMESTAMPTZ,
    result_cost        NUMERIC(14, 2),
    result_capacity    INTEGER,
    status              TEXT NOT NULL DEFAULT 'running' CHECK (
        status IN ('running', 'completed', 'failed')
    ),
    CHECK (
        completed_at IS NULL
        OR completed_at >= started_at
    )
);

CREATE TABLE optimization_path (
    run_id             BIGINT NOT NULL REFERENCES optimization_run(run_id)
                       ON DELETE CASCADE,
    sequence_no        INTEGER NOT NULL CHECK (sequence_no >= 0),
    node_id            BIGINT NOT NULL REFERENCES network_node(node_id),
    cumulative_cost    NUMERIC(14, 2) NOT NULL CHECK (cumulative_cost >= 0),
    PRIMARY KEY (run_id, sequence_no),
    UNIQUE (run_id, node_id, sequence_no)
);

CREATE TABLE mst_selection (
    run_id             BIGINT NOT NULL REFERENCES optimization_run(run_id)
                       ON DELETE CASCADE,
    edge_id             BIGINT NOT NULL REFERENCES network_edge(edge_id),
    selection_order     INTEGER NOT NULL CHECK (selection_order > 0),
    PRIMARY KEY (run_id, edge_id),
    UNIQUE (run_id, selection_order)
);

CREATE TABLE flow_allocation (
    run_id             BIGINT NOT NULL REFERENCES optimization_run(run_id)
                       ON DELETE CASCADE,
    edge_id             BIGINT NOT NULL REFERENCES network_edge(edge_id),
    allocated_units     INTEGER NOT NULL CHECK (allocated_units >= 0),
    PRIMARY KEY (run_id, edge_id)
);

INSERT INTO network_node (node_code, node_name, node_type) VALUES
    ('DC-DEL', 'Delhi Data Center', 'data_center'),
    ('HUB-LKO', 'Lucknow Regional Hub', 'regional_hub'),
    ('HUB-JPR', 'Jaipur Regional Hub', 'regional_hub'),
    ('SITE-AGR', 'Agra Service Site', 'service_site'),
    ('SITE-PAT', 'Patna Service Site', 'service_site'),
    ('BACKUP-BPL', 'Bhopal Backup Site', 'backup_site');

INSERT INTO network_edge
    (source_node_id, target_node_id, distance_cost, capacity_units, directed)
SELECT source.node_id, target.node_id, data.distance_cost,
       data.capacity_units, data.directed
FROM (
    VALUES
        ('DC-DEL', 'HUB-LKO', 4.00, 80, TRUE),
        ('DC-DEL', 'HUB-JPR', 6.00, 70, TRUE),
        ('HUB-LKO', 'HUB-JPR', 2.00, 60, TRUE),
        ('HUB-LKO', 'SITE-AGR', 2.50, 30, TRUE),
        ('HUB-JPR', 'SITE-AGR', 4.00, 40, TRUE),
        ('HUB-LKO', 'SITE-PAT', 5.00, 50, TRUE),
        ('HUB-JPR', 'BACKUP-BPL', 3.00, 45, TRUE),
        ('SITE-PAT', 'BACKUP-BPL', 2.00, 25, TRUE)
) AS data(source_code, target_code, distance_cost, capacity_units, directed)
JOIN network_node source
  ON source.node_code = data.source_code
JOIN network_node target
  ON target.node_code = data.target_code;

INSERT INTO routing_demand
    (source_node_id, target_node_id, demand_units, priority, status)
SELECT source.node_id, target.node_id, data.demand_units,
       data.priority, data.status
FROM (
    VALUES
        ('DC-DEL', 'SITE-PAT', 35, 1, 'open'),
        ('DC-DEL', 'SITE-AGR', 20, 2, 'planned'),
        ('HUB-LKO', 'BACKUP-BPL', 15, 3, 'open')
) AS data(source_code, target_code, demand_units, priority, status)
JOIN network_node source
  ON source.node_code = data.source_code
JOIN network_node target
  ON target.node_code = data.target_code;

-- Direct edge inspection identifies the cheapest immediate link, but it does
-- not solve the shortest-path problem because a multi-edge route can be cheaper.
SELECT
    source.node_code AS source,
    target.node_code AS target,
    edge.distance_cost,
    edge.capacity_units
FROM network_edge edge
JOIN network_node source ON source.node_id = edge.source_node_id
JOIN network_node target ON target.node_id = edge.target_node_id
WHERE edge.active
ORDER BY edge.distance_cost, source.node_code, target.node_code;

-- PostgreSQL recursive CTE for path enumeration on the small demonstration
-- network. The path array prevents revisiting nodes and therefore avoids
-- cycles while evaluating candidate routes.
WITH RECURSIVE routes AS (
    SELECT
        edge.source_node_id AS start_node,
        edge.target_node_id AS current_node,
        ARRAY[edge.source_node_id, edge.target_node_id]::BIGINT[] AS path,
        edge.distance_cost AS total_cost
    FROM network_edge edge
    WHERE edge.active

    UNION ALL

    SELECT
        route.start_node,
        edge.target_node_id,
        route.path || edge.target_node_id,
        route.total_cost + edge.distance_cost
    FROM routes route
    JOIN network_edge edge
      ON edge.source_node_id = route.current_node
     AND edge.active
    WHERE NOT edge.target_node_id = ANY(route.path)
),
ranked_routes AS (
    SELECT
        route.start_node,
        route.current_node AS target_node,
        route.path,
        route.total_cost,
        ROW_NUMBER() OVER (
            PARTITION BY route.start_node, route.current_node
            ORDER BY route.total_cost, cardinality(route.path)
        ) AS route_rank
    FROM routes route
)
SELECT
    source.node_code AS source,
    target.node_code AS target,
    ranked.total_cost,
    ranked.path
FROM ranked_routes ranked
JOIN network_node source
  ON source.node_id = ranked.start_node
JOIN network_node target
  ON target.node_id = ranked.target_node
WHERE ranked.route_rank = 1
ORDER BY source.node_code, target.node_code;

-- A database-level transaction records a completed optimization result and
-- its selected route atomically. If any statement fails, the entire result
-- can be rolled back rather than leaving a partial optimization run.
BEGIN;

INSERT INTO optimization_run (
    objective,
    source_node_id,
    target_node_id,
    result_cost,
    status
)
SELECT
    'shortest_path',
    source.node_id,
    target.node_id,
    9.00,
    'completed'
FROM network_node source
JOIN network_node target ON target.node_code = 'SITE-PAT'
WHERE source.node_code = 'DC-DEL'
RETURNING run_id;

-- The demonstration route is DC-DEL -> HUB-LKO -> SITE-PAT.
INSERT INTO optimization_path
    (run_id, sequence_no, node_id, cumulative_cost)
SELECT
    run.run_id,
    route.sequence_no,
    node.node_id,
    route.cumulative_cost
FROM optimization_run run
CROSS JOIN (
    VALUES
        (0, 'DC-DEL', 0.00::NUMERIC),
        (1, 'HUB-LKO', 4.00::NUMERIC),
        (2, 'SITE-PAT', 9.00::NUMERIC)
) AS route(sequence_no, node_code, cumulative_cost)
JOIN network_node node
  ON node.node_code = route.node_code
WHERE run.objective = 'shortest_path'
  AND run.status = 'completed'
  AND run.run_id = (
      SELECT MAX(run_id)
      FROM optimization_run
      WHERE objective = 'shortest_path'
  );

COMMIT;

-- Capacity feasibility: a requested flow must never exceed the capacity of
-- any edge used by that allocation.
WITH requested AS (
    SELECT
        edge.edge_id,
        edge.capacity_units,
        COALESCE(flow.allocated_units, 0) AS allocated_units
    FROM network_edge edge
    LEFT JOIN flow_allocation flow
      ON flow.edge_id = edge.edge_id
    WHERE edge.active
)
SELECT
    edge_id,
    capacity_units,
    allocated_units,
    capacity_units - allocated_units AS remaining_capacity,
    allocated_units <= capacity_units AS feasible
FROM requested
ORDER BY feasible, edge_id;

-- Operational view combining active links with their utilization.
CREATE OR REPLACE VIEW active_network_utilization AS
SELECT
    edge.edge_id,
    source.node_code AS source,
    target.node_code AS target,
    edge.capacity_units,
    COALESCE(SUM(flow.allocated_units), 0) AS allocated_units,
    edge.capacity_units
        - COALESCE(SUM(flow.allocated_units), 0) AS remaining_capacity,
    CASE
        WHEN edge.capacity_units = 0 THEN NULL
        ELSE ROUND(
            100.0 * COALESCE(SUM(flow.allocated_units), 0)
            / edge.capacity_units,
            2
        )
    END AS utilization_percent
FROM network_edge edge
JOIN network_node source
  ON source.node_id = edge.source_node_id
JOIN network_node target
  ON target.node_id = edge.target_node_id
LEFT JOIN flow_allocation flow
  ON flow.edge_id = edge.edge_id
WHERE edge.active
GROUP BY
    edge.edge_id,
    source.node_code,
    target.node_code,
    edge.capacity_units;

SELECT *
FROM active_network_utilization
ORDER BY utilization_percent DESC NULLS LAST;

-- Integrity checks expose topology conditions that application code should
-- not silently assume. Nodes with no active outgoing edge are operationally
-- isolated from directed routing.
SELECT
    node.node_code,
    node.node_name
FROM network_node node
WHERE NOT EXISTS (
    SELECT 1
    FROM network_edge edge
    WHERE edge.source_node_id = node.node_id
      AND edge.active
);

-- Optimization records can be audited independently from the current graph.
SELECT
    run.run_id,
    run.objective,
    source.node_code AS source,
    target.node_code AS target,
    run.result_cost,
    run.result_capacity,
    run.status,
    run.started_at,
    run.completed_at
FROM optimization_run run
LEFT JOIN network_node source
  ON source.node_id = run.source_node_id
LEFT JOIN network_node target
  ON target.node_id = run.target_node_id
ORDER BY run.run_id;
