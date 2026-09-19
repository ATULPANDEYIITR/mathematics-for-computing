/*
 * Logical Equivalence: Industry-Style C++ Case Study
 *
 * Scenario:
 * A policy evaluation engine determines whether an account should
 * receive access to a protected resource. Policies are represented
 * as Boolean expressions. The engine can evaluate policies, compare
 * logically equivalent policy expressions, identify counterexamples,
 * and report truth-table behavior.
 *
 * Demonstrated concepts:
 *   - Propositional logic
 *   - De Morgan's laws
 *   - Implication equivalence
 *   - Contrapositive
 *   - Distributive laws
 *   - Absorption laws
 *   - Truth tables
 *   - Expression trees
 *   - Recursive evaluation
 *   - Structural representation
 *   - Exhaustive semantic equivalence
 *   - Validation
 *   - Complexity and implementation trade-offs
 *
 * Compile:
 *   g++ -std=c++17 -O2 logical_equivalence.cpp -o logical_equivalence
 *
 * Run:
 *   ./logical_equivalence
 */

#include <algorithm>
#include <bitset>
#include <functional>
#include <iomanip>
#include <iostream>
#include <memory>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using Assignment = std::unordered_map<std::string, bool>;

enum class Operator {
    Not,
    And,
    Or,
    Xor,
    Implies,
    Iff
};

std::string operatorName(Operator op) {
    switch (op) {
        case Operator::Not:
            return "NOT";
        case Operator::And:
            return "AND";
        case Operator::Or:
            return "OR";
        case Operator::Xor:
            return "XOR";
        case Operator::Implies:
            return "->";
        case Operator::Iff:
            return "<->";
    }

    throw std::logic_error("Unknown operator");
}

class Expression {
public:
    virtual ~Expression() = default;

    virtual bool evaluate(const Assignment& assignment) const = 0;

    virtual std::set<std::string> variables() const = 0;

    virtual std::string toString() const = 0;
};

using ExpressionPtr = std::shared_ptr<const Expression>;

// ============================================================
// VARIABLE EXPRESSION
// ============================================================

class Variable final : public Expression {
private:
    std::string name_;

public:
    explicit Variable(std::string name)
        : name_(std::move(name)) {
        if (name_.empty()) {
            throw std::invalid_argument(
                "Variable name cannot be empty"
            );
        }
    }

    bool evaluate(const Assignment& assignment) const override {
        auto iterator = assignment.find(name_);

        if (iterator == assignment.end()) {
            throw std::invalid_argument(
                "Missing variable assignment: " + name_
            );
        }

        return iterator->second;
    }

    std::set<std::string> variables() const override {
        return {name_};
    }

    std::string toString() const override {
        return name_;
    }
};

// ============================================================
// CONSTANT EXPRESSION
// ============================================================

class Constant final : public Expression {
private:
    bool value_;

public:
    explicit Constant(bool value)
        : value_(value) {}

    bool evaluate(const Assignment&) const override {
        return value_;
    }

    std::set<std::string> variables() const override {
        return {};
    }

    std::string toString() const override {
        return value_ ? "T" : "F";
    }
};

// ============================================================
// UNARY EXPRESSION
// ============================================================

class UnaryExpression final : public Expression {
private:
    Operator operation_;
    ExpressionPtr operand_;

public:
    UnaryExpression(
        Operator operation,
        ExpressionPtr operand
    )
        : operation_(operation),
          operand_(std::move(operand)) {
        if (operation_ != Operator::Not) {
            throw std::invalid_argument(
                "UnaryExpression supports only NOT"
            );
        }

        if (!operand_) {
            throw std::invalid_argument(
                "Unary expression requires an operand"
            );
        }
    }

    bool evaluate(const Assignment& assignment) const override {
        return !operand_->evaluate(assignment);
    }

    std::set<std::string> variables() const override {
        return operand_->variables();
    }

    std::string toString() const override {
        return "~(" + operand_->toString() + ")";
    }
};

// ============================================================
// BINARY EXPRESSION
// ============================================================

class BinaryExpression final : public Expression {
private:
    Operator operation_;
    ExpressionPtr left_;
    ExpressionPtr right_;

public:
    BinaryExpression(
        Operator operation,
        ExpressionPtr left,
        ExpressionPtr right
    )
        : operation_(operation),
          left_(std::move(left)),
          right_(std::move(right)) {
        if (!left_ || !right_) {
            throw std::invalid_argument(
                "Binary expression requires two operands"
            );
        }

        if (operation_ == Operator::Not) {
            throw std::invalid_argument(
                "NOT is not a binary operator"
            );
        }
    }

