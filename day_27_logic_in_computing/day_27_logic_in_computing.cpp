/*
 * Logic in Computing
 * ==================
 *
 * C++17 technical case study:
 * Policy-driven transaction authorization and verification engine.
 *
 * The system demonstrates how digital Boolean logic maps into a realistic
 * software system. It includes:
 *
 * - Boolean predicates
 * - Compound logical expressions
 * - Truth-table-style exhaustive verification
 * - Assertions and invariants
 * - Rule composition
 * - Validation and error handling
 * - Decision explanations
 * - Test cases and counterexamples
 * - Complexity considerations
 * - Integer bit-level logic
 *
 * Compile:
 *     g++ -std=c++17 -Wall -Wextra -pedantic logic_case_study.cpp -o logic_case_study
 *
 * Run:
 *     ./logic_case_study
 */

#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <exception>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>


// ============================================================================
// 1. BASIC DIGITAL LOGIC
// ============================================================================

bool logic_not(bool value) {
    return !value;
}

bool logic_and(bool left, bool right) {
    return left && right;
}

bool logic_or(bool left, bool right) {
    return left || right;
}

bool logic_xor(bool left, bool right) {
    return left != right;
}

bool logic_nand(bool left, bool right) {
    return !(left && right);
}

bool logic_nor(bool left, bool right) {
    return !(left || right);
}

bool logic_xnor(bool left, bool right) {
    return left == right;
}

bool implication(bool antecedent, bool consequent) {
    // P -> Q is equivalent to NOT P OR Q.
    return !antecedent || consequent;
}


// ============================================================================
// 2. TRUTH TABLE VERIFICATION
// ============================================================================

void printTwoInputTruthTable(
    const std::string& name,
    const std::function<bool(bool, bool)>& operation
) {
    std::cout << "\n" << name << "\n";
    std::cout << "A B | Result\n";
    std::cout << "----+-------\n";

    for (bool a : {false, true}) {
        for (bool b : {false, true}) {
            std::cout
                << static_cast<int>(a) << " "
                << static_cast<int>(b) << " |   "
                << static_cast<int>(operation(a, b))
                << "\n";
        }
    }
}

void demonstrateDigitalLogic() {
    printTwoInputTruthTable("AND", logic_and);
    printTwoInputTruthTable("OR", logic_or);
    printTwoInputTruthTable("XOR", logic_xor);
    printTwoInputTruthTable("NAND", logic_nand);
    printTwoInputTruthTable("NOR", logic_nor);
    printTwoInputTruthTable("XNOR", logic_xnor);

    std::cout << "\nNOT\n";
    for (bool value : {false, true}) {
        std::cout
            << static_cast<int>(value)
            << " -> "
            << static_cast<int>(logic_not(value))
            << "\n";
    }
}


// ============================================================================
// 3. BIT-LEVEL LOGIC
// ============================================================================

struct HalfAdderResult {
    bool sum;
    bool carry;
};

HalfAdderResult halfAdder(bool a, bool b) {
    /*
     * Sum uses XOR.
     * Carry uses AND.
     */
    return {
        logic_xor(a, b),
        logic_and(a, b)
    };
}

struct FullAdderResult {
    bool sum;
    bool carryOut;
};

FullAdderResult fullAdder(bool a, bool b, bool carryIn) {
    const HalfAdderResult first = halfAdder(a, b);
    const HalfAdderResult second = halfAdder(first.sum, carryIn);

    return {
        second.sum,
        logic_or(first.carry, second.carry)
    };
}

std::uint32_t addUsingFullAdders(
    std::uint32_t left,
    std::uint32_t right
) {
    /*
     * Addition is performed one bit at a time using full adders.
     *
     * This is a software model of the fundamental mechanism behind binary
     * addition hardware. It is intentionally restricted to 32 bits.
     */
    std::uint32_t result = 0;
    bool carry = false;

    for (unsigned bit = 0; bit < 32; ++bit) {
        const bool a = ((left >> bit) & 1U) != 0;
        const bool b = ((right >> bit) & 1U) != 0;

        const FullAdderResult current = fullAdder(a, b, carry);

        if (current.sum) {
            result |= (1U << bit);
        }

        carry = current.carryOut;
    }

    if (carry) {
        /*
         * The fixed-width operation overflowed.
         * The low 32 bits remain available, while the carry represents
         * information outside the selected width.
         */
        std::cerr << "Warning: 32-bit unsigned addition overflowed.\n";
    }

    return result;
}

