"use strict";

/*
 * Partial Orders in JavaScript
 *
 * This file models finite posets and uses JavaScript's Set, Map, classes,
 * recursion, and event-driven callbacks to explore comparability, chains,
 * antichains, and Hasse diagrams.
 */

class Poset {
    constructor(elements, relationPairs) {
        this.elements = new Set(elements);
        this.relation = new Set(
            relationPairs.map(([a, b]) => this.key(a, b))
        );

        this.validate();
    }

    key(a, b) {
        return `${a}\u0000${b}`;
    }

    pairExists(a, b) {
        return this.relation.has(this.key(a, b));
    }

    validate() {
        for (const element of this.elements) {
            if (!this.pairExists(element, element)) {
                throw new Error(`Relation is not reflexive at ${element}`);
            }
        }

        for (const pair of this.relation) {
            const [a, b] = pair.split("\u0000");

            if (!this.elements.has(a) || !this.elements.has(b)) {
                throw new Error(`Relation references an unknown element: ${pair}`);
            }

            if (a !== b && this.pairExists(b, a)) {
                throw new Error(`Relation is not antisymmetric: ${a}, ${b}`);
            }
        }

        for (const pair of this.relation) {
            const [a, b] = pair.split("\u0000");

            for (const c of this.elements) {
                if (this.pairExists(b, c) && !this.pairExists(a, c)) {
                    throw new Error(
                        `Relation is not transitive: ${a} <= ${b} <= ${c}`
                    );
                }
            }
        }
    }

    leq(a, b) {
        return this.pairExists(a, b);
    }

    strictLess(a, b) {
        return a !== b && this.leq(a, b);
    }

    comparable(a, b) {
        return this.leq(a, b) || this.leq(b, a);
    }

    incomparable(a, b) {
        return !this.comparable(a, b);
    }

    comparablePairs() {
        const values = [...this.elements].sort();
        const result = [];

        for (let i = 0; i < values.length; i++) {
            for (let j = i + 1; j < values.length; j++) {
                if (this.comparable(values[i], values[j])) {
                    result.push([values[i], values[j]]);
                }
            }
        }

        return result;
    }

    incomparablePairs() {
        const values = [...this.elements].sort();
        const result = [];

        for (let i = 0; i < values.length; i++) {
            for (let j = i + 1; j < values.length; j++) {
                if (this.incomparable(values[i], values[j])) {
                    result.push([values[i], values[j]]);
                }
            }
        }

        return result;
    }

    minimalElements() {
        return [...this.elements].filter(
            x => ![...this.elements].some(y => this.strictLess(y, x))
        );
    }

    maximalElements() {
        return [...this.elements].filter(
            x => ![...this.elements].some(y => this.strictLess(x, y))
        );
    }

    leastElement() {
        for (const candidate of this.elements) {
            if ([...this.elements].every(x => this.leq(candidate, x))) {
                return candidate;
            }
        }
        return null;
    }

    greatestElement() {
        for (const candidate of this.elements) {
            if ([...this.elements].every(x => this.leq(x, candidate))) {
                return candidate;
            }
        }
        return null;
    }

    isChain(values) {
        const unique = [...new Set(values)];

        if (!unique.every(x => this.elements.has(x))) {
            return false;
        }

        for (let i = 0; i < unique.length; i++) {
            for (let j = i + 1; j < unique.length; j++) {
                if (!this.comparable(unique[i], unique[j])) {
                    return false;
                }
            }
        }

        return true;
    }

    isAntichain(values) {
        const unique = [...new Set(values)];

        if (!unique.every(x => this.elements.has(x))) {
            return false;
        }

        for (let i = 0; i < unique.length; i++) {
            for (let j = i + 1; j < unique.length; j++) {
                if (this.comparable(unique[i], unique[j])) {
                    return false;
                }
            }
        }

        return true;
    }

    coverRelations() {
        const covers = [];

        for (const pair of this.relation) {
            const [lower, upper] = pair.split("\u0000");

            if (!this.strictLess(lower, upper)) {
                continue;
            }

            let hasIntermediate = false;

            for (const middle of this.elements) {
                if (
                    middle !== lower &&
                    middle !== upper &&
                    this.strictLess(lower, middle) &&
                    this.strictLess(middle, upper)
                ) {
                    hasIntermediate = true;
                    break;
                }
            }

            if (!hasIntermediate) {
                covers.push([lower, upper]);
            }
        }

        return covers.sort(([a, b], [c, d]) =>
            a.localeCompare(c) || b.localeCompare(d)
        );
    }

