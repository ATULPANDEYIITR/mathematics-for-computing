/*
 * Logic Foundations: A C++17 Technical Case Study
 *
 * Scenario:
 *   A policy engine evaluates access requests for a security-sensitive
 *   enterprise application.
 *
 * The implementation progressively introduces:
 *   - Boolean propositions
 *   - logical connectives
 *   - compound expressions
 *   - expression trees
 *   - validation
 *   - truth-table analysis
 *   - satisfiability
 *   - argument validity
 *   - counterexamples
 *   - access-control policy evaluation
 *   - complexity considerations
 *
 * Build:
 *   g++ -std=c++17 -O2 logic_foundations.cpp -o logic_foundations
 */

#include <algorithm>
#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using Assignment = std::map<std::string, bool>;
using Evaluator = std::function<bool(const Assignment&)>;


// ============================================================================
// 1. BASIC PROPOSITIONS
// ============================================================================

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

bool implication(bool antecedent, bool consequent) {
    // p -> q is false only when p is true and q is false.
    return !antecedent || consequent;
}

bool biconditional(bool left, bool right) {
    return left == right;
}


// ============================================================================
// 2. GENERATING ALL BOOLEAN ASSIGNMENTS
// ============================================================================

std::vector<Assignment> generateAssignments(
    const std::vector<std::string>& variables
) {
    std::vector<Assignment> assignments;

    const std::size_t count = variables.size();

    // n Boolean variables produce 2^n possible assignments.
    const std::size_t total = std::size_t{1} << count;

    for (std::size_t mask = 0; mask < total; ++mask) {
        Assignment assignment;

        for (std::size_t i = 0; i < count; ++i) {
            assignment[variables[i]] =
                ((mask >> i) & std::size_t{1}) != 0;
        }

        assignments.push_back(std::move(assignment));
    }

    return assignments;
}


// ============================================================================
// 3. TRUTH TABLE SUPPORT
// ============================================================================

struct TruthRow {
    Assignment assignment;
    bool result;
};

std::vector<TruthRow> truthTable(
    const std::vector<std::string>& variables,
    const Evaluator& expression
) {
    std::vector<TruthRow> rows;

    for (const Assignment& assignment : generateAssignments(variables)) {
        rows.push_back({
            assignment,
            expression(assignment)
        });
    }

    return rows;
}

void printTruthTable(
    const std::vector<std::string>& variables,
    const Evaluator& expression,
    const std::string& title
) {
    std::cout << "\n" << title << "\n";

    for (const std::string& variable : variables) {
        std::cout << std::setw(6) << variable;
    }

    std::cout << std::setw(10) << "Result" << "\n";

    for (std::size_t i = 0;
         i < variables.size() * 6 + 10;
         ++i) {
        std::cout << '-';
    }

    std::cout << "\n";

    for (const TruthRow& row : truthTable(variables, expression)) {
        for (const std::string& variable : variables) {
            std::cout
                << std::setw(6)
                << (row.assignment.at(variable) ? "T" : "F");
        }

        std::cout
            << std::setw(10)
            << (row.result ? "T" : "F")
            << "\n";
    }
}


// ============================================================================
// 4. FORMULA CLASSIFICATION
// ============================================================================

bool isTautology(
    const std::vector<std::string>& variables,
    const Evaluator& expression
) {
    for (const TruthRow& row : truthTable(variables, expression)) {
        if (!row.result) {
            return false;
        }
    }

    return true;
}

bool isContradiction(
    const std::vector<std::string>& variables,
    const Evaluator& expression
) {
    for (const TruthRow& row : truthTable(variables, expression)) {
        if (row.result) {
            return false;
        }
    }

    return true;
}

bool isContingency(
    const std::vector<std::string>& variables,
    const Evaluator& expression
) {
    return !isTautology(variables, expression) &&
           !isContradiction(variables, expression);
}

bool logicallyEquivalent(
    const std::vector<std::string>& variables,
    const Evaluator& first,
    const Evaluator& second
) {
    for (const Assignment& assignment : generateAssignments(variables)) {
        if (first(assignment) != second(assignment)) {
            return false;
        }
    }

    return true;
}


