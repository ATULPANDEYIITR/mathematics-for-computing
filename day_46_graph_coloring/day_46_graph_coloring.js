"use strict";

/*
 * Graph coloring through an event-driven resource-planning model.
 * Run with Node.js 18 or later. No third-party packages are required.
 */

const { EventEmitter } = require("node:events");

class Graph {
    #adjacency = new Map();

    constructor(vertices = [], edges = []) {
        for (const vertex of vertices) this.addVertex(vertex);
        for (const [left, right] of edges) this.addEdge(left, right);
    }

    addVertex(vertex) {
        if (typeof vertex !== "string" || vertex.trim() === "") {
            throw new TypeError("Vertex labels must be nonempty strings.");
        }
        if (!this.#adjacency.has(vertex)) {
            this.#adjacency.set(vertex, new Set());
        }
    }

    addEdge(left, right) {
        if (left === right) throw new Error("Self-loops are not supported.");
        this.addVertex(left);
        this.addVertex(right);
        this.#adjacency.get(left).add(right);
        this.#adjacency.get(right).add(left);
    }

    get vertices() {
        return [...this.#adjacency.keys()];
    }

    get edges() {
        const result = [];
        const seen = new Set();
        for (const [left, neighbors] of this.#adjacency) {
            for (const right of neighbors) {
                const key = [left, right].sort().join("\0");
                if (!seen.has(key)) {
                    seen.add(key);
                    result.push([left, right]);
                }
            }
        }
        return result;
    }

    neighbors(vertex) {
        if (!this.#adjacency.has(vertex)) {
            throw new Error(`Unknown vertex: ${vertex}`);
        }
        return new Set(this.#adjacency.get(vertex));
    }

    validateColoring(coloring) {
        if (!(coloring instanceof Map)) return false;
        if (coloring.size !== this.#adjacency.size) return false;

        for (const vertex of this.#adjacency.keys()) {
            if (!coloring.has(vertex)) return false;
            const color = coloring.get(vertex);
            if (!Number.isSafeInteger(color) || color < 0) return false;
        }

        return this.edges.every(
            ([left, right]) => coloring.get(left) !== coloring.get(right)
        );
    }

    greedyColoring() {
        // High-degree-first ordering often reduces the number of colors
        // compared with coloring vertices in arbitrary input order.
        const ordered = this.vertices.sort(
            (left, right) =>
                this.#adjacency.get(right).size - this.#adjacency.get(left).size
        );
        const coloring = new Map();

        for (const vertex of ordered) {
            const unavailable = new Set(
                [...this.#adjacency.get(vertex)]
                    .filter(neighbor => coloring.has(neighbor))
                    .map(neighbor => coloring.get(neighbor))
            );

            let color = 0;
            while (unavailable.has(color)) color++;
            coloring.set(vertex, color);
        }

        if (!this.validateColoring(coloring)) {
            throw new Error("Internal coloring verification failed.");
        }
        return coloring;
    }

    bipartition() {
        const side = new Map();

        for (const start of this.vertices) {
            if (side.has(start)) continue;
            side.set(start, 0);
            const queue = [start];
            let head = 0;

            // A head index avoids the repeated array shifting caused by
            // Array.shift() during large breadth-first searches.
            while (head < queue.length) {
                const vertex = queue[head++];
                for (const neighbor of this.#adjacency.get(vertex)) {
                    if (!side.has(neighbor)) {
                        side.set(neighbor, 1 - side.get(vertex));
                        queue.push(neighbor);
                    } else if (side.get(neighbor) === side.get(vertex)) {
                        return null;
                    }
                }
            }
        }

        return [
            this.vertices.filter(vertex => side.get(vertex) === 0),
            this.vertices.filter(vertex => side.get(vertex) === 1)
        ];
    }
}

class GovernanceError extends Error {}

class ColoringService extends EventEmitter {
    constructor(graph) {
        super();
        this.graph = graph;
        this.currentPlan = null;
        this.revision = 0;
    }

    proposePlan() {
        const coloring = this.graph.greedyColoring();
        const plan = {
            revision: this.revision + 1,
            coloring,
            colorCount: new Set(coloring.values()).size,
            valid: this.graph.validateColoring(coloring)
        };

        this.emit("plan:proposed", {
            revision: plan.revision,
            colorCount: plan.colorCount
        });

        return plan;
    }

    publishPlan(plan) {
        // Revision checks prevent an older computed plan from replacing a
        // newer accepted plan if graph processing becomes asynchronous.
        if (plan.revision !== this.revision + 1) {
            throw new GovernanceError("Stale or out-of-order plan revision.");
        }
        if (!plan.valid || !this.graph.validateColoring(plan.coloring)) {
            throw new GovernanceError("Cannot publish an invalid coloring.");
        }

        this.currentPlan = plan;
        this.revision = plan.revision;
        this.emit("plan:published", {
            revision: plan.revision,
            colorCount: plan.colorCount
        });
    }

    evaluateChanges(candidateGraph, expectedRevision) {
        if (expectedRevision !== this.revision) {
            throw new GovernanceError("Plan changed; recompute against the latest revision.");
        }

        const candidateColoring = candidateGraph.greedyColoring();
        const report = {
            baseRevision: expectedRevision,
            candidateColoring,
            candidateColors: new Set(candidateColoring.values()).size,
            valid: candidateGraph.validateColoring(candidateColoring)
        };

        this.emit("plan:evaluated", {
            baseRevision: expectedRevision,
            candidateColors: report.candidateColors,
            valid: report.valid
        });
        return report;
    }
}

function describeColoring(graph, coloring) {
    for (const vertex of graph.vertices) {
        console.log(`  ${vertex.padEnd(20)} -> color ${coloring.get(vertex)}`);
    }
    console.log(`  Valid: ${graph.validateColoring(coloring)}`);
}

function demonstrateBipartiteGraphs() {
    console.log("\nBIPARTITE GRAPHS");

    const network = new Graph(
        ["API", "Worker-A", "Worker-B", "Database"],
        [
            ["API", "Worker-A"],
            ["API", "Worker-B"],
            ["Worker-A", "Database"],
            ["Worker-B", "Database"]
        ]
    );

    console.log("Bipartition:", network.bipartition());
    describeColoring(network, network.greedyColoring());

    const triangle = new Graph(
        ["A", "B", "C"],
        [["A", "B"], ["B", "C"], ["C", "A"]]
    );
    console.log("Triangle bipartition:", triangle.bipartition());
}

function demonstrateInteractiveWorkflow() {
    console.log("\nEVENT-DRIVEN RESOURCE PLANNING");

    const graph = new Graph(
        ["Payment", "Inventory", "Shipping", "Identity", "Reporting"],
        [
            ["Payment", "Identity"],
            ["Payment", "Inventory"],
            ["Inventory", "Shipping"],
            ["Shipping", "Identity"],
            ["Identity", "Reporting"]
        ]
    );

    const service = new ColoringService(graph);
    service.on("plan:proposed", event => {
        console.log("Plan proposed:", event);
    });
    service.on("plan:published", event => {
        console.log("Plan published:", event);
    });
    service.on("plan:evaluated", event => {
        console.log("Change evaluation:", event);
    });

    const plan = service.proposePlan();
    describeColoring(graph, plan.coloring);
    service.publishPlan(plan);

    const updatedGraph = new Graph(
        [...graph.vertices, "Audit"],
        [...graph.edges, ["Audit", "Payment"], ["Audit", "Reporting"]]
    );

    const report = service.evaluateChanges(updatedGraph, service.revision);
    console.log("Candidate plan valid:", report.valid);
    console.log("Candidate color count:", report.candidateColors);

    try {
        service.evaluateChanges(updatedGraph, 0);
    } catch (error) {
        console.log("Stale plan rejected:", error.message);
    }
}

function demonstrateEdgeCases() {
    console.log("\nEDGE CASES");

    const empty = new Graph();
    console.log("Empty graph coloring:", [...empty.greedyColoring()]);
    console.log("Empty graph bipartition:", empty.bipartition());

    const isolated = new Graph(["unused-1", "unused-2"]);
    console.log("Edgeless graph coloring:", [...isolated.greedyColoring()]);

    const graph = new Graph(["compile", "test"], [["compile", "test"]]);
    const invalid = new Map([["compile", 0], ["test", 0]]);
    console.log("Conflicting assignment accepted:", graph.validateColoring(invalid));

    try {
        graph.addEdge("compile", "compile");
    } catch (error) {
        console.log("Self-loop rejected:", error.message);
    }
}

function main() {
    console.log("GRAPH COLORING: RESOURCE CONFLICTS");
    demonstrateBipartiteGraphs();
    demonstrateInteractiveWorkflow();
    demonstrateEdgeCases();

    console.log("\nCOMPLEXITY");
    console.log("Bipartite testing: O(V + E).");
    console.log("Greedy coloring: O(V^2 + E) with the degree-sorting implementation.");
    console.log("Greedy coloring is a heuristic, not an optimality guarantee.");
    console.log("Exact chromatic-number computation is NP-hard.");
}

main();
