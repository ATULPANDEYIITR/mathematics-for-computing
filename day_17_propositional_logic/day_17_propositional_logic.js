/*
 * Propositional Logic in JavaScript
 *
 * Topics:
 *   AND, OR, NOT, implication, biconditional, precedence,
 *   truth tables, equivalence, logical laws, expression trees,
 *   parsing, validation, satisfiability, entailment, and practical policies.
 *
 * The file is executable in a modern JavaScript runtime such as Node.js.
 */

"use strict";

// =============================================================================
// 1. BOOLEAN PROPOSITIONS
// =============================================================================

console.log("=".repeat(80));
console.log("PROPOSITIONAL LOGIC");
console.log("=".repeat(80));

const P = true;
const Q = false;

console.log("P =", P);
console.log("Q =", Q);


// =============================================================================
// 2. CORE CONNECTIVES
// =============================================================================

function logicalAnd(p, q) {
    // P ∧ Q is true only when both propositions are true.
    return p && q;
}

function logicalOr(p, q) {
    // P ∨ Q is inclusive OR.
    return p || q;
}

function logicalNot(p) {
    // ¬P reverses the truth value.
    return !p;
}

function implies(p, q) {
    // P → Q is logically equivalent to ¬P ∨ Q.
    return !p || q;
}

function biconditional(p, q) {
    // P ↔ Q is true exactly when both values are equal.
    return p === q;
}

function xor(p, q) {
    // XOR differs from logical OR:
    // exactly one operand must be true.
    return p !== q;
}


// =============================================================================
// 3. TRUTH TABLE
// =============================================================================

console.log("\n" + "=".repeat(80));
console.log("CORE TRUTH TABLE");
console.log("=".repeat(80));

for (const p of [false, true]) {
    for (const q of [false, true]) {
        console.log({
            P: p,
            Q: q,
            NOT_P: logicalNot(p),
            "P_AND_Q": logicalAnd(p, q),
            "P_OR_Q": logicalOr(p, q),
            "P_IMPLIES_Q": implies(p, q),
            "P_IFF_Q": biconditional(p, q),
            "P_XOR_Q": xor(p, q)
        });
    }
}


// =============================================================================
// 4. PRECEDENCE
// =============================================================================

console.log("\n" + "=".repeat(80));
console.log("PRECEDENCE");
console.log("=".repeat(80));

/*
 * A conventional propositional precedence hierarchy is:
 *
 *   NOT
 *   AND
 *   OR
 *   IMPLICATION
 *   BICONDITIONAL
 *
 * JavaScript's native operators do not directly implement implication or
 * biconditional, so explicit functions and parentheses are preferable.
 */

const r = true;

const expressionA = (!P) || (Q && r);
const expressionB = ((!P) || Q) && r;

console.log("(NOT P) OR (Q AND R) =", expressionA);
console.log("(NOT P OR Q) AND R =", expressionB);

console.log("P -> (Q -> R) =", implies(P, implies(Q, r)));
console.log("(P -> Q) -> R =", implies(implies(P, Q), r));


// =============================================================================
// 5. TRUTH-TABLE GENERATOR
// =============================================================================

function booleanAssignments(variableNames) {
    /*
     * Generate every possible assignment.
     *
     * n Boolean variables produce 2^n assignments.
     */
    const assignments = [];

    function build(index, current) {
        if (index === variableNames.length) {
            assignments.push({ ...current });
            return;
        }

        const variable = variableNames[index];

        current[variable] = false;
        build(index + 1, current);

        current[variable] = true;
        build(index + 1, current);

        delete current[variable];
    }

    build(0, {});
    return assignments;
}

function truthTable(variableNames, evaluator) {
    return booleanAssignments(variableNames).map(assignment => ({
        ...assignment,
        result: Boolean(evaluator(assignment))
    }));
}

const table = truthTable(["P", "Q", "R"], values =>
    implies(values.P && values.Q, values.R)
);

console.log("\nTruth table for (P AND Q) -> R:");
console.table(table);


// =============================================================================
// 6. CLASSIFY FORMULAS
// =============================================================================

