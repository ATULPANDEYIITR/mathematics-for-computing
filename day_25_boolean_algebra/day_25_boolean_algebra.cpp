/*
 * Boolean Algebra: C++17 Technical Case Study
 *
 * Case study:
 * A configurable industrial safety-control system evaluates Boolean sensor
 * signals to determine whether a machine may operate and whether an alarm
 * must be activated.
 *
 * The implementation demonstrates:
 * - Boolean variables and expressions
 * - Boolean identities
 * - expression trees
 * - truth-table equivalence testing
 * - NAND-based logic
 * - sensor policy evaluation
 * - validation
 * - state modeling
 * - fault handling
 * - bit masks
 * - modular design
 * - complexity considerations
 *
 * Compile:
 *     g++ -std=c++17 -O2 boolean_algebra.cpp -o boolean_algebra
 *
 * Run:
 *     ./boolean_algebra
 */

#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <exception>
#include <functional>
#include <iomanip>
#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using BoolFunction = std::function<bool(const std::vector<bool>&)>;


// ============================================================================
// 1. BASIC BOOLEAN OPERATIONS
// ============================================================================

bool booleanNot(bool a) {
    return !a;
}

bool booleanAnd(bool a, bool b) {
    return a && b;
}

bool booleanOr(bool a, bool b) {
    return a || b;
}

bool nandGate(bool a, bool b) {
    return !(a && b);
}

bool norGate(bool a, bool b) {
    return !(a || b);
}

bool xorGate(bool a, bool b) {
    return a != b;
}

bool xnorGate(bool a, bool b) {
    return a == b;
}


// ============================================================================
// 2. TRUTH-TABLE GENERATOR
// ============================================================================
//
// For n variables there are 2^n possible input combinations.
// Exhaustive enumeration is excellent for small expressions and correctness
// testing, but becomes expensive as n grows.


std::vector<std::vector<bool>> generateInputs(std::size_t variableCount) {
    if (variableCount >= 63) {
        throw std::invalid_argument(
            "Variable count is too large for exhaustive 64-bit enumeration."
        );
    }

    const std::uint64_t combinations =
        std::uint64_t{1} << variableCount;

    std::vector<std::vector<bool>> inputs;
    inputs.reserve(static_cast<std::size_t>(combinations));

    for (std::uint64_t value = 0; value < combinations; ++value) {
        std::vector<bool> row(variableCount);

        for (std::size_t bit = 0; bit < variableCount; ++bit) {
            const std::size_t shift = variableCount - 1 - bit;
            row[bit] = ((value >> shift) & 1U) != 0;
        }

        inputs.push_back(std::move(row));
    }

    return inputs;
}


void printTruthTable(
    std::size_t variableCount,
    const BoolFunction& function
) {
    for (std::size_t index = 0; index < variableCount; ++index) {
        std::cout << " " << static_cast<char>('A' + index);
    }

    std::cout << " | F\n";
    std::cout << std::string(variableCount * 2 + 4, '-') << "\n";

    for (const auto& row : generateInputs(variableCount)) {
        for (bool value : row) {
            std::cout << " " << static_cast<int>(value);
        }

        std::cout << " | "
                  << static_cast<int>(function(row))
                  << "\n";
    }
}


// ============================================================================
// 3. BOOLEAN EXPRESSION EQUIVALENCE
// ============================================================================

bool areEquivalent(
    std::size_t variableCount,
    const BoolFunction& first,
    const BoolFunction& second
) {
    for (const auto& input : generateInputs(variableCount)) {
        if (first(input) != second(input)) {
            return false;
        }
    }

    return true;
}


// ============================================================================
// 4. EXPRESSION TREE
// ============================================================================
//
// Expression trees make Boolean expressions explicit data structures.
//
// Example:
//
//     F = (A AND B) OR (NOT A AND C)
//
// becomes:
//
//                  OR
//                /    \
//              AND    AND
//             /  \    /  \
//            A    B  NOT   C
//                    |
//                    A
//
// A tree representation is useful for symbolic processing, simplification,
// optimization, compilation, and circuit synthesis.


class BooleanExpression {
public:
    virtual ~BooleanExpression() = default;

    virtual bool evaluate(
        const std::unordered_map<std::string, bool>& environment
    ) const = 0;