// ============================================================================
// 5. ARGUMENT VALIDITY
// ============================================================================

bool argumentIsValid(
    const std::vector<std::string>& variables,
    const std::vector<Evaluator>& premises,
    const Evaluator& conclusion
) {
    for (const Assignment& assignment : generateAssignments(variables)) {
        bool allPremisesTrue = true;

        for (const Evaluator& premise : premises) {
            if (!premise(assignment)) {
                allPremisesTrue = false;
                break;
            }
        }

        if (allPremisesTrue && !conclusion(assignment)) {
            return false;
        }
    }

    return true;
}

bool findCounterexample(
    const std::vector<std::string>& variables,
    const std::vector<Evaluator>& premises,
    const Evaluator& conclusion,
    Assignment& counterexample
) {
    for (const Assignment& assignment : generateAssignments(variables)) {
        bool allPremisesTrue = true;

        for (const Evaluator& premise : premises) {
            if (!premise(assignment)) {
                allPremisesTrue = false;
                break;
            }
        }

        if (allPremisesTrue && !conclusion(assignment)) {
            counterexample = assignment;
            return true;
        }
    }

    return false;
}


// ============================================================================
// 6. EXPRESSION TREE ARCHITECTURE
// ============================================================================

class Formula {
public:
    virtual ~Formula() = default;

    virtual bool evaluate(const Assignment& assignment) const = 0;

    virtual std::set<std::string> variables() const = 0;
};

using FormulaPtr = std::shared_ptr<const Formula>;

class Variable final : public Formula {
private:
    std::string name_;

public:
    explicit Variable(std::string name)
        : name_(std::move(name)) {}

    bool evaluate(const Assignment& assignment) const override {
        const auto iterator = assignment.find(name_);

        if (iterator == assignment.end()) {
            throw std::invalid_argument(
                "Missing truth value for variable: " + name_
            );
        }

        return iterator->second;
    }

    std::set<std::string> variables() const override {
        return {name_};
    }
};

class Not final : public Formula {
private:
    FormulaPtr operand_;

public:
    explicit Not(FormulaPtr operand)
        : operand_(std::move(operand)) {
        if (!operand_) {
            throw std::invalid_argument("NOT requires an operand");
        }
    }

    bool evaluate(const Assignment& assignment) const override {
        return !operand_->evaluate(assignment);
    }

    std::set<std::string> variables() const override {
        return operand_->variables();
    }
};

class And final : public Formula {
private:
    FormulaPtr left_;
    FormulaPtr right_;

public:
    And(FormulaPtr left, FormulaPtr right)
        : left_(std::move(left)),
          right_(std::move(right)) {
        if (!left_ || !right_) {
            throw std::invalid_argument(
                "AND requires two operands"
            );
        }
    }

    bool evaluate(const Assignment& assignment) const override {
        return left_->evaluate(assignment) &&
               right_->evaluate(assignment);
    }

    std::set<std::string> variables() const override {
        std::set<std::string> result = left_->variables();

        const auto rightVariables = right_->variables();
        result.insert(rightVariables.begin(), rightVariables.end());

        return result;
    }
};

class Or final : public Formula {
private:
    FormulaPtr left_;
    FormulaPtr right_;

public:
    Or(FormulaPtr left, FormulaPtr right)
        : left_(std::move(left)),
          right_(std::move(right)) {
        if (!left_ || !right_) {
            throw std::invalid_argument(
                "OR requires two operands"
            );
        }
    }

    bool evaluate(const Assignment& assignment) const override {
        return left_->evaluate(assignment) ||
               right_->evaluate(assignment);
    }

    std::set<std::string> variables() const override {
        std::set<std::string> result = left_->variables();

        const auto rightVariables = right_->variables();
        result.insert(rightVariables.begin(), rightVariables.end());

        return result;
    }
};