void demonstrateBitLevelLogic() {
    std::cout << "\n=== BIT-LEVEL LOGIC ===\n";

    const std::uint32_t a = 13;
    const std::uint32_t b = 9;

    std::cout
        << a
        << " + "
        << b
        << " using full adders = "
        << addUsingFullAdders(a, b)
        << "\n";
}


// ============================================================================
// 4. DOMAIN MODEL
// ============================================================================

struct Transaction {
    double amount{};
    int accountAgeDays{};
    bool identityVerified{};
    bool suspiciousLocation{};
    bool trustedDevice{};
};

struct PolicyDecision {
    bool amountValid{};
    bool matureAccount{};
    bool identityVerified{};
    bool safeLocation{};
    bool trustedDeviceOrLowValue{};
    bool allowed{};
};


// ============================================================================
// 5. VALIDATION
// ============================================================================

void validateTransaction(const Transaction& transaction) {
    /*
     * Input validation protects the logical layer from invalid domain data.
     * A predicate should not silently reinterpret impossible input as a valid
     * business state.
     */
    if (!std::isfinite(transaction.amount)) {
        throw std::invalid_argument(
            "Transaction amount must be finite."
        );
    }

    if (transaction.amount < 0.0) {
        throw std::invalid_argument(
            "Transaction amount cannot be negative."
        );
    }

    if (transaction.accountAgeDays < 0) {
        throw std::invalid_argument(
            "Account age cannot be negative."
        );
    }
}


// ============================================================================
// 6. PREDICATE-BASED POLICY
// ============================================================================

PolicyDecision evaluateTransaction(const Transaction& transaction) {
    validateTransaction(transaction);

    const bool amountValid =
        transaction.amount > 0.0;

    const bool matureAccount =
        transaction.accountAgeDays >= 30;

    const bool identityVerified =
        transaction.identityVerified;

    const bool safeLocation =
        !transaction.suspiciousLocation;

    const bool trustedDeviceOrLowValue =
        transaction.trustedDevice ||
        transaction.amount <= 1000.0;

    /*
     * Final compound predicate:
     *
     * amountValid
     * AND matureAccount
     * AND identityVerified
     * AND safeLocation
     * AND (trustedDevice OR lowValue)
     */
    const bool allowed =
        amountValid &&
        matureAccount &&
        identityVerified &&
        safeLocation &&
        trustedDeviceOrLowValue;

    return {
        amountValid,
        matureAccount,
        identityVerified,
        safeLocation,
        trustedDeviceOrLowValue,
        allowed
    };
}

void printDecision(const PolicyDecision& decision) {
    std::cout
        << "  amountValid              = "
        << std::boolalpha << decision.amountValid << "\n";

    std::cout
        << "  matureAccount            = "
        << decision.matureAccount << "\n";

    std::cout
        << "  identityVerified         = "
        << decision.identityVerified << "\n";

    std::cout
        << "  safeLocation             = "
        << decision.safeLocation << "\n";

    std::cout
        << "  trustedDeviceOrLowValue  = "
        << decision.trustedDeviceOrLowValue << "\n";

    std::cout
        << "  ALLOWED                  = "
        << decision.allowed << "\n";
}


// ============================================================================
// 7. RULE ABSTRACTION
// ============================================================================

class Rule {
public:
    using Predicate = std::function<bool(const Transaction&)>;

    Rule(std::string name, Predicate predicate)
        : name_(std::move(name)),
          predicate_(std::move(predicate)) {
        if (name_.empty()) {
            throw std::invalid_argument(
                "Rule name cannot be empty."
            );
        }

        if (!predicate_) {
            throw std::invalid_argument(
                "Rule predicate cannot be empty."
            );
        }
    }

    const std::string& name() const {
        return name_;
    }

    bool evaluate(const Transaction& transaction) const {
        return predicate_(transaction);
    }

private:
    std::string name_;
    Predicate predicate_;
};


// ============================================================================
// 8. RULE ENGINE
// ============================================================================

class RuleEngine {
public:
    void addRule(Rule rule) {
        rules_.push_back(std::move(rule));
    }