function classifyFormula(variableNames, evaluator) {
    const results = truthTable(variableNames, evaluator).map(row => row.result);

    if (results.every(Boolean)) {
        return "tautology";
    }

    if (results.every(value => !value)) {
        return "contradiction";
    }

    return "contingency";
}

console.log("\nFormula classifications:");

console.log(
    "P OR NOT P:",
    classifyFormula(["P"], values => values.P || !values.P)
);

console.log(
    "P AND NOT P:",
    classifyFormula(["P"], values => values.P && !values.P)
);

console.log(
    "P:",
    classifyFormula(["P"], values => values.P)
);


// =============================================================================
// 7. LOGICAL EQUIVALENCE
// =============================================================================

function equivalent(variableNames, first, second) {
    /*
     * Two formulas are equivalent if they have the same result under every
     * possible assignment.
     */
    return booleanAssignments(variableNames).every(assignment => {
        return Boolean(first(assignment)) === Boolean(second(assignment));
    });
}

console.log("\nLogical equivalence tests:");

console.log(
    "P -> Q == NOT P OR Q:",
    equivalent(
        ["P", "Q"],
        values => implies(values.P, values.Q),
        values => !values.P || values.Q
    )
);

console.log(
    "P <-> Q == (P -> Q) AND (Q -> P):",
    equivalent(
        ["P", "Q"],
        values => biconditional(values.P, values.Q),
        values =>
            implies(values.P, values.Q) &&
            implies(values.Q, values.P)
    )
);


// =============================================================================
// 8. LOGICAL LAWS
// =============================================================================

console.log("\n" + "=".repeat(80));
console.log("LOGICAL LAWS");
console.log("=".repeat(80));

for (const p of [false, true]) {
    for (const q of [false, true]) {
        // De Morgan's first law:
        // NOT (P AND Q) == NOT P OR NOT Q
        console.assert(
            !(p && q) === (!p || !q),
            "De Morgan's first law failed"
        );

        // De Morgan's second law:
        // NOT (P OR Q) == NOT P AND NOT Q
        console.assert(
            !(p || q) === (!p && !q),
            "De Morgan's second law failed"
        );

        // Absorption:
        // P OR (P AND Q) == P
        console.assert(
            (p || (p && q)) === p,
            "Absorption OR law failed"
        );

        // Absorption:
        // P AND (P OR Q) == P
        console.assert(
            (p && (p || q)) === p,
            "Absorption AND law failed"
        );
    }
}

console.log("De Morgan and absorption laws verified.");


// =============================================================================
// 9. IMPLICATION FORMS
// =============================================================================

function implicationForms(p, q) {
    return {
        original: implies(p, q),
        converse: implies(q, p),
        inverse: implies(!p, !q),
        contrapositive: implies(!q, !p)
    };
}

console.log("\nImplication forms:");

for (const p of [false, true]) {
    for (const q of [false, true]) {
        console.log(`P=${p}, Q=${q}`, implicationForms(p, q));
    }
}


// =============================================================================
// 10. ARGUMENT VALIDITY
// =============================================================================

function argumentIsValid(variableNames, premises, conclusion) {
    /*
     * An argument is valid if there is no assignment where every premise is
     * true and the conclusion is false.
     */
    return booleanAssignments(variableNames).every(assignment => {
        const premisesHold = premises.every(premise =>
            Boolean(premise(assignment))
        );

        return !premisesHold || Boolean(conclusion(assignment));
    });
}

const modusPonens = argumentIsValid(
    ["P", "Q"],
    [
        values => implies(values.P, values.Q),
        values => values.P
    ],
    values => values.Q
);

const invalidConverse = argumentIsValid(
    ["P", "Q"],
    [
        values => implies(values.P, values.Q),
        values => values.Q
    ],
    values => values.P
);

console.log("\nModus Ponens valid:", modusPonens);
console.log("Converse-style argument valid:", invalidConverse);


// =============================================================================
// 11. SATISFIABILITY
// =============================================================================

function satisfyingAssignments(variableNames, evaluator) {
    return booleanAssignments(variableNames).filter(
        assignment => Boolean(evaluator(assignment))
    );
}