    virtual std::string toString() const = 0;
};


using ExpressionPtr = std::shared_ptr<const BooleanExpression>;


class BooleanVariable final : public BooleanExpression {
private:
    std::string name;

public:
    explicit BooleanVariable(std::string variableName)
        : name(std::move(variableName)) {}

    bool evaluate(
        const std::unordered_map<std::string, bool>& environment
    ) const override {
        const auto iterator = environment.find(name);

        if (iterator == environment.end()) {
            throw std::invalid_argument(
                "Missing Boolean variable: " + name
            );
        }

        return iterator->second;
    }

    std::string toString() const override {
        return name;
    }
};


class BooleanConstant final : public BooleanExpression {
private:
    bool value;

public:
    explicit BooleanConstant(bool booleanValue)
        : value(booleanValue) {}

    bool evaluate(
        const std::unordered_map<std::string, bool>&
    ) const override {
        return value;
    }

    std::string toString() const override {
        return value ? "1" : "0";
    }
};


class BooleanNot final : public BooleanExpression {
private:
    ExpressionPtr operand;

public:
    explicit BooleanNot(ExpressionPtr expression)
        : operand(std::move(expression)) {}

    bool evaluate(
        const std::unordered_map<std::string, bool>& environment
    ) const override {
        return !operand->evaluate(environment);
    }

    std::string toString() const override {
        return "(NOT " + operand->toString() + ")";
    }
};


class BooleanAnd final : public BooleanExpression {
private:
    ExpressionPtr left;
    ExpressionPtr right;

public:
    BooleanAnd(ExpressionPtr leftExpression, ExpressionPtr rightExpression)
        : left(std::move(leftExpression)),
          right(std::move(rightExpression)) {}

    bool evaluate(
        const std::unordered_map<std::string, bool>& environment
    ) const override {
        return left->evaluate(environment) &&
               right->evaluate(environment);
    }

    std::string toString() const override {
        return "(" + left->toString() +
               " AND " +
               right->toString() + ")";
    }
};


class BooleanOr final : public BooleanExpression {
private:
    ExpressionPtr left;
    ExpressionPtr right;

public:
    BooleanOr(ExpressionPtr leftExpression, ExpressionPtr rightExpression)
        : left(std::move(leftExpression)),
          right(std::move(rightExpression)) {}

    bool evaluate(
        const std::unordered_map<std::string, bool>& environment
    ) const override {
        return left->evaluate(environment) ||
               right->evaluate(environment);
    }

    std::string toString() const override {
        return "(" + left->toString() +
               " OR " +
               right->toString() + ")";
    }
};


// ============================================================================
// 5. FACTORY HELPERS FOR EXPRESSION TREES
// ============================================================================

ExpressionPtr variable(const std::string& name) {
    return std::make_shared<BooleanVariable>(name);
}

ExpressionPtr constant(bool value) {
    return std::make_shared<BooleanConstant>(value);
}

ExpressionPtr booleanNot(ExpressionPtr expression) {
    return std::make_shared<BooleanNot>(std::move(expression));
}

ExpressionPtr booleanAnd(
    ExpressionPtr left,
    ExpressionPtr right
) {
    return std::make_shared<BooleanAnd>(
        std::move(left),
        std::move(right)
    );
}

ExpressionPtr booleanOr(
    ExpressionPtr left,
    ExpressionPtr right
) {
    return std::make_shared<BooleanOr>(
        std::move(left),
        std::move(right)
    );
}


// ============================================================================
// 6. INDUSTRIAL SAFETY CONTROLLER
// ============================================================================
//
// Scenario:
//
// A manufacturing cell has:
//
//     E = emergency stop is NOT active
//     G = safety gate is closed
//     P = operator is authenticated
//     T = temperature is within safe range
//     R = required resources are available
//     M = maintenance lock is active
//
// Machine permission:
//
//     RUN = E AND G AND P AND T AND R AND NOT M
//
// Alarm condition:
//
//     ALARM = NOT E OR NOT G OR NOT T OR M
//
// This model demonstrates how Boolean algebra can represent safety interlocks.
//
// A real safety-critical controller would require certified hardware,
// redundancy, formal verification, fail-safe design, deterministic timing,
// hardware diagnostics, and applicable regulatory compliance. This program
// is an educational model, not a safety-certified controller.


