/*
 * Truth Tables: Construction, Tautologies, Contradictions, and Contingencies
 *
 * A self-contained JavaScript study program for propositional logic.
 *
 * Supported concepts:
 *   - Boolean propositions
 *   - NOT, AND, OR, XOR
 *   - implication and biconditional
 *   - truth-table construction
 *   - tautologies, contradictions, contingencies
 *   - formula evaluation
 *   - logical equivalence
 *   - satisfiability
 *   - counterexamples
 *   - argument validity
 *   - canonical DNF and CNF
 *   - parser and abstract syntax tree
 *   - bit-mask truth vectors
 *   - JavaScript-specific implementation considerations
 *
 * Run with:
 *   node truth_tables.js
 */


// -----------------------------------------------------------------------------
// 1. Basic logical operators
// -----------------------------------------------------------------------------

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

function logicalImplies(antecedent, consequent) {
    // Material implication is false only when antecedent is true
    // and consequent is false.
    return !antecedent || consequent;
}

function logicalIff(left, right) {
    return left === right;
}

function demonstrateBasicOperators() {
    console.log("\n" + "=".repeat(78));
    console.log("1. BASIC LOGICAL OPERATORS");
    console.log("=".repeat(78));

    console.log("p   q   ¬p  p∧q p∨q p⊕q p→q p↔q");

    for (const p of [false, true]) {
        for (const q of [false, true]) {
            console.log(
                `${p ? "T" : "F"}   ` +
                `${q ? "T" : "F"}   ` +
                `${!p ? "T" : "F"}   ` +
                `${p && q ? "T" : "F"}   ` +
                `${p || q ? "T" : "F"}   ` +
                `${p !== q ? "T" : "F"}   ` +
                `${logicalImplies(p, q) ? "T" : "F"}   ` +
                `${p === q ? "T" : "F"}`
            );
        }
    }

    console.log("\nJavaScript note:");
    console.log(
        "Use strict boolean values for propositional logic. " +
        "Do not rely on truthy/falsy coercion when teaching or implementing " +
        "formal Boolean semantics."
    );
}


// -----------------------------------------------------------------------------
// 2. Generate all truth assignments
// -----------------------------------------------------------------------------

function generateAssignments(variables) {
    if (variables.length === 0) {
        return [{}];
    }

    const assignments = [];
    const rowCount = 2 ** variables.length;

    for (let row = 0; row < rowCount; row += 1) {
        const assignment = {};

        variables.forEach((variable, index) => {
            const shift = variables.length - index - 1;
            assignment[variable] = Boolean((row >> shift) & 1);
        });

        assignments.push(assignment);
    }

    return assignments;
}


function printTruthTable(variables, expressionName, evaluator) {
    const rows = generateAssignments(variables);

    console.log("\n" + [...variables, expressionName].join(" | "));
    console.log("-".repeat(
        variables.reduce((sum, variable) => sum + variable.length + 3, 0) +
        expressionName.length
    ));

    for (const assignment of rows) {
        const values = variables.map(
            variable => assignment[variable] ? "T" : "F"
        );

        values.push(evaluator(assignment) ? "T" : "F");
        console.log(values.join(" | "));
    }

    return rows;
}


function demonstrateTruthTableConstruction() {
    console.log("\n" + "=".repeat(78));
    console.log("2. TRUTH-TABLE CONSTRUCTION");
    console.log("=".repeat(78));

    const variables = ["p", "q"];

    console.log("\nExpression: p ∧ (p → q)");

    printTruthTable(
        variables,
        "p ∧ (p → q)",
        assignment =>
            assignment.p &&
            logicalImplies(assignment.p, assignment.q)
    );

    console.log("\nRow-count rule:");

    for (let variableCount = 0; variableCount <= 8; variableCount += 1) {
        console.log(
            `${variableCount} variable(s): ${2 ** variableCount} row(s)`
        );
    }
}


// -----------------------------------------------------------------------------
// 3. Classification
// -----------------------------------------------------------------------------

function classifyTruthValues(values) {
    if (values.every(Boolean)) {
        return "tautology";
    }

    if (values.every(value => !value)) {
        return "contradiction";
    }

    return "contingency";
}


function classifyExpression(variables, evaluator) {
    const values = generateAssignments(variables).map(evaluator);

    return {
        classification: classifyTruthValues(values),
        values
    };
}