    bool evaluate(const Assignment& assignment) const override {
        const bool left = left_->evaluate(assignment);

        /*
         * Short-circuiting is important in real applications.
         *
         * For AND:
         *   false AND anything == false.
         *
         * For OR:
         *   true OR anything == true.
         *
         * Short-circuiting can reduce work and can also prevent
         * unnecessary evaluation of a failing or expensive condition.
         */
        switch (operation_) {
            case Operator::And:
                if (!left) {
                    return false;
                }
                return right_->evaluate(assignment);

            case Operator::Or:
                if (left) {
                    return true;
                }
                return right_->evaluate(assignment);

            case Operator::Xor:
                return left != right_->evaluate(assignment);

            case Operator::Implies:
                /*
                 * P -> Q is equivalent to ~P OR Q.
                 *
                 * If P is false, the implication is true immediately.
                 */
                if (!left) {
                    return true;
                }
                return right_->evaluate(assignment);

            case Operator::Iff:
                return left == right_->evaluate(assignment);

            case Operator::Not:
                break;
        }

        throw std::logic_error("Unsupported binary operation");
    }

    std::set<std::string> variables() const override {
        std::set<std::string> result = left_->variables();

        const auto rightVariables = right_->variables();

        result.insert(
            rightVariables.begin(),
            rightVariables.end()
        );

        return result;
    }

    std::string toString() const override {
        return "("
            + left_->toString()
            + " "
            + operatorName(operation_)
            + " "
            + right_->toString()
            + ")";
    }
};

// ============================================================
// EXPRESSION FACTORY FUNCTIONS
// ============================================================

ExpressionPtr variable(const std::string& name) {
    return std::make_shared<Variable>(name);
}

ExpressionPtr constant(bool value) {
    return std::make_shared<Constant>(value);
}

ExpressionPtr logicalNot(ExpressionPtr operand) {
    return std::make_shared<UnaryExpression>(
        Operator::Not,
        std::move(operand)
    );
}

ExpressionPtr logicalAnd(
    ExpressionPtr left,
    ExpressionPtr right
) {
    return std::make_shared<BinaryExpression>(
        Operator::And,
        std::move(left),
        std::move(right)
    );
}

ExpressionPtr logicalOr(
    ExpressionPtr left,
    ExpressionPtr right
) {
    return std::make_shared<BinaryExpression>(
        Operator::Or,
        std::move(left),
        std::move(right)
    );
}

ExpressionPtr logicalXor(
    ExpressionPtr left,
    ExpressionPtr right
) {
    return std::make_shared<BinaryExpression>(
        Operator::Xor,
        std::move(left),
        std::move(right)
    );
}

ExpressionPtr implies(
    ExpressionPtr left,
    ExpressionPtr right
) {
    return std::make_shared<BinaryExpression>(
        Operator::Implies,
        std::move(left),
        std::move(right)
    );
}

ExpressionPtr iff(
    ExpressionPtr left,
    ExpressionPtr right
) {
    return std::make_shared<BinaryExpression>(
        Operator::Iff,
        std::move(left),
        std::move(right)
    );
}

// ============================================================
// ASSIGNMENT GENERATION
// ============================================================

std::vector<std::string> sortedVariables(
    const ExpressionPtr& expression
) {
    const auto variableSet = expression->variables();

    return {
        variableSet.begin(),
        variableSet.end()
    };
}

std::vector<Assignment> generateAssignments(
    const std::vector<std::string>& names
) {
    if (names.size() > 20) {
        /*
         * 2^20 assignments is already more than one million rows.
         * This case study intentionally protects the demonstration
         * from accidentally creating an excessive workload.
         */
        throw std::runtime_error(
            "Too many variables for exhaustive truth-table generation"
        );
    }

    const std::size_t total =
        static_cast<std::size_t>(1) << names.size();

    std::vector<Assignment> assignments;
    assignments.reserve(total);

    for (std::size_t mask = 0; mask < total; ++mask) {
        Assignment assignment;

        for (std::size_t index = 0; index < names.size(); ++index) {
            const std::size_t bit =
                names.size() - index - 1;

            assignment[names[index]] =
                ((mask >> bit) & 1U) != 0;
        }

        assignments.push_back(std::move(assignment));
    }

    return assignments;
}

