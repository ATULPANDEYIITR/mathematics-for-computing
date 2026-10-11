-- PostgreSQL graph theory fundamentals.
--
-- The schema stores vertices separately from edges so isolated vertices
-- remain visible. A single logical edge table represents directed and
-- undirected graphs. Undirected edges use canonical endpoint ordering.

BEGIN;

DROP SCHEMA IF EXISTS graph_lab CASCADE;
CREATE SCHEMA graph_lab;
SET search_path TO graph_lab, public;

CREATE TYPE graph_kind AS ENUM ('DIRECTED', 'UNDIRECTED');

CREATE TABLE graph (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name TEXT NOT NULL UNIQUE,
    kind graph_kind NOT NULL,
    weighted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(graph_name)) > 0)
);

CREATE TABLE vertex (
    graph_id BIGINT NOT NULL REFERENCES graph(graph_id) ON DELETE CASCADE,
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY,
    vertex_key TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (graph_id, vertex_id),
    UNIQUE (graph_id, vertex_key),
    CHECK (length(trim(vertex_key)) > 0)
);

CREATE TABLE edge (
    graph_id BIGINT NOT NULL,
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY,
    source_vertex_id BIGINT NOT NULL,
    target_vertex_id BIGINT NOT NULL,
    weight DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    PRIMARY KEY (graph_id, edge_id),
    FOREIGN KEY (graph_id, source_vertex_id)
        REFERENCES vertex(graph_id, vertex_id) ON DELETE CASCADE,
    FOREIGN KEY (graph_id, target_vertex_id)
        REFERENCES vertex(graph_id, vertex_id) ON DELETE CASCADE,
    CHECK (weight > '-Infinity'::DOUBLE PRECISION),
    CHECK (weight < 'Infinity'::DOUBLE PRECISION),
    UNIQUE (graph_id, source_vertex_id, target_vertex_id)
);

-- An undirected graph stores each edge once with the smaller vertex ID first.
-- The trigger below normalizes endpoints and prevents duplicate reverse edges.

CREATE OR REPLACE FUNCTION normalize_graph_edge()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    selected_kind graph_kind;
BEGIN
    SELECT kind
      INTO selected_kind
      FROM graph
     WHERE graph_id = NEW.graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown graph %', NEW.graph_id;
    END IF;

    IF NEW.source_vertex_id = NEW.target_vertex_id THEN
        -- Self-loops are valid and remain a single stored edge.
        RETURN NEW;
    END IF;

    IF selected_kind = 'UNDIRECTED'
       AND NEW.source_vertex_id > NEW.target_vertex_id THEN
        SELECT NEW.target_vertex_id, NEW.source_vertex_id
          INTO NEW.source_vertex_id, NEW.target_vertex_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER edge_endpoint_normalization
BEFORE INSERT OR UPDATE OF graph_id, source_vertex_id, target_vertex_id
ON edge
FOR EACH ROW
EXECUTE FUNCTION normalize_graph_edge();

CREATE INDEX edge_source_lookup
    ON edge(graph_id, source_vertex_id);

CREATE INDEX edge_target_lookup
    ON edge(graph_id, target_vertex_id);

INSERT INTO graph (graph_name, kind, weighted)
VALUES
    ('campus_network', 'UNDIRECTED', TRUE),
    ('service_dependencies', 'DIRECTED', FALSE);

INSERT INTO vertex (graph_id, vertex_key, description)
SELECT g.graph_id, v.vertex_key, v.description
FROM graph AS g
CROSS JOIN (
    VALUES
        ('Gateway', 'Campus Internet gateway'),
        ('CoreSwitch', 'Central network switch'),
        ('Library', 'Library access network'),
        ('ServerRoom', 'Application and database servers'),
        ('OfflineLab', 'Currently isolated laboratory')
) AS v(vertex_key, description)
WHERE g.graph_name = 'campus_network';