function demonstrateClassification() {
    console.log("\n" + "=".repeat(78));
    console.log("3. FORMULA CLASSIFICATION");
    console.log("=".repeat(78));

    const examples = [
        {
            name: "p ∨ ¬p",
            variables: ["p"],
            evaluator: a => a.p || !a.p
        },
        {
            name: "p ∧ ¬p",
            variables: ["p"],
            evaluator: a => a.p && !a.p
        },
        {
            name: "p ∧ q",
            variables: ["p", "q"],
            evaluator: a => a.p && a.q
        },
        {
            name: "(p → q) ↔ (¬p ∨ q)",
            variables: ["p", "q"],
            evaluator: a =>
                logicalImplies(a.p, a.q) === (!a.p || a.q)
        }
    ];

    for (const example of examples) {
        const result = classifyExpression(
            example.variables,
            example.evaluator
        );

        console.log(
            `${example.name.padEnd(35)} ` +
            `${result.classification.padEnd(15)} ` +
            result.values.map(value => value ? "T" : "F").join("")
        );
    }
}


// -----------------------------------------------------------------------------
// 4. Formula classes
// -----------------------------------------------------------------------------

class Formula {
    evaluate(_assignment) {
        throw new Error("Formula.evaluate must be implemented");
    }

    variables() {
        throw new Error("Formula.variables must be implemented");
    }

    toString() {
        throw new Error("Formula.toString must be implemented");
    }
}


class Variable extends Formula {
    constructor(name) {
        super();
        this.name = name;
    }

    evaluate(assignment) {
        if (!(this.name in assignment)) {
            throw new Error(`Missing truth value for variable ${this.name}`);
        }

        return assignment[this.name];
    }

    variables() {
        return new Set([this.name]);
    }

    toString() {
        return this.name;
    }
}


class Not extends Formula {
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

    toString() {
        return `¬(${this.operand})`;
    }
}


class BinaryFormula extends Formula {
    constructor(left, operator, right) {
        super();
        this.left = left;
        this.operator = operator;
        this.right = right;
    }

    evaluate(assignment) {
        const leftValue = this.left.evaluate(assignment);
        const rightValue = this.right.evaluate(assignment);

        switch (this.operator) {
            case "∧":
                return leftValue && rightValue;
            case "∨":
                return leftValue || rightValue;
            case "⊕":
                return leftValue !== rightValue;
            case "→":
                return logicalImplies(leftValue, rightValue);
            case "↔":
                return leftValue === rightValue;
            default:
                throw new Error(`Unsupported operator: ${this.operator}`);
        }
    }

    variables() {
        return new Set([
            ...this.left.variables(),
            ...this.right.variables()
        ]);
    }

    toString() {
        return `(${this.left} ${this.operator} ${this.right})`;
    }
}


const Var = name => new Variable(name);
const And = (left, right) => new BinaryFormula(left, "∧", right);
const Or = (left, right) => new BinaryFormula(left, "∨", right);
const Xor = (left, right) => new BinaryFormula(left, "⊕", right);
const Implies = (left, right) => new BinaryFormula(left, "→", right);
const Iff = (left, right) => new BinaryFormula(left, "↔", right);


function formulaVariables(formula) {
    return [...formula.variables()].sort();
}


function demonstrateFormulaTree() {
    console.log("\n" + "=".repeat(78));
    console.log("4. STRUCTURAL FORMULAS");
    console.log("=".repeat(78));

    const p = Var("p");
    const q = Var("q");
    const r = Var("r");

    const formula = And(p, Or(q, new Not(r)));

    console.log(`Formula: ${formula}`);

    printTruthTable(
        formulaVariables(formula),
        formula.toString(),
        assignment => formula.evaluate(assignment)
    );
}


// -----------------------------------------------------------------------------
// 5. Equivalence
// -----------------------------------------------------------------------------

function logicallyEquivalent(first, second) {
    const variables = [
        ...new Set([
            ...first.variables(),
            ...second.variables()
        ])
    ].sort();

    return generateAssignments(variables).every(assignment =>
        first.evaluate(assignment) === second.evaluate(assignment)
    );
}


