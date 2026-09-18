/*
 * Truth Tables: Construction, Tautologies, Contradictions, and Contingencies
 *
 * C++17 case study:
 * A rule-validation engine for a security access-control system.
 *
 * The system models:
 *
 *   A = employee has a valid badge
 *   B = employee has completed required training
 *   C = request originates from an approved network
 *   D = request is during an allowed operating period
 *
 * Access policy:
 *
 *   (A AND B AND C) OR (A AND B AND D)
 *
 * The program demonstrates how propositional logic and truth tables can be
 * used to validate rules, detect contradictions, find counterexamples,
 * compare equivalent policies, and reason about policy changes.
 *
 * Compile:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic truth_tables.cpp -o truth_tables
 *
 * Run:
 *   ./truth_tables
 */

#include <algorithm>
#include <array>
#include <bitset>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using Assignment = std::map<char, bool>;


// -----------------------------------------------------------------------------
// 1. Fundamental logical operators
// -----------------------------------------------------------------------------

bool logical_not(bool value) {
    return !value;
}

bool logical_and(bool left, bool right) {
    return left && right;
}

bool logical_or(bool left, bool right) {
    return left || right;
}

bool logical_xor(bool left, bool right) {
    return left != right;
}

bool logical_implies(bool antecedent, bool consequent) {
    // Material implication p -> q is equivalent to !p || q.
    return !antecedent || consequent;
}

bool logical_iff(bool left, bool right) {
    return left == right;
}


// -----------------------------------------------------------------------------
// 2. Formula abstraction
// -----------------------------------------------------------------------------

class Formula {
public:
    virtual ~Formula() = default;

    virtual bool evaluate(const Assignment& assignment) const = 0;

    virtual std::set<char> variables() const = 0;

    virtual std::string name() const = 0;
};


class Variable final : public Formula {
private:
    char variable_;

public:
    explicit Variable(char variable)
        : variable_(variable) {
        if (!std::isalpha(static_cast<unsigned char>(variable_))) {
            throw std::invalid_argument(
                "Variable must be an alphabetic character."
            );
        }
    }

    bool evaluate(const Assignment& assignment) const override {
        const auto iterator = assignment.find(variable_);

        if (iterator == assignment.end()) {
            throw std::invalid_argument(
                std::string("Missing value for variable ") + variable_
            );
        }

        return iterator->second;
    }

    std::set<char> variables() const override {
        return {variable_};
    }

    std::string name() const override {
        return std::string(1, variable_);
    }
};


class NotFormula final : public Formula {
private:
    const Formula& operand_;

public:
    explicit NotFormula(const Formula& operand)
        : operand_(operand) {}

    bool evaluate(const Assignment& assignment) const override {
        return !operand_.evaluate(assignment);
    }

    std::set<char> variables() const override {
        return operand_.variables();
    }

    std::string name() const override {
        return "NOT(" + operand_.name() + ")";
    }
};


class BinaryFormula final : public Formula {
private:
    const Formula& left_;
    const Formula& right_;
    char operation_;

public:
    BinaryFormula(
        const Formula& left,
        char operation,
        const Formula& right
    )
        : left_(left),
          right_(right),
          operation_(operation) {

        const std::string validOperations = "&|^>=";

        if (validOperations.find(operation_) == std::string::npos) {
            throw std::invalid_argument("Unsupported logical operator.");
        }
    }

    bool evaluate(const Assignment& assignment) const override {
        const bool leftValue = left_.evaluate(assignment);
        const bool rightValue = right_.evaluate(assignment);

        switch (operation_) {
            case '&':
                return leftValue && rightValue;

            case '|':
                return leftValue || rightValue;

            case '^':
                return leftValue != rightValue;

            case '>':
                return logical_implies(leftValue, rightValue);

            case '=':
                return leftValue == rightValue;

            default:
                throw std::logic_error("Unexpected operator.");
        }
    }

    std::set<char> variables() const override {
        std::set<char> result = left_.variables();

        const std::set<char> rightVariables = right_.variables();

        result.insert(
            rightVariables.begin(),
            rightVariables.end()
        );

        return result;
    }

