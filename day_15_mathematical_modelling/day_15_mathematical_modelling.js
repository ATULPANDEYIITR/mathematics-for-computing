/*
 * Mathematical Modeling
 * ======================
 *
 * A self-contained JavaScript study program for translating computing
 * problems into mathematical expressions, variables, constraints,
 * assumptions, simulations, optimization models, and validation rules.
 *
 * Run in Node.js:
 *     node mathematical_modeling.js
 *
 * No external packages are required.
 */

"use strict";

// ============================================================================
// 1. OUTPUT HELPERS
// ============================================================================

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function subsection(title) {
    console.log("\n" + "-".repeat(78));
    console.log(title);
    console.log("-".repeat(78));
}

// ============================================================================
// 2. VARIABLES AND EXPRESSIONS
// ============================================================================

function demonstrateVariables() {
    subsection("Variables, constants, expressions, and equations");

    // Mathematical model:
    // income = regularHours * rate + overtimeHours * rate * multiplier
    const hourlyRate = 25;
    const regularHours = 8;
    const overtimeHours = 2;
    const overtimeMultiplier = 1.5;

    const income =
        regularHours * hourlyRate +
        overtimeHours * hourlyRate * overtimeMultiplier;

    console.log({ hourlyRate, regularHours, overtimeHours, income });

    // Mathematical function:
    // f(x) = x² + 2x + 1
    function polynomial(x) {
        return x * x + 2 * x + 1;
    }

    console.log(`f(3) = ${polynomial(3)}`);
}

// ============================================================================
// 3. BUSINESS MODEL
// ============================================================================

function createSalesModel({ price, variableCost, fixedCost, maximumDemand }) {
    if (![price, variableCost, fixedCost, maximumDemand].every(Number.isFinite)) {
        throw new TypeError("All model parameters must be finite numbers.");
    }

    if (price < 0 || variableCost < 0 || fixedCost < 0 || maximumDemand < 0) {
        throw new RangeError("Model parameters cannot be negative.");
    }

    if (price <= variableCost) {
        throw new RangeError(
            "Price must exceed variable cost for positive unit contribution."
        );
    }

    return {
        price,
        variableCost,
        fixedCost,
        maximumDemand,

        revenue(quantity) {
            if (quantity < 0 || quantity > maximumDemand) {
                throw new RangeError("Quantity is outside the model domain.");
            }
            return price * quantity;
        },

        cost(quantity) {
            if (quantity < 0 || quantity > maximumDemand) {
                throw new RangeError("Quantity is outside the model domain.");
            }
            return fixedCost + variableCost * quantity;
        },

        profit(quantity) {
            return this.revenue(quantity) - this.cost(quantity);
        },

        breakEven() {
            return fixedCost / (price - variableCost);
        }
    };
}

function demonstrateBusinessModel() {
    subsection("Translating a business problem into equations");

    const model = createSalesModel({
        price: 80,
        variableCost: 35,
        fixedCost: 18000,
        maximumDemand: 2000
    });

    console.log(`Break-even quantity: ${model.breakEven()}`);
    console.log(`Profit at 500 units: ${model.profit(500)}`);

    try {
        model.profit(2500);
    } catch (error) {
        console.log(`Expected validation error: ${error.message}`);
    }
}

// ============================================================================
// 4. CONSTRAINTS
// ============================================================================

function isProductionPlanFeasible(x, y) {
    // Resource constraints:
    // 2x + y <= 100
    // x + 3y <= 90
    // x >= 0
    // y >= 0
    return (
        x >= 0 &&
        y >= 0 &&
        2 * x + y <= 100 &&
        x + 3 * y <= 90
    );
}

function demonstrateConstraints() {
    subsection("Constraints and feasible regions");

    const plans = [];

    for (let x = 0; x <= 100; x++) {
        for (let y = 0; y <= 90; y++) {
            if (isProductionPlanFeasible(x, y)) {
                plans.push([x, y]);
            }
        }
    }

    console.log(`Feasible integer plans: ${plans.length}`);
    console.log("First plans:", plans.slice(0, 10));

    const invalidPlan = [40, 30];
    console.log(
        `Plan ${invalidPlan}: feasible=${isProductionPlanFeasible(...invalidPlan)}`
    );
}

