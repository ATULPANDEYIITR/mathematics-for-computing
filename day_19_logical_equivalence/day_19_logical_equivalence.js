/*
 * Logical Equivalence
 *
 * De Morgan's laws, implication equivalence, distributive laws,
 * absorption laws, Boolean identities, symbolic expressions,
 * truth-table verification, and a practical JavaScript rule engine.
 *
 * This file uses only standard JavaScript features and can be executed
 * with a modern Node.js runtime.
 */

"use strict";

// ============================================================
// 1. BASIC BOOLEAN OPERATORS
// ============================================================

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
    return left !== right;
}

function logicalImplies(left, right) {
    // Material implication is false only for true -> false.
    return !left || right;
}

function logicalIff(left, right) {
    return left === right;
}

function truth(value) {
    return value ? "T" : "F";
}

function printSection(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

// ============================================================
// 2. BASIC TRUTH TABLE
// ============================================================

function demonstrateBasicOperators() {
    printSection("Basic Boolean operators");

    console.log("P Q | !P | P&&Q | P||Q | P XOR Q | P->Q | P<->Q");
    console.log("-".repeat(55));

    for (const p of [false, true]) {
        for (const q of [false, true]) {
            console.log(
                `${truth(p)} ${truth(q)} | ` +
                `${truth(!p)}  | ` +
                `${truth(p && q)}   | ` +
                `${truth(p || q)}   | ` +
                `${truth(p !== q)}     | ` +
                `${truth(logicalImplies(p, q))}   | ` +
                `${truth(p === q)}`
            );
        }
    }
}

// ============================================================
// 3. SYMBOLIC EXPRESSION HIERARCHY
// ============================================================

class Proposition {
    evaluate(assignment) {
        throw new Error("evaluate() must be implemented");
    }

    variables() {
        throw new Error("variables() must be implemented");
    }

    precedence() {
        throw new Error("precedence() must be implemented");
    }

    toString(parentPrecedence = 0) {
        throw new Error("toString() must be implemented");
    }

    and(other) {
        return new And(this, other);
    }

    or(other) {
        return new Or(this, other);
    }

    not() {
        return new Not(this);
    }

    implies(other) {
        return new Implies(this, other);
    }

    iff(other) {
        return new Iff(this, other);
    }

    xor(other) {
        return new Xor(this, other);
    }
}

class Variable extends Proposition {
    constructor(name) {
        super();
        this.name = name;
    }

    evaluate(assignment) {
        if (!(this.name in assignment)) {
            throw new Error(`Missing value for variable ${this.name}`);
        }
        return Boolean(assignment[this.name]);
    }

    variables() {
        return new Set([this.name]);
    }

    precedence() {
        return 100;
    }

    toString() {
        return this.name;
    }
}

class Constant extends Proposition {
    constructor(value) {
        super();
        this.value = Boolean(value);
    }

    evaluate() {
        return this.value;
    }

    variables() {
        return new Set();
    }

    precedence() {
        return 100;
    }

    toString() {
        return this.value ? "T" : "F";
    }
}

class Not extends Proposition {
    constructor(operand) {
        super();
        this.operand = operand;
    }

    evaluate(assignment) {
        return !this.operand.evaluate(assignment);
    }

    variables() {
        return this.operand.variables();
    }

    precedence() {
        return 80;
    }

    toString(parentPrecedence = 0) {
        const text = this.operand.toString(this.precedence());
        const result = `~${text}`;
        return this.precedence() < parentPrecedence
            ? `(${result})`
            : result;
    }
}

class BinaryProposition extends Proposition {
    constructor(left, right) {
        super();
        this.left = left;
        this.right = right;
    }

    variables() {
        return new Set([
            ...this.left.variables(),
            ...this.right.variables()
        ]);
    }
}

class And extends BinaryProposition {
    evaluate(assignment) {
        return (
            this.left.evaluate(assignment) &&
            this.right.evaluate(assignment)
        );
    }

    precedence() {
        return 60;
    }

    toString(parentPrecedence = 0) {
        const result =
            `${this.left.toString(this.precedence())} AND ` +
            `${this.right.toString(this.precedence())}`;

        return this.precedence() < parentPrecedence
            ? `(${result})`
            : result;
    }
}

class Or extends BinaryProposition {
    evaluate(assignment) {
        return (
            this.left.evaluate(assignment) ||
            this.right.evaluate(assignment)
        );
    }

    precedence() {
        return 50;
    }

    toString(parentPrecedence = 0) {
        const result =
            `${this.left.toString(this.precedence())} OR ` +
            `${this.right.toString(this.precedence())}`;

        return this.precedence() < parentPrecedence
            ? `(${result})`
            : result;
    }
}

class Xor extends BinaryProposition {
    evaluate(assignment) {
        return (
            this.left.evaluate(assignment) !==
            this.right.evaluate(assignment)
        );
    }

    precedence() {
        return 40;
    }

    toString(parentPrecedence = 0) {
        const result =
            `${this.left.toString(this.precedence())} XOR ` +
            `${this.right.toString(this.precedence())}`;

        return this.precedence() < parentPrecedence
            ? `(${result})`
            : result;
    }
}

class Implies extends BinaryProposition {
    evaluate(assignment) {
        return logicalImplies(
            this.left.evaluate(assignment),
            this.right.evaluate(assignment)
        );
    }

    precedence() {
        return 30;
    }

    toString(parentPrecedence = 0) {
        const result =
            `${this.left.toString(this.precedence())} -> ` +
            `${this.right.toString(this.precedence())}`;

        return this.precedence() < parentPrecedence
            ? `(${result})`
            : result;
    }
}

class Iff extends BinaryProposition {
    evaluate(assignment) {
        return (
            this.left.evaluate(assignment) ===
            this.right.evaluate(assignment)
        );
    }

    precedence() {
        return 20;
    }

    toString(parentPrecedence = 0) {
        const result =
            `${this.left.toString(this.precedence())} <-> ` +
            `${this.right.toString(this.precedence())}`;

        return this.precedence() < parentPrecedence
            ? `(${result})`
            : result;
    }
}

// ============================================================
// 4. ASSIGNMENT GENERATION
// ============================================================

function generateAssignments(variableNames) {
    const names = [...new Set(variableNames)].sort();
    const assignments = [];
    const total = 2 ** names.length;

    for (let mask = 0; mask < total; mask += 1) {
        const assignment = {};

        names.forEach((name, index) => {
            const bit = names.length - index - 1;
            assignment[name] = Boolean((mask >> bit) & 1);
        });

        assignments.push(assignment);
    }

    return assignments;
}

function getVariableNames(expression) {
    return [...expression.variables()].sort();
}

// ============================================================
// 5. TRUTH TABLE AND EQUIVALENCE
// ============================================================

function truthTable(expression) {
    const names = getVariableNames(expression);

    return generateAssignments(names).map(assignment => ({
        assignment,
        result: expression.evaluate(assignment)
    }));
}

function areEquivalent(first, second) {
    const names = [
        ...new Set([
            ...getVariableNames(first),
            ...getVariableNames(second)
        ])
    ].sort();

    return generateAssignments(names).every(assignment => (
        first.evaluate(assignment) ===
        second.evaluate(assignment)
    ));
}

function findCounterexample(first, second) {
    const names = [
        ...new Set([
            ...getVariableNames(first),
            ...getVariableNames(second)
        ])
    ].sort();

    for (const assignment of generateAssignments(names)) {
        if (
            first.evaluate(assignment) !==
            second.evaluate(assignment)
        ) {
            return assignment;
        }
    }

    return null;
}

function printTruthTable(expression) {
    const names = getVariableNames(expression);

    console.log(`\nExpression: ${expression}`);
    console.log([...names, String(expression)].join(" | "));
    console.log("-".repeat(60));

    for (const row of truthTable(expression)) {
        const values = names.map(name => truth(row.assignment[name]));
        values.push(truth(row.result));
        console.log(values.join(" | "));
    }
}

// ============================================================
// 6. DE MORGAN'S LAWS
// ============================================================

function demonstrateDeMorgan() {
    printSection("De Morgan's laws");

    const P = new Variable("P");
    const Q = new Variable("Q");

    const firstLeft = new Not(new And(P, Q));
    const firstRight = new Or(new Not(P), new Not(Q));

    const secondLeft = new Not(new Or(P, Q));
    const secondRight = new And(new Not(P), new Not(Q));

    console.log("First law:");
    console.log(`  ${firstLeft}`);
    console.log(`  ${firstRight}`);
    console.log(`  Equivalent: ${areEquivalent(firstLeft, firstRight)}`);

    console.log("\nSecond law:");
    console.log(`  ${secondLeft}`);
    console.log(`  ${secondRight}`);
    console.log(`  Equivalent: ${areEquivalent(secondLeft, secondRight)}`);

    console.log(
        "\nDe Morgan transformation changes the connective while " +
        "negating each operand."
    );
}

// ============================================================
// 7. IMPLICATION EQUIVALENCES
// ============================================================

function demonstrateImplication() {
    printSection("Implication equivalences");

    const P = new Variable("P");
    const Q = new Variable("Q");

    const implication = new Implies(P, Q);
    const disjunction = new Or(new Not(P), Q);
    const contrapositive = new Implies(new Not(Q), new Not(P));
    const converse = new Implies(Q, P);
    const negatedImplication = new Not(implication);
    const failureCondition = new And(P, new Not(Q));

    console.log(`P -> Q: ${implication}`);
    console.log(`~P OR Q: ${disjunction}`);
    console.log(
        `Implication elimination: ${areEquivalent(implication, disjunction)}`
    );

    console.log(`\nContrapositive: ${contrapositive}`);
    console.log(
        `Equivalent to original: ${areEquivalent(implication, contrapositive)}`
    );

    console.log(`\nConverse: ${converse}`);
    console.log(
        `Equivalent to original: ${areEquivalent(implication, converse)}`
    );

    console.log(`\n~(P -> Q): ${negatedImplication}`);
    console.log(`P AND ~Q: ${failureCondition}`);
    console.log(
        `Negated implication equivalence: ` +
        `${areEquivalent(negatedImplication, failureCondition)}`
    );
}

// ============================================================
// 8. DISTRIBUTIVE LAWS
// ============================================================

function demonstrateDistributiveLaws() {
    printSection("Distributive laws");

    const P = new Variable("P");
    const Q = new Variable("Q");
    const R = new Variable("R");

    const andOverOrLeft = new And(P, new Or(Q, R));
    const andOverOrRight = new Or(
        new And(P, Q),
        new And(P, R)
    );

    const orOverAndLeft = new Or(P, new And(Q, R));
    const orOverAndRight = new And(
        new Or(P, Q),
        new Or(P, R)
    );

    console.log("AND over OR:");
    console.log(`  ${andOverOrLeft}`);
    console.log(`  ${andOverOrRight}`);
    console.log(
        `  Equivalent: ${areEquivalent(andOverOrLeft, andOverOrRight)}`
    );

    console.log("\nOR over AND:");
    console.log(`  ${orOverAndLeft}`);
    console.log(`  ${orOverAndRight}`);
    console.log(
        `  Equivalent: ${areEquivalent(orOverAndLeft, orOverAndRight)}`
    );
}

// ============================================================
// 9. ABSORPTION LAWS
// ============================================================

function demonstrateAbsorption() {
    printSection("Absorption laws");

    const P = new Variable("P");
    const Q = new Variable("Q");

    const firstLeft = new Or(P, new And(P, Q));
    const secondLeft = new And(P, new Or(P, Q));

    console.log("P OR (P AND Q) <-> P");
    console.log(`  Equivalent: ${areEquivalent(firstLeft, P)}`);

    console.log("P AND (P OR Q) <-> P");
    console.log(`  Equivalent: ${areEquivalent(secondLeft, P)}`);
}

// ============================================================
// 10. OTHER CLASSIC LAWS
// ============================================================

function demonstrateOtherLaws() {
    printSection("Other Boolean identities");

    const P = new Variable("P");
    const Q = new Variable("Q");

    const tests = [
        [
            "Double negation",
            new Not(new Not(P)),
            P
        ],
        [
            "Identity AND",
            new And(P, new Constant(true)),
            P
        ],
        [
            "Identity OR",
            new Or(P, new Constant(false)),
            P
        ],
        [
            "Domination AND",
            new And(P, new Constant(false)),
            new Constant(false)
        ],
        [
            "Domination OR",
            new Or(P, new Constant(true)),
            new Constant(true)
        ],
        [
            "Idempotent AND",
            new And(P, P),
            P
        ],
        [
            "Idempotent OR",
            new Or(P, P),
            P
        ],
        [
            "Complement AND",
            new And(P, new Not(P)),
            new Constant(false)
        ],
        [
            "Complement OR",
            new Or(P, new Not(P)),
            new Constant(true)
        ],
        [
            "Commutative AND",
            new And(P, Q),
            new And(Q, P)
        ],
        [
            "Commutative OR",
            new Or(P, Q),
            new Or(Q, P)
        ],
        [
            "Biconditional expansion",
            new Iff(P, Q),
            new Or(
                new And(P, Q),
                new And(new Not(P), new Not(Q))
            )
        ]
    ];

    for (const [name, first, second] of tests) {
        console.log(
            `${name.padEnd(28)} ` +
            `${areEquivalent(first, second) ? "PASS" : "FAIL"}`
        );
    }
}

// ============================================================
// 11. TAUTOLOGY, CONTRADICTION, CONTINGENCY
// ============================================================

function classifyExpression(expression) {
    const values = truthTable(expression).map(row => row.result);

    if (values.every(Boolean)) {
        return "tautology";
    }

    if (values.every(value => !value)) {
        return "contradiction";
    }

    return "contingency";
}

function demonstrateClassification() {
    printSection("Logical classification");

    const P = new Variable("P");
    const Q = new Variable("Q");

    const examples = [
        ["P OR ~P", new Or(P, new Not(P))],
        ["P AND ~P", new And(P, new Not(P))],
        ["P -> Q", new Implies(P, Q)],
        ["P <-> Q", new Iff(P, Q)]
    ];

    for (const [name, expression] of examples) {
        console.log(`${name.padEnd(12)} -> ${classifyExpression(expression)}`);
    }
}

// ============================================================
// 12. COUNTEREXAMPLE
// ============================================================

function demonstrateCounterexample() {
    printSection("Counterexample to a false equivalence");

    const P = new Variable("P");
    const Q = new Variable("Q");

    const implication = new Implies(P, Q);
    const converse = new Implies(Q, P);

    const counterexample = findCounterexample(implication, converse);

    console.log(`Original: ${implication}`);
    console.log(`Converse: ${converse}`);
    console.log(`Counterexample: ${JSON.stringify(counterexample)}`);

    if (counterexample) {
        console.log(
            `Original value: ${implication.evaluate(counterexample)}`
        );
        console.log(
            `Converse value: ${converse.evaluate(counterexample)}`
        );
    }
}

// ============================================================
// 13. PRACTICAL SECURITY CONDITION
// ============================================================

function demonstrateSecurityCondition() {
    printSection("Security-condition transformation");

    const authenticated = new Variable("Authenticated");
    const authorized = new Variable("Authorized");
    const suspended = new Variable("Suspended");

    const access = new And(
        new And(authenticated, authorized),
        new Not(suspended)
    );

    const denied = new Not(access);

    const equivalentDenied = new Or(
        new Or(
            new Not(authenticated),
            new Not(authorized)
        ),
        suspended
    );

    console.log(`Access: ${access}`);
    console.log(`Denied: ${denied}`);
    console.log(`De Morgan form: ${equivalentDenied}`);

    console.log(
        `Equivalent: ${areEquivalent(denied, equivalentDenied)}`
    );

    console.log(
        "\nLogical equivalence validates a transformation, but an " +
        "authorization system still requires correct identity, policy, " +
        "state management, and enforcement."
    );
}

// ============================================================
// 14. PRACTICAL QUERY CONDITION
// ============================================================

function demonstrateQueryCondition() {
    printSection("Query-style Boolean conditions");

    const ageEligible = new Variable("AgeEligible");
    const verified = new Variable("Verified");

    const original = new Not(
        new And(ageEligible, verified)
    );

    const transformed = new Or(
        new Not(ageEligible),
        new Not(verified)
    );

    console.log(`Original:   ${original}`);
    console.log(`Equivalent: ${transformed}`);
    console.log(`Verified:   ${areEquivalent(original, transformed)}`);
}

// ============================================================
// 15. RULE ENGINE
// ============================================================

class Rule {
    constructor(name, condition, result) {
        this.name = name;
        this.condition = condition;
        this.result = result;
    }

    fires(assignment) {
        return this.condition.evaluate(assignment);
    }
}

class RuleEngine {
    constructor(rules) {
        this.rules = [...rules];
    }

    evaluate(assignment) {
        return this.rules
            .filter(rule => rule.fires(assignment))
            .map(rule => ({
                rule: rule.name,
                result: rule.result.evaluate(assignment)
            }));
    }
}

function demonstrateRuleEngine() {
    printSection("Rule engine using logical expressions");

    const verified = new Variable("Verified");
    const premium = new Variable("Premium");
    const suspended = new Variable("Suspended");

    const rules = [
        new Rule(
            "Permit verified premium user",
            new And(
                new And(verified, premium),
                new Not(suspended)
            ),
            new Constant(true)
        ),
        new Rule(
            "Permit verified standard user",
            new And(
                new And(verified, new Not(premium)),
                new Not(suspended)
            ),
            new Constant(true)
        ),
        new Rule(
            "Deny suspended user",
            suspended,
            new Constant(false)
        )
    ];

    const engine = new RuleEngine(rules);

    const assignments = [
        { Verified: true, Premium: true, Suspended: false },
        { Verified: true, Premium: false, Suspended: false },
        { Verified: false, Premium: true, Suspended: false },
        { Verified: true, Premium: true, Suspended: true }
    ];

    for (const assignment of assignments) {
        console.log(
            JSON.stringify(assignment),
            "->",
            engine.evaluate(assignment)
        );
    }
}

// ============================================================
// 16. ASYNCHRONOUS EQUIVALENCE CHECK
// ============================================================

function equivalentAsync(first, second) {
    /*
     * The computation itself is synchronous, but returning a Promise
     * demonstrates how an equivalence checker could integrate with
     * asynchronous JavaScript applications such as web interfaces.
     */
    return Promise.resolve(areEquivalent(first, second));
}

async function demonstrateAsyncUsage() {
    printSection("Asynchronous application integration");

    const P = new Variable("P");
    const Q = new Variable("Q");

    const first = new Not(new And(P, Q));
    const second = new Or(new Not(P), new Not(Q));

    const result = await equivalentAsync(first, second);

    console.log(`Asynchronous equivalence result: ${result}`);
}

// ============================================================
// 17. PERFORMANCE CONSIDERATIONS
// ============================================================

function demonstrateComplexity() {
    printSection("Truth-table complexity");

    console.log("n variables -> 2^n assignments");

    for (let n = 1; n <= 12; n += 1) {
        console.log(
            `${String(n).padStart(2)} -> ${2 ** n}`
        );
    }

    console.log(
        "\nExhaustive equivalence checking grows exponentially with " +
        "the number of independent variables."
    );
}

// ============================================================
// 18. ERROR HANDLING
// ============================================================

function demonstrateValidation() {
    printSection("Validation and failure handling");

    const P = new Variable("P");

    try {
        P.evaluate({});
    } catch (error) {
        console.log(`Expected error: ${error.message}`);
    }

    const validAssignment = { P: true };
    console.log(
        `Valid assignment result: ${P.evaluate(validAssignment)}`
    );
}

// ============================================================
// 19. MAIN
// ============================================================

async function main() {
    printSection("LOGICAL EQUIVALENCE STUDY PROGRAM");

    demonstrateBasicOperators();

    const P = new Variable("P");
    const Q = new Variable("Q");

    console.log("\nSimple symbolic example:");
    console.log(`P: ${P}`);
    console.log(`Q: ${Q}`);
    console.log(`P AND Q: ${P.and(Q)}`);
    console.log(`P OR Q: ${P.or(Q)}`);
    console.log(`P -> Q: ${P.implies(Q)}`);

    demonstrateDeMorgan();
    demonstrateImplication();
    demonstrateDistributiveLaws();
    demonstrateAbsorption();
    demonstrateOtherLaws();
    demonstrateClassification();
    demonstrateCounterexample();
    demonstrateSecurityCondition();
    demonstrateQueryCondition();
    demonstrateRuleEngine();
    demonstrateComplexity();
    demonstrateValidation();
    await demonstrateAsyncUsage();

    printSection("Explicit truth table example");

    const expression = new Not(
        new And(P, Q)
    );

    printTruthTable(expression);

    console.log("\nStudy program completed.");
}

main().catch(error => {
    console.error("Program failed:", error);
    process.exitCode = 1;
});
