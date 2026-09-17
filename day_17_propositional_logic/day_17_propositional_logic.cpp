/*
 * Propositional Logic Case Study
 *
 * C++17+
 *
 * This program develops a small rule-evaluation engine for an enterprise
 * authorization system. The implementation demonstrates:
 *
 *   - Boolean propositions
 *   - AND, OR, NOT
 *   - implication
 *   - biconditional
 *   - precedence-aware expression trees
 *   - symbolic variables
 *   - truth-table generation
 *   - satisfiability search
 *   - logical equivalence
 *   - argument validity
 *   - validation
 *   - error handling
 *   - policy evaluation
 *   - performance considerations
 *
 * The central practical rule is:
 *
 *   authenticated
 *   AND active account
 *   AND MFA verified
 *   AND (administrator OR resource owner)
 *   AND NOT emergency lock
 *
 * The program uses only the C++ standard library.
 */

#include <algorithm>
#include <cassert>
#include <cctype>
#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using Assignment = std::unordered_map<std::string, bool>;


// =============================================================================
// 1. CORE PROPOSITIONAL OPERATORS
// =============================================================================

bool logical_and(bool p, bool q) {
    return p && q;
}

bool logical_or(bool p, bool q) {
    return p || q;
}

bool logical_not(bool p) {
    return !p;
}

bool implies(bool p, bool q) {
    // P -> Q is equivalent to NOT P OR Q.
    return !p || q;
}

bool biconditional(bool p, bool q) {
    // P <-> Q is true when P and Q have the same truth value.
    return p == q;
}

bool exclusive_or(bool p, bool q) {
    return p != q;
}


// =============================================================================
// 2. TRUTH-TABLE GENERATION
// =============================================================================

std::vector<Assignment> generate_assignments(
    const std::vector<std::string>& variables
) {
    /*
     * n Boolean variables have 2^n possible assignments.
     *
     * This brute-force mechanism is excellent for small formulas because it is
     * easy to verify and makes the semantics of propositional logic explicit.
     */
    if (variables.size() >= 63) {
        throw std::invalid_argument(
            "Too many variables for safe 64-bit assignment enumeration"
        );
    }

    const std::size_t row_count =
        static_cast<std::size_t>(1ULL << variables.size());

    std::vector<Assignment> assignments;
    assignments.reserve(row_count);

    for (std::size_t mask = 0; mask < row_count; ++mask) {
        Assignment assignment;

        for (std::size_t index = 0; index < variables.size(); ++index) {
            assignment[variables[index]] =
                ((mask >> index) & 1ULL) != 0;
        }

        assignments.push_back(std::move(assignment));
    }

    return assignments;
}


// =============================================================================
// 3. EXPRESSION HIERARCHY
// =============================================================================

class Expression {
public:
    virtual ~Expression() = default;

    virtual bool evaluate(const Assignment& assignment) const = 0;

    virtual std::string describe() const = 0;

    virtual void collect_variables(
        std::set<std::string>& variables
    ) const = 0;
};

using ExpressionPtr = std::shared_ptr<const Expression>;


// =============================================================================
// 4. VARIABLE
// =============================================================================

class VariableExpression final : public Expression {
private:
    std::string name_;

public:
    explicit VariableExpression(std::string name)
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
            throw std::runtime_error(
                "Missing value for variable: " + name_
            );
        }

        return iterator->second;
    }

    std::string describe() const override {
        return name_;
    }

    void collect_variables(
        std::set<std::string>& variables
    ) const override {
        variables.insert(name_);
    }
};


// =============================================================================
// 5. CONSTANT
// =============================================================================

class ConstantExpression final : public Expression {
private:
    bool value_;

public:
    explicit ConstantExpression(bool value)
        : value_(value) {}

    bool evaluate(const Assignment&) const override {
        return value_;
    }

    std::string describe() const override {
        return value_ ? "TRUE" : "FALSE";
    }

    void collect_variables(
        std::set<std::string>&
    ) const override {
        // Constants contain no variables.
    }
};


// =============================================================================
// 6. NOT EXPRESSION
// =============================================================================