class Implies final : public Formula {
private:
    FormulaPtr antecedent_;
    FormulaPtr consequent_;

public:
    Implies(FormulaPtr antecedent, FormulaPtr consequent)
        : antecedent_(std::move(antecedent)),
          consequent_(std::move(consequent)) {
        if (!antecedent_ || !consequent_) {
            throw std::invalid_argument(
                "Implication requires two operands"
            );
        }
    }

    bool evaluate(const Assignment& assignment) const override {
        return !antecedent_->evaluate(assignment) ||
               consequent_->evaluate(assignment);
    }

    std::set<std::string> variables() const override {
        std::set<std::string> result = antecedent_->variables();

        const auto rightVariables = consequent_->variables();
        result.insert(rightVariables.begin(), rightVariables.end());

        return result;
    }
};

class Iff final : public Formula {
private:
    FormulaPtr left_;
    FormulaPtr right_;

public:
    Iff(FormulaPtr left, FormulaPtr right)
        : left_(std::move(left)),
          right_(std::move(right)) {
        if (!left_ || !right_) {
            throw std::invalid_argument(
                "Biconditional requires two operands"
            );
        }
    }

    bool evaluate(const Assignment& assignment) const override {
        return left_->evaluate(assignment) ==
               right_->evaluate(assignment);
    }

    std::set<std::string> variables() const override {
        std::set<std::string> result = left_->variables();

        const auto rightVariables = right_->variables();
        result.insert(rightVariables.begin(), rightVariables.end());

        return result;
    }
};


// ============================================================================
// 7. STRUCTURED FORMULA ANALYSIS
// ============================================================================

std::string classifyFormula(const FormulaPtr& formula) {
    if (!formula) {
        throw std::invalid_argument("Formula cannot be null");
    }

    const std::set<std::string> variableSet = formula->variables();

    const std::vector<std::string> variables(
        variableSet.begin(),
        variableSet.end()
    );

    const Evaluator evaluator =
        [formula](const Assignment& assignment) {
            return formula->evaluate(assignment);
        };

    if (isTautology(variables, evaluator)) {
        return "tautology";
    }

    if (isContradiction(variables, evaluator)) {
        return "contradiction";
    }

    return "contingency";
}


// ============================================================================
// 8. ACCESS-CONTROL DOMAIN MODEL
// ============================================================================

struct AccessRequest {
    bool authenticated = false;
    bool administrator = false;
    bool accountActive = false;
    bool multiFactorAuthenticated = false;
    bool networkTrusted = false;
};

class AccessPolicy {
public:
    virtual ~AccessPolicy() = default;

    virtual bool authorize(
        const AccessRequest& request
    ) const = 0;

    virtual std::string name() const = 0;
};

class BasicAdminPolicy final : public AccessPolicy {
public:
    bool authorize(
        const AccessRequest& request
    ) const override {
        // Formal proposition:
        //
        // authenticated AND administrator AND accountActive
        //
        // Every condition must be true.
        return request.authenticated &&
               request.administrator &&
               request.accountActive;
    }

    std::string name() const override {
        return "Basic administrator policy";
    }
};

class StrongAdminPolicy final : public AccessPolicy {
public:
    bool authorize(
        const AccessRequest& request
    ) const override {
        // A stronger compound policy:
        //
        // authenticated
        // AND administrator
        // AND accountActive
        // AND multiFactorAuthenticated
        // AND networkTrusted
        //
        // The expression is deliberately explicit so the logical structure
        // can be reviewed independently from the surrounding application.
        return request.authenticated &&
               request.administrator &&
               request.accountActive &&
               request.multiFactorAuthenticated &&
               request.networkTrusted;
    }

    std::string name() const override {
        return "Strong administrator policy";
    }
};


// ============================================================================
// 9. POLICY VALIDATION
// ============================================================================

void validateAccessRequest(const AccessRequest& request) {
    // The fields are already Boolean, so structural validation is trivial.
    // In a real application, additional validation would normally concern
    // identity provenance, freshness, authorization context, and policy
    // configuration.
    (void)request;
}