    std::map<std::string, bool> evaluate(
        const Transaction& transaction
    ) const {
        std::map<std::string, bool> results;

        for (const Rule& rule : rules_) {
            results[rule.name()] = rule.evaluate(transaction);
        }

        return results;
    }

    bool isAllowed(const Transaction& transaction) const {
        for (const Rule& rule : rules_) {
            /*
             * Short-circuit behavior means later rules are not evaluated
             * after a failure. This can improve performance, but if every
             * rule must be audited, evaluate() should be used instead.
             */
            if (!rule.evaluate(transaction)) {
                return false;
            }
        }

        return true;
    }

private:
    std::vector<Rule> rules_;
};


// ============================================================================
// 9. POLICY CONSTRUCTION
// ============================================================================

RuleEngine createPolicyEngine() {
    RuleEngine engine;

    engine.addRule(
        Rule(
            "Positive transaction amount",
            [](const Transaction& transaction) {
                return transaction.amount > 0.0;
            }
        )
    );

    engine.addRule(
        Rule(
            "Account age at least 30 days",
            [](const Transaction& transaction) {
                return transaction.accountAgeDays >= 30;
            }
        )
    );

    engine.addRule(
        Rule(
            "Identity verified",
            [](const Transaction& transaction) {
                return transaction.identityVerified;
            }
        )
    );

    engine.addRule(
        Rule(
            "Location is not suspicious",
            [](const Transaction& transaction) {
                return !transaction.suspiciousLocation;
            }
        )
    );

    engine.addRule(
        Rule(
            "Trusted device or low-value transaction",
            [](const Transaction& transaction) {
                return (
                    transaction.trustedDevice ||
                    transaction.amount <= 1000.0
                );
            }
        )
    );

    return engine;
}


// ============================================================================
// 10. INVARIANT-MAINTAINING ACCOUNT
// ============================================================================

class Account {
public:
    explicit Account(double initialBalance)
        : balance_(initialBalance) {
        if (initialBalance < 0.0) {
            throw std::invalid_argument(
                "Initial balance cannot be negative."
            );
        }

        checkInvariant();
    }

    double balance() const {
        return balance_;
    }

    void deposit(double amount) {
        if (!std::isfinite(amount) || amount <= 0.0) {
            throw std::invalid_argument(
                "Deposit must be a positive finite amount."
            );
        }

        balance_ += amount;
        checkInvariant();
    }

    void withdraw(double amount) {
        if (!std::isfinite(amount) || amount <= 0.0) {
            throw std::invalid_argument(
                "Withdrawal must be a positive finite amount."
            );
        }

        if (amount > balance_) {
            throw std::domain_error(
                "Insufficient account balance."
            );
        }

        balance_ -= amount;
        checkInvariant();
    }

private:
    double balance_;

    void checkInvariant() const {
        /*
         * Class invariant:
         *
         * balance >= 0
         *
         * In debug builds assert can detect programming errors. Explicit
         * exceptions are used for external invalid input.
         */
        assert(balance_ >= 0.0);
        assert(std::isfinite(balance_));
    }
};


// ============================================================================
// 11. EXHAUSTIVE BOOLEAN VERIFICATION
// ============================================================================

struct VerificationFailure {
    bool first{};
    bool second{};
    bool expected{};
    bool actual{};
};

std::vector<VerificationFailure> verifyEquivalent(
    const std::function<bool(bool, bool)>& first,
    const std::function<bool(bool, bool)>& second
) {
    std::vector<VerificationFailure> failures;

    for (bool a : {false, true}) {
        for (bool b : {false, true}) {
            const bool actual = first(a, b);
            const bool expected = second(a, b);

            if (actual != expected) {
                failures.push_back({
                    a,
                    b,
                    expected,
                    actual
                });
            }
        }
    }

    return failures;
}

