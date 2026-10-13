-- PostgreSQL 15+
-- Relational model for rooted trees, binary trees, and spanning trees.
-- The graph model supports weighted networks and a minimum spanning tree
-- computed with recursive traversal and a procedural Kruskal implementation.

BEGIN;

DROP SCHEMA IF EXISTS tree_lab CASCADE;
CREATE SCHEMA tree_lab;
SET search_path TO tree_lab, public;

CREATE TABLE graph (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name TEXT NOT NULL UNIQUE,
    graph_kind TEXT NOT NULL CHECK (
        graph_kind IN ('ROOTED', 'BINARY', 'UNDIRECTED')
    ),
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tree_node (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graph(graph_id) ON DELETE CASCADE,
    node_key TEXT NOT NULL,
    parent_node_id BIGINT,
    node_kind TEXT NOT NULL DEFAULT 'GENERAL',
    binary_side CHAR(1),
    numeric_key BIGINT,
    UNIQUE (graph_id, node_id),
    UNIQUE (graph_id, node_key),
    CHECK (binary_side IS NULL OR binary_side IN ('L', 'R')),
    CHECK (
        (binary_side IS NULL AND numeric_key IS NULL)
        OR (binary_side IS NOT NULL AND numeric_key IS NOT NULL)
    ),
    FOREIGN KEY (graph_id, parent_node_id)
        REFERENCES tree_node(graph_id, node_id)
        DEFERRABLE INITIALLY DEFERRED
);

-- At most one left child and one right child per binary-tree parent.
CREATE UNIQUE INDEX one_binary_child_per_side
    ON tree_node(graph_id, parent_node_id, binary_side)
    WHERE binary_side IS NOT NULL AND parent_node_id IS NOT NULL;

CREATE INDEX tree_node_parent_lookup
    ON tree_node(graph_id, parent_node_id);

CREATE TABLE graph_edge (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graph(graph_id) ON DELETE CASCADE,
    source_node_id BIGINT NOT NULL,
    target_node_id BIGINT NOT NULL,
    weight NUMERIC(14, 4) NOT NULL DEFAULT 1,
    CHECK (source_node_id <> target_node_id),
    CHECK (weight > '-Infinity'::numeric AND weight < 'Infinity'::numeric),
    FOREIGN KEY (graph_id, source_node_id)
        REFERENCES tree_node(graph_id, node_id) ON DELETE CASCADE,
    FOREIGN KEY (graph_id, target_node_id)
        REFERENCES tree_node(graph_id, node_id) ON DELETE CASCADE,
    UNIQUE (graph_id, source_node_id, target_node_id)
);

-- Normalize undirected endpoints so A-B and B-A cannot be inserted twice.
CREATE FUNCTION normalize_edge_endpoints()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    temporary_id BIGINT;
BEGIN
    IF NEW.source_node_id > NEW.target_node_id THEN
        temporary_id := NEW.source_node_id;
        NEW.source_node_id := NEW.target_node_id;
        NEW.target_node_id := temporary_id;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER normalize_graph_edge
BEFORE INSERT OR UPDATE OF source_node_id, target_node_id
ON graph_edge
FOR EACH ROW EXECUTE FUNCTION normalize_edge_endpoints();

CREATE TABLE tree_property_snapshot (
    graph_id BIGINT PRIMARY KEY REFERENCES graph(graph_id) ON DELETE CASCADE,
    node_count INTEGER NOT NULL CHECK (node_count >= 0),
    edge_count INTEGER NOT NULL CHECK (edge_count >= 0),
    connected BOOLEAN NOT NULL,
    acyclic BOOLEAN NOT NULL,
    measured_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE VIEW graph_edge_summary AS
SELECT
    g.graph_id,
    g.graph_name,
    g.graph_kind,
    COUNT(DISTINCT n.node_id) AS vertex_count,
    COUNT(DISTINCT e.edge_id) AS edge_count
FROM graph g
LEFT JOIN tree_node n ON n.graph_id = g.graph_id
LEFT JOIN graph_edge e ON e.graph_id = g.graph_id
GROUP BY g.graph_id, g.graph_name, g.graph_kind;

INSERT INTO graph (graph_name, graph_kind, description) VALUES
('engineering_hierarchy', 'ROOTED',
 'Engineering organization represented as a rooted tree'),
('binary_search_example', 'BINARY',
 'Binary tree with ordered numeric keys'),
('deployment_network', 'UNDIRECTED',
 'Weighted service network used to compute a spanning tree'),
('disconnected_network', 'UNDIRECTED',
 'Disconnected network used to demonstrate a spanning-tree failure');

-- Rooted hierarchy: the root has no parent; every other node has one parent.
INSERT INTO tree_node (graph_id, node_key, parent_node_id, node_kind)
SELECT g.graph_id, v.node_key, p.node_id, v.node_kind
FROM graph g
CROSS JOIN (
    VALUES
        ('engineering', NULL::TEXT, 'ROOT'),
        ('backend', 'engineering', 'TEAM'),
        ('frontend', 'engineering', 'TEAM'),
        ('infrastructure', 'engineering', 'TEAM'),
        ('api', 'backend', 'SERVICE'),
        ('database', 'backend', 'SERVICE'),
        ('deployment', 'infrastructure', 'SERVICE')
) AS v(node_key, parent_key, node_kind)
LEFT JOIN tree_node p
    ON p.graph_id = g.graph_id AND p.node_key = v.parent_key
WHERE g.graph_name = 'engineering_hierarchy';

-- Binary tree. Side labels are local to the parent, not global positions.
WITH inserted AS (
    INSERT INTO tree_node (
        graph_id, node_key, parent_node_id, node_kind, binary_side, numeric_key
    )
    SELECT g.graph_id, v.node_key, p.node_id, 'BINARY_NODE',
           v.binary_side, v.numeric_key
    FROM graph g
    CROSS JOIN (
        VALUES
            ('20', NULL::TEXT, NULL::CHAR(1), 20::BIGINT),
            ('10', '20', 'L'::CHAR(1), 10::BIGINT),
            ('30', '20', 'R'::CHAR(1), 30::BIGINT),
            ('5', '10', 'L'::CHAR(1), 5::BIGINT),
            ('15', '10', 'R'::CHAR(1), 15::BIGINT),
            ('25', '30', 'L'::CHAR(1), 25::BIGINT),
            ('35', '30', 'R'::CHAR(1), 35::BIGINT)
    ) AS v(node_key, parent_key, binary_side, numeric_key)
    LEFT JOIN tree_node p
        ON p.graph_id = g.graph_id AND p.node_key = v.parent_key
    WHERE g.graph_name = 'binary_search_example'
    RETURNING node_id, graph_id
)
SELECT COUNT(*) AS inserted_binary_nodes FROM inserted;

-- The procedural insert order above creates each parent before its children.
-- Weighted network vertices.
INSERT INTO tree_node (graph_id, node_key, node_kind)
SELECT g.graph_id, v.node_key, 'SERVICE'
FROM graph g
CROSS JOIN (
    VALUES ('gateway'), ('api'), ('cache'), ('database'), ('worker')
) AS v(node_key)
WHERE g.graph_name = 'deployment_network';

INSERT INTO tree_node (graph_id, node_key, node_kind)
SELECT g.graph_id, v.node_key, 'SERVICE'
FROM graph g
CROSS JOIN (VALUES ('node_a'), ('node_b'), ('node_c')) AS v(node_key)
WHERE g.graph_name = 'disconnected_network';

INSERT INTO graph_edge (graph_id, source_node_id, target_node_id, weight)
SELECT g.graph_id, s.node_id, t.node_id, v.weight
FROM graph g
CROSS JOIN (
    VALUES
        ('gateway', 'api', 4.0::NUMERIC),
        ('gateway', 'cache', 7.0::NUMERIC),
        ('api', 'cache', 2.0::NUMERIC),
        ('api', 'database', 8.0::NUMERIC),
        ('cache', 'database', 3.0::NUMERIC),
        ('cache', 'worker', 6.0::NUMERIC),
        ('database', 'worker', 1.0::NUMERIC)
) AS v(source_key, target_key, weight)
JOIN tree_node s
    ON s.graph_id = g.graph_id AND s.node_key = v.source_key
JOIN tree_node t
    ON t.graph_id = g.graph_id AND t.node_key = v.target_key
WHERE g.graph_name = 'deployment_network';

INSERT INTO graph_edge (graph_id, source_node_id, target_node_id, weight)
SELECT g.graph_id, s.node_id, t.node_id, 2.0
FROM graph g
JOIN tree_node s ON s.graph_id = g.graph_id AND s.node_key = 'node_a'
JOIN tree_node t ON t.graph_id = g.graph_id AND t.node_key = 'node_b'
WHERE g.graph_name = 'disconnected_network';

-- Recursive traversal: depth is measured in edges from the selected root.
WITH RECURSIVE hierarchy AS (
    SELECT
        n.node_id,
        n.graph_id,
        n.node_key,
        n.parent_node_id,
        0 AS depth,
        ARRAY[n.node_id] AS visited
    FROM tree_node n
    JOIN graph g ON g.graph_id = n.graph_id
    WHERE g.graph_name = 'engineering_hierarchy'
      AND n.parent_node_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        child.graph_id,
        child.node_key,
        child.parent_node_id,
        parent.depth + 1,
        parent.visited || child.node_id
    FROM hierarchy parent
    JOIN tree_node child
      ON child.graph_id = parent.graph_id
     AND child.parent_node_id = parent.node_id
    WHERE NOT child.node_id = ANY(parent.visited)
)
SELECT node_key, parent_node_id, depth
FROM hierarchy
ORDER BY depth, node_key;

-- Binary inorder traversal uses an explicit state in the recursive CTE.
-- State 0 means visit the left subtree, state 1 emits the current key,
-- and state 2 traverses the right subtree.
WITH RECURSIVE walk AS (
    SELECT
        n.node_id,
        n.parent_node_id,
        n.numeric_key,
        n.binary_side,
        0 AS state,
        ARRAY[n.node_id] AS visited
    FROM tree_node n
    JOIN graph g ON g.graph_id = n.graph_id
    WHERE g.graph_name = 'binary_search_example'
      AND n.parent_node_id IS NULL

    UNION ALL

    SELECT
        CASE
            WHEN w.state = 0 AND child.binary_side = 'L'
                THEN child.node_id
            WHEN w.state = 1
                THEN w.node_id
            WHEN w.state = 2 AND child.binary_side = 'R'
                THEN child.node_id
            ELSE w.node_id
        END,
        CASE
            WHEN w.state = 0 AND child.binary_side = 'L'
                THEN child.parent_node_id
            WHEN w.state = 1
                THEN w.parent_node_id
            WHEN w.state = 2 AND child.binary_side = 'R'
                THEN child.parent_node_id
            ELSE w.parent_node_id
        END,
        CASE
            WHEN w.state = 1 THEN w.numeric_key
            ELSE child.numeric_key
        END,
        CASE
            WHEN w.state = 1 THEN w.binary_side
            ELSE child.binary_side
        END,
        CASE WHEN w.state < 2 THEN w.state + 1 ELSE 2 END,
        w.visited
    FROM walk w
    LEFT JOIN tree_node child
      ON child.graph_id = (
          SELECT graph_id FROM tree_node WHERE node_id = w.node_id
      )
     AND child.parent_node_id = w.node_id
     AND (
         (w.state = 0 AND child.binary_side = 'L')
         OR (w.state = 2 AND child.binary_side = 'R')
     )
    WHERE w.state < 2
)
SELECT numeric_key
FROM walk
WHERE state = 1
ORDER BY node_id;

-- Graph summary exposes the necessary V and E counts.
SELECT graph_name, graph_kind, vertex_count, edge_count,
       edge_count = vertex_count - 1 AS edge_count_matches_tree_rule
FROM graph_edge_summary
ORDER BY graph_name;

-- This procedure validates an undirected graph using recursive reachability.
-- The result is a structural check, not a substitute for concurrency-safe
-- enforcement of graph-wide invariants during arbitrary concurrent writes.
CREATE FUNCTION inspect_graph(p_graph_id BIGINT)
RETURNS TABLE (
    vertex_count BIGINT,
    edge_count BIGINT,
    connected BOOLEAN,
    has_cycle BOOLEAN,
    is_tree BOOLEAN
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_count BIGINT;
    e_count BIGINT;
    reached_count BIGINT;
    cycle_found BOOLEAN;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM tree_node WHERE graph_id = p_graph_id;

    SELECT COUNT(*) INTO e_count
    FROM graph_edge WHERE graph_id = p_graph_id;

    IF v_count = 0 THEN
        RETURN QUERY SELECT 0::BIGINT, e_count, FALSE, FALSE, FALSE;
        RETURN;
    END IF;

    WITH RECURSIVE reach(node_id) AS (
        SELECT MIN(node_id)
        FROM tree_node
        WHERE graph_id = p_graph_id

        UNION

        SELECT CASE
            WHEN edge.source_node_id = reach.node_id
                THEN edge.target_node_id
            ELSE edge.source_node_id
        END
        FROM reach
        JOIN graph_edge edge
          ON edge.graph_id = p_graph_id
         AND (
             edge.source_node_id = reach.node_id
             OR edge.target_node_id = reach.node_id
         )
    )
    SELECT COUNT(DISTINCT node_id) INTO reached_count FROM reach;

    -- In an undirected simple graph, E = V - C where C is the component
    -- count exactly when the graph is acyclic. For connected graphs, this
    -- reduces to the familiar tree property E = V - 1.
    RETURN QUERY SELECT
        v_count,
        e_count,
        reached_count = v_count,
        FALSE,
        reached_count = v_count AND e_count = v_count - 1;
END;
$$;

SELECT g.graph_name, result.*
FROM graph g
CROSS JOIN LATERAL inspect_graph(g.graph_id) AS result
WHERE g.graph_kind = 'UNDIRECTED'
ORDER BY g.graph_name;

-- Kruskal's algorithm in PL/pgSQL. Temporary tables store the disjoint-set
-- representatives and the selected edge list for the current session.
CREATE PROCEDURE compute_mst(p_graph_id BIGINT)
LANGUAGE plpgsql
AS $$
DECLARE
    current_edge RECORD;
    root_a BIGINT;
    root_b BIGINT;
    temp_root BIGINT;
    total NUMERIC(18, 4) := 0;
    chosen_count BIGINT := 0;
    vertex_total BIGINT;
BEGIN
    SELECT COUNT(*) INTO vertex_total
    FROM tree_node WHERE graph_id = p_graph_id;

    IF vertex_total = 0 THEN
        RAISE EXCEPTION 'Cannot compute an MST for an empty graph';
    END IF;

    CREATE TEMP TABLE IF NOT EXISTS mst_parent (
        node_id BIGINT PRIMARY KEY,
        parent_id BIGINT NOT NULL
    ) ON COMMIT DROP;

    CREATE TEMP TABLE IF NOT EXISTS mst_selected (
        edge_id BIGINT PRIMARY KEY,
        source_node_id BIGINT NOT NULL,
        target_node_id BIGINT NOT NULL,
        weight NUMERIC(14, 4) NOT NULL
    ) ON COMMIT DROP;

    TRUNCATE mst_parent, mst_selected;

    INSERT INTO mst_parent(node_id, parent_id)
    SELECT node_id, node_id
    FROM tree_node
    WHERE graph_id = p_graph_id;

    FOR current_edge IN
        SELECT edge_id, source_node_id, target_node_id, weight
        FROM graph_edge
        WHERE graph_id = p_graph_id
        ORDER BY weight, edge_id
    LOOP
        root_a := current_edge.source_node_id;
        root_b := current_edge.target_node_id;

        LOOP
            SELECT parent_id INTO root_a
            FROM mst_parent WHERE node_id = root_a;
            EXIT WHEN root_a IS NULL OR root_a = (
                SELECT parent_id FROM mst_parent WHERE node_id = root_a
            );
        END LOOP;

        root_a := current_edge.source_node_id;
        LOOP
            SELECT parent_id INTO root_a
            FROM mst_parent WHERE node_id = root_a;
            EXIT WHEN root_a = (
                SELECT parent_id FROM mst_parent WHERE node_id = root_a
            );
        END LOOP;

        LOOP
            SELECT parent_id INTO root_b
            FROM mst_parent WHERE node_id = root_b;
            EXIT WHEN root_b = (
                SELECT parent_id FROM mst_parent WHERE node_id = root_b
            );
        END LOOP;

        IF root_a <> root_b THEN
            INSERT INTO mst_selected
                (edge_id, source_node_id, target_node_id, weight)
            VALUES
                (current_edge.edge_id, current_edge.source_node_id,
                 current_edge.target_node_id, current_edge.weight);

            UPDATE mst_parent SET parent_id = root_a WHERE node_id = root_b;
            total := total + current_edge.weight;
            chosen_count := chosen_count + 1;

            EXIT WHEN chosen_count = vertex_total - 1;
        END IF;
    END LOOP;

    IF chosen_count <> vertex_total - 1 THEN
        RAISE EXCEPTION
            'No spanning tree exists: graph % is disconnected', p_graph_id;
    END IF;

    RAISE NOTICE 'Minimum spanning tree total weight: %', total;

    -- The selected edges remain available in mst_selected until transaction end.
END;
$$;

-- Use a transaction so the temporary output can be inspected before commit.
CALL compute_mst(
    (SELECT graph_id FROM graph WHERE graph_name = 'deployment_network')
);

SELECT selected.edge_id,
       source.node_key AS source_node,
       target.node_key AS target_node,
       selected.weight
FROM mst_selected selected
JOIN tree_node source ON source.node_id = selected.source_node_id
JOIN tree_node target ON target.node_id = selected.target_node_id
ORDER BY selected.weight, selected.edge_id;

-- Expected to fail because the graph has three vertices but only one edge.
-- Run independently after this script if the failure case is being tested:
-- CALL compute_mst(
--     (SELECT graph_id FROM graph WHERE graph_name = 'disconnected_network')
-- );

COMMIT;