// ============================================================
// EQUIVALENCE ENGINE
// ============================================================

struct EquivalenceResult {
    bool equivalent;
    std::optional<Assignment> counterexample;
};

EquivalenceResult compareExpressions(
    const ExpressionPtr& first,
    const ExpressionPtr& second
) {
    std::set<std::string> allVariableSet =
        first->variables();

    const auto secondVariables = second->variables();

    allVariableSet.insert(
        secondVariables.begin(),
        secondVariables.end()
    );

    const std::vector<std::string> names(
        allVariableSet.begin(),
        allVariableSet.end()
    );

    const auto assignments = generateAssignments(names);

    for (const auto& assignment : assignments) {
        const bool firstValue =
            first->evaluate(assignment);

        const bool secondValue =
            second->evaluate(assignment);

        if (firstValue != secondValue) {
            return {
                false,
                assignment
            };
        }
    }

    return {
        true,
        std::nullopt
    };
}

void printAssignment(const Assignment& assignment) {
    std::vector<std::string> names;

    names.reserve(assignment.size());

    for (const auto& [name, value] : assignment) {
        static_cast<void>(value);
        names.push_back(name);
    }

    std::sort(names.begin(), names.end());

    std::cout << "{ ";

    for (std::size_t index = 0; index < names.size(); ++index) {
        const auto& name = names[index];

        std::cout
            << name
            << "="
            << (assignment.at(name) ? "T" : "F");

        if (index + 1 < names.size()) {
            std::cout << ", ";
        }
    }

    std::cout << " }";
}

void reportEquivalence(
    const std::string& name,
    const ExpressionPtr& first,
    const ExpressionPtr& second
) {
    const EquivalenceResult result =
        compareExpressions(first, second);

    std::cout
        << std::left
        << std::setw(42)
        << name
        << (result.equivalent ? "PASS" : "FAIL")
        << "\n";

    if (!result.equivalent &&
        result.counterexample.has_value()) {
        std::cout << "  Counterexample: ";
        printAssignment(*result.counterexample);
        std::cout << "\n";
    }
}

// ============================================================
// TRUTH TABLE
// ============================================================

void printTruthTable(
    const ExpressionPtr& expression
) {
    const auto names = sortedVariables(expression);
    const auto assignments = generateAssignments(names);

    std::cout << "\nTruth table for:\n";
    std::cout << "  " << expression->toString() << "\n\n";

    for (const auto& name : names) {
        std::cout
            << std::setw(5)
            << name;
    }

    std::cout
        << std::setw(8)
        << "Result"
        << "\n";

    std::cout << std::string(
        names.size() * 5 + 8,
        '-'
    ) << "\n";

    for (const auto& assignment : assignments) {
        for (const auto& name : names) {
            std::cout
                << std::setw(5)
                << (assignment.at(name) ? "T" : "F");
        }

        std::cout
            << std::setw(8)
            << (
                expression->evaluate(assignment)
                    ? "T"
                    : "F"
            )
            << "\n";
    }
}

// ============================================================
// CLASSIFICATION
// ============================================================

enum class Classification {
    Tautology,
    Contradiction,
    Contingency
};

Classification classify(
    const ExpressionPtr& expression
) {
    const auto names = sortedVariables(expression);
    const auto assignments = generateAssignments(names);

    bool foundTrue = false;
    bool foundFalse = false;

    for (const auto& assignment : assignments) {
        if (expression->evaluate(assignment)) {
            foundTrue = true;
        } else {
            foundFalse = true;
        }
    }

    if (foundTrue && !foundFalse) {
        return Classification::Tautology;
    }

    if (!foundTrue && foundFalse) {
        return Classification::Contradiction;
    }

    return Classification::Contingency;
}

std::string classificationName(
    Classification classification
) {
    switch (classification) {
        case Classification::Tautology:
            return "tautology";

        case Classification::Contradiction:
            return "contradiction";

        case Classification::Contingency:
            return "contingency";
    }

    throw std::logic_error("Unknown classification");
}

// ============================================================
// POLICY ENGINE
// ============================================================

struct Policy {
    std::string name;
    ExpressionPtr condition;
    bool decision;
};

class PolicyEngine {
private:
    std::vector<Policy> policies_;

public:
    explicit PolicyEngine(std::vector<Policy> policies)
        : policies_(std::move(policies)) {}