    std::string name() const override {
        std::string operation;

        switch (operation_) {
            case '&':
                operation = " AND ";
                break;
            case '|':
                operation = " OR ";
                break;
            case '^':
                operation = " XOR ";
                break;
            case '>':
                operation = " -> ";
                break;
            case '=':
                operation = " <-> ";
                break;
            default:
                operation = " ? ";
        }

        return "(" + left_.name() + operation + right_.name() + ")";
    }
};


// -----------------------------------------------------------------------------
// 3. Truth-table row generation
// -----------------------------------------------------------------------------

std::vector<char> sortedVariables(const Formula& formula) {
    const std::set<char> variableSet = formula.variables();

    return std::vector<char>(
        variableSet.begin(),
        variableSet.end()
    );
}


std::vector<Assignment> generateAssignments(
    const std::vector<char>& variables
) {
    if (variables.size() >= sizeof(std::size_t) * 8) {
        throw std::overflow_error(
            "Too many variables for exhaustive enumeration."
        );
    }

    const std::size_t rowCount =
        static_cast<std::size_t>(1) << variables.size();

    std::vector<Assignment> assignments;
    assignments.reserve(rowCount);

    for (std::size_t row = 0; row < rowCount; ++row) {
        Assignment assignment;

        for (std::size_t index = 0; index < variables.size(); ++index) {
            const std::size_t shift =
                variables.size() - index - 1;

            assignment[variables[index]] =
                ((row >> shift) & 1U) != 0;
        }

        assignments.push_back(assignment);
    }

    return assignments;
}


void printAssignment(
    const Assignment& assignment,
    const std::vector<char>& variables
) {
    for (char variable : variables) {
        std::cout
            << std::setw(4)
            << (assignment.at(variable) ? 'T' : 'F');
    }
}


// -----------------------------------------------------------------------------
// 4. Formula classification
// -----------------------------------------------------------------------------

enum class FormulaClassification {
    Tautology,
    Contradiction,
    Contingency
};


std::string classificationName(FormulaClassification classification) {
    switch (classification) {
        case FormulaClassification::Tautology:
            return "tautology";

        case FormulaClassification::Contradiction:
            return "contradiction";

        case FormulaClassification::Contingency:
            return "contingency";
    }

    return "unknown";
}


FormulaClassification classifyFormula(
    const Formula& formula
) {
    const std::vector<char> variables = sortedVariables(formula);
    const std::vector<Assignment> assignments =
        generateAssignments(variables);

    bool foundTrue = false;
    bool foundFalse = false;

    for (const Assignment& assignment : assignments) {
        if (formula.evaluate(assignment)) {
            foundTrue = true;
        } else {
            foundFalse = true;
        }

        if (foundTrue && foundFalse) {
            return FormulaClassification::Contingency;
        }
    }

    if (foundTrue) {
        return FormulaClassification::Tautology;
    }

    return FormulaClassification::Contradiction;
}


// -----------------------------------------------------------------------------
// 5. Complete truth-table printer
// -----------------------------------------------------------------------------

void printTruthTable(const Formula& formula) {
    const std::vector<char> variables = sortedVariables(formula);

    std::cout << "\n" << formula.name() << "\n\n";

    for (char variable : variables) {
        std::cout << std::setw(4) << variable;
    }

    std::cout << std::setw(8) << "RESULT\n";

    std::cout << std::string(
        variables.size() * 4 + 8,
        '-'
    ) << "\n";

    const std::vector<Assignment> assignments =
        generateAssignments(variables);

    for (const Assignment& assignment : assignments) {
        printAssignment(assignment, variables);

        std::cout
            << std::setw(8)
            << (formula.evaluate(assignment) ? 'T' : 'F')
            << "\n";
    }

    std::cout
        << "\nClassification: "
        << classificationName(classifyFormula(formula))
        << "\n";
}


// -----------------------------------------------------------------------------
// 6. Counterexample search
// -----------------------------------------------------------------------------