const solutions = satisfyingAssignments(
    ["P", "Q", "R"],
    values => implies(values.P && values.Q, values.R)
);

console.log("\nNumber of satisfying assignments:", solutions.length);
console.table(solutions);


// =============================================================================
// 12. COUNTEREXAMPLE SEARCH
// =============================================================================

function findCounterexample(variableNames, first, second) {
    for (const assignment of booleanAssignments(variableNames)) {
        if (Boolean(first(assignment)) !== Boolean(second(assignment))) {
            return assignment;
        }
    }

    return null;
}

const counterexample = findCounterexample(
    ["P", "Q"],
    values => implies(values.P, values.Q),
    values => implies(values.Q, values.P)
);

console.log(
    "\nCounterexample to P -> Q == Q -> P:",
    counterexample
);


// =============================================================================
// 13. EXPRESSION TREE
// =============================================================================

class Literal {
    constructor(name, value) {
        this.name = name;
        this.value = Boolean(value);
    }

    evaluate() {
        return this.value;
    }
}

class NotNode {
    constructor(operand) {
        this.operand = operand;
    }

    evaluate() {
        return !this.operand.evaluate();
    }
}

class BinaryNode {
    constructor(left, operator, right) {
        this.left = left;
        this.operator = operator;
        this.right = right;
    }

    evaluate() {
        const leftValue = this.left.evaluate();
        const rightValue = this.right.evaluate();

        switch (this.operator) {
            case "AND":
                return leftValue && rightValue;
            case "OR":
                return leftValue || rightValue;
            case "IMPLIES":
                return !leftValue || rightValue;
            case "IFF":
                return leftValue === rightValue;
            default:
                throw new Error(`Unknown operator: ${this.operator}`);
        }
    }
}

const tree = new BinaryNode(
    new NotNode(new Literal("P", true)),
    "OR",
    new BinaryNode(
        new Literal("Q", false),
        "AND",
        new Literal("R", true)
    )
);

console.log("\nExpression tree result:", tree.evaluate());


// =============================================================================
// 14. PRACTICAL AUTHORIZATION
// =============================================================================

function canAccess(authenticated, administrator, owner) {
    /*
     * authenticated AND (administrator OR owner)
     *
     * Parentheses are explicit because policy expressions should not depend
     * on readers remembering host-language precedence.
     */
    return authenticated && (administrator || owner);
}

console.log("\nAuthorization examples:");

const accessCases = [
    { authenticated: false, administrator: true, owner: true },
    { authenticated: true, administrator: false, owner: false },
    { authenticated: true, administrator: false, owner: true },
    { authenticated: true, administrator: true, owner: false }
];

for (const scenario of accessCases) {
    console.log({
        ...scenario,
        access: canAccess(
            scenario.authenticated,
            scenario.administrator,
            scenario.owner
        )
    });
}


// =============================================================================
// 15. STRICT BOOLEAN VALIDATION
// =============================================================================

function requireBoolean(value, name) {
    /*
     * JavaScript has truthy and falsy values. A policy engine should sometimes
     * reject values such as "false", 0, null, and undefined rather than silently
     * interpreting them as Boolean policy decisions.
     */
    if (typeof value !== "boolean") {
        throw new TypeError(`${name} must be a Boolean`);
    }

    return value;
}

function secureAccessPolicy(
    authenticated,
    accountActive,
    mfaVerified,
    administrator,
    owner,
    emergencyLock
) {
    authenticated = requireBoolean(authenticated, "authenticated");
    accountActive = requireBoolean(accountActive, "accountActive");
    mfaVerified = requireBoolean(mfaVerified, "mfaVerified");
    administrator = requireBoolean(administrator, "administrator");
    owner = requireBoolean(owner, "owner");
    emergencyLock = requireBoolean(emergencyLock, "emergencyLock");

    return (
        authenticated &&
        accountActive &&
        mfaVerified &&
        (administrator || owner) &&
        !emergencyLock
    );
}

console.log(
    "\nSecure policy:",
    secureAccessPolicy(true, true, true, false, true, false)
);

try {
    secureAccessPolicy(true, "yes", true, false, true, false);
} catch (error) {
    console.log("Validation error:", error.message);
}