    std::vector<std::pair<std::string, bool>> evaluate(
        const Assignment& assignment
    ) const {
        std::vector<std::pair<std::string, bool>> decisions;

        for (const auto& policy : policies_) {
            if (policy.condition->evaluate(assignment)) {
                decisions.emplace_back(
                    policy.name,
                    policy.decision
                );
            }
        }

        return decisions;
    }
};

// ============================================================
// CASE STUDY: ACCESS-CONTROL POLICY
// ============================================================

void runAccessControlCaseStudy() {
    std::cout
        << "\n"
        << "============================================================\n"
        << "ACCESS-CONTROL POLICY CASE STUDY\n"
        << "============================================================\n";

    /*
     * Protected resource:
     *
     * Access is granted when:
     *
     *   Authenticated AND Authorized AND NOT Suspended
     *
     * This is intentionally simple enough to reason about formally,
     * while still resembling a real policy condition.
     */
    const auto authenticated =
        variable("Authenticated");

    const auto authorized =
        variable("Authorized");

    const auto suspended =
        variable("Suspended");

    const auto accessPolicy =
        logicalAnd(
            logicalAnd(
                authenticated,
                authorized
            ),
            logicalNot(suspended)
        );

    /*
     * Denial is the logical negation of access.
     *
     * Applying De Morgan's laws gives:
     *
     * NOT Authenticated
     * OR NOT Authorized
     * OR Suspended
     */
    const auto deniedPolicy =
        logicalNot(accessPolicy);

    const auto deMorganDeniedPolicy =
        logicalOr(
            logicalOr(
                logicalNot(authenticated),
                logicalNot(authorized)
            ),
            suspended
        );

    std::cout << "\nOriginal access policy:\n";
    std::cout
        << "  "
        << accessPolicy->toString()
        << "\n";

    std::cout << "\nOriginal denial expression:\n";
    std::cout
        << "  "
        << deniedPolicy->toString()
        << "\n";

    std::cout << "\nDe Morgan transformed denial expression:\n";
    std::cout
        << "  "
        << deMorganDeniedPolicy->toString()
        << "\n";

    reportEquivalence(
        "De Morgan denial transformation",
        deniedPolicy,
        deMorganDeniedPolicy
    );

    /*
     * Generate realistic input cases.
     */
    const std::vector<Assignment> users = {
        {
            {"Authenticated", true},
            {"Authorized", true},
            {"Suspended", false}
        },
        {
            {"Authenticated", true},
            {"Authorized", false},
            {"Suspended", false}
        },
        {
            {"Authenticated", true},
            {"Authorized", true},
            {"Suspended", true}
        },
        {
            {"Authenticated", false},
            {"Authorized", true},
            {"Suspended", false}
        }
    };

    std::cout << "\nPolicy decisions:\n";

    for (const auto& user : users) {
        std::cout << "  ";
        printAssignment(user);

        std::cout
            << " -> access="
            << (
                accessPolicy->evaluate(user)
                    ? "GRANT"
                    : "DENY"
            )
            << "\n";
    }

    /*
     * Security design observation:
     *
     * The transformed expression is logically identical, so changing
     * between the two forms should not alter the decision. A production
     * system still needs authentication, authorization data integrity,
     * secure state management, logging, testing, and fail-safe behavior.
     */
}

// ============================================================
// IMPLICATION CASE STUDY
// ============================================================

void runImplicationCaseStudy() {
    std::cout
        << "\n"
        << "============================================================\n"
        << "IMPLICATION CASE STUDY\n"
        << "============================================================\n";

    const auto requestValid =
        variable("RequestValid");

    const auto identityVerified =
        variable("IdentityVerified");

    /*
     * Rule:
     *
     *   RequestValid -> IdentityVerified
     *
     * Equivalent form:
     *
     *   NOT RequestValid OR IdentityVerified
     */
    const auto implication =
        implies(
            requestValid,
            identityVerified
        );

    const auto implicationEliminated =
        logicalOr(
            logicalNot(requestValid),
            identityVerified
        );

    /*
     * Contrapositive:
     *
     *   NOT IdentityVerified -> NOT RequestValid
     */
    const auto contrapositive =
        implies(
            logicalNot(identityVerified),
            logicalNot(requestValid)
        );

    /*
     * Converse:
     *
     *   IdentityVerified -> RequestValid
     *
     * This is not generally equivalent to the original.
     */
    const auto converse =
        implies(
            identityVerified,
            requestValid
        );

    reportEquivalence(
        "Implication elimination",
        implication,
        implicationEliminated
    );

    reportEquivalence(
        "Contrapositive",
        implication,
        contrapositive
    );

    reportEquivalence(
        "Converse",
        implication,
        converse
    );
}

