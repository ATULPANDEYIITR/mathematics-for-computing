"use strict";

/*
 * Graph optimization laboratory for Node.js.
 *
 * The implementation deliberately uses JavaScript-specific mechanisms:
 * Maps for sparse graph state, async generators for streamed optimization
 * events, structured cloning of graph state, and event-driven reporting.
 */

class GraphError extends Error {}

class WeightedGraph {
    constructor(directed = false) {
        this.directed = directed;
        this.adjacency = new Map();
        this.edges = [];
    }

    addVertex(vertex) {
        if (typeof vertex !== "string" || vertex.trim() === "") {
            throw new GraphError("A graph vertex must be a non-empty string.");
        }
        if (!this.adjacency.has(vertex)) {
            this.adjacency.set(vertex, []);
        }
    }

    addEdge(source, target, weight) {
        if (!Number.isFinite(weight) || weight < 0) {
            throw new GraphError(
                "Dijkstra-compatible graph edges require finite non-negative weights."
            );
        }

        this.addVertex(source);
        this.addVertex(target);

        this.adjacency.get(source).push({ vertex: target, weight });
        this.edges.push({ source, target, weight });

        if (!this.directed) {
            this.adjacency.get(target).push({ vertex: source, weight });
        }
    }

    neighbors(vertex) {
        if (!this.adjacency.has(vertex)) {
            throw new GraphError(`Unknown vertex: ${vertex}`);
        }
        return this.adjacency.get(vertex);
    }
}

class MinPriorityQueue {
    constructor() {
        this.heap = [];
    }

    push(item) {
        this.heap.push(item);
        this.#bubbleUp(this.heap.length - 1);
    }

    pop() {
        if (this.heap.length === 0) {
            return undefined;
        }

        const minimum = this.heap[0];
        const last = this.heap.pop();

        if (this.heap.length > 0) {
            this.heap[0] = last;
            this.#bubbleDown(0);
        }

        return minimum;
    }

    get size() {
        return this.heap.length;
    }

    #bubbleUp(index) {
        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (this.heap[parent].distance <= this.heap[index].distance) {
                break;
            }

            [this.heap[parent], this.heap[index]] =
                [this.heap[index], this.heap[parent]];
            index = parent;
        }
    }

    #bubbleDown(index) {
        while (true) {
            const left = index * 2 + 1;
            const right = index * 2 + 2;
            let smallest = index;

            if (
                left < this.heap.length &&
                this.heap[left].distance < this.heap[smallest].distance
            ) {
                smallest = left;
            }

            if (
                right < this.heap.length &&
                this.heap[right].distance < this.heap[smallest].distance
            ) {
                smallest = right;
            }

            if (smallest === index) {
                break;
            }

            [this.heap[index], this.heap[smallest]] =
                [this.heap[smallest], this.heap[index]];
            index = smallest;
        }
    }
}

function dijkstra(graph, source) {
    if (!graph.adjacency.has(source)) {
        throw new GraphError(`Unknown source vertex: ${source}`);
    }

    const distance = new Map();
    const previous = new Map();
    const queue = new MinPriorityQueue();

    for (const vertex of graph.adjacency.keys()) {
        distance.set(vertex, Infinity);
        previous.set(vertex, null);
    }

    distance.set(source, 0);
    queue.push({ vertex: source, distance: 0 });

    while (queue.size > 0) {
        const current = queue.pop();

        // Multiple heap entries can exist for a vertex. Older entries are
        // ignored rather than requiring an explicit decrease-key operation.
        if (current.distance !== distance.get(current.vertex)) {
            continue;
        }

        for (const edge of graph.neighbors(current.vertex)) {
            const candidate = current.distance + edge.weight;

            if (candidate < distance.get(edge.vertex)) {
                distance.set(edge.vertex, candidate);
                previous.set(edge.vertex, current.vertex);
                queue.push({
                    vertex: edge.vertex,
                    distance: candidate
                });
            }
        }
    }

    return { distance, previous };
}

function reconstructPath(previous, source, target) {
    const path = [];
    let current = target;

    while (current !== null) {
        path.push(current);

        if (current === source) {
            return path.reverse();
        }

        current = previous.get(current) ?? null;
    }

    return [];
}

class DisjointSet {
    constructor(vertices) {
        this.parent = new Map();
        this.rank = new Map();

        for (const vertex of vertices) {
            this.parent.set(vertex, vertex);
            this.rank.set(vertex, 0);
        }
    }

    find(vertex) {
        const parent = this.parent.get(vertex);

        if (parent !== vertex) {
            this.parent.set(vertex, this.find(parent));
        }

        return this.parent.get(vertex);
    }

    union(a, b) {
        let rootA = this.find(a);
        let rootB = this.find(b);

        if (rootA === rootB) {
            return false;
        }

        if (this.rank.get(rootA) < this.rank.get(rootB)) {
            [rootA, rootB] = [rootB, rootA];
        }

        this.parent.set(rootB, rootA);

        if (this.rank.get(rootA) === this.rank.get(rootB)) {
            this.rank.set(rootA, this.rank.get(rootA) + 1);
        }