void demonstrateVerification() {
    std::cout << "\n=== EXHAUSTIVE VERIFICATION ===\n";

    const auto deMorganFailures = verifyEquivalent(
        [](bool a, bool b) {
            return !(a && b);
        },
        [](bool a, bool b) {
            return !a || !b;
        }
    );

    std::cout
        << "De Morgan equivalence: "
        << (deMorganFailures.empty() ? "PASS" : "FAIL")
        << "\n";

    const auto incorrectFailures = verifyEquivalent(
        logic_xor,
        logic_or
    );

    std::cout
        << "XOR == OR: "
        << (incorrectFailures.empty() ? "PASS" : "FAIL")
        << "\n";

    if (!incorrectFailures.empty()) {
        const auto& counterexample = incorrectFailures.front();

        std::cout
            << "Counterexample: A="
            << counterexample.first
            << ", B="
            << counterexample.second
            << ", expected="
            << counterexample.expected
            << ", actual="
            << counterexample.actual
            << "\n";
    }
}


// ============================================================================
// 12. POLICY TEST CASES
// ============================================================================

struct PolicyTestCase {
    std::string name;
    Transaction transaction;
    bool expected;
};

void runPolicyTests(const RuleEngine& engine) {
    std::cout << "\n=== POLICY TEST CASES ===\n";

    const std::vector<PolicyTestCase> tests = {
        {
            "Valid low-value transaction",
            {500.0, 120, true, false, false},
            true
        },
        {
            "Valid trusted-device transaction",
            {5000.0, 120, true, false, true},
            true
        },
        {
            "Unverified identity",
            {500.0, 120, false, false, true},
            false
        },
        {
            "New account",
            {500.0, 10, true, false, true},
            false
        },
        {
            "Suspicious location",
            {500.0, 120, true, true, true},
            false
        },
        {
            "High-value untrusted device",
            {5000.0, 120, true, false, false},
            false
        },
        {
            "Zero amount",
            {0.0, 120, true, false, true},
            false
        }
    };

    std::size_t failures = 0;

    for (const auto& test : tests) {
        bool actual = false;

        try {
            actual = engine.isAllowed(test.transaction);
        } catch (const std::exception& error) {
            std::cout
                << "[ERROR] "
                << test.name
                << ": "
                << error.what()
                << "\n";
            ++failures;
            continue;
        }

        const bool passed = actual == test.expected;

        std::cout
            << (passed ? "[PASS] " : "[FAIL] ")
            << std::left
            << std::setw(32)
            << test.name
            << " expected="
            << test.expected
            << " actual="
            << actual
            << "\n";

        if (!passed) {
            ++failures;
        }
    }

    std::cout
        << "Policy test failures: "
        << failures
        << "\n";

    assert(failures == 0);
}


// ============================================================================
// 13. ERROR HANDLING AND FAILURE CONDITIONS
// ============================================================================

void demonstrateErrorHandling() {
    std::cout << "\n=== ERROR HANDLING ===\n";

    try {
        Transaction invalid{
            -10.0,
            100,
            true,
            false,
            true
        };

        evaluateTransaction(invalid);
    } catch (const std::exception& error) {
        std::cout
            << "Invalid transaction rejected: "
            << error.what()
            << "\n";
    }

    try {
        Account account(100.0);
        account.withdraw(150.0);
    } catch (const std::exception& error) {
        std::cout
            << "Invalid withdrawal rejected: "
            << error.what()
            << "\n";
    }

    try {
        Account account(-1.0);
    } catch (const std::exception& error) {
        std::cout
            << "Invalid account rejected: "
            << error.what()
            << "\n";
    }
}


// ============================================================================
// 14. DECISION EXPLANATION
// ============================================================================

void demonstrateDecisionExplanation() {
    std::cout << "\n=== DECISION EXPLANATION ===\n";

    const Transaction transaction{
        750.0,
        180,
        true,
        false,
        false
    };

    const PolicyDecision decision =
        evaluateTransaction(transaction);

    printDecision(decision);

    /*
     * Separating individual predicates from the final decision makes
     * debugging and auditability easier. A single Boolean result tells us
     * what happened; the predicate vector tells us why.
     */
}


// ============================================================================
// 15. LOGICAL EQUIVALENCE OF POLICY COMPONENTS
// ============================================================================

bool safeDeviceOrLowValue(
    bool trustedDevice,
    double amount
) {
    return trustedDevice || amount <= 1000.0;
}

bool equivalentPolicyForm(
    bool trustedDevice,
    double amount
) {
    /*
     * A OR B is equivalent to NOT(NOT A AND NOT B).
     *
     * This form demonstrates De Morgan's transformation.
     */
    return !(
        !trustedDevice &&
        !(amount <= 1000.0)
    );
}