// =============================================================================
// 16. SYMBOLIC EXPRESSION CLASSES
// =============================================================================

class SymbolicExpression {
    evaluate(_assignment) {
        throw new Error("evaluate() must be implemented");
    }
}

class Variable extends SymbolicExpression {
    constructor(name) {
        super();
        this.name = name;
    }

    evaluate(assignment) {
        if (!(this.name in assignment)) {
            throw new Error(`Missing value for variable ${this.name}`);
        }

        if (typeof assignment[this.name] !== "boolean") {
            throw new TypeError(
                `Variable ${this.name} must have a Boolean value`
            );
        }

        return assignment[this.name];
    }

    toString() {
        return this.name;
    }
}

class UnaryNot extends SymbolicExpression {
    constructor(operand) {
        super();
        this.operand = operand;
    }

    evaluate(assignment) {
        return !this.operand.evaluate(assignment);
    }

    toString() {
        return `NOT (${this.operand})`;
    }
}

class BinaryExpression extends SymbolicExpression {
    constructor(left, operator, right) {
        super();
        this.left = left;
        this.operator = operator;
        this.right = right;
    }

    evaluate(assignment) {
        const left = this.left.evaluate(assignment);
        const right = this.right.evaluate(assignment);

        switch (this.operator) {
            case "AND":
                return left && right;
            case "OR":
                return left || right;
            case "IMPLIES":
                return !left || right;
            case "IFF":
                return left === right;
            default:
                throw new Error(`Unsupported operator: ${this.operator}`);
        }
    }

    toString() {
        const symbols = {
            AND: "AND",
            OR: "OR",
            IMPLIES: "->",
            IFF: "<->"
        };

        return `(${this.left} ${symbols[this.operator]} ${this.right})`;
    }
}

const p = new Variable("P");
const q = new Variable("Q");
const rVariable = new Variable("R");

const symbolicFormula = new BinaryExpression(
    new UnaryNot(p),
    "OR",
    new BinaryExpression(q, "AND", rVariable)
);

console.log("\nSymbolic formula:", symbolicFormula.toString());
console.log(
    "Evaluation:",
    symbolicFormula.evaluate({
        P: true,
        Q: false,
        R: true
    })
);


// =============================================================================
// 17. TOKENIZER
// =============================================================================

function tokenize(text) {
    const tokens = [];
    let index = 0;

    while (index < text.length) {
        const character = text[index];

        if (/\s/.test(character)) {
            index++;
            continue;
        }

        if (text.startsWith("<->", index)) {
            tokens.push("<->");
            index += 3;
            continue;
        }

        if (text.startsWith("->", index)) {
            tokens.push("->");
            index += 2;
            continue;
        }

        if (character === "(" || character === ")") {
            tokens.push(character);
            index++;
            continue;
        }

        if (/[A-Za-z_]/.test(character)) {
            const start = index;
            index++;

            while (
                index < text.length &&
                /[A-Za-z0-9_]/.test(text[index])
            ) {
                index++;
            }

            tokens.push(text.slice(start, index));
            continue;
        }

        throw new SyntaxError(`Unexpected character '${character}'`);
    }

    return tokens;
}

console.log("\nTokens:");
console.log(tokenize("NOT P OR Q AND R"));


// =============================================================================
// 18. RECURSIVE-DESCENT PARSER
// =============================================================================

class Parser {
    constructor(tokens) {
        this.tokens = tokens;
        this.position = 0;
    }

    current() {
        return this.tokens[this.position] ?? null;
    }

    consume(expected = null) {
        const token = this.current();

        if (token === null) {
            throw new SyntaxError("Unexpected end of expression");
        }

        if (
            expected !== null &&
            token.toUpperCase() !== expected.toUpperCase()
        ) {
            throw new SyntaxError(
                `Expected '${expected}', found '${token}'`
            );
        }

        this.position++;
        return token;
    }

    parse() {
        const expression = this.parseBiconditional();

        if (this.current() !== null) {
            throw new SyntaxError(
                `Unexpected token '${this.current()}'`
            );
        }

        return expression;
    }