// ============================================================================
// 5. INTEGER OPTIMIZATION
// ============================================================================

function optimizeProduction() {
    /*
     * Objective:
     *
     *     maximize 50x + 70y
     *
     * Subject to:
     *
     *     2x + 3y <= 100
     *     3x + 2y <= 90
     *     x >= 0
     *     y >= 0
     *     x,y integers
     *
     * This brute-force implementation is educational. It makes the
     * mathematical model explicit without depending on an optimizer.
     */

    let best = null;

    for (let x = 0; x <= 100; x++) {
        for (let y = 0; y <= 100; y++) {
            if (2 * x + 3 * y > 100) continue;
            if (3 * x + 2 * y > 90) continue;

            const objective = 50 * x + 70 * y;

            if (best === null || objective > best.objective) {
                best = { x, y, objective };
            }
        }
    }

    return best;
}

function demonstrateOptimization() {
    subsection("Objective functions and optimization");

    const solution = optimizeProduction();

    console.log("Optimal integer solution:", solution);
}

// ============================================================================
// 6. PIECEWISE MODEL
// ============================================================================

function shippingCost(weightKg) {
    if (!Number.isFinite(weightKg)) {
        throw new TypeError("Weight must be finite.");
    }

    if (weightKg < 0) {
        throw new RangeError("Weight cannot be negative.");
    }

    if (weightKg <= 1) return 5;
    if (weightKg <= 5) return 8;

    return 8 + 2 * Math.ceil(weightKg - 5);
}

function demonstratePiecewiseModel() {
    subsection("Piecewise mathematical functions");

    for (const weight of [0.5, 1, 3, 5, 6.2]) {
        console.log(
            `${weight.toFixed(1)} kg -> ${shippingCost(weight).toFixed(2)}`
        );
    }
}

// ============================================================================
// 7. CONTINUOUS AND DISCRETE VARIABLES
// ============================================================================

function demonstrateContinuousAndDiscrete() {
    subsection("Continuous versus discrete variables");

    const continuousBreakEven = 18000 / (80 - 35);
    const wholeUnitRequirement = Math.ceil(continuousBreakEven);

    console.log(`Continuous break-even: ${continuousBreakEven}`);
    console.log(`Whole-unit requirement: ${wholeUnitRequirement}`);

    /*
     * The equation may produce a fractional result even when the physical
     * decision variable must be integral.
     */
}

// ============================================================================
// 8. DIMENSIONAL MODEL
// ============================================================================

function demonstrateDimensionalAnalysis() {
    subsection("Units and dimensional consistency");

    // distance = speed × time
    const speedKmPerHour = 60;
    const timeHours = 2.5;
    const distanceKm = speedKmPerHour * timeHours;

    console.log(`Distance: ${distanceKm} km`);

    const speedMetersPerSecond = speedKmPerHour * 1000 / 3600;
    const timeSeconds = timeHours * 3600;
    const distanceMeters = speedMetersPerSecond * timeSeconds;

    console.log(`Equivalent distance: ${distanceMeters} m`);
}

// ============================================================================
// 9. PROBABILITY
// ============================================================================

function expectedValue(outcomes, probabilities) {
    if (outcomes.length !== probabilities.length) {
        throw new Error("Outcome and probability lengths must match.");
    }

    const probabilitySum = probabilities.reduce(
        (sum, probability) => sum + probability,
        0
    );

    if (
        probabilities.some(
            probability =>
                !Number.isFinite(probability) ||
                probability < 0 ||
                probability > 1
        )
    ) {
        throw new RangeError("Every probability must be between 0 and 1.");
    }

    if (Math.abs(probabilitySum - 1) > 1e-12) {
        throw new RangeError("Probabilities must sum to 1.");
    }

    return outcomes.reduce(
        (sum, outcome, index) =>
            sum + outcome * probabilities[index],
        0
    );
}