    layers() {
        const remaining = new Set(this.elements);
        const layers = [];

        while (remaining.size > 0) {
            const layer = [...remaining]
                .filter(x => {
                    for (const y of remaining) {
                        if (this.strictLess(y, x)) {
                            return false;
                        }
                    }
                    return true;
                })
                .sort();

            if (layer.length === 0) {
                throw new Error("Unable to construct a DAG layering.");
            }

            layers.push(layer);

            for (const element of layer) {
                remaining.delete(element);
            }
        }

        return layers;
    }

    allSubsets() {
        const values = [...this.elements];
        const subsets = [];

        for (let mask = 1; mask < (1 << values.length); mask++) {
            const subset = [];

            for (let bit = 0; bit < values.length; bit++) {
                if (mask & (1 << bit)) {
                    subset.push(values[bit]);
                }
            }

            subsets.push(subset);
        }

        return subsets;
    }

    maximumChain() {
        const chains = this.allSubsets().filter(subset => this.isChain(subset));

        return chains.reduce(
            (best, current) => current.length > best.length ? current : best,
            []
        );
    }

    maximumAntichain() {
        const antichains = this.allSubsets()
            .filter(subset => this.isAntichain(subset));

        return antichains.reduce(
            (best, current) => current.length > best.length ? current : best,
            []
        );
    }

    hasseText() {
        const lines = ["Hasse diagram cover relations:"];

        for (const [lower, upper] of this.coverRelations()) {
            lines.push(`  ${lower} -> ${upper}`);
        }

        lines.push("");
        lines.push("Bottom-to-top layers:");

        this.layers().forEach((layer, index) => {
            lines.push(`  level ${index}: ${layer.join("   ")}`);
        });

        return lines.join("\n");
    }
}


function divisibilityPoset(numbers) {
    const values = [...new Set(numbers)].sort((a, b) => a - b);
    const elements = values.map(String);
    const relation = [];

    for (const a of values) {
        for (const b of values) {
            if (b % a === 0) {
                relation.push([String(a), String(b)]);
            }
        }
    }

    return new Poset(elements, relation);
}


function subsetInclusionPoset(subsets) {
    const normalized = subsets.map(
        subset => [...new Set(subset)].sort()
    );

    const labels = normalized.map(
        subset => subset.length === 0 ? "∅" : `{${subset.join(",")}}`
    );

    const relation = [];

    const containsAll = (small, large) =>
        small.every(value => large.includes(value));

    for (let i = 0; i < normalized.length; i++) {
        for (let j = 0; j < normalized.length; j++) {
            if (containsAll(normalized[i], normalized[j])) {
                relation.push([labels[i], labels[j]]);
            }
        }
    }

    return new Poset(labels, relation);
}


/*
 * Event-driven lifecycle model:
 *
 * A finite poset can be represented as a dependency ordering. Events here
 * simulate work becoming available as prerequisite elements complete.
 */
class DependencyScheduler {
    constructor(dependencies) {
        this.dependencies = new Map(
            Object.entries(dependencies).map(
                ([task, prerequisites]) => [task, new Set(prerequisites)]
            )
        );

        for (const prerequisites of this.dependencies.values()) {
            for (const prerequisite of prerequisites) {
                if (!this.dependencies.has(prerequisite)) {
                    this.dependencies.set(prerequisite, new Set());
                }
            }
        }

        this.completed = new Set();
        this.listeners = new Map();
        this.assertAcyclic();
    }

    on(eventName, callback) {
        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, []);
        }

        this.listeners.get(eventName).push(callback);
    }

    emit(eventName, payload) {
        for (const callback of this.listeners.get(eventName) || []) {
            callback(payload);
        }
    }

    assertAcyclic() {
        const state = new Map(
            [...this.dependencies.keys()].map(task => [task, 0])
        );

        const visit = task => {
            if (state.get(task) === 1) {
                throw new Error(`Dependency cycle detected at ${task}`);
            }

            if (state.get(task) === 2) {
                return;
            }

            state.set(task, 1);

            for (const prerequisite of this.dependencies.get(task)) {
                visit(prerequisite);
            }

            state.set(task, 2);
        };

        for (const task of this.dependencies.keys()) {
            visit(task);
        }
    }

    readyTasks() {
        return [...this.dependencies.keys()]
            .filter(task => {
                if (this.completed.has(task)) {
                    return false;
                }

                return [...this.dependencies.get(task)]
                    .every(prerequisite => this.completed.has(prerequisite));
            })
            .sort();
    }

    complete(task) {
        if (!this.dependencies.has(task)) {
            throw new Error(`Unknown task: ${task}`);
        }

        if (!this.readyTasks().includes(task)) {
            throw new Error(
                `Task ${task} cannot complete before its prerequisites.`
            );
        }

        this.completed.add(task);

        this.emit("completed", {
            task,
            newlyReady: this.readyTasks()
        });
    }
}