        return true;
    }
}

function kruskal(graph) {
    if (graph.directed) {
        throw new GraphError("Kruskal requires an undirected graph.");
    }

    const dsu = new DisjointSet(graph.adjacency.keys());
    const selected = [];
    let total = 0;

    const sorted = [...graph.edges].sort((a, b) => a.weight - b.weight);

    for (const edge of sorted) {
        if (dsu.union(edge.source, edge.target)) {
            selected.push(edge);
            total += edge.weight;
        }

        if (selected.length === graph.adjacency.size - 1) {
            break;
        }
    }

    if (selected.length !== graph.adjacency.size - 1) {
        throw new GraphError("A disconnected graph has no spanning tree.");
    }

    return { edges: selected, total };
}

/*
 * Event-driven optimization makes algorithm progress observable without
 * coupling the algorithm to a specific UI. A browser or Node consumer can
 * subscribe to the same events.
 */
class OptimizationMonitor extends EventTarget {
    report(type, payload) {
        this.dispatchEvent(
            new CustomEvent(type, { detail: payload })
        );
    }
}

async function* shortestPathEvents(graph, source) {
    const distance = new Map();
    const previous = new Map();
    const queue = new MinPriorityQueue();

    for (const vertex of graph.adjacency.keys()) {
        distance.set(vertex, Infinity);
        previous.set(vertex, null);
    }

    distance.set(source, 0);
    queue.push({ vertex: source, distance: 0 });

    while (queue.size > 0) {
        const current = queue.pop();

        if (current.distance !== distance.get(current.vertex)) {
            continue;
        }

        yield {
            type: "vertex-settled",
            vertex: current.vertex,
            distance: current.distance
        };

        for (const edge of graph.neighbors(current.vertex)) {
            const candidate = current.distance + edge.weight;

            if (candidate < distance.get(edge.vertex)) {
                distance.set(edge.vertex, candidate);
                previous.set(edge.vertex, current.vertex);

                yield {
                    type: "distance-relaxed",
                    source: current.vertex,
                    target: edge.vertex,
                    distance: candidate
                };

                queue.push({
                    vertex: edge.vertex,
                    distance: candidate
                });
            }
        }
    }

    return { distance, previous };
}

function demonstrateShortestPaths() {
    const graph = new WeightedGraph(true);

    [
        ["DataCenter", "Router-A", 4],
        ["DataCenter", "Router-B", 2],
        ["Router-B", "Router-A", 1],
        ["Router-A", "Router-C", 3],
        ["Router-B", "Router-C", 5],
        ["Router-C", "Service", 2],
        ["Router-A", "Service", 9]
    ].forEach(([source, target, weight]) =>
        graph.addEdge(source, target, weight)
    );

    const result = dijkstra(graph, "DataCenter");
    const path = reconstructPath(
        result.previous,
        "DataCenter",
        "Service"
    );

    console.log("Shortest route:", path.join(" -> "));
    console.log("Minimum latency:", result.distance.get("Service"));
}

function demonstrateMinimumSpanningTree() {
    const graph = new WeightedGraph(false);

    [
        ["A", "B", 6],
        ["A", "C", 3],
        ["B", "C", 2],
        ["B", "D", 5],
        ["C", "D", 4],
        ["C", "E", 7],
        ["D", "E", 1]
    ].forEach(([source, target, weight]) =>
        graph.addEdge(source, target, weight)
    );

    const result = kruskal(graph);

    console.log("\nMinimum-cost physical network:");
    for (const edge of result.edges) {
        console.log(
            `${edge.source} -- ${edge.target}: ${edge.weight}`
        );
    }
    console.log("Total deployment cost:", result.total);
}

async function demonstrateEventStream() {
    const graph = new WeightedGraph(true);

    graph.addEdge("A", "B", 2);
    graph.addEdge("A", "C", 7);
    graph.addEdge("B", "C", 2);
    graph.addEdge("C", "D", 1);

    const monitor = new OptimizationMonitor();

    monitor.addEventListener("relaxation", event => {
        const { source, target, distance } = event.detail;
        console.log(
            `relaxed ${source} -> ${target}, distance=${distance}`
        );
    });

    for await (const event of shortestPathEvents(graph, "A")) {
        if (event.type === "distance-relaxed") {
            monitor.report("relaxation", event);
        }
    }
}

function demonstrateValidation() {
    console.log("\nValidation:");

    try {
        const graph = new WeightedGraph(true);
        graph.addEdge("A", "B", -1);
    } catch (error) {
        console.log("Negative weight rejected:", error.message);
    }

    try {
        const graph = new WeightedGraph(true);
        dijkstra(graph, "missing");
    } catch (error) {
        console.log("Unknown source rejected:", error.message);
    }
}

async function main() {
    demonstrateShortestPaths();
    demonstrateMinimumSpanningTree();
    demonstrateValidation();
    await demonstrateEventStream();
}

main().catch(error => {
    console.error("Optimization failure:", error.message);
    process.exitCode = 1;
});