function demonstrateProbability() {
    subsection("Expected value");

    const outcomes = [1000, 300, -500];
    const probabilities = [0.2, 0.5, 0.3];

    console.log(
        `Expected value: ${expectedValue(outcomes, probabilities)}`
    );
}

// ============================================================================
// 10. DETERMINISTIC RANDOM GENERATOR
// ============================================================================

class LinearCongruentialGenerator {
    /*
     * A deterministic pseudo-random generator is useful in simulations
     * because a seed makes experiments reproducible.
     *
     * X_(n+1) = (aX_n + c) mod m
     *
     * This is an educational implementation, not a cryptographic generator.
     */

    constructor(seed = 123456789) {
        this.state = seed >>> 0;
        this.multiplier = 1664525;
        this.increment = 1013904223;
        this.modulus = 2 ** 32;
    }

    next() {
        this.state =
            (this.multiplier * this.state + this.increment) %
            this.modulus;

        return this.state / this.modulus;
    }
}

function monteCarloPi(samples, seed = 42) {
    if (!Number.isInteger(samples) || samples <= 0) {
        throw new RangeError("Sample count must be a positive integer.");
    }

    const random = new LinearCongruentialGenerator(seed);
    let inside = 0;

    for (let i = 0; i < samples; i++) {
        const x = random.next();
        const y = random.next();

        if (x * x + y * y <= 1) {
            inside++;
        }
    }

    return 4 * inside / samples;
}

function demonstrateSimulation() {
    subsection("Monte Carlo simulation");

    for (const samples of [100, 1000, 10000, 100000]) {
        const estimate = monteCarloPi(samples);
        console.log(
            `samples=${samples}, estimate=${estimate.toFixed(8)}, ` +
            `error=${Math.abs(estimate - Math.PI).toFixed(8)}`
        );
    }
}

// ============================================================================
// 11. NUMERICAL DERIVATIVE
// ============================================================================

function numericalDerivative(fn, x, step = 1e-5) {
    if (!Number.isFinite(step) || step <= 0) {
        throw new RangeError("Step must be positive and finite.");
    }

    // Central difference:
    // f'(x) ≈ [f(x+h) - f(x-h)] / (2h)
    return (fn(x + step) - fn(x - step)) / (2 * step);
}

function demonstrateDerivative() {
    subsection("Numerical derivatives and sensitivity");

    const profit = quantity =>
        -0.02 * quantity ** 2 + 40 * quantity - 5000;

    for (const quantity of [100, 500, 1000]) {
        const derivative = numericalDerivative(profit, quantity);

        console.log(
            `q=${quantity}, profit=${profit(quantity).toFixed(2)}, ` +
            `marginal profit=${derivative.toFixed(4)}`
        );
    }
}

// ============================================================================
// 12. BISECTION
// ============================================================================

function bisection(fn, low, high, tolerance = 1e-10, maxIterations = 200) {
    if (low >= high) {
        throw new RangeError("Low must be less than high.");
    }

    let lowValue = fn(low);
    let highValue = fn(high);

    if (lowValue === 0) return low;
    if (highValue === 0) return high;

    if (lowValue * highValue > 0) {
        throw new RangeError("The interval does not bracket a root.");
    }

    for (let i = 0; i < maxIterations; i++) {
        const middle = (low + high) / 2;
        const middleValue = fn(middle);

        if (
            Math.abs(middleValue) <= tolerance ||
            Math.abs(high - low) <= tolerance
        ) {
            return middle;
        }

        if (lowValue * middleValue <= 0) {
            high = middle;
            highValue = middleValue;
        } else {
            low = middle;
            lowValue = middleValue;
        }
    }

    return (low + high) / 2;
}

function demonstrateRootFinding() {
    subsection("Numerical equation solving");

    const root = bisection(x => x * x - 10, 0, 10);

    console.log(`Root: ${root}`);
    console.log(`Reference: ${Math.sqrt(10)}`);
}

// ============================================================================
// 13. ASYNCHRONOUS MODEL EVALUATION
// ============================================================================