bool findCounterexample(
    const Formula& first,
    const Formula& second,
    Assignment& counterexample
) {
    std::set<char> variableSet = first.variables();

    const std::set<char> secondVariables = second.variables();

    variableSet.insert(
        secondVariables.begin(),
        secondVariables.end()
    );

    const std::vector<char> variables(
        variableSet.begin(),
        variableSet.end()
    );

    for (const Assignment& assignment :
         generateAssignments(variables)) {

        if (
            first.evaluate(assignment) !=
            second.evaluate(assignment)
        ) {
            counterexample = assignment;
            return true;
        }
    }

    return false;
}


bool logicallyEquivalent(
    const Formula& first,
    const Formula& second
) {
    Assignment counterexample;
    return !findCounterexample(
        first,
        second,
        counterexample
    );
}


// -----------------------------------------------------------------------------
// 7. Argument validity
// -----------------------------------------------------------------------------

bool argumentIsValid(
    const std::vector<const Formula*>& premises,
    const Formula& conclusion,
    Assignment& counterexample
) {
    std::set<char> variableSet = conclusion.variables();

    for (const Formula* premise : premises) {
        if (premise == nullptr) {
            throw std::invalid_argument(
                "A premise pointer cannot be null."
            );
        }

        const std::set<char> premiseVariables =
            premise->variables();

        variableSet.insert(
            premiseVariables.begin(),
            premiseVariables.end()
        );
    }

    const std::vector<char> variables(
        variableSet.begin(),
        variableSet.end()
    );

    /*
     * An argument is invalid exactly when:
     *
     *   all premises are true
     *   AND
     *   conclusion is false
     *
     * This assignment is called a countermodel or counterexample.
     */
    for (const Assignment& assignment :
         generateAssignments(variables)) {

        bool allPremisesTrue = true;

        for (const Formula* premise : premises) {
            if (!premise->evaluate(assignment)) {
                allPremisesTrue = false;
                break;
            }
        }

        if (
            allPremisesTrue &&
            !conclusion.evaluate(assignment)
        ) {
            counterexample = assignment;
            return false;
        }
    }

    return true;
}


// -----------------------------------------------------------------------------
// 8. Industry-style case study: access-control policy engine
// -----------------------------------------------------------------------------
/*
 * Security policy:
 *
 * A = valid badge
 * B = completed security training
 * C = approved network
 * D = allowed operating period
 *
 * Policy 1:
 *
 *     (A AND B AND C) OR (A AND B AND D)
 *
 * This can be factored algebraically:
 *
 *     A AND B AND (C OR D)
 *
 * A second policy implementation uses the factored expression. Truth-table
 * equivalence proves that both policies make exactly the same decision for
 * every possible input.
 *
 * This is useful in real systems because a rule engine may have several
 * independently implemented policy expressions. Truth-table comparison can
 * detect semantic mismatches before deployment.
 */

class AccessRequest {
public:
    bool validBadge;
    bool completedTraining;
    bool approvedNetwork;
    bool allowedTime;
};


bool originalAccessPolicy(const AccessRequest& request) {
    const bool routeOne =
        request.validBadge &&
        request.completedTraining &&
        request.approvedNetwork;

    const bool routeTwo =
        request.validBadge &&
        request.completedTraining &&
        request.allowedTime;

    return routeOne || routeTwo;
}


bool factoredAccessPolicy(const AccessRequest& request) {
    return
        request.validBadge &&
        request.completedTraining &&
        (
            request.approvedNetwork ||
            request.allowedTime
        );
}


bool intentionallyDifferentPolicy(const AccessRequest& request) {
    /*
     * This deliberately incorrect policy requires BOTH the network and
     * operating-time conditions. The truth-table comparison should find
     * counterexamples.
     */
    return
        request.validBadge &&
        request.completedTraining &&
        request.approvedNetwork &&
        request.allowedTime;
}