function findCounterexample(first, second) {
    const variables = [
        ...new Set([
            ...first.variables(),
            ...second.variables()
        ])
    ].sort();

    for (const assignment of generateAssignments(variables)) {
        if (first.evaluate(assignment) !== second.evaluate(assignment)) {
            return assignment;
        }
    }

    return null;
}


function demonstrateEquivalence() {
    console.log("\n" + "=".repeat(78));
    console.log("5. LOGICAL EQUIVALENCE");
    console.log("=".repeat(78));

    const p = Var("p");
    const q = Var("q");

    const implication = Implies(p, q);
    const replacement = Or(new Not(p), q);

    console.log(`${implication} ≡ ${replacement}`);
    console.log(`Equivalent: ${logicallyEquivalent(implication, replacement)}`);

    const firstDeMorgan = new Not(And(p, q));
    const secondDeMorgan = Or(new Not(p), new Not(q));

    console.log(`${firstDeMorgan} ≡ ${secondDeMorgan}`);
    console.log(
        `Equivalent: ${logicallyEquivalent(firstDeMorgan, secondDeMorgan)}`
    );

    console.log(
        "Counterexample for p and q:",
        findCounterexample(p, q)
    );
}


// -----------------------------------------------------------------------------
// 6. Satisfiability
// -----------------------------------------------------------------------------

function satisfyingAssignments(formula) {
    const variables = formulaVariables(formula);

    return generateAssignments(variables)
        .filter(assignment => formula.evaluate(assignment));
}


function falsifyingAssignments(formula) {
    const variables = formulaVariables(formula);

    return generateAssignments(variables)
        .filter(assignment => !formula.evaluate(assignment));
}


function demonstrateSatisfiability() {
    console.log("\n" + "=".repeat(78));
    console.log("6. SATISFIABILITY");
    console.log("=".repeat(78));

    const p = Var("p");
    const q = Var("q");

    const examples = [
        And(p, q),
        Or(p, new Not(p)),
        And(p, new Not(p))
    ];

    for (const formula of examples) {
        const satisfying = satisfyingAssignments(formula);

        console.log(`\nFormula: ${formula}`);
        console.log(`Satisfiable: ${satisfying.length > 0}`);
        console.log("Satisfying assignments:", satisfying);
    }
}


// -----------------------------------------------------------------------------
// 7. Canonical DNF and CNF
// -----------------------------------------------------------------------------

function canonicalDNF(formula) {
    const variables = formulaVariables(formula);
    const terms = [];

    for (const assignment of generateAssignments(variables)) {
        if (formula.evaluate(assignment)) {
            const literals = variables.map(variable =>
                assignment[variable] ? variable : `¬${variable}`
            );

            terms.push(`(${literals.join(" ∧ ")})`);
        }
    }

    return terms.length === 0 ? "⊥" : terms.join(" ∨ ");
}


function canonicalCNF(formula) {
    const variables = formulaVariables(formula);
    const clauses = [];

    for (const assignment of generateAssignments(variables)) {
        if (!formula.evaluate(assignment)) {
            const literals = variables.map(variable =>
                assignment[variable] ? `¬${variable}` : variable
            );

            clauses.push(`(${literals.join(" ∨ ")})`);
        }
    }

    return clauses.length === 0 ? "⊤" : clauses.join(" ∧ ");
}


function demonstrateNormalForms() {
    console.log("\n" + "=".repeat(78));
    console.log("7. CANONICAL NORMAL FORMS");
    console.log("=".repeat(78));

    const p = Var("p");
    const q = Var("q");
    const formula = And(p, Or(new Not(p), q));

    console.log(`Formula: ${formula}`);
    console.log(`Canonical DNF: ${canonicalDNF(formula)}`);
    console.log(`Canonical CNF: ${canonicalCNF(formula)}`);
}


// -----------------------------------------------------------------------------
// 8. Argument validity
// -----------------------------------------------------------------------------

function argumentIsValid(premises, conclusion) {
    const variableSet = new Set(conclusion.variables());

    for (const premise of premises) {
        for (const variable of premise.variables()) {
            variableSet.add(variable);
        }
    }

    const variables = [...variableSet].sort();

    for (const assignment of generateAssignments(variables)) {
        const premisesTrue = premises.every(
            premise => premise.evaluate(assignment)
        );

        if (premisesTrue && !conclusion.evaluate(assignment)) {
            return false;
        }
    }

    return true;
}