    parseBiconditional() {
        let left = this.parseImplication();

        while (this.current() === "<->") {
            this.consume("<->");
            const right = this.parseImplication();
            left = new BinaryExpression(left, "IFF", right);
        }

        return left;
    }

    parseImplication() {
        const left = this.parseOr();

        /*
         * Recursive parsing of the right side makes implication right
         * associative:
         *
         * P -> Q -> R
         *
         * becomes:
         *
         * P -> (Q -> R)
         */
        if (this.current() === "->") {
            this.consume("->");
            const right = this.parseImplication();
            return new BinaryExpression(left, "IMPLIES", right);
        }

        return left;
    }

    parseOr() {
        let left = this.parseAnd();

        while (
            this.current() !== null &&
            this.current().toUpperCase() === "OR"
        ) {
            this.consume();
            const right = this.parseAnd();
            left = new BinaryExpression(left, "OR", right);
        }

        return left;
    }

    parseAnd() {
        let left = this.parseNot();

        while (
            this.current() !== null &&
            this.current().toUpperCase() === "AND"
        ) {
            this.consume();
            const right = this.parseNot();
            left = new BinaryExpression(left, "AND", right);
        }

        return left;
    }

    parseNot() {
        if (
            this.current() !== null &&
            this.current().toUpperCase() === "NOT"
        ) {
            this.consume();
            return new UnaryNot(this.parseNot());
        }

        return this.parseAtom();
    }

    parseAtom() {
        const token = this.current();

        if (token === null) {
            throw new SyntaxError("Expected an expression");
        }

        if (token === "(") {
            this.consume("(");
            const expression = this.parseBiconditional();

            if (this.current() !== ")") {
                throw new SyntaxError("Expected ')'");
            }

            this.consume(")");
            return expression;
        }

        if (
            token === ")" ||
            ["AND", "OR", "NOT", "->", "<->"].includes(token.toUpperCase())
        ) {
            throw new SyntaxError(`Unexpected token '${token}'`);
        }

        this.consume();
        return new Variable(token);
    }
}

function parseExpression(text) {
    return new Parser(tokenize(text)).parse();
}

const parsed = parseExpression(
    "(P OR Q) AND (NOT P OR R)"
);

console.log("\nParsed expression:");
console.log(parsed.toString());

console.log(
    "Parsed evaluation:",
    parsed.evaluate({
        P: false,
        Q: true,
        R: false
    })
);


// =============================================================================
// 19. PARSER TRUTH TABLE
// =============================================================================

function parsedTruthTable(expressionText, variables) {
    const expression = parseExpression(expressionText);

    return truthTable(
        variables,
        assignment => expression.evaluate(assignment)
    );
}

console.log("\nParsed formula truth table:");
console.table(
    parsedTruthTable(
        "(P OR Q) AND (NOT P OR R)",
        ["P", "Q", "R"]
    )
);


// =============================================================================
// 20. ENTAILMENT
// =============================================================================

function entails(variableNames, premise, conclusion) {
    /*
     * Premises entail a conclusion when there is no assignment satisfying all
     * premises while falsifying the conclusion.
     */
    return booleanAssignments(variableNames).every(assignment => {
        const premisesHold = premise(assignment);

        return !premisesHold || Boolean(conclusion(assignment));
    });
}

console.log("\nEntailment:");
console.log(
    "(P AND Q) entails P:",
    entails(
        ["P", "Q"],
        values => values.P && values.Q,
        values => values.P
    )
);

console.log(
    "P entails Q:",
    entails(
        ["P", "Q"],
        values => values.P,
        values => values.Q
    )
);


// =============================================================================
// 21. NECESSARY AND SUFFICIENT CONDITIONS
// =============================================================================

function isSufficient(p, q) {
    // P is sufficient for Q exactly when P -> Q is true.
    return implies(p, q);
}

function isNecessary(p, q) {
    /*
     * Q is necessary for P when P -> Q.
     *
     * The function is parameterized as:
     * p = condition whose requirement is being tested
     * q = required condition
     */
    return implies(p, q);
}

console.log("\nNecessary and sufficient examples:");
console.log("P sufficient for Q:", isSufficient(true, true));
console.log("Q necessary for P:", isNecessary(true, true));