struct SafetyInputs {
    bool emergencyStopClear;
    bool safetyGateClosed;
    bool operatorAuthenticated;
    bool temperatureSafe;
    bool resourcesAvailable;
    bool maintenanceLock;
};


struct SafetyDecision {
    bool machineMayRun;
    bool alarmActive;
    std::vector<std::string> reasons;
};


class SafetyController {
public:
    SafetyDecision evaluate(const SafetyInputs& input) const {
        SafetyDecision decision;

        decision.machineMayRun =
            input.emergencyStopClear &&
            input.safetyGateClosed &&
            input.operatorAuthenticated &&
            input.temperatureSafe &&
            input.resourcesAvailable &&
            !input.maintenanceLock;

        decision.alarmActive =
            !input.emergencyStopClear ||
            !input.safetyGateClosed ||
            !input.temperatureSafe ||
            input.maintenanceLock;

        if (!input.emergencyStopClear) {
            decision.reasons.emplace_back(
                "Emergency stop is active."
            );
        }

        if (!input.safetyGateClosed) {
            decision.reasons.emplace_back(
                "Safety gate is open."
            );
        }

        if (!input.operatorAuthenticated) {
            decision.reasons.emplace_back(
                "Operator authentication is missing."
            );
        }

        if (!input.temperatureSafe) {
            decision.reasons.emplace_back(
                "Temperature is outside the permitted range."
            );
        }

        if (!input.resourcesAvailable) {
            decision.reasons.emplace_back(
                "Required resources are unavailable."
            );
        }

        if (input.maintenanceLock) {
            decision.reasons.emplace_back(
                "Maintenance lock is active."
            );
        }

        return decision;
    }
};


// ============================================================================
// 7. INPUT VALIDATION
// ============================================================================
//
// A Boolean value should already be validated before it reaches the controller
// in a real application. This parser accepts only explicit 0 or 1 values,
// avoiding ambiguous textual input such as "maybe" or "yes".


bool parseBooleanToken(const std::string& token) {
    if (token == "0") {
        return false;
    }

    if (token == "1") {
        return true;
    }

    throw std::invalid_argument(
        "Boolean input must be exactly 0 or 1."
    );
}


// ============================================================================
// 8. BIT-MASK REPRESENTATION
// ============================================================================
//
// A bit mask can efficiently represent many independent Boolean flags.
//
// Bit 0: emergency stop clear
// Bit 1: gate closed
// Bit 2: operator authenticated
// Bit 3: temperature safe
// Bit 4: resources available
// Bit 5: maintenance lock
//
// This is useful when storing or transmitting compact status information.


enum SafetyFlag : std::uint8_t {
    EmergencyStopClear = 1U << 0,
    SafetyGateClosed = 1U << 1,
    OperatorAuthenticated = 1U << 2,
    TemperatureSafe = 1U << 3,
    ResourcesAvailable = 1U << 4,
    MaintenanceLock = 1U << 5
};


std::uint8_t buildSafetyMask(const SafetyInputs& input) {
    std::uint8_t mask = 0;

    if (input.emergencyStopClear) {
        mask |= EmergencyStopClear;
    }

    if (input.safetyGateClosed) {
        mask |= SafetyGateClosed;
    }

    if (input.operatorAuthenticated) {
        mask |= OperatorAuthenticated;
    }

    if (input.temperatureSafe) {
        mask |= TemperatureSafe;
    }

    if (input.resourcesAvailable) {
        mask |= ResourcesAvailable;
    }

    if (input.maintenanceLock) {
        mask |= MaintenanceLock;
    }

    return mask;
}


bool hasFlag(std::uint8_t mask, SafetyFlag flag) {
    return (mask & flag) != 0;
}


// ============================================================================
// 9. LOGIC EQUIVALENCE OF THE SAFETY RULE
// ============================================================================
//
// The controller's run condition:
//
//     E G P T R M'
//
// can also be evaluated using a nested expression tree.
//
// The purpose of this test is not to prove the entire controller safe. It
// verifies that two mathematical implementations produce identical results
// over the complete input domain of six Boolean variables.
//
// There are:
//
//     2^6 = 64
//
// possible input combinations.


