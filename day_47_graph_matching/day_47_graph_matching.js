"use strict";

/*
 * Graph matching through an event-driven job allocation model.
 * Run with Node.js 18 or later.
 */

class BipartiteMatcher {
    constructor(leftVertices, rightVertices) {
        this.left = [...leftVertices];
        this.right = [...rightVertices];

        if (new Set(this.left).size !== this.left.length) {
            throw new Error("Duplicate left-side vertex.");
        }
        if (new Set(this.right).size !== this.right.length) {
            throw new Error("Duplicate right-side vertex.");
        }

        this.leftSet = new Set(this.left);
        this.rightSet = new Set(this.right);

        for (const vertex of this.left) {
            if (this.rightSet.has(vertex)) {
                throw new Error("Bipartite partitions must be disjoint.");
            }
        }

        this.adjacency = new Map(
            this.left.map(vertex => [vertex, new Set()])
        );
    }

    addEligibility(worker, task) {
        if (!this.leftSet.has(worker) || !this.rightSet.has(task)) {
            throw new Error("Eligibility must connect a worker to a task.");
        }
        this.adjacency.get(worker).add(task);
    }

    maximumMatching() {
        const taskOwner = new Map();

        const augment = (worker, visitedTasks) => {
            for (const task of this.adjacency.get(worker)) {
                if (visitedTasks.has(task)) continue;
                visitedTasks.add(task);

                const currentOwner = taskOwner.get(task);

                // Reassigning an occupied task is valid only if its
                // current worker can move to another eligible task.
                if (
                    currentOwner === undefined ||
                    augment(currentOwner, visitedTasks)
                ) {
                    taskOwner.set(task, worker);
                    return true;
                }
            }
            return false;
        };

        let size = 0;
        for (const worker of this.left) {
            if (augment(worker, new Set())) size++;
        }

        const assignments = [...taskOwner.entries()].map(
            ([task, worker]) => ({ worker, task })
        );

        const assignedWorkers = new Set(
            assignments.map(item => item.worker)
        );

        return {
            assignments,
            cardinality: size,
            unmatchedWorkers: this.left.filter(
                worker => !assignedWorkers.has(worker)
            ),
            unmatchedTasks: this.right.filter(
                task => !taskOwner.has(task)
            )
        };
    }

    validate(assignments) {
        const workers = new Set();
        const tasks = new Set();

        for (const { worker, task } of assignments) {
            if (!this.leftSet.has(worker) || !this.rightSet.has(task)) {
                return false;
            }
            if (!this.adjacency.get(worker).has(task)) return false;
            if (workers.has(worker) || tasks.has(task)) return false;

            workers.add(worker);
            tasks.add(task);
        }
        return true;
    }
}

class AllocationService {
    constructor(matcher) {
        this.matcher = matcher;
        this.listeners = new Map();
        this.history = [];
        this.state = "OPEN";
    }

    on(eventName, listener) {
        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, []);
        }
        this.listeners.get(eventName).push(listener);
    }

    emit(eventName, payload) {
        for (const listener of this.listeners.get(eventName) ?? []) {
            listener(payload);
        }
    }

    allocate() {
        if (this.state !== "OPEN") {
            throw new Error(`Cannot allocate while state is ${this.state}.`);
        }

        const result = this.matcher.maximumMatching();
        if (!this.matcher.validate(result.assignments)) {
            this.state = "FAILED";
            this.emit("failure", { reason: "Matching validation failed." });
            throw new Error("Computed assignments violate matching constraints.");
        }

        this.state = "ALLOCATED";
        this.history.push({
            state: this.state,
            assignmentCount: result.cardinality
        });

        this.emit("allocated", result);
        return result;
    }

    close() {
        if (this.state !== "ALLOCATED") {
            throw new Error("Allocation must complete before closure.");
        }

        this.state = "CLOSED";
        this.history.push({ state: this.state });
        this.emit("closed", { state: this.state });
    }
}

function main() {
    const matcher = new BipartiteMatcher(
        ["Analyst-A", "Analyst-B", "Analyst-C", "Analyst-D"],
        ["Case-101", "Case-102", "Case-103", "Case-104"]
    );

    matcher.addEligibility("Analyst-A", "Case-101");
    matcher.addEligibility("Analyst-A", "Case-102");
    matcher.addEligibility("Analyst-B", "Case-101");
    matcher.addEligibility("Analyst-C", "Case-102");
    matcher.addEligibility("Analyst-C", "Case-103");
    matcher.addEligibility("Analyst-D", "Case-103");

    const service = new AllocationService(matcher);

    service.on("allocated", result => {
        console.log("Assignments:", result.assignments);
        console.log("Matching cardinality:", result.cardinality);
        console.log("Unassigned analysts:", result.unmatchedWorkers);
        console.log("Unfilled cases:", result.unmatchedTasks);
    });

    service.on("closed", event => {
        console.log("Allocation lifecycle:", event.state);
    });

    service.on("failure", event => {
        console.error("Allocation failure:", event.reason);
    });

    const result = service.allocate();
    if (result.cardinality !== result.assignments.length) {
        throw new Error("Cardinality does not match assignment count.");
    }
    service.close();

    console.log("Lifecycle history:", service.history);

    // An unmatched worker or task is legitimate when eligibility is limited.
    const constrained = new BipartiteMatcher(["W1", "W2"], ["T1"]);
    constrained.addEligibility("W1", "T1");
    constrained.addEligibility("W2", "T1");
    console.log("Constrained matching:", constrained.maximumMatching());

    try {
        matcher.addEligibility("Case-101", "Analyst-A");
    } catch (error) {
        console.log("Invalid edge rejected:", error.message);
    }

    try {
        service.allocate();
    } catch (error) {
        console.log("Invalid lifecycle transition rejected:", error.message);
    }
}

main();
