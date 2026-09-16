"use strict";

/*
 * Logic Foundations in JavaScript
 *
 * This file complements the Python implementation by emphasizing:
 * - JavaScript Boolean semantics
 * - short-circuit evaluation
 * - functions and higher-order functions
 * - classes and expression trees
 * - validation
 * - exhaustive truth-table generation
 * - practical rule evaluation
 * - asynchronous policy evaluation
 * - performance considerations
 *
 * No external packages are required.
 */


// ============================================================================
// 1. BASIC PROPOSITIONS
// ============================================================================

console.log("\n=== 1. Basic propositions ===");

const propositions = {
    p: true,   // 2 + 2 = 4
    q: false,  // 7 is even
    r: true
};

for (const [symbol, value] of Object.entries(propositions)) {
    console.log(`${symbol} = ${value}`);
}


// ============================================================================
// 2. LOGICAL CONNECTIVES
// ============================================================================

console.log("\n=== 2. Logical connectives ===");

function logicalNot(value) {
    return !value;
}

function logicalAnd(left, right) {
    return left && right;
}

function logicalOr(left, right) {
    return left || right;
}

function logicalXor(left, right) {
    // XOR is true when exactly one operand is true.
    return Boolean(left) !== Boolean(right);
}

function implication(antecedent, consequent) {
    // p -> q is equivalent to NOT p OR q.
    return !antecedent || consequent;
}

function biconditional(left, right) {
    return Boolean(left) === Boolean(right);
}

const p = true;
const q = false;

console.log("NOT p:", logicalNot(p));
console.log("p AND q:", logicalAnd(p, q));
console.log("p OR q:", logicalOr(p, q));
console.log("p XOR q:", logicalXor(p, q));
console.log("p -> q:", implication(p, q));
console.log("p <-> q:", biconditional(p, q));


// ============================================================================
// 3. STRICT BOOLEAN VALIDATION
// ============================================================================

console.log("\n=== 3. Strict Boolean validation ===");

function requireBoolean(value, name = "value") {
    if (typeof value !== "boolean") {
        throw new TypeError(`${name} must be a Boolean`);
    }
    return value;
}

function strictAnd(left, right) {
    requireBoolean(left, "left");
    requireBoolean(right, "right");
    return left && right;
}

for (const candidate of [true, false]) {
    console.log("Accepted:", candidate);
}

for (const candidate of [0, 1, null, "", "true", [], {}]) {
    try {
        strictAnd(candidate, true);
    } catch (error) {
        console.log("Rejected:", candidate, "->", error.message);
    }
}


// ============================================================================
// 4. TRUTH TABLE GENERATION
// ============================================================================

console.log("\n=== 4. Truth tables ===");

function generateAssignments(variableNames) {
    const assignments = [];

    function buildAssignment(index, current) {
        if (index === variableNames.length) {
            assignments.push({ ...current });
            return;
        }

        const variable = variableNames[index];

        current[variable] = false;
        buildAssignment(index + 1, current);

        current[variable] = true;
        buildAssignment(index + 1, current);

        delete current[variable];
    }

    buildAssignment(0, {});
    return assignments;
}

function truthTable(variableNames, expression) {
    return generateAssignments(variableNames).map((assignment) => ({
        assignment,
        result: Boolean(expression(assignment))
    }));
}

function printTruthTable(variableNames, expression, title) {
    console.log(`\n${title}`);

    for (const variable of variableNames) {
        process.stdout.write(`${variable}\t`);
    }

    console.log("Result");

    for (const row of truthTable(variableNames, expression)) {
        for (const variable of variableNames) {
            process.stdout.write(`${row.assignment[variable] ? "T" : "F"}\t`);
        }

        console.log(row.result ? "T" : "F");
    }
}

printTruthTable(
    ["p", "q"],
    ({ p, q }) => p && q,
    "p AND q"
);