function evaluateModelAsync(name, evaluator) {
    /*
     * JavaScript applications often obtain model parameters asynchronously
     * from APIs, databases, files, or user interfaces.
     *
     * Promise-based structure separates data retrieval from computation.
     */

    return Promise.resolve()
        .then(() => evaluator())
        .then(value => ({ name, value }));
}

async function demonstrateAsyncModeling() {
    subsection("Asynchronous model execution");

    const models = [
        evaluateModelAsync("base", () => {
            const quantity = 1000;
            return (80 - 35) * quantity - 18000;
        }),

        evaluateModelAsync("optimistic", () => {
            const quantity = 1400;
            return (90 - 30) * quantity - 18000;
        }),

        evaluateModelAsync("pessimistic", () => {
            const quantity = 600;
            return (70 - 40) * quantity - 18000;
        })
    ];

    const results = await Promise.all(models);

    for (const result of results) {
        console.log(`${result.name}: ${result.value.toFixed(2)}`);
    }
}

// ============================================================================
// 14. QUEUE MODEL
// ============================================================================

function simulateSingleServerQueue(interarrivalTimes, serviceTimes) {
    if (interarrivalTimes.length !== serviceTimes.length) {
        throw new Error("Input arrays must have equal lengths.");
    }

    const observations = [];
    let arrivalTime = 0;
    let previousServiceEnd = 0;

    for (let i = 0; i < interarrivalTimes.length; i++) {
        const interarrival = interarrivalTimes[i];
        const service = serviceTimes[i];

        if (interarrival < 0 || service < 0) {
            throw new RangeError("Times cannot be negative.");
        }

        arrivalTime += interarrival;

        const serviceStart = Math.max(
            arrivalTime,
            previousServiceEnd
        );

        const serviceEnd = serviceStart + service;

        observations.push({
            customer: i + 1,
            arrivalTime,
            serviceStart,
            serviceEnd,
            waitingTime: serviceStart - arrivalTime,
            timeInSystem: serviceEnd - arrivalTime
        });

        previousServiceEnd = serviceEnd;
    }

    return observations;
}

function demonstrateQueueModel() {
    subsection("Queueing model");

    const observations = simulateSingleServerQueue(
        [0, 2, 1, 1.5, 3],
        [2.5, 3, 1, 4, 2]
    );

    for (const observation of observations) {
        console.log(observation);
    }
}

// ============================================================================
// 15. GRAPH MODEL
// ============================================================================

function dijkstra(graph, start) {
    const distances = {};

    for (const node of Object.keys(graph)) {
        distances[node] = Infinity;
    }

    distances[start] = 0;

    // A simple array-based priority queue keeps this implementation
    // dependency-free. A binary heap would improve performance for large
    // graphs.
    const queue = [{ node: start, distance: 0 }];

    while (queue.length > 0) {
        queue.sort((a, b) => a.distance - b.distance);

        const current = queue.shift();

        if (current.distance > distances[current.node]) {
            continue;
        }

        for (const edge of graph[current.node]) {
            if (edge.weight < 0) {
                throw new RangeError(
                    "Dijkstra's algorithm requires non-negative weights."
                );
            }

            const candidate = current.distance + edge.weight;

            if (candidate < distances[edge.node]) {
                distances[edge.node] = candidate;
                queue.push({
                    node: edge.node,
                    distance: candidate
                });
            }
        }
    }

    return distances;
}

function demonstrateGraphModel() {
    subsection("Graph-based model");

    const graph = {
        A: [
            { node: "B", weight: 4 },
            { node: "C", weight: 2 }
        ],
        B: [
            { node: "C", weight: 1 },
            { node: "D", weight: 5 }
        ],
        C: [
            { node: "B", weight: 1 },
            { node: "D", weight: 8 },
            { node: "E", weight: 10 }
        ],
        D: [
            { node: "E", weight: 2 }
        ],
        E: []
    };

    console.log(dijkstra(graph, "A"));
}

// ============================================================================
// 16. REGRESSION
// ============================================================================