// ============================================================
// DISTRIBUTIVE LAW CASE STUDY
// ============================================================

void runDistributiveCaseStudy() {
    std::cout
        << "\n"
        << "============================================================\n"
        << "DISTRIBUTIVE LAW CASE STUDY\n"
        << "============================================================\n";

    const auto P = variable("P");
    const auto Q = variable("Q");
    const auto R = variable("R");

    /*
     * AND distributes over OR:
     *
     * P AND (Q OR R)
     *
     * becomes
     *
     * (P AND Q) OR (P AND R)
     */
    const auto left =
        logicalAnd(
            P,
            logicalOr(Q, R)
        );

    const auto right =
        logicalOr(
            logicalAnd(P, Q),
            logicalAnd(P, R)
        );

    reportEquivalence(
        "AND distributes over OR",
        left,
        right
    );

    /*
     * OR distributes over AND:
     *
     * P OR (Q AND R)
     *
     * becomes
     *
     * (P OR Q) AND (P OR R)
     */
    const auto reverseLeft =
        logicalOr(
            P,
            logicalAnd(Q, R)
        );

    const auto reverseRight =
        logicalAnd(
            logicalOr(P, Q),
            logicalOr(P, R)
        );

    reportEquivalence(
        "OR distributes over AND",
        reverseLeft,
        reverseRight
    );
}

// ============================================================
// ABSORPTION CASE STUDY
// ============================================================

void runAbsorptionCaseStudy() {
    std::cout
        << "\n"
        << "============================================================\n"
        << "ABSORPTION LAW CASE STUDY\n"
        << "============================================================\n";

    const auto P = variable("P");
    const auto Q = variable("Q");

    /*
     * P OR (P AND Q) == P
     */
    const auto first =
        logicalOr(
            P,
            logicalAnd(P, Q)
        );

    reportEquivalence(
        "P OR (P AND Q) == P",
        first,
        P
    );

    /*
     * P AND (P OR Q) == P
     */
    const auto second =
        logicalAnd(
            P,
            logicalOr(P, Q)
        );

    reportEquivalence(
        "P AND (P OR Q) == P",
        second,
        P
    );
}

// ============================================================
// BASIC LAW VERIFICATION
// ============================================================

void runBasicLawSuite() {
    std::cout
        << "\n"
        << "============================================================\n"
        << "AUTOMATED LAW VERIFICATION\n"
        << "============================================================\n";

    const auto P = variable("P");
    const auto Q = variable("Q");
    const auto R = variable("R");

    reportEquivalence(
        "Double negation",
        logicalNot(logicalNot(P)),
        P
    );

    reportEquivalence(
        "Identity AND",
        logicalAnd(P, constant(true)),
        P
    );

    reportEquivalence(
        "Identity OR",
        logicalOr(P, constant(false)),
        P
    );

    reportEquivalence(
        "Domination AND",
        logicalAnd(P, constant(false)),
        constant(false)
    );

    reportEquivalence(
        "Domination OR",
        logicalOr(P, constant(true)),
        constant(true)
    );

    reportEquivalence(
        "Idempotent AND",
        logicalAnd(P, P),
        P
    );

    reportEquivalence(
        "Idempotent OR",
        logicalOr(P, P),
        P
    );

    reportEquivalence(
        "Complement AND",
        logicalAnd(P, logicalNot(P)),
        constant(false)
    );

    reportEquivalence(
        "Complement OR",
        logicalOr(P, logicalNot(P)),
        constant(true)
    );

    reportEquivalence(
        "Commutative AND",
        logicalAnd(P, Q),
        logicalAnd(Q, P)
    );

    reportEquivalence(
        "Commutative OR",
        logicalOr(P, Q),
        logicalOr(Q, P)
    );

    reportEquivalence(
        "Associative AND",
        logicalAnd(logicalAnd(P, Q), R),
        logicalAnd(P, logicalAnd(Q, R))
    );

    reportEquivalence(
        "Associative OR",
        logicalOr(logicalOr(P, Q), R),
        logicalOr(P, logicalOr(Q, R))
    );

    reportEquivalence(
        "Biconditional expansion",
        iff(P, Q),
        logicalOr(
            logicalAnd(P, Q),
            logicalAnd(logicalNot(P), logicalNot(Q))
        )
    );
}