class NotExpression final : public Expression {
private:
    ExpressionPtr operand_;

public:
    explicit NotExpression(ExpressionPtr operand)
        : operand_(std::move(operand)) {
        if (!operand_) {
            throw std::invalid_argument(
                "NOT requires an operand"
            );
        }
    }

    bool evaluate(const Assignment& assignment) const override {
        return !operand_->evaluate(assignment);
    }

    std::string describe() const override {
        return "NOT (" + operand_->describe() + ")";
    }

    void collect_variables(
        std::set<std::string>& variables
    ) const override {
        operand_->collect_variables(variables);
    }
};


// =============================================================================
// 7. BINARY EXPRESSION
// =============================================================================

enum class BinaryOperator {
    And,
    Or,
    Implies,
    Biconditional
};

std::string operator_symbol(BinaryOperator operation) {
    switch (operation) {
        case BinaryOperator::And:
            return "AND";
        case BinaryOperator::Or:
            return "OR";
        case BinaryOperator::Implies:
            return "->";
        case BinaryOperator::Biconditional:
            return "<->";
    }

    throw std::logic_error("Unknown binary operator");
}


class BinaryExpression final : public Expression {
private:
    ExpressionPtr left_;
    ExpressionPtr right_;
    BinaryOperator operation_;

public:
    BinaryExpression(
        ExpressionPtr left,
        BinaryOperator operation,
        ExpressionPtr right
    )
        : left_(std::move(left)),
          right_(std::move(right)),
          operation_(operation) {
        if (!left_ || !right_) {
            throw std::invalid_argument(
                "Binary expression requires two operands"
            );
        }
    }

    bool evaluate(const Assignment& assignment) const override {
        const bool left = left_->evaluate(assignment);

        switch (operation_) {
            case BinaryOperator::And: {
                // Short-circuit semantics avoid unnecessary evaluation of the
                // right operand when the left side is already false.
                if (!left) {
                    return false;
                }

                return right_->evaluate(assignment);
            }

            case BinaryOperator::Or: {
                // Short-circuit semantics avoid unnecessary evaluation of the
                // right operand when the left side is already true.
                if (left) {
                    return true;
                }

                return right_->evaluate(assignment);
            }

            case BinaryOperator::Implies:
                return !left || right_->evaluate(assignment);

            case BinaryOperator::Biconditional: {
                const bool right = right_->evaluate(assignment);
                return left == right;
            }
        }

        throw std::logic_error(
            "Unsupported binary operator"
        );
    }

    std::string describe() const override {
        return "(" +
               left_->describe() +
               " " +
               operator_symbol(operation_) +
               " " +
               right_->describe() +
               ")";
    }

    void collect_variables(
        std::set<std::string>& variables
    ) const override {
        left_->collect_variables(variables);
        right_->collect_variables(variables);
    }
};


// =============================================================================
// 8. FACTORY FUNCTIONS
// =============================================================================

ExpressionPtr variable(const std::string& name) {
    return std::make_shared<VariableExpression>(name);
}

ExpressionPtr constant(bool value) {
    return std::make_shared<ConstantExpression>(value);
}

ExpressionPtr logical_not(ExpressionPtr expression) {
    return std::make_shared<NotExpression>(
        std::move(expression)
    );
}

ExpressionPtr binary(
    ExpressionPtr left,
    BinaryOperator operation,
    ExpressionPtr right
) {
    return std::make_shared<BinaryExpression>(
        std::move(left),
        operation,
        std::move(right)
    );
}

ExpressionPtr logical_and(
    ExpressionPtr left,
    ExpressionPtr right
) {
    return binary(
        std::move(left),
        BinaryOperator::And,
        std::move(right)
    );
}

ExpressionPtr logical_or(
    ExpressionPtr left,
    ExpressionPtr right
) {
    return binary(
        std::move(left),
        BinaryOperator::Or,
        std::move(right)
    );
}

ExpressionPtr logical_implies(
    ExpressionPtr left,
    ExpressionPtr right
) {
    return binary(
        std::move(left),
        BinaryOperator::Implies,
        std::move(right)
    );
}