void printAccessPolicyTable() {
    std::cout << "\n";
    std::cout
        << "A B C D | Original | Factored | Different\n";

    std::cout
        << "------------------------------------------\n";

    for (bool a : {false, true}) {
        for (bool b : {false, true}) {
            for (bool c : {false, true}) {
                for (bool d : {false, true}) {

                    AccessRequest request{
                        a, b, c, d
                    };

                    const bool original =
                        originalAccessPolicy(request);

                    const bool factored =
                        factoredAccessPolicy(request);

                    const bool different =
                        intentionallyDifferentPolicy(request);

                    std::cout
                        << (a ? 'T' : 'F') << " "
                        << (b ? 'T' : 'F') << " "
                        << (c ? 'T' : 'F') << " "
                        << (d ? 'T' : 'F') << " | "
                        << std::setw(8)
                        << (original ? 'T' : 'F') << " | "
                        << std::setw(8)
                        << (factored ? 'T' : 'F') << " | "
                        << std::setw(9)
                        << (different ? 'T' : 'F')
                        << "\n";
                }
            }
        }
    }
}


bool policiesEquivalent() {
    for (bool a : {false, true}) {
        for (bool b : {false, true}) {
            for (bool c : {false, true}) {
                for (bool d : {false, true}) {

                    AccessRequest request{
                        a, b, c, d
                    };

                    if (
                        originalAccessPolicy(request) !=
                        factoredAccessPolicy(request)
                    ) {
                        return false;
                    }
                }
            }
        }
    }

    return true;
}


void showPolicyCounterexample() {
    for (bool a : {false, true}) {
        for (bool b : {false, true}) {
            for (bool c : {false, true}) {
                for (bool d : {false, true}) {

                    AccessRequest request{
                        a, b, c, d
                    };

                    const bool original =
                        originalAccessPolicy(request);

                    const bool different =
                        intentionallyDifferentPolicy(request);

                    if (original != different) {
                        std::cout
                            << "\nCounterexample found:\n"
                            << "  Badge: "
                            << (a ? "valid" : "invalid") << "\n"
                            << "  Training: "
                            << (b ? "complete" : "incomplete") << "\n"
                            << "  Network: "
                            << (c ? "approved" : "unapproved") << "\n"
                            << "  Time: "
                            << (d ? "allowed" : "disallowed") << "\n"
                            << "  Original policy: "
                            << (original ? "ALLOW" : "DENY") << "\n"
                            << "  Different policy: "
                            << (different ? "ALLOW" : "DENY")
                            << "\n";

                        return;
                    }
                }
            }
        }
    }

    std::cout << "\nNo counterexample found.\n";
}


// -----------------------------------------------------------------------------
// 9. Demonstrate classic logical laws
// -----------------------------------------------------------------------------

void demonstrateLogicalLaws() {
    std::cout << "\n" << std::string(78, '=')
              << "\n";
    std::cout << "CLASSIC LOGICAL LAWS\n";
    std::cout << std::string(78, '=')
              << "\n";

    Variable p('p');
    Variable q('q');
    Variable r('r');

    NotFormula notP(p);
    NotFormula notQ(q);
    NotFormula notR(r);

    BinaryFormula excludedMiddle(
        p, '|', notP
    );

    BinaryFormula contradictionInner(
        p, '&', notP
    );

    NotFormula lawOfContradiction(
        contradictionInner
    );

    NotFormula notPQ(
        BinaryFormula(p, '&', q)
    );

    BinaryFormula deMorganRight(
        notP, '|', notQ
    );

    BinaryFormula deMorganEquivalence(
        notPQ, '=', deMorganRight
    );

    BinaryFormula implication(
        p, '>', q
    );

    BinaryFormula implicationReplacement(
        notP, '|', q
    );

    BinaryFormula implicationEquivalence(
        implication, '=', implicationReplacement
    );

    BinaryFormula contrapositiveRight(
        notQ, '>', notP
    );

    BinaryFormula contrapositiveEquivalence(
        implication, '=', contrapositiveRight
    );

    std::vector<const Formula*> laws{
        &excludedMiddle,
        &lawOfContradiction,
        &deMorganEquivalence,
        &implicationEquivalence,
        &contrapositiveEquivalence
    };

    for (const Formula* law : laws) {
        std::cout
            << law->name()
            << "\n  -> "
            << classificationName(
                classifyFormula(*law)
            )
            << "\n";
    }

    // Avoid unused-variable warnings in strict builds.
    (void)notR;
    (void)r;
}