printTruthTable(
    ["p", "q"],
    ({ p, q }) => implication(p, q),
    "p -> q"
);


// ============================================================================
// 5. COMPOUND PROPOSITIONS
// ============================================================================

console.log("\n=== 5. Compound propositions ===");

function compoundExpression({ p, q, r }) {
    return (p && q) || !r;
}

printTruthTable(
    ["p", "q", "r"],
    compoundExpression,
    "(p AND q) OR NOT r"
);


// ============================================================================
// 6. FORMULA CLASSIFICATION
// ============================================================================

console.log("\n=== 6. Formula classification ===");

function isTautology(variableNames, expression) {
    return truthTable(variableNames, expression)
        .every((row) => row.result);
}

function isContradiction(variableNames, expression) {
    return truthTable(variableNames, expression)
        .every((row) => !row.result);
}

function isContingency(variableNames, expression) {
    return !isTautology(variableNames, expression) &&
           !isContradiction(variableNames, expression);
}

console.log(
    "p OR NOT p:",
    isTautology(["p"], ({ p }) => p || !p)
);

console.log(
    "p AND NOT p:",
    isContradiction(["p"], ({ p }) => p && !p)
);

console.log(
    "p AND q:",
    isContingency(["p", "q"], ({ p, q }) => p && q)
);


// ============================================================================
// 7. LOGICAL EQUIVALENCE
// ============================================================================

console.log("\n=== 7. Logical equivalence ===");

function logicallyEquivalent(variableNames, first, second) {
    return truthTable(variableNames, first)
        .every((row) => Boolean(row.result) === Boolean(second(row.assignment)));
}

console.log(
    "De Morgan AND:",
    logicallyEquivalent(
        ["p", "q"],
        ({ p, q }) => !(p && q),
        ({ p, q }) => !p || !q
    )
);

console.log(
    "De Morgan OR:",
    logicallyEquivalent(
        ["p", "q"],
        ({ p, q }) => !(p || q),
        ({ p, q }) => !p && !q
    )
);

console.log(
    "Implication:",
    logicallyEquivalent(
        ["p", "q"],
        ({ p, q }) => implication(p, q),
        ({ p, q }) => !p || q
    )
);


// ============================================================================
// 8. IMPLICATION FORMS
// ============================================================================

console.log("\n=== 8. Implication forms ===");

const original = ({ p, q }) => implication(p, q);
const converse = ({ p, q }) => implication(q, p);
const inverse = ({ p, q }) => implication(!p, !q);
const contrapositive = ({ p, q }) => implication(!q, !p);

console.log(
    "Original == converse:",
    logicallyEquivalent(["p", "q"], original, converse)
);

console.log(
    "Original == inverse:",
    logicallyEquivalent(["p", "q"], original, inverse)
);

console.log(
    "Original == contrapositive:",
    logicallyEquivalent(["p", "q"], original, contrapositive)
);

console.log(
    "Converse == inverse:",
    logicallyEquivalent(["p", "q"], converse, inverse)
);


// ============================================================================
// 9. ARGUMENT VALIDITY
// ============================================================================

console.log("\n=== 9. Argument validity ===");

function argumentIsValid(variableNames, premises, conclusion) {
    for (const assignment of generateAssignments(variableNames)) {
        const allPremisesTrue = premises.every(
            (premise) => Boolean(premise(assignment))
        );

        if (allPremisesTrue && !Boolean(conclusion(assignment))) {
            return false;
        }
    }

    return true;
}

const modusPonensValid = argumentIsValid(
    ["p", "q"],
    [
        ({ p, q }) => implication(p, q),
        ({ p }) => p
    ],
    ({ q }) => q
);

console.log("Modus ponens valid:", modusPonensValid);

const affirmingConsequentValid = argumentIsValid(
    ["p", "q"],
    [
        ({ p, q }) => implication(p, q),
        ({ q }) => q
    ],
    ({ p }) => p
);