// =============================================================================
// 22. SHORT-CIRCUIT BEHAVIOR
// =============================================================================

function shouldNotRun() {
    throw new Error("This function should not have been evaluated");
}

console.log("\nShort-circuit evaluation:");

const shortCircuitAnd = false && shouldNotRun();
const shortCircuitOr = true || shouldNotRun();

console.log("false && function =", shortCircuitAnd);
console.log("true || function =", shortCircuitOr);


// =============================================================================
// 23. PERFORMANCE
// =============================================================================

console.log("\n" + "=".repeat(80));
console.log("TRUTH-TABLE GROWTH");
console.log("=".repeat(80));

for (let variableCount = 1; variableCount <= 20; variableCount += 3) {
    const rows = 2 ** variableCount;
    console.log(
        `${variableCount} variables -> ${rows.toLocaleString()} assignments`
    );
}


// =============================================================================
// 24. REALISTIC ENTERPRISE POLICY
// =============================================================================

function enterpriseAccessPolicy({
    authenticated,
    accountActive,
    mfaVerified,
    administrator,
    resourceOwner,
    emergencyLock
}) {
    /*
     * Explicit policy:
     *
     * authenticated
     * AND accountActive
     * AND mfaVerified
     * AND (administrator OR resourceOwner)
     * AND NOT emergencyLock
     */
    for (const [name, value] of Object.entries({
        authenticated,
        accountActive,
        mfaVerified,
        administrator,
        resourceOwner,
        emergencyLock
    })) {
        requireBoolean(value, name);
    }

    return (
        authenticated &&
        accountActive &&
        mfaVerified &&
        (administrator || resourceOwner) &&
        !emergencyLock
    );
}

const scenarios = [
    {
        name: "Administrator",
        authenticated: true,
        accountActive: true,
        mfaVerified: true,
        administrator: true,
        resourceOwner: false,
        emergencyLock: false
    },
    {
        name: "Resource owner",
        authenticated: true,
        accountActive: true,
        mfaVerified: true,
        administrator: false,
        resourceOwner: true,
        emergencyLock: false
    },
    {
        name: "Emergency lock",
        authenticated: true,
        accountActive: true,
        mfaVerified: true,
        administrator: true,
        resourceOwner: true,
        emergencyLock: true
    },
    {
        name: "Unauthenticated",
        authenticated: false,
        accountActive: true,
        mfaVerified: true,
        administrator: true,
        resourceOwner: false,
        emergencyLock: false
    }
];

console.log("\nEnterprise policy:");

for (const scenario of scenarios) {
    const { name, ...policy } = scenario;

    console.log(
        name,
        "->",
        enterpriseAccessPolicy(policy)
    );
}


// =============================================================================
// 25. ASSERTION-BASED SELF TESTS
// =============================================================================

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

assert(logicalAnd(true, true) === true, "AND");
assert(logicalAnd(true, false) === false, "AND");
assert(logicalOr(false, false) === false, "OR");
assert(logicalOr(true, false) === true, "OR");
assert(logicalNot(true) === false, "NOT");
assert(implies(false, false) === true, "implication");
assert(implies(false, true) === true, "implication");
assert(implies(true, false) === false, "implication");
assert(implies(true, true) === true, "implication");
assert(biconditional(false, false) === true, "biconditional");
assert(biconditional(false, true) === false, "biconditional");
assert(biconditional(true, false) === false, "biconditional");
assert(biconditional(true, true) === true, "biconditional");

for (const assignment of booleanAssignments(["P", "Q"])) {
    assert(
        implies(assignment.P, assignment.Q) ===
            (!assignment.P || assignment.Q),
        "implication equivalence"
    );

    assert(
        biconditional(assignment.P, assignment.Q) ===
            (
                implies(assignment.P, assignment.Q) &&
                implies(assignment.Q, assignment.P)
            ),
        "biconditional equivalence"
    );
}

console.log("\nAll JavaScript propositional-logic tests passed.");


// =============================================================================
// 26. END
// =============================================================================

console.log("\n" + "=".repeat(80));
console.log("END OF PROPOSITIONAL LOGIC STUDY");
console.log("=".repeat(80));