// -----------------------------------------------------------------------------
// 10. Normal-form generation
// -----------------------------------------------------------------------------

std::string canonicalDNF(const Formula& formula) {
    const std::vector<char> variables =
        sortedVariables(formula);

    const std::vector<Assignment> assignments =
        generateAssignments(variables);

    std::vector<std::string> terms;

    for (const Assignment& assignment : assignments) {
        if (!formula.evaluate(assignment)) {
            continue;
        }

        std::string term = "(";

        for (std::size_t index = 0;
             index < variables.size();
             ++index) {

            if (index != 0) {
                term += " AND ";
            }

            const char variable = variables[index];

            if (!assignment.at(variable)) {
                term += "NOT ";
            }

            term += variable;
        }

        term += ")";
        terms.push_back(term);
    }

    if (terms.empty()) {
        return "FALSE";
    }

    std::string result;

    for (std::size_t index = 0;
         index < terms.size();
         ++index) {

        if (index != 0) {
            result += " OR ";
        }

        result += terms[index];
    }

    return result;
}


std::string canonicalCNF(const Formula& formula) {
    const std::vector<char> variables =
        sortedVariables(formula);

    const std::vector<Assignment> assignments =
        generateAssignments(variables);

    std::vector<std::string> clauses;

    for (const Assignment& assignment : assignments) {
        if (formula.evaluate(assignment)) {
            continue;
        }

        std::string clause = "(";

        for (std::size_t index = 0;
             index < variables.size();
             ++index) {

            if (index != 0) {
                clause += " OR ";
            }

            const char variable = variables[index];

            /*
             * A false row receives:
             *   variable      when variable is false
             *   NOT variable when variable is true
             */
            if (assignment.at(variable)) {
                clause += "NOT ";
            }

            clause += variable;
        }

        clause += ")";
        clauses.push_back(clause);
    }

    if (clauses.empty()) {
        return "TRUE";
    }

    std::string result;

    for (std::size_t index = 0;
         index < clauses.size();
         ++index) {

        if (index != 0) {
            result += " AND ";
        }

        result += clauses[index];
    }

    return result;
}


// -----------------------------------------------------------------------------
// 11. Main
// -----------------------------------------------------------------------------