ExpressionPtr logical_iff(
    ExpressionPtr left,
    ExpressionPtr right
) {
    return binary(
        std::move(left),
        BinaryOperator::Biconditional,
        std::move(right)
    );
}


// =============================================================================
// 9. FORMULA ANALYSIS
// =============================================================================

std::vector<std::string> variables_of(
    const Expression& expression
) {
    std::set<std::string> unique_variables;
    expression.collect_variables(unique_variables);

    return {
        unique_variables.begin(),
        unique_variables.end()
    };
}

struct TruthRow {
    Assignment assignment;
    bool result;
};

std::vector<TruthRow> truth_table(
    const Expression& expression
) {
    const auto variables = variables_of(expression);
    const auto assignments = generate_assignments(variables);

    std::vector<TruthRow> rows;
    rows.reserve(assignments.size());

    for (const auto& assignment : assignments) {
        rows.push_back({
            assignment,
            expression.evaluate(assignment)
        });
    }

    return rows;
}

enum class FormulaClassification {
    Tautology,
    Contradiction,
    Contingency
};

FormulaClassification classify(
    const Expression& expression
) {
    const auto rows = truth_table(expression);

    const bool all_true = std::all_of(
        rows.begin(),
        rows.end(),
        [](const TruthRow& row) {
            return row.result;
        }
    );

    const bool all_false = std::all_of(
        rows.begin(),
        rows.end(),
        [](const TruthRow& row) {
            return !row.result;
        }
    );

    if (all_true) {
        return FormulaClassification::Tautology;
    }

    if (all_false) {
        return FormulaClassification::Contradiction;
    }

    return FormulaClassification::Contingency;
}

std::string classification_name(
    FormulaClassification classification
) {
    switch (classification) {
        case FormulaClassification::Tautology:
            return "tautology";
        case FormulaClassification::Contradiction:
            return "contradiction";
        case FormulaClassification::Contingency:
            return "contingency";
    }

    throw std::logic_error("Unknown classification");
}


// =============================================================================
// 10. LOGICAL EQUIVALENCE
// =============================================================================

bool equivalent(
    const Expression& first,
    const Expression& second
) {
    std::set<std::string> variables;

    first.collect_variables(variables);
    second.collect_variables(variables);

    std::vector<std::string> names(
        variables.begin(),
        variables.end()
    );

    for (const auto& assignment : generate_assignments(names)) {
        if (
            first.evaluate(assignment) !=
            second.evaluate(assignment)
        ) {
            return false;
        }
    }

    return true;
}


// =============================================================================
// 11. SATISFIABILITY
// =============================================================================

std::vector<Assignment> satisfying_assignments(
    const Expression& expression
) {
    std::vector<Assignment> solutions;

    for (const auto& row : truth_table(expression)) {
        if (row.result) {
            solutions.push_back(row.assignment);
        }
    }

    return solutions;
}


// =============================================================================
// 12. COUNTEREXAMPLE SEARCH
// =============================================================================

std::optional<Assignment> find_counterexample(
    const Expression& first,
    const Expression& second
) {
    std::set<std::string> variables;

    first.collect_variables(variables);
    second.collect_variables(variables);

    std::vector<std::string> names(
        variables.begin(),
        variables.end()
    );

    for (const auto& assignment : generate_assignments(names)) {
        if (
            first.evaluate(assignment) !=
            second.evaluate(assignment)
        ) {
            return assignment;
        }
    }

    return std::nullopt;
}


// =============================================================================
// 13. ARGUMENT VALIDITY
// =============================================================================

bool argument_valid(
    const std::vector<ExpressionPtr>& premises,
    const Expression& conclusion
) {
    std::set<std::string> variables;

    for (const auto& premise : premises) {
        premise->collect_variables(variables);
    }

    conclusion.collect_variables(variables);

    std::vector<std::string> names(
        variables.begin(),
        variables.end()
    );

    for (const auto& assignment : generate_assignments(names)) {
        const bool all_premises_true = std::all_of(
            premises.begin(),
            premises.end(),
            [&assignment](const ExpressionPtr& premise) {
                return premise->evaluate(assignment);
            }
        );

        if (
            all_premises_true &&
            !conclusion.evaluate(assignment)
        ) {
            return false;
        }
    }

    return true;
}