function findArgumentCounterexample(premises, conclusion) {
    const variableSet = new Set(conclusion.variables());

    for (const premise of premises) {
        for (const variable of premise.variables()) {
            variableSet.add(variable);
        }
    }

    for (const assignment of generateAssignments([...variableSet].sort())) {
        if (
            premises.every(premise => premise.evaluate(assignment)) &&
            !conclusion.evaluate(assignment)
        ) {
            return assignment;
        }
    }

    return null;
}


function demonstrateArgumentValidity() {
    console.log("\n" + "=".repeat(78));
    console.log("8. ARGUMENT VALIDITY");
    console.log("=".repeat(78));

    const p = Var("p");
    const q = Var("q");

    const validPremises = [
        Implies(p, q),
        p
    ];

    console.log("Argument:");
    console.log("  p → q");
    console.log("  p");
    console.log("  Therefore q");

    console.log(
        "Valid:",
        argumentIsValid(validPremises, q)
    );

    const invalidPremises = [
        Implies(p, q),
        q
    ];

    console.log("\nArgument:");
    console.log("  p → q");
    console.log("  q");
    console.log("  Therefore p");

    console.log(
        "Valid:",
        argumentIsValid(invalidPremises, p)
    );

    console.log(
        "Counterexample:",
        findArgumentCounterexample(invalidPremises, p)
    );
}


// -----------------------------------------------------------------------------
// 9. Bit-mask truth vectors
// -----------------------------------------------------------------------------
//
// A Boolean truth table can be represented as a bit sequence.
// For n variables there are 2^n rows.
//
// Bitwise operations allow compact manipulation of all rows:
//
//   AND -> &
//   OR  -> |
//   XOR -> ^
//   NOT -> XOR with an all-ones mask
//
// JavaScript bitwise operators work on signed 32-bit integers, so this
// demonstration intentionally limits the vector to at most 30 rows.
// BigInt is used for larger truth vectors.
// -----------------------------------------------------------------------------

class TruthVector {
    constructor(variableCount, bits) {
        if (!Number.isInteger(variableCount) || variableCount < 0) {
            throw new Error("Variable count must be a non-negative integer");
        }

        const rowCount = 2 ** variableCount;

        if (rowCount > 30) {
            throw new Error(
                "This Number-based vector supports at most 30 rows"
            );
        }

        this.variableCount = variableCount;
        this.rowCount = rowCount;
        this.mask = 2 ** rowCount - 1;
        this.bits = bits & this.mask;
    }

    static fromValues(values) {
        if (values.length === 0) {
            throw new Error("Truth vector cannot be empty");
        }

        if ((values.length & (values.length - 1)) !== 0) {
            throw new Error(
                "Truth vector length must be a power of two"
            );
        }

        let bits = 0;

        values.forEach((value, index) => {
            if (value) {
                bits |= 1 << index;
            }
        });

        const variableCount = Math.log2(values.length);

        return new TruthVector(variableCount, bits);
    }

    assertCompatible(other) {
        if (this.variableCount !== other.variableCount) {
            throw new Error("Truth vectors have different sizes");
        }
    }

    and(other) {
        this.assertCompatible(other);
        return new TruthVector(
            this.variableCount,
            this.bits & other.bits
        );
    }

    or(other) {
        this.assertCompatible(other);
        return new TruthVector(
            this.variableCount,
            this.bits | other.bits
        );
    }

    xor(other) {
        this.assertCompatible(other);
        return new TruthVector(
            this.variableCount,
            this.bits ^ other.bits
        );
    }

    not() {
        return new TruthVector(
            this.variableCount,
            (~this.bits) & this.mask
        );
    }

    implies(other) {
        return this.not().or(other);
    }

    values() {
        return Array.from(
            { length: this.rowCount },
            (_, index) => Boolean(this.bits & (1 << index))
        );
    }

    toString() {
        return this.values()
            .map(value => value ? "T" : "F")
            .join("");
    }
}