bool directRunRule(const std::vector<bool>& values) {
    if (values.size() != 6) {
        throw std::invalid_argument(
            "The safety rule requires exactly six inputs."
        );
    }

    const bool E = values[0];
    const bool G = values[1];
    const bool P = values[2];
    const bool T = values[3];
    const bool R = values[4];
    const bool M = values[5];

    return E && G && P && T && R && !M;
}


bool alternativeRunRule(const std::vector<bool>& values) {
    if (values.size() != 6) {
        throw std::invalid_argument(
            "The safety rule requires exactly six inputs."
        );
    }

    // Reconstruct the same condition using helper functions.
    const bool E = values[0];
    const bool G = values[1];
    const bool P = values[2];
    const bool T = values[3];
    const bool R = values[4];
    const bool M = values[5];

    return booleanAnd(
        booleanAnd(E, G),
        booleanAnd(
            booleanAnd(P, T),
            booleanAnd(R, booleanNot(M))
        )
    );
}


// ============================================================================
// 10. NAND-ONLY SAFETY RULE
// ============================================================================
//
// NAND is functionally complete. Every Boolean operation can therefore be
// constructed from NAND operations alone.
//
// A direct NAND-only expression is generally less readable than the original
// safety rule, which illustrates an important engineering trade-off:
//
//     algebraic minimality and gate-level implementation
//
// are related but not identical design goals.


bool nandOnlyNot(bool a) {
    return nandGate(a, a);
}


bool nandOnlyAnd(bool a, bool b) {
    const bool temporary = nandGate(a, b);
    return nandGate(temporary, temporary);
}


bool nandOnlyAnd6(
    bool a,
    bool b,
    bool c,
    bool d,
    bool e,
    bool f
) {
    const bool first = nandOnlyAnd(a, b);
    const bool second = nandOnlyAnd(c, d);
    const bool third = nandOnlyAnd(e, f);

    return nandOnlyAnd(
        nandOnlyAnd(first, second),
        third
    );
}


bool nandOnlyRunRule(const std::vector<bool>& values) {
    if (values.size() != 6) {
        throw std::invalid_argument(
            "The NAND safety rule requires exactly six inputs."
        );
    }

    const bool E = values[0];
    const bool G = values[1];
    const bool P = values[2];
    const bool T = values[3];
    const bool R = values[4];
    const bool M = values[5];

    return nandOnlyAnd6(
        E,
        G,
        P,
        T,
        R,
        nandOnlyNot(M)
    );
}


// ============================================================================
// 11. SAFETY CONTROLLER DEMONSTRATION
// ============================================================================

void printDecision(
    const SafetyInputs& input,
    const SafetyDecision& decision
) {
    std::cout
        << "E=" << input.emergencyStopClear
        << " G=" << input.safetyGateClosed
        << " P=" << input.operatorAuthenticated
        << " T=" << input.temperatureSafe
        << " R=" << input.resourcesAvailable
        << " M=" << input.maintenanceLock
        << " | RUN=" << decision.machineMayRun
        << " ALARM=" << decision.alarmActive
        << "\n";

    if (!decision.reasons.empty()) {
        std::cout << "  Reasons:\n";

        for (const auto& reason : decision.reasons) {
            std::cout << "    - " << reason << "\n";
        }
    }
}


void demonstrateSafetyController() {
    std::cout << "\n"
              << std::string(80, '=')
              << "\n"
              << "INDUSTRIAL SAFETY CONTROLLER"
              << "\n"
              << std::string(80, '=')
              << "\n";

    SafetyController controller;

    const std::vector<SafetyInputs> scenarios = {
        {true, true, true, true, true, false},
        {false, true, true, true, true, false},
        {true, false, true, true, true, false},
        {true, true, false, true, true, false},
        {true, true, true, false, true, false},
        {true, true, true, true, false, false},
        {true, true, true, true, true, true}
    };

    for (const auto& scenario : scenarios) {
        const SafetyDecision decision =
            controller.evaluate(scenario);

        printDecision(scenario, decision);

        const std::uint8_t mask =
            buildSafetyMask(scenario);

        std::cout << "  Bit mask: "
                  << static_cast<int>(mask)
                  << "\n";
    }
}