INSERT INTO vertex (graph_id, vertex_key, description)
SELECT g.graph_id, v.vertex_key, v.description
FROM graph AS g
CROSS JOIN (
    VALUES
        ('IdentityService', 'Authentication service'),
        ('OrderAPI', 'Order processing API'),
        ('InventoryService', 'Inventory service'),
        ('AuditPipeline', 'Audit event consumer')
) AS v(vertex_key, description)
WHERE g.graph_name = 'service_dependencies';

INSERT INTO edge (graph_id, source_vertex_id, target_vertex_id, weight)
SELECT g.graph_id, source.vertex_id, target.vertex_id, e.weight
FROM graph AS g
JOIN (
    VALUES
        ('Gateway', 'CoreSwitch', 2.0::DOUBLE PRECISION),
        ('CoreSwitch', 'Library', 3.0::DOUBLE PRECISION),
        ('CoreSwitch', 'ServerRoom', 1.0::DOUBLE PRECISION)
) AS e(source_key, target_key, weight) ON TRUE
JOIN vertex AS source
  ON source.graph_id = g.graph_id
 AND source.vertex_key = e.source_key
JOIN vertex AS target
  ON target.graph_id = g.graph_id
 AND target.vertex_key = e.target_key
WHERE g.graph_name = 'campus_network';

INSERT INTO edge (graph_id, source_vertex_id, target_vertex_id, weight)
SELECT g.graph_id, source.vertex_id, target.vertex_id, 1.0
FROM graph AS g
JOIN (
    VALUES
        ('OrderAPI', 'IdentityService'),
        ('OrderAPI', 'InventoryService'),
        ('InventoryService', 'AuditPipeline')
) AS e(source_key, target_key) ON TRUE
JOIN vertex AS source
  ON source.graph_id = g.graph_id
 AND source.vertex_key = e.source_key
JOIN vertex AS target
  ON target.graph_id = g.graph_id
 AND target.vertex_key = e.target_key
WHERE g.graph_name = 'service_dependencies';

-- Adjacency-list view: one row per vertex, including vertices with no edges.
CREATE VIEW adjacency_list AS
SELECT
    g.graph_name,
    g.kind,
    source.vertex_key AS vertex,
    COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'vertex', target.vertex_key,
                'weight', e.weight
            )
            ORDER BY target.vertex_key
        ) FILTER (WHERE e.edge_id IS NOT NULL),
        '[]'::jsonb
    ) AS neighbors
FROM graph AS g
JOIN vertex AS source
  ON source.graph_id = g.graph_id
LEFT JOIN edge AS e
  ON e.graph_id = source.graph_id
 AND e.source_vertex_id = source.vertex_id
LEFT JOIN vertex AS target
  ON target.graph_id = e.graph_id
 AND target.vertex_id = e.target_vertex_id
GROUP BY g.graph_name, g.kind, source.vertex_id, source.vertex_key;

-- Logical edge listing does not duplicate undirected edges.
SELECT
    g.graph_name,
    source.vertex_key AS source_vertex,
    target.vertex_key AS target_vertex,
    e.weight
FROM edge AS e
JOIN graph AS g ON g.graph_id = e.graph_id
JOIN vertex AS source
  ON source.graph_id = e.graph_id
 AND source.vertex_id = e.source_vertex_id
JOIN vertex AS target
  ON target.graph_id = e.graph_id
 AND target.vertex_id = e.target_vertex_id
ORDER BY g.graph_name, source.vertex_key, target.vertex_key;

-- Calculate in-degree and out-degree. In an undirected graph the stored
-- canonical edge orientation is only a storage convention, so each endpoint
-- receives one incident-edge contribution. A self-loop contributes two.
WITH incident_degrees AS (
    SELECT
        graph_id,
        vertex_id,
        SUM(degree_increment)::BIGINT AS degree
    FROM (
        SELECT
            e.graph_id,
            e.source_vertex_id AS vertex_id,
            CASE
                WHEN e.source_vertex_id = e.target_vertex_id THEN 2
                ELSE 1
            END AS degree_increment
        FROM edge AS e
        JOIN graph AS g ON g.graph_id = e.graph_id
        WHERE g.kind = 'UNDIRECTED'

        UNION ALL

        SELECT
            e.graph_id,
            e.target_vertex_id AS vertex_id,
            1 AS degree_increment
        FROM edge AS e
        JOIN graph AS g ON g.graph_id = e.graph_id
        WHERE g.kind = 'UNDIRECTED'
          AND e.source_vertex_id <> e.target_vertex_id
    ) AS contributions
    GROUP BY graph_id, vertex_id
)
SELECT
    g.graph_name,
    v.vertex_key,
    COALESCE(d.degree, 0) AS degree