function demonstrateBitVectors() {
    console.log("\n" + "=".repeat(78));
    console.log("9. BIT-MASK TRUTH VECTORS");
    console.log("=".repeat(78));

    const p = TruthVector.fromValues([
        false, false, true, true
    ]);

    const q = TruthVector.fromValues([
        false, true, false, true
    ]);

    console.log(`p     = ${p}`);
    console.log(`q     = ${q}`);
    console.log(`p ∧ q = ${p.and(q)}`);
    console.log(`p ∨ q = ${p.or(q)}`);
    console.log(`¬p    = ${p.not()}`);
    console.log(`p → q = ${p.implies(q)}`);
}


// -----------------------------------------------------------------------------
// 10. Advanced asynchronous example
// -----------------------------------------------------------------------------
//
// Truth-table rows can be processed asynchronously in real applications,
// for example when a formula evaluation depends on external services.
// Here the evaluator is local, but Promise-based execution demonstrates the
// event-driven structure without requiring a package or network connection.
// -----------------------------------------------------------------------------

async function evaluateRowsAsynchronously(variables, evaluator) {
    const assignments = generateAssignments(variables);

    const results = await Promise.all(
        assignments.map(async assignment => ({
            assignment,
            value: Boolean(evaluator(assignment))
        }))
    );

    return results;
}


async function demonstrateAsyncEvaluation() {
    console.log("\n" + "=".repeat(78));
    console.log("10. ASYNCHRONOUS TRUTH-TABLE EVALUATION");
    console.log("=".repeat(78));

    const p = Var("p");
    const q = Var("q");
    const formula = Implies(p, q);

    const rows = await evaluateRowsAsynchronously(
        ["p", "q"],
        assignment => formula.evaluate(assignment)
    );

    for (const row of rows) {
        console.log(row);
    }
}


// -----------------------------------------------------------------------------
// 11. JavaScript edge cases
// -----------------------------------------------------------------------------

function demonstrateJavaScriptEdgeCases() {
    console.log("\n" + "=".repeat(78));
    console.log("11. JAVASCRIPT EDGE CASES");
    console.log("=".repeat(78));

    console.log("\nStrict Boolean semantics:");
    console.log(`true && false = ${true && false}`);
    console.log(`Boolean(1) = ${Boolean(1)}`);
    console.log(`Boolean(0) = ${Boolean(0)}`);

    console.log("\nDo not confuse equality with assignment:");
    const left = true;
    const right = true;
    console.log(`left === right = ${left === right}`);

    console.log("\nShort-circuit behavior:");
    let evaluated = false;

    false && (() => {
        evaluated = true;
        return true;
    })();

    console.log(`Right side evaluated after false && ...: ${evaluated}`);

    console.log("\nBigInt can represent larger bit vectors:");
    const largeMask = (1n << 40n) - 1n;
    console.log(`40-bit mask: ${largeMask.toString(2).length} bits`);
}


// -----------------------------------------------------------------------------
// 12. Complexity demonstration
// -----------------------------------------------------------------------------

function demonstrateComplexity() {
    console.log("\n" + "=".repeat(78));
    console.log("12. COMPLEXITY OF EXHAUSTIVE TRUTH TABLES");
    console.log("=".repeat(78));

    for (let n = 0; n <= 20; n += 1) {
        console.log(
            `n=${String(n).padStart(2, " ")} -> ` +
            `${String(2 ** n).padStart(8, " ")} rows`
        );
    }

    console.log(
        "\nThe exponential row count is the principal scalability limitation."
    );
}


// -----------------------------------------------------------------------------
// 13. Run complete study
// -----------------------------------------------------------------------------

async function main() {
    console.log("=".repeat(78));
    console.log("TRUTH TABLES: PROPOSITIONAL LOGIC STUDY PROGRAM");
    console.log("=".repeat(78));

    demonstrateBasicOperators();
    demonstrateTruthTableConstruction();
    demonstrateClassification();
    demonstrateFormulaTree();
    demonstrateEquivalence();
    demonstrateSatisfiability();
    demonstrateNormalForms();
    demonstrateArgumentValidity();
    demonstrateBitVectors();
    await demonstrateAsyncEvaluation();
    demonstrateJavaScriptEdgeCases();
    demonstrateComplexity();

    console.log("\n" + "=".repeat(78));
    console.log("END OF STUDY PROGRAM");
    console.log("=".repeat(78));
}


main().catch(error => {
    console.error("Program failed:", error.message);
    process.exitCode = 1;
});