void printRequest(
    const AccessRequest& request,
    const AccessPolicy& policy
) {
    validateAccessRequest(request);

    std::cout
        << policy.name()
        << " => "
        << (policy.authorize(request) ? "ALLOW" : "DENY")
        << "\n";
}


// ============================================================================
// 10. BUSINESS TRANSACTION POLICY
// ============================================================================

struct TransactionRequest {
    bool accountActive = false;
    bool amountWithinLimit = false;
    bool managerApproved = false;
};

bool transactionAllowed(
    const TransactionRequest& request
) {
    // accountActive AND
    // (amountWithinLimit OR managerApproved)
    return request.accountActive &&
           (request.amountWithinLimit ||
            request.managerApproved);
}


// ============================================================================
// 11. SATISFIABILITY OF A FORMULA
// ============================================================================

std::vector<Assignment> satisfyingAssignments(
    const std::vector<std::string>& variables,
    const Evaluator& expression
) {
    std::vector<Assignment> solutions;

    for (const Assignment& assignment : generateAssignments(variables)) {
        if (expression(assignment)) {
            solutions.push_back(assignment);
        }
    }

    return solutions;
}

void printAssignment(const Assignment& assignment) {
    std::cout << "{ ";

    bool first = true;

    for (const auto& [variable, value] : assignment) {
        if (!first) {
            std::cout << ", ";
        }

        std::cout
            << variable
            << "="
            << (value ? "T" : "F");

        first = false;
    }

    std::cout << " }";
}


// ============================================================================
// 12. COMPLEXITY MEASUREMENT
// ============================================================================

void printTruthTableGrowth() {
    std::cout << "\nTruth-table growth:\n";

    for (int variableCount = 1; variableCount <= 15; ++variableCount) {
        const std::size_t rows =
            std::size_t{1} << variableCount;

        std::cout
            << std::setw(2)
            << variableCount
            << " variables -> "
            << std::setw(6)
            << rows
            << " assignments\n";
    }
}


// ============================================================================
// 13. MAIN CASE STUDY
// ============================================================================