int main() {
    try {
        std::cout
            << std::string(78, '=')
            << "\nTRUTH TABLES AND PROPOSITIONAL LOGIC\n"
            << std::string(78, '=')
            << "\n";

        // Basic operator table.
        std::cout << "\nBasic implication values:\n";
        std::cout << "p q | p -> q\n";
        std::cout << "---------\n";

        for (bool p : {false, true}) {
            for (bool q : {false, true}) {
                std::cout
                    << (p ? 'T' : 'F') << " "
                    << (q ? 'T' : 'F') << " | "
                    << (logical_implies(p, q) ? 'T' : 'F')
                    << "\n";
            }
        }

        // Build p AND (q OR NOT r).
        Variable p('p');
        Variable q('q');
        Variable r('r');

        NotFormula notR(r);

        BinaryFormula qOrNotR(
            q, '|', notR
        );

        BinaryFormula example(
            p, '&', qOrNotR
        );

        std::cout
            << "\nFormula-tree example:\n";

        printTruthTable(example);

        // Tautology: p OR NOT p.
        NotFormula notP(p);

        BinaryFormula excludedMiddle(
            p, '|', notP
        );

        std::cout
            << "\nTautology test:\n"
            << excludedMiddle.name()
            << " -> "
            << classificationName(
                classifyFormula(excludedMiddle)
            )
            << "\n";

        // Contradiction: p AND NOT p.
        BinaryFormula contradiction(
            p, '&', notP
        );

        std::cout
            << "\nContradiction test:\n"
            << contradiction.name()
            << " -> "
            << classificationName(
                classifyFormula(contradiction)
            )
            << "\n";

        // Contingency: p AND q.
        BinaryFormula contingency(
            p, '&', q
        );

        std::cout
            << "\nContingency test:\n"
            << contingency.name()
            << " -> "
            << classificationName(
                classifyFormula(contingency)
            )
            << "\n";

        // Equivalence: p -> q is equivalent to NOT p OR q.
        BinaryFormula implication(
            p, '>', q
        );

        BinaryFormula implicationReplacement(
            notP, '|', q
        );

        std::cout
            << "\nEquivalence test:\n"
            << implication.name()
            << " <=> "
            << implicationReplacement.name()
            << "\nEquivalent: "
            << (
                logicallyEquivalent(
                    implication,
                    implicationReplacement
                ) ? "true" : "false"
            )
            << "\n";

        // Argument validity: modus ponens.
        std::cout
            << "\nArgument-validity test: Modus Ponens\n";

        std::vector<const Formula*> modusPonensPremises{
            &implication,
            &p
        };

        Assignment counterexample;

        const bool valid =
            argumentIsValid(
                modusPonensPremises,
                q,
                counterexample
            );

        std::cout
            << "  p -> q\n"
            << "  p\n"
            << "  Therefore q\n"
            << "Valid: "
            << (valid ? "true" : "false")
            << "\n";

        if (!valid) {
            std::cout << "Counterexample: ";
            printAssignment(
                counterexample,
                {'p', 'q'}
            );
            std::cout << "\n";
        }

        // Canonical normal forms.
        std::cout
            << "\nCanonical normal forms for "
            << contingency.name()
            << ":\n";

        std::cout
            << "DNF: "
            << canonicalDNF(contingency)
            << "\n";

        std::cout
            << "CNF: "
            << canonicalCNF(contingency)
            << "\n";

        // ---------------------------------------------------------------------
        // Industry case study.
        // ---------------------------------------------------------------------

        std::cout
            << "\n"
            << std::string(78, '=')
            << "\n"
            << "INDUSTRY CASE STUDY: ACCESS-CONTROL POLICY\n"
            << std::string(78, '=')
            << "\n";

        std::cout
            << "\nVariables:\n"
            << "A = valid badge\n"
            << "B = completed security training\n"
            << "C = approved network\n"
            << "D = allowed operating period\n";

        std::cout
            << "\nPolicy:\n"
            << "(A AND B AND C) OR (A AND B AND D)\n";

        printAccessPolicyTable();

        std::cout
            << "\nOriginal policy and factored policy equivalent: "
            << (
                policiesEquivalent()
                    ? "true"
                    : "false"
            )
            << "\n";

        showPolicyCounterexample();

        // Classic laws.
        demonstrateLogicalLaws();

        // Normal forms for the access rule.
        /*
         * This section uses a Formula tree corresponding to:
         *
         *   (A AND B AND C) OR (A AND B AND D)
         */
        Variable A('A');
        Variable B('B');
        Variable C('C');
        Variable D('D');

        BinaryFormula AB(
            A, '&', B
        );

        BinaryFormula ABC(
            AB, '&', C
        );

        BinaryFormula ABD(
            AB, '&', D
        );

        BinaryFormula accessFormula(
            ABC, '|', ABD
        );

        std::cout
            << "\nAccess-control formula classification: "
            << classificationName(
                classifyFormula(accessFormula)
            )
            << "\n";

        std::cout
            << "\nAccess-control canonical DNF:\n"
            << canonicalDNF(accessFormula)
            << "\n";

        std::cout
            << "\nAccess-control canonical CNF:\n"
            << canonicalCNF(accessFormula)
            << "\n";

        // Complexity.
        std::cout
            << "\n"
            << std::string(78, '=')
            << "\n"
            << "EXHAUSTIVE TRUTH-TABLE COMPLEXITY\n"
            << std::string(78, '=')
            << "\n";

        for (unsigned int variableCount = 0;
             variableCount <= 20;
             ++variableCount) {

            const std::size_t rows =
                static_cast<std::size_t>(1) << variableCount;

            std::cout
                << "Variables: "
                << std::setw(2)
                << variableCount
                << " | Rows: "
                << std::setw(8)
                << rows
                << "\n";
        }

        std::cout
            << "\nProgram completed successfully.\n";

    } catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << "\n";

        return 1;
    }

    return 0;
}