function linearRegression(xValues, yValues) {
    if (xValues.length !== yValues.length) {
        throw new Error("x and y lengths must match.");
    }

    if (xValues.length < 2) {
        throw new Error("At least two observations are required.");
    }

    const xMean =
        xValues.reduce((sum, value) => sum + value, 0) /
        xValues.length;

    const yMean =
        yValues.reduce((sum, value) => sum + value, 0) /
        yValues.length;

    let numerator = 0;
    let denominator = 0;

    for (let i = 0; i < xValues.length; i++) {
        numerator +=
            (xValues[i] - xMean) *
            (yValues[i] - yMean);

        denominator +=
            (xValues[i] - xMean) ** 2;
    }

    if (denominator === 0) {
        throw new Error("Predictor values cannot all be identical.");
    }

    const slope = numerator / denominator;
    const intercept = yMean - slope * xMean;

    return {
        slope,
        intercept,
        predict(x) {
            return slope * x + intercept;
        }
    };
}

function demonstrateRegression() {
    subsection("Regression as data-driven mathematical modeling");

    const advertisingSpend = [1, 2, 3, 4, 5, 6];
    const sales = [12, 18, 25, 29, 38, 43];

    const model = linearRegression(
        advertisingSpend,
        sales
    );

    console.log(`Slope: ${model.slope.toFixed(4)}`);
    console.log(`Intercept: ${model.intercept.toFixed(4)}`);
    console.log(`Prediction at x=7: ${model.predict(7).toFixed(2)}`);
}

// ============================================================================
// 17. MODEL ERROR
// ============================================================================

function meanAbsoluteError(actual, predicted) {
    if (actual.length !== predicted.length || actual.length === 0) {
        throw new Error("Arrays must have equal non-zero length.");
    }

    return actual.reduce(
        (sum, value, index) =>
            sum + Math.abs(value - predicted[index]),
        0
    ) / actual.length;
}

function rootMeanSquaredError(actual, predicted) {
    if (actual.length !== predicted.length || actual.length === 0) {
        throw new Error("Arrays must have equal non-zero length.");
    }

    const meanSquaredError =
        actual.reduce(
            (sum, value, index) =>
                sum + (value - predicted[index]) ** 2,
            0
        ) / actual.length;

    return Math.sqrt(meanSquaredError);
}

function demonstrateValidation() {
    subsection("Validation and error metrics");

    const actual = [10, 20, 30, 40];
    const predicted = [11, 18, 31, 37];

    console.log(`MAE: ${meanAbsoluteError(actual, predicted).toFixed(4)}`);
    console.log(
        `RMSE: ${rootMeanSquaredError(actual, predicted).toFixed(4)}`
    );
}

// ============================================================================
// 18. FINANCIAL MODEL
// ============================================================================

function netPresentValue(initialInvestment, cashFlows, discountRate) {
    if (discountRate <= -1) {
        throw new RangeError("Discount rate must exceed -100%.");
    }

    return initialInvestment + cashFlows.reduce(
        (sum, cashFlow, index) =>
            sum + cashFlow / ((1 + discountRate) ** (index + 1)),
        0
    );
}

function demonstrateFinancialModel() {
    subsection("Discounted cash flow model");

    const npv = netPresentValue(
        -100000,
        [30000, 35000, 40000, 45000],
        0.10
    );

    console.log(`NPV: ${npv.toFixed(2)}`);
}

// ============================================================================
// 19. SENSITIVITY ANALYSIS
// ============================================================================

function demonstrateSensitivity() {
    subsection("Parameter sensitivity");

    const quantity = 1000;
    const prices = [70, 80, 90];
    const variableCosts = [30, 35, 40];
    const fixedCost = 18000;

    for (const price of prices) {
        for (const cost of variableCosts) {
            const profit =
                (price - cost) * quantity -
                fixedCost;

            console.log(
                `price=${price}, cost=${cost}, profit=${profit.toFixed(2)}`
            );
        }
    }
}

// ============================================================================
// 20. SECURITY AND INPUT VALIDATION
// ============================================================================