function demonstrateCorePoset() {
    console.log("PARTIAL ORDER STRUCTURE");

    const poset = divisibilityPoset([1, 2, 3, 4, 6, 12]);

    console.log("Elements:", [...poset.elements]);
    console.log("Minimal:", poset.minimalElements());
    console.log("Maximal:", poset.maximalElements());
    console.log("Least:", poset.leastElement());
    console.log("Greatest:", poset.greatestElement());

    console.log("2 and 4 comparable:", poset.comparable("2", "4"));
    console.log("2 and 3 comparable:", poset.comparable("2", "3"));

    console.log("\nComparable pairs:");
    console.log(poset.comparablePairs());

    console.log("\nIncomparable pairs:");
    console.log(poset.incomparablePairs());

    console.log("\n" + poset.hasseText());
}


function demonstrateSubsetPoset() {
    console.log("\nSUBSET INCLUSION");

    const poset = subsetInclusionPoset([
        [],
        ["a"],
        ["b"],
        ["c"],
        ["a", "b"],
        ["a", "c"],
        ["b", "c"],
        ["a", "b", "c"]
    ]);

    console.log(poset.hasseText());

    console.log(
        "{a}, {b}, {c} is an antichain:",
        poset.isAntichain(["{a}", "{b}", "{c}"])
    );

    console.log(
        "{a}, {a,b}, {a,b,c} is a chain:",
        poset.isChain(["{a}", "{a,b}", "{a,b,c}"])
    );
}


function demonstrateEventDrivenDependencies() {
    console.log("\nEVENT-DRIVEN DEPENDENCY MODEL");

    const scheduler = new DependencyScheduler({
        design: [],
        implementation: ["design"],
        unitTests: ["implementation"],
        securityReview: ["implementation"],
        releaseCandidate: ["unitTests", "securityReview"]
    });

    scheduler.on("completed", event => {
        console.log(
            `Completed ${event.task}; ready tasks: ${event.newlyReady.join(", ")}`
        );
    });

    console.log("Initial ready tasks:", scheduler.readyTasks());

    scheduler.complete("design");
    scheduler.complete("implementation");

    /*
     * unitTests and securityReview are now incomparable with each other:
     * neither requires the other, so both are independently ready.
     */
    console.log(
        "Independent tasks after implementation:",
        scheduler.readyTasks()
    );

    scheduler.complete("securityReview");
    scheduler.complete("unitTests");
    scheduler.complete("releaseCandidate");
}


function demonstrateFailures() {
    console.log("\nFAILURE CONDITIONS");

    try {
        new Poset(
            ["A", "B"],
            [
                ["A", "A"],
                ["B", "B"],
                ["A", "B"],
                ["B", "A"]
            ]
        );
    } catch (error) {
        console.log("Antisymmetry failure:", error.message);
    }

    try {
        new Poset(
            ["A", "B", "C"],
            [
                ["A", "A"],
                ["B", "B"],
                ["C", "C"],
                ["A", "B"],
                ["B", "C"]
            ]
        );
    } catch (error) {
        console.log("Transitivity failure:", error.message);
    }

    try {
        new DependencyScheduler({
            build: ["test"],
            test: ["build"]
        });
    } catch (error) {
        console.log("Cycle failure:", error.message);
    }

    try {
        const scheduler = new DependencyScheduler({
            compile: [],
            test: ["compile"]
        });

        scheduler.complete("test");
    } catch (error) {
        console.log("Invalid completion order:", error.message);
    }
}


function main() {
    demonstrateCorePoset();
    demonstrateSubsetPoset();
    demonstrateEventDrivenDependencies();
    demonstrateFailures();
}


main();