// ============================================================
// CLASSIFICATION CASE STUDY
// ============================================================

void runClassificationCaseStudy() {
    std::cout
        << "\n"
        << "============================================================\n"
        << "EXPRESSION CLASSIFICATION\n"
        << "============================================================\n";

    const auto P = variable("P");
    const auto Q = variable("Q");

    const auto tautology =
        logicalOr(P, logicalNot(P));

    const auto contradiction =
        logicalAnd(P, logicalNot(P));

    const auto contingency =
        implies(P, Q);

    std::cout
        << std::setw(28)
        << std::left
        << "P OR ~P"
        << classificationName(classify(tautology))
        << "\n";

    std::cout
        << std::setw(28)
        << std::left
        << "P AND ~P"
        << classificationName(classify(contradiction))
        << "\n";

    std::cout
        << std::setw(28)
        << std::left
        << "P -> Q"
        << classificationName(classify(contingency))
        << "\n";
}

// ============================================================
// COMPLEXITY ANALYSIS
// ============================================================

void runComplexityAnalysis() {
    std::cout
        << "\n"
        << "============================================================\n"
        << "EXHAUSTIVE EQUIVALENCE COMPLEXITY\n"
        << "============================================================\n";

    std::cout
        << "Variables"
        << std::setw(20)
        << "Assignments"
        << "\n";

    for (std::size_t n = 1; n <= 15; ++n) {
        const std::size_t assignments =
            static_cast<std::size_t>(1) << n;

        std::cout
            << std::setw(9)
            << n
            << std::setw(20)
            << assignments
            << "\n";
    }

    std::cout
        << "\nTruth-table verification requires 2^n assignments "
        << "for n variables.\n";

    std::cout
        << "This is practical for small expressions but becomes "
        << "expensive as n grows.\n";
}

// ============================================================
// EDGE-CASE VALIDATION
// ============================================================

void runValidationCaseStudy() {
    std::cout
        << "\n"
        << "============================================================\n"
        << "EDGE-CASE VALIDATION\n"
        << "============================================================\n";

    try {
        const auto invalidVariable =
            variable("");

        static_cast<void>(invalidVariable);
    } catch (const std::exception& error) {
        std::cout
            << "Caught expected invalid-variable error: "
            << error.what()
            << "\n";
    }

    try {
        const auto P = variable("P");

        Assignment incomplete;
        P->evaluate(incomplete);
    } catch (const std::exception& error) {
        std::cout
            << "Caught expected missing-assignment error: "
            << error.what()
            << "\n";
    }

    try {
        std::vector<std::string> tooManyVariables;

        for (int index = 0; index < 21; ++index) {
            tooManyVariables.push_back(
                "V" + std::to_string(index)
            );
        }

        static_cast<void>(
            generateAssignments(tooManyVariables)
        );
    } catch (const std::exception& error) {
        std::cout
            << "Caught expected workload-protection error: "
            << error.what()
            << "\n";
    }
}

// ============================================================
// TRUTH TABLE DEMONSTRATION
// ============================================================

void runTruthTableCaseStudy() {
    std::cout
        << "\n"
        << "============================================================\n"
        << "TRUTH TABLE DEMONSTRATION\n"
        << "============================================================\n";

    const auto P = variable("P");
    const auto Q = variable("Q");

    const auto expression =
        logicalNot(
            logicalAnd(P, Q)
        );

    printTruthTable(expression);
}

// ============================================================
// MAIN
// ============================================================

int main() {
    try {
        std::cout
            << "LOGICAL EQUIVALENCE CASE STUDY\n"
            << "==============================\n"
            << "De Morgan's laws, implication equivalence, "
               "distributive laws, and absorption laws.\n";

        runBasicLawSuite();
        runTruthTableCaseStudy();
        runImplicationCaseStudy();
        runDistributiveCaseStudy();
        runAbsorptionCaseStudy();
        runClassificationCaseStudy();
        runAccessControlCaseStudy();
        runComplexityAnalysis();
        runValidationCaseStudy();

        std::cout
            << "\n"
            << "============================================================\n"
            << "CASE STUDY COMPLETED\n"
            << "============================================================\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << "\n";

        return 1;
    }
}