// ============================================================================
// 12. EXPRESSION-TREE DEMONSTRATION
// ============================================================================

void demonstrateExpressionTree() {
    std::cout << "\n"
              << std::string(80, '=')
              << "\n"
              << "BOOLEAN EXPRESSION TREE"
              << "\n"
              << std::string(80, '=')
              << "\n";

    auto A = variable("A");
    auto B = variable("B");
    auto C = variable("C");

    // F = AB + A'C
    auto expression = booleanOr(
        booleanAnd(A, B),
        booleanAnd(booleanNot(A), C)
    );

    std::cout << "Expression: "
              << expression->toString()
              << "\n";

    const std::unordered_map<std::string, bool> environment = {
        {"A", true},
        {"B", false},
        {"C", true}
    };

    std::cout << "A=1 B=0 C=1\n";
    std::cout << "Result: "
              << expression->evaluate(environment)
              << "\n";
}


// ============================================================================
// 13. IDENTITY TESTS
// ============================================================================

void runIdentityTests() {
    std::cout << "\n"
              << std::string(80, '=')
              << "\n"
              << "BOOLEAN IDENTITY TESTS"
              << "\n"
              << std::string(80, '=')
              << "\n";

    const BoolFunction identityA = [](const std::vector<bool>& v) {
        return v[0] || false;
    };

    const BoolFunction identityB = [](const std::vector<bool>& v) {
        return v[0];
    };

    assert(areEquivalent(1, identityA, identityB));
    std::cout << "A + 0 = A: PASSED\n";

    const BoolFunction complementA = [](const std::vector<bool>& v) {
        return v[0] || !v[0];
    };

    const BoolFunction complementB = [](const std::vector<bool>&) {
        return true;
    };

    assert(areEquivalent(1, complementA, complementB));
    std::cout << "A + A' = 1: PASSED\n";

    const BoolFunction deMorganA = [](const std::vector<bool>& v) {
        return !(v[0] && v[1]);
    };

    const BoolFunction deMorganB = [](const std::vector<bool>& v) {
        return !v[0] || !v[1];
    };

    assert(areEquivalent(2, deMorganA, deMorganB));
    std::cout << "(AB)' = A' + B': PASSED\n";

    const BoolFunction absorptionA = [](const std::vector<bool>& v) {
        return v[0] || (v[0] && v[1]);
    };

    const BoolFunction absorptionB = [](const std::vector<bool>& v) {
        return v[0];
    };

    assert(areEquivalent(2, absorptionA, absorptionB));
    std::cout << "A + AB = A: PASSED\n";
}


// ============================================================================
// 14. XOR-BASED FULL ADDER
// ============================================================================

struct AdderResult {
    bool sum;
    bool carry;
};


AdderResult fullAdder(bool a, bool b, bool carryIn) {
    const bool partialSum = xorGate(a, b);
    const bool sum = xorGate(partialSum, carryIn);

    const bool carry =
        (a && b) ||
        (carryIn && partialSum);

    return {sum, carry};
}


void demonstrateFullAdder() {
    std::cout << "\n"
              << std::string(80, '=')
              << "\n"
              << "FULL ADDER"
              << "\n"
              << std::string(80, '=')
              << "\n";

    std::cout << "A B Cin | Sum Cout\n";

    for (bool a : {false, true}) {
        for (bool b : {false, true}) {
            for (bool carryIn : {false, true}) {
                const AdderResult result =
                    fullAdder(a, b, carryIn);

                std::cout
                    << a << " "
                    << b << "  "
                    << carryIn << "   |  "
                    << result.sum << "   "
                    << result.carry
                    << "\n";
            }
        }
    }
}


// ============================================================================
// 15. EDGE CASES
// ============================================================================

void demonstrateEdgeCases() {
    std::cout << "\n"
              << std::string(80, '=')
              << "\n"
              << "EDGE CASES AND FAILURE CONDITIONS"
              << "\n"
              << std::string(80, '=')
              << "\n";

    try {
        parseBooleanToken("2");
    }
    catch (const std::invalid_argument& error) {
        std::cout << "Invalid input caught: "
                  << error.what()
                  << "\n";
    }

    try {
        generateInputs(63);
    }
    catch (const std::invalid_argument& error) {
        std::cout << "Excessive truth-table size caught: "
                  << error.what()
                  << "\n";
    }

    try {
        auto missingVariable = variable("MISSING");

        missingVariable->evaluate({
            {"A", true}
        });
    }
    catch (const std::invalid_argument& error) {
        std::cout << "Missing variable caught: "
                  << error.what()
                  << "\n";
    }
}