// =============================================================================
// 14. ENTERPRISE ACCESS-CONTROL DOMAIN
// =============================================================================

struct UserContext {
    bool authenticated = false;
    bool account_active = false;
    bool mfa_verified = false;
    bool administrator = false;
    bool resource_owner = false;
    bool emergency_lock = false;
};

class AccessPolicy {
private:
    ExpressionPtr expression_;

public:
    explicit AccessPolicy(ExpressionPtr expression)
        : expression_(std::move(expression)) {
        if (!expression_) {
            throw std::invalid_argument(
                "Access policy requires an expression"
            );
        }
    }

    bool evaluate(const UserContext& context) const {
        Assignment assignment{
            {"authenticated", context.authenticated},
            {"account_active", context.account_active},
            {"mfa_verified", context.mfa_verified},
            {"administrator", context.administrator},
            {"resource_owner", context.resource_owner},
            {"emergency_lock", context.emergency_lock}
        };

        return expression_->evaluate(assignment);
    }

    const Expression& expression() const {
        return *expression_;
    }
};


// =============================================================================
// 15. POLICY CONSTRUCTION
// =============================================================================

ExpressionPtr build_enterprise_policy() {
    auto authenticated = variable("authenticated");
    auto active = variable("account_active");
    auto mfa = variable("mfa_verified");
    auto administrator = variable("administrator");
    auto owner = variable("resource_owner");
    auto emergency_lock = variable("emergency_lock");

    /*
     * Policy:
     *
     * authenticated
     * AND account_active
     * AND mfa_verified
     * AND (administrator OR resource_owner)
     * AND NOT emergency_lock
     *
     * Parentheses are represented structurally in the expression tree.
     */
    auto privileged_or_owner =
        logical_or(administrator, owner);

    auto identity_verified =
        logical_and(
            authenticated,
            logical_and(active, mfa)
        );

    auto access_requirements =
        logical_and(
            identity_verified,
            privileged_or_owner
        );

    return logical_and(
        access_requirements,
        logical_not(emergency_lock)
    );
}


// =============================================================================
// 16. POLICY EVALUATION
// =============================================================================

void print_context(
    const UserContext& context,
    const AccessPolicy& policy,
    const std::string& label
) {
    std::cout
        << std::left
        << std::setw(22)
        << label
        << " -> access="
        << std::boolalpha
        << policy.evaluate(context)
        << '\n';
}


// =============================================================================
// 17. POLICY TESTING
// =============================================================================

void test_core_operators() {
    assert(logical_and(true, true));
    assert(!logical_and(true, false));
    assert(!logical_and(false, true));
    assert(!logical_and(false, false));

    assert(!logical_or(false, false));
    assert(logical_or(true, false));
    assert(logical_or(false, true));
    assert(logical_or(true, true));

    assert(!logical_not(true));
    assert(logical_not(false));

    assert(implies(false, false));
    assert(implies(false, true));
    assert(!implies(true, false));
    assert(implies(true, true));

    assert(biconditional(false, false));
    assert(!biconditional(false, true));
    assert(!biconditional(true, false));
    assert(biconditional(true, true));
}

void test_logical_laws() {
    auto p = variable("P");
    auto q = variable("Q");

    auto demorgan_left =
        logical_not(
            logical_and(p, q)
        );

    auto demorgan_right =
        logical_or(
            logical_not(p),
            logical_not(q)
        );

    assert(equivalent(
        *demorgan_left,
        *demorgan_right
    ));

    auto implication =
        logical_implies(p, q);

    auto implication_definition =
        logical_or(
            logical_not(p),
            q
        );

    assert(equivalent(
        *implication,
        *implication_definition
    ));

    auto iff_formula =
        logical_iff(p, q);

    auto iff_expansion =
        logical_and(
            logical_implies(p, q),
            logical_implies(q, p)
        );

    assert(equivalent(
        *iff_formula,
        *iff_expansion
    ));
}


// =============================================================================
// 18. TRUTH-TABLE OUTPUT
// =============================================================================