FROM graph AS g
JOIN vertex AS v ON v.graph_id = g.graph_id
LEFT JOIN incident_degrees AS d
  ON d.graph_id = v.graph_id
 AND d.vertex_id = v.vertex_id
WHERE g.kind = 'UNDIRECTED'
ORDER BY g.graph_name, v.vertex_key;

SELECT
    g.graph_name,
    v.vertex_key,
    COUNT(e.edge_id) FILTER (
        WHERE e.target_vertex_id = v.vertex_id
    ) AS in_degree,
    COUNT(e.edge_id) FILTER (
        WHERE e.source_vertex_id = v.vertex_id
    ) AS out_degree
FROM graph AS g
JOIN vertex AS v ON v.graph_id = g.graph_id
LEFT JOIN edge AS e ON e.graph_id = v.graph_id
WHERE g.kind = 'DIRECTED'
GROUP BY g.graph_name, v.vertex_id, v.vertex_key
ORDER BY v.vertex_key;

-- Recursive reachability follows outgoing edges. UNION, rather than UNION ALL,
-- deduplicates visited vertices and prevents infinite recursion when cycles exist.
WITH RECURSIVE reachable(graph_id, vertex_id) AS (
    SELECT g.graph_id, v.vertex_id
    FROM graph AS g
    JOIN vertex AS v ON v.graph_id = g.graph_id
    WHERE g.graph_name = 'service_dependencies'
      AND v.vertex_key = 'OrderAPI'

    UNION

    SELECT r.graph_id, e.target_vertex_id
    FROM reachable AS r
    JOIN edge AS e
      ON e.graph_id = r.graph_id
     AND e.source_vertex_id = r.vertex_id
)
SELECT g.graph_name, v.vertex_key AS reachable_vertex
FROM reachable AS r
JOIN graph AS g ON g.graph_id = r.graph_id
JOIN vertex AS v
  ON v.graph_id = r.graph_id
 AND v.vertex_id = r.vertex_id
ORDER BY v.vertex_key;

-- Detect isolated vertices in each graph.
SELECT g.graph_name, v.vertex_key AS isolated_vertex
FROM vertex AS v
JOIN graph AS g ON g.graph_id = v.graph_id
WHERE NOT EXISTS (
    SELECT 1
    FROM edge AS e
    WHERE e.graph_id = v.graph_id
      AND (
          e.source_vertex_id = v.vertex_id
          OR e.target_vertex_id = v.vertex_id
      )
)
ORDER BY g.graph_name, v.vertex_key;

-- Demonstrate transactional edge insertion and rollback.
-- The temporary edge is visible during the transaction but is not retained.
SAVEPOINT before_temporary_link;

INSERT INTO edge (graph_id, source_vertex_id, target_vertex_id, weight)
SELECT
    g.graph_id,
    source.vertex_id,
    target.vertex_id,
    0.0
FROM graph AS g
JOIN vertex AS source
  ON source.graph_id = g.graph_id
 AND source.vertex_key = 'Gateway'
JOIN vertex AS target
  ON target.graph_id = g.graph_id
 AND target.vertex_key = 'ServerRoom'
WHERE g.graph_name = 'campus_network'
ON CONFLICT (graph_id, source_vertex_id, target_vertex_id)
DO NOTHING;

ROLLBACK TO SAVEPOINT before_temporary_link;
RELEASE SAVEPOINT before_temporary_link;

-- Integrity test: PostgreSQL raises a foreign-key violation for an edge
-- referencing a nonexistent vertex. Run separately to observe the failure:
--
-- INSERT INTO edge (graph_id, source_vertex_id, target_vertex_id, weight)
-- VALUES (1, -999, -998, 1.0);

COMMIT;