function parsePositiveFiniteNumber(value, fieldName) {
    /*
     * External input should be validated before entering a mathematical
     * model. Never pass arbitrary user strings to eval().
     */
    const number = Number(value);

    if (!Number.isFinite(number)) {
        throw new TypeError(`${fieldName} must be a finite number.`);
    }

    if (number <= 0) {
        throw new RangeError(`${fieldName} must be positive.`);
    }

    return number;
}

function demonstrateSafeInput() {
    subsection("Safe model input");

    for (const value of ["100", "Infinity", "-5"]) {
        try {
            console.log(
                `Accepted: ${parsePositiveFiniteNumber(value, "price")}`
            );
        } catch (error) {
            console.log(`Rejected ${value}: ${error.message}`);
        }
    }
}

// ============================================================================
// 21. FLOATING-POINT PRECISION
// ============================================================================

function demonstrateFloatingPoint() {
    subsection("Floating-point precision");

    const result = 0.1 + 0.2;

    console.log(`0.1 + 0.2 = ${result}`);
    console.log(`Exact comparison with 0.3: ${result === 0.3}`);
    console.log(
        `Absolute error: ${Math.abs(result - 0.3)}`
    );
}

// ============================================================================
// 22. PERFORMANCE AND SEARCH SPACE
// ============================================================================

function demonstrateComplexity() {
    subsection("Computational complexity");

    /*
     * If n decision variables each have k candidate values, exhaustive
     * enumeration requires approximately k^n combinations.
     *
     * This illustrates the combinatorial explosion that motivates
     * optimization algorithms.
     */

    for (let variables = 1; variables <= 8; variables++) {
        const combinations = 10 ** variables;

        console.log(
            `variables=${variables}, combinations=${combinations.toLocaleString()}`
        );
    }
}

// ============================================================================
// 23. TESTS
// ============================================================================

function runTests() {
    subsection("Model tests");

    const model = createSalesModel({
        price: 80,
        variableCost: 35,
        fixedCost: 18000,
        maximumDemand: 2000
    });

    console.assert(model.profit(0) === -18000);
    console.assert(Math.abs(model.profit(1) + 17955) < 1e-12);
    console.assert(model.breakEven() === 400);

    const root = bisection(x => x * x - 25, 0, 10);
    console.assert(Math.abs(root - 5) < 1e-8);

    const expected = expectedValue(
        [0, 100],
        [0.75, 0.25]
    );
    console.assert(expected === 25);

    const regression = linearRegression(
        [1, 2, 3],
        [2, 4, 6]
    );

    console.assert(Math.abs(regression.slope - 2) < 1e-12);
    console.assert(Math.abs(regression.intercept) < 1e-12);

    console.log("All model assertions passed.");
}

// ============================================================================
// 24. MAIN
// ============================================================================

async function main() {
    section(
        "MATHEMATICAL MODELING: TRANSLATING COMPUTING PROBLEMS INTO MATHEMATICS"
    );

    demonstrateVariables();
    demonstrateBusinessModel();
    demonstrateConstraints();
    demonstrateOptimization();
    demonstratePiecewiseModel();
    demonstrateContinuousAndDiscrete();
    demonstrateDimensionalAnalysis();
    demonstrateProbability();
    demonstrateSimulation();
    demonstrateDerivative();
    demonstrateRootFinding();
    await demonstrateAsyncModeling();
    demonstrateQueueModel();
    demonstrateGraphModel();
    demonstrateRegression();
    demonstrateValidation();
    demonstrateFinancialModel();
    demonstrateSensitivity();
    demonstrateSafeInput();
    demonstrateFloatingPoint();
    demonstrateComplexity();
    runTests();

    section("END OF STUDY PROGRAM");
    console.log(
        "The program demonstrates abstraction, variables, equations, " +
        "constraints, objectives, simulation, numerical methods, " +
        "optimization, validation, and interpretation."
    );
}

main().catch(error => {
    console.error("Fatal execution error:", error.message);
    process.exitCode = 1;
});
