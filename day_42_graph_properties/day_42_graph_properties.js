"use strict";

/*
 * Graph properties through event-driven graph updates and query operations.
 * Run with Node.js 18 or later. No external packages are required.
 */

class GraphError extends Error {
    constructor(message) {
        super(message);
        this.name = "GraphError";
    }
}

class Graph {
    #adjacency = new Map();
    #listeners = new Set();
    #revision = 0;

    constructor({ directed = false } = {}) {
        this.directed = directed;
    }

    get revision() {
        return this.#revision;
    }

    get size() {
        return this.#adjacency.size;
    }

    subscribe(listener) {
        if (typeof listener !== "function") {
            throw new GraphError("A graph listener must be a function.");
        }
        this.#listeners.add(listener);
        return () => this.#listeners.delete(listener);
    }

    #publish(type, details) {
        this.#revision += 1;
        const event = Object.freeze({
            type,
            revision: this.#revision,
            ...details
        });

        // Observers receive an immutable event rather than mutable internals.
        for (const listener of this.#listeners) {
            try {
                listener(event);
            } catch (error) {
                // An observer failure must not roll back an already completed
                // graph mutation or prevent other observers from being notified.
                console.error("Graph observer failed:", error.message);
            }
        }
    }

    #validateVertex(vertex) {
        if (typeof vertex !== "string" || vertex.trim().length === 0) {
            throw new GraphError("Vertex names must be nonempty strings.");
        }
    }

    addVertex(vertex) {
        this.#validateVertex(vertex);
        if (this.#adjacency.has(vertex)) {
            return false;
        }

        this.#adjacency.set(vertex, new Set());
        this.#publish("vertex-added", { vertex });
        return true;
    }

    addEdge(source, target) {
        this.#validateVertex(source);
        this.#validateVertex(target);

        this.addVertex(source);
        this.addVertex(target);

        const existed = this.#adjacency.get(source).has(target);
        if (existed) {
            return false;
        }

        this.#adjacency.get(source).add(target);
        if (!this.directed) {
            this.#adjacency.get(target).add(source);
        }

        this.#publish("edge-added", { source, target });
        return true;
    }

    hasVertex(vertex) {
        return this.#adjacency.has(vertex);
    }

    neighbors(vertex) {
        this.#requireVertex(vertex);
        return [...this.#adjacency.get(vertex)].sort();
    }

    #requireVertex(vertex) {
        if (!this.#adjacency.has(vertex)) {
            throw new GraphError(`Unknown vertex: ${vertex}`);
        }
    }

    vertices() {
        return [...this.#adjacency.keys()].sort();
    }

    edges() {
        const result = [];
        for (const [source, targets] of this.#adjacency) {
            for (const target of targets) {
                if (this.directed || source <= target) {
                    result.push([source, target]);
                }
            }
        }
        return result.sort((a, b) =>
            a[0].localeCompare(b[0]) || a[1].localeCompare(b[1])
        );
    }

    degree(vertex) {
        this.#requireVertex(vertex);
        if (this.directed) {
            throw new GraphError("Use inDegree() and outDegree() for directed graphs.");
        }

        const neighbors = this.#adjacency.get(vertex);
        return neighbors.size + (neighbors.has(vertex) ? 1 : 0);
    }

    outDegree(vertex) {
        this.#requireVertex(vertex);
        if (!this.directed) {
            throw new GraphError("outDegree() requires a directed graph.");
        }
        return this.#adjacency.get(vertex).size;
    }

    inDegree(vertex) {
        this.#requireVertex(vertex);
        if (!this.directed) {
            throw new GraphError("inDegree() requires a directed graph.");
        }

        let degree = 0;
        for (const targets of this.#adjacency.values()) {
            if (targets.has(vertex)) degree += 1;
        }
        return degree;
    }

    bfs(start) {
        this.#requireVertex(start);
        const visited = new Set([start]);
        const queue = [start];
        const order = [];

        // A head index avoids the repeated array shifting of Array.shift().
        for (let head = 0; head < queue.length; head += 1) {
            const current = queue[head];
            order.push(current);

            for (const neighbor of this.neighbors(current)) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    queue.push(neighbor);
                }
            }
        }
        return order;
    }

    shortestPath(source, target) {
        this.#requireVertex(source);
        this.#requireVertex(target);

        const queue = [source];
        const predecessor = new Map([[source, null]]);

        for (let head = 0; head < queue.length; head += 1) {
            const current = queue[head];
            if (current === target) {
                const path = [];
                let cursor = target;

                while (cursor !== null) {
                    path.push(cursor);
                    cursor = predecessor.get(cursor);
                }
                return path.reverse();
            }

            for (const neighbor of this.neighbors(current)) {
                if (!predecessor.has(neighbor)) {
                    predecessor.set(neighbor, current);
                    queue.push(neighbor);
                }
            }
        }
        return null;
    }

    isWalk(sequence) {
        if (!Array.isArray(sequence) || sequence.length === 0) return false;
        if (sequence.some(vertex => !this.#adjacency.has(vertex))) return false;

        return sequence.slice(1).every((target, index) =>
            this.#adjacency.get(sequence[index]).has(target)
        );
    }

    isSimplePath(sequence) {
        return this.isWalk(sequence) &&
            new Set(sequence).size === sequence.length;
    }

    connectedComponents() {
        // Directed graphs use weak connectivity for this operation.
        const undirected = new Map(
            this.vertices().map(vertex => [vertex, new Set()])
        );

        for (const [source, target] of this.edges()) {
            undirected.get(source).add(target);
            undirected.get(target).add(source);
        }

        const unseen = new Set(this.vertices());
        const components = [];

        while (unseen.size > 0) {
            const start = [...unseen].sort()[0];
            unseen.delete(start);
            const queue = [start];
            const component = [];

            for (let head = 0; head < queue.length; head += 1) {
                const current = queue[head];
                component.push(current);

                for (const neighbor of [...undirected.get(current)].sort()) {
                    if (unseen.delete(neighbor)) {
                        queue.push(neighbor);
                    }
                }
            }

            components.push(component.sort());
        }
        return components;
    }

    isConnected() {
        return this.size > 0 && this.connectedComponents().length === 1;
    }

    hasCycle() {
        if (this.directed) return this.hasDirectedCycle();

        const visited = new Set();

        for (const start of this.vertices()) {
            if (visited.has(start)) continue;

            const stack = [[start, null]];
            while (stack.length > 0) {
                const [current, parent] = stack.pop();
                if (visited.has(current)) continue;
                visited.add(current);

                for (const neighbor of this.#adjacency.get(current)) {
                    if (neighbor === current) return true;
                    if (!visited.has(neighbor)) {
                        stack.push([neighbor, current]);
                    } else if (neighbor !== parent) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    hasDirectedCycle() {
        if (!this.directed) {
            throw new GraphError("Directed cycle detection requires a directed graph.");
        }

        const state = new Map(this.vertices().map(v => [v, 0]));

        const visit = vertex => {
            state.set(vertex, 1);
            for (const neighbor of this.#adjacency.get(vertex)) {
                if (state.get(neighbor) === 1) return true;
                if (state.get(neighbor) === 0 && visit(neighbor)) return true;
            }
            state.set(vertex, 2);
            return false;
        };

        for (const vertex of this.vertices()) {
            if (state.get(vertex) === 0 && visit(vertex)) return true;
        }
        return false;
    }

    degreeDistribution() {
        if (this.directed) {
            throw new GraphError("Use inDegree() and outDegree() for directed graphs.");
        }

        const distribution = new Map();
        for (const vertex of this.vertices()) {
            const degree = this.degree(vertex);
            distribution.set(degree, (distribution.get(degree) ?? 0) + 1);
        }
        return Object.fromEntries(
            [...distribution.entries()].sort((a, b) => a[0] - b[0])
        );
    }
}

function assert(condition, message) {
    if (!condition) throw new Error(`Assertion failed: ${message}`);
}

function demonstrateNetworkMonitoring() {
    console.log("\n=== Event-driven network monitoring ===");

    const graph = new Graph();
    const unsubscribe = graph.subscribe(event => {
        console.log(`revision=${event.revision} event=${event.type}`, event);
    });

    graph.addEdge("gateway", "api");
    graph.addEdge("api", "worker");
    graph.addEdge("worker", "database");
    graph.addEdge("api", "cache");

    console.log("Vertices:", graph.vertices());
    console.log("Edges:", graph.edges());
    console.log("Degree distribution:", graph.degreeDistribution());
    console.log("Reachable from gateway:", graph.bfs("gateway"));
    console.log("Shortest route:", graph.shortestPath("gateway", "database"));
    console.log("Simple path:", graph.isSimplePath(
        ["gateway", "api", "worker", "database"]
    ));
    console.log("Connected components:", graph.connectedComponents());
    console.log("Contains cycle:", graph.hasCycle());

    graph.addEdge("cache", "gateway");
    console.log("Cycle after redundant network link:", graph.hasCycle());

    unsubscribe();
    graph.addVertex("offline-monitor");
    console.log("Revision after unsubscribe:", graph.revision);
}

function demonstrateDirectedDependencies() {
    console.log("\n=== Directed dependency graph ===");

    const graph = new Graph({ directed: true });
    graph.addEdge("compile", "unit-tests");
    graph.addEdge("unit-tests", "package");
    graph.addEdge("package", "deploy");

    console.log("Out-degree of compile:", graph.outDegree("compile"));
    console.log("In-degree of deploy:", graph.inDegree("deploy"));
    console.log("Deployment route:", graph.shortestPath("compile", "deploy"));
    console.log("Directed cycle:", graph.hasDirectedCycle());

    graph.addEdge("deploy", "compile");
    console.log("Cycle after feedback dependency:", graph.hasDirectedCycle());
    console.log("Weak components:", graph.connectedComponents());
}

function runChecks() {
    const graph = new Graph();
    graph.addEdge("A", "B");
    graph.addEdge("B", "C");

    assert(graph.degree("B") === 2, "middle vertex degree");
    assert(graph.isConnected(), "path graph connectedness");
    assert(!graph.hasCycle(), "a tree path has no cycle");
    assert(
        JSON.stringify(graph.shortestPath("A", "C")) === '["A","B","C"]',
        "shortest path"
    );
    assert(graph.isWalk(["A", "B", "A"]), "walk may repeat vertices");
    assert(!graph.isSimplePath(["A", "B", "A"]), "simple path cannot repeat vertices");

    graph.addEdge("C", "A");
    assert(graph.hasCycle(), "triangle contains a cycle");

    const directed = new Graph({ directed: true });
    directed.addEdge("A", "B");
    assert(!directed.hasDirectedCycle(), "single directed edge is acyclic");
    directed.addEdge("B", "A");
    assert(directed.hasDirectedCycle(), "two opposite arcs form a directed cycle");

    try {
        graph.degree("missing");
        throw new Error("Unknown vertices must be rejected.");
    } catch (error) {
        assert(error instanceof GraphError, "unknown vertex validation");
    }

    console.log("\nAll JavaScript graph checks passed.");
}

demonstrateNetworkMonitoring();
demonstrateDirectedDependencies();
runChecks();