void print_truth_table(
    const Expression& expression
) {
    const auto variables = variables_of(expression);
    const auto rows = truth_table(expression);

    for (const auto& variable_name : variables) {
        std::cout
            << std::setw(8)
            << variable_name;
    }

    std::cout
        << std::setw(10)
        << "RESULT"
        << '\n';

    std::cout
        << std::string(
            variables.size() * 8 + 10,
            '-'
        )
        << '\n';

    for (const auto& row : rows) {
        for (const auto& variable_name : variables) {
            std::cout
                << std::setw(8)
                << (
                    row.assignment.at(variable_name)
                    ? "T"
                    : "F"
                );
        }

        std::cout
            << std::setw(10)
            << (row.result ? "T" : "F")
            << '\n';
    }
}


// =============================================================================
// 19. MAIN CASE STUDY
// =============================================================================

int main() {
    try {
        std::cout
            << "============================================================\n"
            << "PROPOSITIONAL LOGIC CASE STUDY\n"
            << "============================================================\n\n";

        test_core_operators();
        test_logical_laws();

        // ---------------------------------------------------------------------
        // Basic truth table for implication.
        // ---------------------------------------------------------------------

        auto p = variable("P");
        auto q = variable("Q");

        auto implication =
            logical_implies(p, q);

        std::cout
            << "Formula: "
            << implication->describe()
            << "\n\n";

        print_truth_table(*implication);

        std::cout
            << "\nClassification: "
            << classification_name(
                classify(*implication)
            )
            << "\n";

        // ---------------------------------------------------------------------
        // Biconditional.
        // ---------------------------------------------------------------------

        auto iff_formula =
            logical_iff(
                variable("P"),
                variable("Q")
            );

        std::cout
            << "\nFormula: "
            << iff_formula->describe()
            << "\n";

        print_truth_table(*iff_formula);

        // ---------------------------------------------------------------------
        // Precedence example.
        //
        // NOT P OR Q AND R
        //
        // means:
        //
        // (NOT P) OR (Q AND R)
        //
        // because NOT has higher precedence than AND, and AND has higher
        // precedence than OR in the conventional hierarchy.
        // ---------------------------------------------------------------------

        auto precedence_formula =
            logical_or(
                logical_not(variable("P")),
                logical_and(
                    variable("Q"),
                    variable("R")
                )
            );

        std::cout
            << "\nPrecedence formula:\n"
            << precedence_formula->describe()
            << "\n";

        print_truth_table(*precedence_formula);

        // ---------------------------------------------------------------------
        // Enterprise authorization policy.
        // ---------------------------------------------------------------------

        auto policy_expression =
            build_enterprise_policy();

        AccessPolicy policy(
            policy_expression
        );

        std::cout
            << "\n============================================================\n"
            << "ENTERPRISE ACCESS POLICY\n"
            << "============================================================\n";

        std::cout
            << "Policy:\n"
            << policy.expression().describe()
            << "\n\n";

        UserContext administrator{
            true,
            true,
            true,
            true,
            false,
            false
        };

        UserContext owner{
            true,
            true,
            true,
            false,
            true,
            false
        };

        UserContext unauthenticated{
            false,
            true,
            true,
            true,
            false,
            false
        };

        UserContext missing_mfa{
            true,
            true,
            false,
            true,
            false,
            false
        };

        UserContext emergency_locked{
            true,
            true,
            true,
            true,
            true,
            true
        };

        UserContext inactive_account{
            true,
            false,
            true,
            true,
            false,
            false
        };

        print_context(
            administrator,
            policy,
            "Administrator"
        );

        print_context(
            owner,
            policy,
            "Resource owner"
        );

        print_context(
            unauthenticated,
            policy,
            "Unauthenticated"
        );

        print_context(
            missing_mfa,
            policy,
            "Missing MFA"
        );

        print_context(
            emergency_locked,
            policy,
            "Emergency lock"
        );

        print_context(
            inactive_account,
            policy,
            "Inactive account"
        );

        // ---------------------------------------------------------------------
        // Satisfiability.
        // ---------------------------------------------------------------------

        const auto solutions =
            satisfying_assignments(
                *precedence_formula
            );

        std::cout
            << "\n============================================================\n"
            << "SATISFIABILITY\n"
            << "============================================================\n";

        std::cout
            << "Number of satisfying assignments: "
            << solutions.size()
            << "\n";

        for (const auto& assignment : solutions) {
            std::cout << "{ ";

            for (const auto& [name, value] : assignment) {
                std::cout
                    << name
                    << "="
                    << std::boolalpha
                    << value
                    << " ";
            }

            std::cout << "}\n";
        }

        // ---------------------------------------------------------------------
        // Equivalence.
        // ---------------------------------------------------------------------

        auto implication_definition =
            logical_or(
                logical_not(variable("P")),
                variable("Q")
            );

        std::cout
            << "\nP -> Q equivalent to NOT P OR Q: "
            << std::boolalpha
            << equivalent(
                *implication,
                *implication_definition
            )
            << '\n';

        // ---------------------------------------------------------------------
        // Counterexample.
        // ---------------------------------------------------------------------

        auto converse =
            logical_implies(
                variable("Q"),
                variable("P")
            );

        const auto counterexample =
            find_counterexample(
                *implication,
                *converse
            );

        std::cout
            << "\nCounterexample to P -> Q == Q -> P:\n";

        if (counterexample.has_value()) {
            for (const auto& [name, value] :
                 counterexample.value()) {
                std::cout
                    << name
                    << "="
                    << value
                    << " ";
            }

            std::cout << '\n';
        } else {
            std::cout << "No counterexample exists.\n";
        }

        // ---------------------------------------------------------------------
        // Argument validity.
        //
        // Modus Ponens:
        //
        // P -> Q
        // P
        // therefore Q
        // ---------------------------------------------------------------------

        auto premise_one =
            logical_implies(
                variable("P"),
                variable("Q")
            );

        auto premise_two =
            variable("P");

        auto conclusion =
            variable("Q");

        const bool modus_ponens =
            argument_valid(
                {
                    premise_one,
                    premise_two
                },
                *conclusion
            );

        std::cout
            << "\nModus Ponens valid: "
            << modus_ponens
            << '\n';

        // ---------------------------------------------------------------------
        // Invalid converse-style argument.
        //
        // P -> Q
        // Q
        // therefore P
        //
        // This is not valid because P=false, Q=true is a counterexample.
        // ---------------------------------------------------------------------

        auto invalid_premise_two =
            variable("Q");

        const bool converse_argument =
            argument_valid(
                {
                    premise_one,
                    invalid_premise_two
                },
                *variable("P")
            );

        std::cout
            << "Converse-style argument valid: "
            << converse_argument
            << '\n';

        // ---------------------------------------------------------------------
        // Complexity demonstration.
        // ---------------------------------------------------------------------

        std::cout
            << "\n============================================================\n"
            << "TRUTH-TABLE COMPLEXITY\n"
            << "============================================================\n";

        for (std::size_t n = 1; n <= 20; n += 3) {
            const unsigned long long rows =
                1ULL << n;

            std::cout
                << n
                << " variables -> "
                << rows
                << " assignments\n";
        }

        // ---------------------------------------------------------------------
        // Error handling demonstration.
        // ---------------------------------------------------------------------

        std::cout
            << "\n============================================================\n"
            << "ERROR HANDLING\n"
            << "============================================================\n";

        try {
            Assignment incomplete{
                {"P", true}
            };

            implication->evaluate(incomplete);
        }
        catch (const std::exception& error) {
            std::cout
                << "Handled evaluation error: "
                << error.what()
                << '\n';
        }

        // ---------------------------------------------------------------------
        // Security-oriented observation.
        // ---------------------------------------------------------------------
        //
        // The policy engine does not infer intent. It evaluates an explicitly
        // constructed logical expression against an explicitly supplied
        // context. This separation improves auditability.
        // ---------------------------------------------------------------------

        std::cout
            << "\nThe authorization policy was evaluated using an explicit\n"
            << "Boolean expression tree and validated input context.\n";

        std::cout
            << "\n============================================================\n"
            << "CASE STUDY COMPLETE\n"
            << "============================================================\n";

        return 0;
    }
    catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }
}