int main() {
    try {
        std::cout
            << "Logic Foundations: C++ Access Policy Case Study\n";

        // --------------------------------------------------------------------
        // Basic truth-functional examples
        // --------------------------------------------------------------------

        const bool p = true;
        const bool q = false;

        std::cout << "\nBasic propositions:\n";
        std::cout << "p = " << std::boolalpha << p << "\n";
        std::cout << "q = " << q << "\n";
        std::cout << "NOT p = " << logical_not(p) << "\n";
        std::cout << "p AND q = " << logical_and(p, q) << "\n";
        std::cout << "p OR q = " << logical_or(p, q) << "\n";
        std::cout << "p XOR q = " << logical_xor(p, q) << "\n";
        std::cout << "p -> q = " << implication(p, q) << "\n";
        std::cout << "p <-> q = " << biconditional(p, q) << "\n";

        // --------------------------------------------------------------------
        // Truth table
        // --------------------------------------------------------------------

        printTruthTable(
            {"p", "q"},
            [](const Assignment& assignment) {
                return assignment.at("p") &&
                       assignment.at("q");
            },
            "Truth table: p AND q"
        );

        printTruthTable(
            {"p", "q"},
            [](const Assignment& assignment) {
                return implication(
                    assignment.at("p"),
                    assignment.at("q")
                );
            },
            "Truth table: p -> q"
        );

        // --------------------------------------------------------------------
        // Compound formula
        // --------------------------------------------------------------------

        const Evaluator compound =
            [](const Assignment& assignment) {
                return (
                    assignment.at("p") &&
                    assignment.at("q")
                ) || !assignment.at("r");
            };

        printTruthTable(
            {"p", "q", "r"},
            compound,
            "Truth table: (p AND q) OR NOT r"
        );

        // --------------------------------------------------------------------
        // Logical laws
        // --------------------------------------------------------------------

        std::cout << "\nLogical equivalence tests:\n";

        const bool deMorganAnd = logicallyEquivalent(
            {"p", "q"},
            [](const Assignment& a) {
                return !(a.at("p") && a.at("q"));
            },
            [](const Assignment& a) {
                return !a.at("p") || !a.at("q");
            }
        );

        std::cout
            << "De Morgan AND: "
            << deMorganAnd
            << "\n";

        const bool deMorganOr = logicallyEquivalent(
            {"p", "q"},
            [](const Assignment& a) {
                return !(a.at("p") || a.at("q"));
            },
            [](const Assignment& a) {
                return !a.at("p") && !a.at("q");
            }
        );

        std::cout
            << "De Morgan OR: "
            << deMorganOr
            << "\n";

        const bool implicationRewrite = logicallyEquivalent(
            {"p", "q"},
            [](const Assignment& a) {
                return implication(
                    a.at("p"),
                    a.at("q")
                );
            },
            [](const Assignment& a) {
                return !a.at("p") || a.at("q");
            }
        );

        std::cout
            << "Implication rewrite: "
            << implicationRewrite
            << "\n";

        // --------------------------------------------------------------------
        // Classification
        // --------------------------------------------------------------------

        std::cout << "\nFormula classification:\n";

        std::cout
            << "p OR NOT p: "
            << (isTautology(
                    {"p"},
                    [](const Assignment& a) {
                        return a.at("p") ||
                               !a.at("p");
                    }
                ) ? "tautology" : "not a tautology")
            << "\n";

        std::cout
            << "p AND NOT p: "
            << (isContradiction(
                    {"p"},
                    [](const Assignment& a) {
                        return a.at("p") &&
                               !a.at("p");
                    }
                ) ? "contradiction" : "not a contradiction")
            << "\n";

        // --------------------------------------------------------------------
        // Argument validity
        // --------------------------------------------------------------------

        const bool modusPonens = argumentIsValid(
            {"p", "q"},
            {
                [](const Assignment& a) {
                    return implication(
                        a.at("p"),
                        a.at("q")
                    );
                },
                [](const Assignment& a) {
                    return a.at("p");
                }
            },
            [](const Assignment& a) {
                return a.at("q");
            }
        );

        std::cout
            << "\nModus ponens valid: "
            << modusPonens
            << "\n";

        const bool affirmingConsequent = argumentIsValid(
            {"p", "q"},
            {
                [](const Assignment& a) {
                    return implication(
                        a.at("p"),
                        a.at("q")
                    );
                },
                [](const Assignment& a) {
                    return a.at("q");
                }
            },
            [](const Assignment& a) {
                return a.at("p");
            }
        );

        std::cout
            << "Affirming the consequent valid: "
            << affirmingConsequent
            << "\n";

        Assignment counterexample;

        if (findCounterexample(
                {"p", "q"},
                {
                    [](const Assignment& a) {
                        return implication(
                            a.at("p"),
                            a.at("q")
                        );
                    },
                    [](const Assignment& a) {
                        return a.at("q");
                    }
                },
                [](const Assignment& a) {
                    return a.at("p");
                },
                counterexample
            )) {
            std::cout << "Counterexample: ";
            printAssignment(counterexample);
            std::cout << "\n";
        }

        // --------------------------------------------------------------------
        // Expression tree
        // --------------------------------------------------------------------

        const FormulaPtr P =
            std::make_shared<Variable>("p");

        const FormulaPtr Q =
            std::make_shared<Variable>("q");

        const FormulaPtr R =
            std::make_shared<Variable>("r");

        // (p AND q) OR NOT r
        const FormulaPtr expression =
            std::make_shared<Or>(
                std::make_shared<And>(P, Q),
                std::make_shared<Not>(R)
            );

        const std::set<std::string> expressionVariables =
            expression->variables();

        const std::vector<std::string> expressionVariableList(
            expressionVariables.begin(),
            expressionVariables.end()
        );

        std::cout
            << "\nExpression tree classification: "
            << classifyFormula(expression)
            << "\n";

        printTruthTable(
            expressionVariableList,
            [expression](const Assignment& assignment) {
                return expression->evaluate(assignment);
            },
            "Expression-tree truth table"
        );

        // --------------------------------------------------------------------
        // Expression-tree implication
        // --------------------------------------------------------------------

        const FormulaPtr implicationExpression =
            std::make_shared<Implies>(P, Q);

        std::cout
            << "\nImplication expression classification: "
            << classifyFormula(implicationExpression)
            << "\n";

        // --------------------------------------------------------------------
        // Access-control case study
        // --------------------------------------------------------------------

        std::cout
            << "\nAccess-control case study:\n";

        const BasicAdminPolicy basicPolicy;
        const StrongAdminPolicy strongPolicy;

        const std::vector<AccessRequest> requests = {
            {true, true, true, true, true},
            {true, true, false, true, true},
            {true, false, true, true, true},
            {false, true, true, true, true},
            {true, true, true, false, true},
            {true, true, true, true, false}
        };

        for (const AccessRequest& request : requests) {
            printRequest(request, basicPolicy);
            printRequest(request, strongPolicy);
            std::cout << "\n";
        }

        // --------------------------------------------------------------------
        // Transaction policy
        // --------------------------------------------------------------------

        std::cout
            << "Transaction policy:\n";

        const std::vector<TransactionRequest> transactions = {
            {true, true, false},
            {true, false, true},
            {true, false, false},
            {false, true, true}
        };

        for (const TransactionRequest& request : transactions) {
            std::cout
                << "accountActive="
                << request.accountActive
                << ", amountWithinLimit="
                << request.amountWithinLimit
                << ", managerApproved="
                << request.managerApproved
                << " => "
                << transactionAllowed(request)
                << "\n";
        }

        // --------------------------------------------------------------------
        // Satisfiability
        // --------------------------------------------------------------------

        const Evaluator satisfiableFormula =
            [](const Assignment& assignment) {
                const bool p = assignment.at("p");
                const bool q = assignment.at("q");
                const bool r = assignment.at("r");

                return (p || q) && (!p || r);
            };

        const auto solutions =
            satisfyingAssignments(
                {"p", "q", "r"},
                satisfiableFormula
            );

        std::cout
            << "\nSatisfying assignments: "
            << solutions.size()
            << "\n";

        for (const Assignment& solution : solutions) {
            printAssignment(solution);
            std::cout << "\n";
        }

        // --------------------------------------------------------------------
        // Edge case: missing variable
        // --------------------------------------------------------------------

        std::cout << "\nEdge-case validation:\n";

        try {
            Assignment incomplete{{"p", true}};
            expression->evaluate(incomplete);
        } catch (const std::exception& error) {
            std::cout
                << "Expected validation error: "
                << error.what()
                << "\n";
        }

        // --------------------------------------------------------------------
        // Complexity
        // --------------------------------------------------------------------

        printTruthTableGrowth();

        // --------------------------------------------------------------------
        // Assertions through runtime checks
        // --------------------------------------------------------------------

        if (!isTautology(
                {"p"},
                [](const Assignment& a) {
                    return a.at("p") ||
                           !a.at("p");
                }
            )) {
            throw std::runtime_error(
                "Excluded-middle law verification failed"
            );
        }

        if (!isContradiction(
                {"p"},
                [](const Assignment& a) {
                    return a.at("p") &&
                           !a.at("p");
                }
            )) {
            throw std::runtime_error(
                "Non-contradiction law verification failed"
            );
        }

        if (!logicallyEquivalent(
                {"p", "q"},
                [](const Assignment& a) {
                    return implication(
                        a.at("p"),
                        a.at("q")
                    );
                },
                [](const Assignment& a) {
                    return implication(
                        !a.at("q"),
                        !a.at("p")
                    );
                }
            )) {
            throw std::runtime_error(
                "Contrapositive verification failed"
            );
        }

        std::cout
            << "\nAll technical verification checks passed.\n";

    } catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << "\n";

        return 1;
    }

    return 0;
}