console.log(
    "Affirming the consequent valid:",
    affirmingConsequentValid
);


// ============================================================================
// 10. COUNTEREXAMPLES
// ============================================================================

console.log("\n=== 10. Counterexample search ===");

function findCounterexample(variableNames, premises, conclusion) {
    for (const assignment of generateAssignments(variableNames)) {
        const premisesTrue = premises.every(
            (premise) => Boolean(premise(assignment))
        );

        if (premisesTrue && !Boolean(conclusion(assignment))) {
            return assignment;
        }
    }

    return null;
}

console.log(
    "Counterexample:",
    findCounterexample(
        ["p", "q"],
        [
            ({ p, q }) => implication(p, q),
            ({ q }) => q
        ],
        ({ p }) => p
    )
);


// ============================================================================
// 11. SATISFIABILITY
// ============================================================================

console.log("\n=== 11. Satisfiability ===");

function satisfyingAssignments(variableNames, expression) {
    return truthTable(variableNames, expression)
        .filter((row) => row.result)
        .map((row) => row.assignment);
}

const satisfiableFormula = ({ p, q, r }) =>
    (p || q) && (!p || r);

console.log(
    satisfyingAssignments(
        ["p", "q", "r"],
        satisfiableFormula
    )
);


// ============================================================================
// 12. EXPRESSION TREE
// ============================================================================

console.log("\n=== 12. Expression tree ===");

class Formula {
    evaluate(_environment) {
        throw new Error("evaluate() must be implemented");
    }

    variables() {
        throw new Error("variables() must be implemented");
    }
}

class Variable extends Formula {
    constructor(name) {
        super();
        this.name = name;
    }

    evaluate(environment) {
        if (!Object.hasOwn(environment, this.name)) {
            throw new Error(`Missing truth value for ${this.name}`);
        }

        return requireBoolean(environment[this.name], this.name);
    }

    variables() {
        return new Set([this.name]);
    }
}

class Not extends Formula {
    constructor(operand) {
        super();
        this.operand = operand;
    }

    evaluate(environment) {
        return !this.operand.evaluate(environment);
    }

    variables() {
        return this.operand.variables();
    }
}

class And extends Formula {
    constructor(left, right) {
        super();
        this.left = left;
        this.right = right;
    }

    evaluate(environment) {
        return this.left.evaluate(environment) &&
               this.right.evaluate(environment);
    }

    variables() {
        return new Set([
            ...this.left.variables(),
            ...this.right.variables()
        ]);
    }
}

class Or extends Formula {
    constructor(left, right) {
        super();
        this.left = left;
        this.right = right;
    }

    evaluate(environment) {
        return this.left.evaluate(environment) ||
               this.right.evaluate(environment);
    }

    variables() {
        return new Set([
            ...this.left.variables(),
            ...this.right.variables()
        ]);
    }
}

class Implies extends Formula {
    constructor(antecedent, consequent) {
        super();
        this.antecedent = antecedent;
        this.consequent = consequent;
    }

    evaluate(environment) {
        return !this.antecedent.evaluate(environment) ||
               this.consequent.evaluate(environment);
    }

    variables() {
        return new Set([
            ...this.antecedent.variables(),
            ...this.consequent.variables()
        ]);
    }
}

class Iff extends Formula {
    constructor(left, right) {
        super();
        this.left = left;
        this.right = right;
    }

    evaluate(environment) {
        return this.left.evaluate(environment) ===
               this.right.evaluate(environment);
    }

    variables() {
        return new Set([
            ...this.left.variables(),
            ...this.right.variables()
        ]);
    }
}

const P = new Variable("p");
const Q = new Variable("q");
const R = new Variable("r");

const structuredFormula = new Or(
    new And(P, Q),
    new Not(R)
);

for (const environment of [
    { p: false, q: false, r: false },
    { p: true, q: true, r: true },
    { p: true, q: false, r: true }
]) {
    console.log(
        environment,
        "=>",
        structuredFormula.evaluate(environment)
    );
}


