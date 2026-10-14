-- PostgreSQL graph traversal matrix laboratory.
-- Models graph vertices and edges, builds adjacency matrices, and uses
-- recursive CTEs for BFS-style shortest unweighted paths and reachability.
--
-- Run in a disposable PostgreSQL database:
--   psql -v ON_ERROR_STOP=1 -f graph_traversal_matrix.sql

BEGIN;

DROP VIEW IF EXISTS graph_edge_list CASCADE;
DROP TABLE IF EXISTS traversal_results CASCADE;
DROP TABLE IF EXISTS graph_edges CASCADE;
DROP TABLE IF EXISTS graph_vertices CASCADE;
DROP TABLE IF EXISTS graph_definitions CASCADE;

CREATE TABLE graph_definitions (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name TEXT NOT NULL UNIQUE,
    graph_type TEXT NOT NULL CHECK (
        graph_type IN ('directed', 'undirected')
    ),
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE graph_vertices (
    graph_id BIGINT NOT NULL REFERENCES graph_definitions(graph_id)
        ON DELETE CASCADE,
    vertex_id INTEGER NOT NULL CHECK (vertex_id >= 0),
    vertex_label TEXT NOT NULL,
    PRIMARY KEY (graph_id, vertex_id),
    UNIQUE (graph_id, vertex_label)
);

CREATE TABLE graph_edges (
    graph_id BIGINT NOT NULL,
    source_vertex INTEGER NOT NULL,
    target_vertex INTEGER NOT NULL,
    edge_weight NUMERIC(12, 3) NOT NULL DEFAULT 1
        CHECK (edge_weight > 0),
    PRIMARY KEY (graph_id, source_vertex, target_vertex),
    FOREIGN KEY (graph_id, source_vertex)
        REFERENCES graph_vertices(graph_id, vertex_id)
        ON DELETE CASCADE,
    FOREIGN KEY (graph_id, target_vertex)
        REFERENCES graph_vertices(graph_id, vertex_id)
        ON DELETE CASCADE,
    CHECK (source_vertex <> target_vertex)
);

CREATE INDEX graph_edges_target_idx
    ON graph_edges (graph_id, target_vertex, source_vertex);

CREATE TABLE traversal_results (
    traversal_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graph_definitions(graph_id)
        ON DELETE CASCADE,
    start_vertex INTEGER NOT NULL,
    target_vertex INTEGER NOT NULL,
    traversal_algorithm TEXT NOT NULL CHECK (
        traversal_algorithm IN ('bfs', 'dfs')
    ),
    path_vertices INTEGER[] NOT NULL,
    distance INTEGER NOT NULL CHECK (distance >= 0),
    computed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (graph_id, start_vertex)
        REFERENCES graph_vertices(graph_id, vertex_id),
    FOREIGN KEY (graph_id, target_vertex)
        REFERENCES graph_vertices(graph_id, vertex_id)
);

CREATE VIEW graph_edge_list AS
SELECT
    g.graph_name,
    g.graph_type,
    source.vertex_label AS source_label,
    target.vertex_label AS target_label,
    e.edge_weight
FROM graph_edges AS e
JOIN graph_definitions AS g USING (graph_id)
JOIN graph_vertices AS source
    ON source.graph_id = e.graph_id
   AND source.vertex_id = e.source_vertex
JOIN graph_vertices AS target
    ON target.graph_id = e.graph_id
   AND target.vertex_id = e.target_vertex;

INSERT INTO graph_definitions (graph_name, graph_type, description)
VALUES
    (
        'service_dependencies',
        'directed',
        'Services and their directed dependency relationships'
    ),
    (
        'transport_network',
        'undirected',
        'Intersections connected by bidirectional roads'
    );

INSERT INTO graph_vertices (graph_id, vertex_id, vertex_label)
SELECT g.graph_id, v.vertex_id, v.vertex_label
FROM graph_definitions AS g
CROSS JOIN (
    VALUES
        (0, 'gateway'),
        (1, 'identity'),
        (2, 'catalog'),
        (3, 'orders'),
        (4, 'inventory'),
        (5, 'reporting')
) AS v(vertex_id, vertex_label)
WHERE g.graph_name = 'service_dependencies';

INSERT INTO graph_edges (
    graph_id, source_vertex, target_vertex, edge_weight
)
SELECT g.graph_id, e.source_vertex, e.target_vertex, e.edge_weight
FROM graph_definitions AS g
CROSS JOIN (
    VALUES
        (0, 1, 1.0::NUMERIC),
        (0, 2, 1.0::NUMERIC),
        (1, 3, 1.0::NUMERIC),
        (1, 4, 1.0::NUMERIC),
        (2, 4, 1.0::NUMERIC),
        (3, 5, 1.0::NUMERIC),
        (4, 5, 1.0::NUMERIC)
) AS e(source_vertex, target_vertex, edge_weight)
WHERE g.graph_name = 'service_dependencies';

INSERT INTO graph_vertices (graph_id, vertex_id, vertex_label)
SELECT g.graph_id, v.vertex_id, v.vertex_label
FROM graph_definitions AS g
CROSS JOIN (
    VALUES
        (0, 'north_station'),
        (1, 'central_station'),
        (2, 'east_station'),
        (3, 'airport'),
        (4, 'harbor')
) AS v(vertex_id, vertex_label)
WHERE g.graph_name = 'transport_network';

-- Each undirected road is stored once in each direction so that the
-- adjacency relation and traversal queries remain straightforward.
INSERT INTO graph_edges (
    graph_id, source_vertex, target_vertex, edge_weight
)
SELECT g.graph_id, e.source_vertex, e.target_vertex, e.edge_weight
FROM graph_definitions AS g
CROSS JOIN (
    VALUES
        (0, 1, 4.0::NUMERIC),
        (1, 2, 2.0::NUMERIC),
        (1, 3, 7.0::NUMERIC),
        (2, 3, 3.0::NUMERIC),
        (3, 4, 5.0::NUMERIC)
) AS e(source_vertex, target_vertex, edge_weight)
WHERE g.graph_name = 'transport_network';

INSERT INTO graph_edges (
    graph_id, source_vertex, target_vertex, edge_weight
)
SELECT
    graph_id,
    target_vertex,
    source_vertex,
    edge_weight
FROM graph_edges
WHERE graph_id = (
    SELECT graph_id
    FROM graph_definitions
    WHERE graph_name = 'transport_network'
);

-- Inspect graph edges with human-readable vertex labels.
SELECT *
FROM graph_edge_list
ORDER BY graph_name, source_label, target_label;

-- Construct a matrix-shaped result. Missing edges become zero.
-- This result is a display representation; graph_edges remains the
-- normalized source of truth for relational queries.
SELECT
    g.graph_name,
    source.vertex_id AS row_vertex,
    target.vertex_id AS column_vertex,
    COALESCE(e.edge_weight, 0) AS matrix_value
FROM graph_definitions AS g
JOIN graph_vertices AS source USING (graph_id)
JOIN graph_vertices AS target USING (graph_id)
LEFT JOIN graph_edges AS e
    ON e.graph_id = g.graph_id
   AND e.source_vertex = source.vertex_id
   AND e.target_vertex = target.vertex_id
WHERE g.graph_name = 'service_dependencies'
ORDER BY source.vertex_id, target.vertex_id;

-- BFS-style traversal using a recursive CTE.
-- Each recursive step extends a path by one edge. The array membership
-- check prevents cycles within an individual candidate path.
-- DISTINCT ON selects a shortest discovered path for each target.
WITH RECURSIVE walk AS (
    SELECT
        e.graph_id,
        e.source_vertex AS start_vertex,
        e.target_vertex AS current_vertex,
        ARRAY[e.source_vertex, e.target_vertex] AS path_vertices,
        1 AS distance
    FROM graph_edges AS e
    JOIN graph_definitions AS g USING (graph_id)
    WHERE g.graph_name = 'service_dependencies'
      AND e.source_vertex = 0

    UNION ALL

    SELECT
        w.graph_id,
        w.start_vertex,
        e.target_vertex,
        w.path_vertices || e.target_vertex,
        w.distance + 1
    FROM walk AS w
    JOIN graph_edges AS e
      ON e.graph_id = w.graph_id
     AND e.source_vertex = w.current_vertex
    WHERE NOT e.target_vertex = ANY(w.path_vertices)
),
candidates AS (
    SELECT
        graph_id,
        start_vertex,
        current_vertex AS target_vertex,
        path_vertices,
        distance
    FROM walk

    UNION ALL

    SELECT
        g.graph_id,
        0,
        0,
        ARRAY[0],
        0
    FROM graph_definitions AS g
    WHERE g.graph_name = 'service_dependencies'
)
SELECT DISTINCT ON (target_vertex)
    target_vertex,
    path_vertices,
    distance
FROM candidates
WHERE graph_id = (
    SELECT graph_id
    FROM graph_definitions
    WHERE graph_name = 'service_dependencies'
)
ORDER BY target_vertex, distance, path_vertices;

-- Persist shortest unweighted paths from the gateway.
WITH RECURSIVE walk AS (
    SELECT
        e.graph_id,
        e.source_vertex AS start_vertex,
        e.target_vertex AS current_vertex,
        ARRAY[e.source_vertex, e.target_vertex] AS path_vertices,
        1 AS distance
    FROM graph_edges AS e
    JOIN graph_definitions AS g USING (graph_id)
    WHERE g.graph_name = 'service_dependencies'
      AND e.source_vertex = 0

    UNION ALL

    SELECT
        w.graph_id,
        w.start_vertex,
        e.target_vertex,
        w.path_vertices || e.target_vertex,
        w.distance + 1
    FROM walk AS w
    JOIN graph_edges AS e
      ON e.graph_id = w.graph_id
     AND e.source_vertex = w.current_vertex
    WHERE NOT e.target_vertex = ANY(w.path_vertices)
),
candidates AS (
    SELECT
        graph_id,
        start_vertex,
        current_vertex AS target_vertex,
        path_vertices,
        distance
    FROM walk

    UNION ALL

    SELECT
        graph_id,
        0,
        0,
        ARRAY[0],
        0
    FROM graph_definitions
    WHERE graph_name = 'service_dependencies'
)
INSERT INTO traversal_results (
    graph_id,
    start_vertex,
    target_vertex,
    traversal_algorithm,
    path_vertices,
    distance
)
SELECT DISTINCT ON (target_vertex)
    graph_id,
    start_vertex,
    target_vertex,
    'bfs',
    path_vertices,
    distance
FROM candidates
WHERE graph_id = (
    SELECT graph_id
    FROM graph_definitions
    WHERE graph_name = 'service_dependencies'
)
ORDER BY target_vertex, distance, path_vertices;

SELECT
    result.target_vertex,
    vertex.vertex_label AS target_label,
    result.path_vertices,
    result.distance
FROM traversal_results AS result
JOIN graph_vertices AS vertex
    ON vertex.graph_id = result.graph_id
   AND vertex.vertex_id = result.target_vertex
ORDER BY result.distance, result.target_vertex;

-- Evaluate reachability from a specified vertex without persisting results.
WITH RECURSIVE reachable(vertex_id) AS (
    SELECT 0

    UNION

    SELECT e.target_vertex
    FROM reachable AS r
    JOIN graph_edges AS e
      ON e.source_vertex = r.vertex_id
    JOIN graph_definitions AS g USING (graph_id)
    WHERE g.graph_name = 'service_dependencies'
)
SELECT
    v.vertex_id,
    v.vertex_label,
    r.vertex_id IS NOT NULL AS reachable_from_gateway
FROM graph_vertices AS v
JOIN graph_definitions AS g USING (graph_id)
LEFT JOIN reachable AS r USING (vertex_id)
WHERE g.graph_name = 'service_dependencies'
ORDER BY v.vertex_id;

-- A matrix is appropriate for dense graphs and predictable vertex indices.
-- For sparse graphs, the normalized edge table usually consumes less space.
SELECT
    g.graph_name,
    COUNT(DISTINCT v.vertex_id) AS vertex_count,
    COUNT(e.source_vertex) AS directed_edge_count,
    COUNT(DISTINCT v.vertex_id) ^ 2 AS matrix_cell_count
FROM graph_definitions AS g
JOIN graph_vertices AS v USING (graph_id)
LEFT JOIN graph_edges AS e USING (graph_id)
GROUP BY g.graph_id, g.graph_name
ORDER BY g.graph_name;

-- Demonstrate transaction rollback for an invalid edge.
-- The foreign key rejects a nonexistent target vertex.
SAVEPOINT invalid_edge_test;

DO $$
BEGIN
    BEGIN
        INSERT INTO graph_edges (
            graph_id, source_vertex, target_vertex, edge_weight
        )
        VALUES (
            (
                SELECT graph_id
                FROM graph_definitions
                WHERE graph_name = 'service_dependencies'
            ),
            0,
            999,
            1
        );

        RAISE EXCEPTION 'Expected foreign-key validation to fail.';
    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE 'Invalid edge rejected by foreign-key constraint.';
    END;
END;
$$;

ROLLBACK TO SAVEPOINT invalid_edge_test;
RELEASE SAVEPOINT invalid_edge_test;

COMMIT;