void demonstratePolicyEquivalence() {
    std::cout << "\n=== POLICY EQUIVALENCE ===\n";

    bool allEquivalent = true;

    const std::array<double, 5> amounts{
        0.0,
        100.0,
        1000.0,
        1000.01,
        5000.0
    };

    for (bool trusted : {false, true}) {
        for (double amount : amounts) {
            const bool first =
                safeDeviceOrLowValue(trusted, amount);

            const bool second =
                equivalentPolicyForm(trusted, amount);

            if (first != second) {
                allEquivalent = false;

                std::cout
                    << "Counterexample: trusted="
                    << trusted
                    << ", amount="
                    << amount
                    << "\n";
            }
        }
    }

    std::cout
        << "Equivalent policy forms: "
        << allEquivalent
        << "\n";

    assert(allEquivalent);
}


// ============================================================================
// 16. COMPLEXITY ANALYSIS
// ============================================================================

void printComplexityDiscussion() {
    std::cout << "\n=== COMPLEXITY CONSIDERATIONS ===\n";

    std::cout << "One Boolean operation: O(1)\n";
    std::cout << "Evaluating k independent rules: O(k)\n";
    std::cout << "Truth table for n Boolean variables: O(2^n)\n";
    std::cout
        << "Exhaustive verification is practical for small finite input spaces,\n"
        << "but the number of combinations grows exponentially.\n";

    /*
     * For example:
     *
     * n = 10 -> 1,024 combinations
     * n = 20 -> 1,048,576 combinations
     * n = 30 -> 1,073,741,824 combinations
     *
     * Production verification therefore often combines exhaustive checking
     * for small domains with symbolic methods, model checking, static
     * analysis, targeted tests, invariants, and other techniques.
     */
}


// ============================================================================
// 17. END-TO-END CASE STUDY
// ============================================================================

void runCaseStudy() {
    std::cout << "\n";
    std::cout << "============================================================\n";
    std::cout << "TRANSACTION AUTHORIZATION CASE STUDY\n";
    std::cout << "============================================================\n";

    RuleEngine engine = createPolicyEngine();

    const Transaction transaction{
        750.0,
        180,
        true,
        false,
        false
    };

    std::cout << "\nTransaction:\n";
    std::cout << "  amount = " << transaction.amount << "\n";
    std::cout
        << "  accountAgeDays = "
        << transaction.accountAgeDays
        << "\n";
    std::cout
        << "  identityVerified = "
        << std::boolalpha
        << transaction.identityVerified
        << "\n";
    std::cout
        << "  suspiciousLocation = "
        << transaction.suspiciousLocation
        << "\n";
    std::cout
        << "  trustedDevice = "
        << transaction.trustedDevice
        << "\n";

    std::cout << "\nRule results:\n";

    const auto results = engine.evaluate(transaction);

    for (const auto& [name, result] : results) {
        std::cout
            << "  "
            << std::left
            << std::setw(42)
            << name
            << " = "
            << result
            << "\n";
    }

    std::cout
        << "\nFinal authorization: "
        << engine.isAllowed(transaction)
        << "\n";

    /*
     * The architecture separates:
     *
     * 1. Domain data.
     * 2. Input validation.
     * 3. Individual predicates.
     * 4. Rule composition.
     * 5. Final decision.
     * 6. Decision explanation.
     * 7. Verification.
     *
     * This separation makes logical conditions easier to inspect and test.
     */
}


// ============================================================================
// 18. MAIN
// ============================================================================

int main() {
    try {
        std::cout << "============================================================\n";
        std::cout << "LOGIC IN COMPUTING - C++ CASE STUDY\n";
        std::cout << "============================================================\n";

        demonstrateDigitalLogic();
        demonstrateBitLevelLogic();
        demonstrateVerification();
        demonstrateDecisionExplanation();
        demonstratePolicyEquivalence();
        runPolicyTests(createPolicyEngine());
        demonstrateErrorHandling();
        printComplexityDiscussion();
        runCaseStudy();

        std::cout
            << "\nAll C++ logic demonstrations completed successfully.\n";

        return 0;
    }
    catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << "\n";

        return 1;
    }
}