// ============================================================================
// 13. STRUCTURED FORMULA CLASSIFICATION
// ============================================================================

console.log("\n=== 13. Structured formula classification ===");

function classifyFormula(formula) {
    const variables = [...formula.variables()].sort();

    const expression = (assignment) =>
        formula.evaluate(assignment);

    if (isTautology(variables, expression)) {
        return "tautology";
    }

    if (isContradiction(variables, expression)) {
        return "contradiction";
    }

    return "contingency";
}

console.log("Classification:", classifyFormula(structuredFormula));


// ============================================================================
// 14. DISTRIBUTIVE AND DE MORGAN LAWS
// ============================================================================

console.log("\n=== 14. Verification of logical laws ===");

const logicalLawTests = [
    {
        name: "Double negation",
        variables: ["p"],
        first: ({ p }) => !!p,
        second: ({ p }) => p
    },
    {
        name: "Commutative AND",
        variables: ["p", "q"],
        first: ({ p, q }) => p && q,
        second: ({ p, q }) => q && p
    },
    {
        name: "Distributive AND",
        variables: ["p", "q", "r"],
        first: ({ p, q, r }) => p && (q || r),
        second: ({ p, q, r }) => (p && q) || (p && r)
    },
    {
        name: "Distributive OR",
        variables: ["p", "q", "r"],
        first: ({ p, q, r }) => p || (q && r),
        second: ({ p, q, r }) => (p || q) && (p || r)
    }
];

for (const test of logicalLawTests) {
    console.log(
        `${test.name}:`,
        logicallyEquivalent(
            test.variables,
            test.first,
            test.second
        )
    );
}


// ============================================================================
// 15. JAVASCRIPT SHORT-CIRCUIT SEMANTICS
// ============================================================================

console.log("\n=== 15. JavaScript short-circuit behavior ===");

// JavaScript's && and || return operands, not necessarily true or false.
// This differs from formal propositional logic when non-Boolean values
// are allowed.

console.log("true && false:", true && false);
console.log("5 && 10:", 5 && 10);
console.log("0 || 10:", 0 || 10);

// Normalize the result when a true/false value is required.
console.log("Boolean(5 && 10):", Boolean(5 && 10));


// ============================================================================
// 16. PRACTICAL ACCESS CONTROL
// ============================================================================

console.log("\n=== 16. Access-control policy ===");

function canAccessAdminPanel({
    authenticated,
    administrator,
    accountActive
}) {
    requireBoolean(authenticated, "authenticated");
    requireBoolean(administrator, "administrator");
    requireBoolean(accountActive, "accountActive");

    return authenticated &&
           administrator &&
           accountActive;
}

const accessCases = [
    { authenticated: true, administrator: true, accountActive: true },
    { authenticated: true, administrator: true, accountActive: false },
    { authenticated: true, administrator: false, accountActive: true },
    { authenticated: false, administrator: true, accountActive: true }
];

for (const testCase of accessCases) {
    console.log(
        testCase,
        "=>",
        canAccessAdminPanel(testCase)
    );
}


// ============================================================================
// 17. BUSINESS RULE
// ============================================================================

console.log("\n=== 17. Transaction policy ===");

function transactionAllowed({
    accountActive,
    amountWithinLimit,
    managerApproved
}) {
    return requireBoolean(accountActive, "accountActive") &&
        (
            requireBoolean(amountWithinLimit, "amountWithinLimit") ||
            requireBoolean(managerApproved, "managerApproved")
        );
}

for (const testCase of [
    {
        accountActive: true,
        amountWithinLimit: true,
        managerApproved: false
    },
    {
        accountActive: true,
        amountWithinLimit: false,
        managerApproved: true
    },
    {
        accountActive: true,
        amountWithinLimit: false,
        managerApproved: false
    },
    {
        accountActive: false,
        amountWithinLimit: true,
        managerApproved: true
    }
]) {
    console.log(testCase, "=>", transactionAllowed(testCase));
}