// ============================================================================
// 16. COMPLETE SIX-VARIABLE EQUIVALENCE TEST
// ============================================================================
//
// 64 combinations are small enough for exhaustive verification.


void verifyControllerImplementations() {
    std::cout << "\n"
              << std::string(80, '=')
              << "\n"
              << "COMPLETE CONTROLLER EQUIVALENCE TEST"
              << "\n"
              << std::string(80, '=')
              << "\n";

    const bool directVsAlternative =
        areEquivalent(
            6,
            directRunRule,
            alternativeRunRule
        );

    const bool directVsNand =
        areEquivalent(
            6,
            directRunRule,
            nandOnlyRunRule
        );

    std::cout
        << "Direct rule == alternative rule: "
        << (directVsAlternative ? "PASS" : "FAIL")
        << "\n";

    std::cout
        << "Direct rule == NAND implementation: "
        << (directVsNand ? "PASS" : "FAIL")
        << "\n";

    assert(directVsAlternative);
    assert(directVsNand);
}


// ============================================================================
// 17. TRUTH TABLE FOR A THREE-VARIABLE CONTROL FUNCTION
// ============================================================================

void demonstrateTruthTable() {
    std::cout << "\n"
              << std::string(80, '=')
              << "\n"
              << "TRUTH TABLE: F = AB + A'C"
              << "\n"
              << std::string(80, '=')
              << "\n";

    const BoolFunction function = [](const std::vector<bool>& values) {
        const bool A = values[0];
        const bool B = values[1];
        const bool C = values[2];

        return (A && B) || (!A && C);
    };

    printTruthTable(3, function);
}


// ============================================================================
// 18. COMPLEXITY DISCUSSION
// ============================================================================
//
// Important complexity observations:
//
// Basic Boolean evaluation:
//     O(1) for a fixed-size expression.
//
// Expression tree evaluation:
//     O(N), where N is the number of expression nodes visited.
//
// Truth-table generation:
//     O(2^n) rows for n variables.
//
// Exhaustive equivalence checking:
//     O(2^n * E), where E is the cost of evaluating each expression.
//
// Bit-mask operations:
//     O(1) for a fixed machine word.
//
// Industrial optimization may use:
//     - algebraic simplification
//     - Karnaugh maps for small variable counts
//     - Quine-McCluskey-style methods
//     - binary decision diagrams
//     - SAT solving
//     - technology mapping
//     - hardware-specific synthesis
//
// There is no single representation that is optimal for every workload.

void demonstrateComplexity() {
    std::cout << "\n"
              << std::string(80, '=')
              << "\n"
              << "TRUTH-TABLE GROWTH"
              << "\n"
              << std::string(80, '=')
              << "\n";

    for (std::size_t variables = 1; variables <= 12; ++variables) {
        const std::uint64_t combinations =
            std::uint64_t{1} << variables;

        std::cout
            << std::setw(2)
            << variables
            << " variables -> "
            << std::setw(5)
            << combinations
            << " rows\n";
    }
}


// ============================================================================
// 19. MAIN
// ============================================================================

int main() {
    try {
        std::cout
            << std::string(80, '=')
            << "\n"
            << "BOOLEAN ALGEBRA: C++ INDUSTRIAL CASE STUDY"
            << "\n"
            << std::string(80, '=')
            << "\n";

        runIdentityTests();

        demonstrateTruthTable();

        demonstrateExpressionTree();

        demonstrateFullAdder();

        demonstrateSafetyController();

        verifyControllerImplementations();

        demonstrateEdgeCases();

        demonstrateComplexity();

        std::cout
            << "\n"
            << std::string(80, '=')
            << "\n"
            << "ALL C++ BOOLEAN ALGEBRA DEMONSTRATIONS COMPLETED"
            << "\n"
            << std::string(80, '=')
            << "\n";

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