// ============================================================================
// 18. HIGHER-ORDER LOGICAL RULES
// ============================================================================

console.log("\n=== 18. Higher-order rule evaluation ===");

function allRulesPass(rules, input) {
    return rules.every((rule) => rule(input));
}

function anyRulePasses(rules, input) {
    return rules.some((rule) => rule(input));
}

const securityRules = [
    ({ authenticated }) => authenticated,
    ({ accountActive }) => accountActive,
    ({ administrator }) => administrator
];

const user = {
    authenticated: true,
    accountActive: true,
    administrator: true
};

console.log("All security rules:", allRulesPass(securityRules, user));


// ============================================================================
// 19. ASYNCHRONOUS LOGIC
// ============================================================================

console.log("\n=== 19. Asynchronous policy evaluation ===");

// Real applications may obtain truth values from APIs, databases, or other
// asynchronous services. The logical formula can remain the same after the
// required facts have been collected.

function fetchAccountStatus() {
    return Promise.resolve(true);
}

function fetchAuthenticationStatus() {
    return Promise.resolve(true);
}

function fetchAdministratorStatus() {
    return Promise.resolve(false);
}

async function evaluateRemoteAccessPolicy() {
    const [
        authenticated,
        accountActive,
        administrator
    ] = await Promise.all([
        fetchAuthenticationStatus(),
        fetchAccountStatus(),
        fetchAdministratorStatus()
    ]);

    return canAccessAdminPanel({
        authenticated,
        administrator,
        accountActive
    });
}


// ============================================================================
// 20. PERFORMANCE OF EXHAUSTIVE TRUTH TABLES
// ============================================================================

console.log("\n=== 20. Truth-table growth ===");

for (let variableCount = 1; variableCount <= 12; variableCount++) {
    console.log(
        `${variableCount} variables -> ${2 ** variableCount} assignments`
    );
}


// ============================================================================
// 21. EDGE CASES
// ============================================================================

console.log("\n=== 21. Edge cases ===");

// No variables means one empty assignment for a constant formula.
console.log(
    "Constant true:",
    truthTable([], () => true)
);

console.log(
    "Constant false:",
    truthTable([], () => false)
);

try {
    P.evaluate({});
} catch (error) {
    console.log("Expected missing-variable error:", error.message);
}


// ============================================================================
// 22. SIMPLE ASSERTION-BASED TESTING
// ============================================================================

console.log("\n=== 22. Automated tests ===");

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }

    console.log("PASS:", message);
}

assert(
    isTautology(["p"], ({ p }) => p || !p),
    "Law of excluded middle"
);

assert(
    isContradiction(["p"], ({ p }) => p && !p),
    "Law of non-contradiction"
);

assert(
    logicallyEquivalent(
        ["p", "q"],
        ({ p, q }) => !(p && q),
        ({ p, q }) => !p || !q
    ),
    "De Morgan's law"
);

assert(
    logicallyEquivalent(
        ["p", "q"],
        ({ p, q }) => implication(p, q),
        ({ p, q }) => implication(!q, !p)
    ),
    "Contrapositive equivalence"
);

assert(
    argumentIsValid(
        ["p", "q"],
        [
            ({ p, q }) => implication(p, q),
            ({ p }) => p
        ],
        ({ q }) => q
    ),
    "Modus ponens"
);


// ============================================================================
// 23. FINAL ASYNCHRONOUS EXECUTION
// ============================================================================

evaluateRemoteAccessPolicy()
    .then((result) => {
        console.log(
            "Remote access policy result:",
            result
        );
        console.log("\nLogic foundations demonstration completed.");
    })
    .catch((error) => {
        console.error("Policy evaluation failed:", error.message);
        process.exitCode = 1;
    });
