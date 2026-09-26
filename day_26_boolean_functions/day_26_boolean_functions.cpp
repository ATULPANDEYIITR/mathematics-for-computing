/*
 * Boolean Functions: Truth Tables, Minterms, and Maxterms
 *
 * C++17 case study:
 * A configurable access-control and safety decision system.
 *
 * The program demonstrates:
 *   - Boolean functions
 *   - Truth tables
 *   - Binary minterm indexing
 *   - Minterm and maxterm construction
 *   - Canonical SOP/POS
 *   - Functional equivalence
 *   - Boolean specification validation
 *   - Don't-care conditions
 *   - Minterm adjacency
 *   - Quine-McCluskey-style implicant combination
 *   - Error handling
 *   - Complexity considerations
 *   - A realistic multi-input control policy
 */

#include <algorithm>
#include <cassert>
#include <bitset>
#include <cstdint>
#include <exception>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

using BooleanVector = std::vector<int>;


// ============================================================
// 1. GENERAL BOOLEAN UTILITIES
// ============================================================

int booleanAnd(int left, int right) {
    return left && right;
}

int booleanOr(int left, int right) {
    return left || right;
}

int booleanNot(int value) {
    return !value;
}

int booleanXor(int left, int right) {
    return left != right;
}

int booleanXnor(int left, int right) {
    return left == right;
}

void validateBit(int value) {
    if (value != 0 && value != 1) {
        throw std::invalid_argument(
            "Boolean values must be either 0 or 1."
        );
    }
}


// ============================================================
// 2. BINARY INDEXING
// ============================================================

int binaryIndex(const BooleanVector& inputs) {
    int index = 0;

    for (int bit : inputs) {
        validateBit(bit);
        index = (index << 1) | bit;
    }

    return index;
}

BooleanVector indexToBits(int index, int variableCount) {
    if (variableCount <= 0) {
        throw std::invalid_argument(
            "Variable count must be positive."
        );
    }

    const int maximum = (1 << variableCount) - 1;

    if (index < 0 || index > maximum) {
        throw std::out_of_range(
            "Index is outside the valid Boolean range."
        );
    }

    BooleanVector bits(variableCount);

    for (int position = variableCount - 1;
         position >= 0;
         --position) {

        bits[position] = index & 1;
        index >>= 1;
    }

    return bits;
}


// ============================================================
// 3. BOOLEAN FUNCTION TYPE
// ============================================================

using BooleanFunction =
    std::function<int(const BooleanVector&)>;


// ============================================================
// 4. TRUTH TABLE
// ============================================================

class TruthTable {
private:
    std::vector<std::string> variables;
    std::vector<BooleanVector> rows;
    std::vector<int> outputs;

public:
    TruthTable(
        std::vector<std::string> variableNames,
        const BooleanFunction& function
    )
        : variables(std::move(variableNames)) {

        if (variables.empty()) {
            throw std::invalid_argument(
                "A truth table requires at least one variable."
            );
        }

        const int rowCount =
            1 << static_cast<int>(variables.size());

        rows.reserve(rowCount);
        outputs.reserve(rowCount);

        for (int index = 0; index < rowCount; ++index) {
            BooleanVector inputs =
                indexToBits(
                    index,
                    static_cast<int>(variables.size())
                );

            const int output = function(inputs);

            validateBit(output);

            rows.push_back(inputs);
            outputs.push_back(output);
        }
    }

    const std::vector<BooleanVector>& getRows() const {
        return rows;
    }

    const std::vector<int>& getOutputs() const {
        return outputs;
    }

    const std::vector<std::string>& getVariables() const {
        return variables;
    }

    void print(const std::string& title) const {
        std::cout << "\n" << title << "\n";
        std::cout << std::string(78, '-') << "\n";

        for (const auto& variable : variables) {
            std::cout << variable << " | ";
        }

        std::cout << "F\n";
        std::cout << std::string(78, '-') << "\n";

        for (std::size_t row = 0;
             row < rows.size();
             ++row) {

            for (int value : rows[row]) {
                std::cout << value << " | ";
            }

            std::cout << outputs[row] << "\n";
        }
    }
};


// ============================================================
// 5. MAJORITY FUNCTION
// ============================================================

int majorityFunction(const BooleanVector& inputs) {
    if (inputs.size() != 3) {
        throw std::invalid_argument(
            "Majority function requires exactly three inputs."
        );
    }

    const int a = inputs[0];
    const int b = inputs[1];
    const int c = inputs[2];

    // F = AB + AC + BC
    return (a && b) || (a && c) || (b && c);
}


// ============================================================
// 6. MINTERM AND MAXTERM REPRESENTATION
// ============================================================

std::string mintermExpression(
    const std::vector<std::string>& variables,
    int index
) {
    const int variableCount =
        static_cast<int>(variables.size());

    const int maximum =
        (1 << variableCount) - 1;

    if (index < 0 || index > maximum) {
        throw std::out_of_range(
            "Invalid minterm index."
        );
    }

    BooleanVector bits =
        indexToBits(index, variableCount);

    std::ostringstream expression;

    for (int i = 0; i < variableCount; ++i) {
        expression << variables[i];

        if (bits[i] == 0) {
            expression << "'";
        }
    }

    return expression.str();
}

std::string maxtermExpression(
    const std::vector<std::string>& variables,
    int index
) {
    const int variableCount =
        static_cast<int>(variables.size());

    const int maximum =
        (1 << variableCount) - 1;

    if (index < 0 || index > maximum) {
        throw std::out_of_range(
            "Invalid maxterm index."
        );
    }

    BooleanVector bits =
        indexToBits(index, variableCount);

    std::ostringstream expression;

    expression << "(";

    for (int i = 0; i < variableCount; ++i) {
        if (i > 0) {
            expression << " + ";
        }

        expression << variables[i];

        if (bits[i] == 1) {
            expression << "'";
        }
    }

    expression << ")";

    return expression.str();
}


// ============================================================
// 7. CANONICAL FORM EXTRACTION
// ============================================================

struct CanonicalRepresentation {
    std::vector<int> minterms;
    std::vector<int> maxterms;
};

CanonicalRepresentation extractCanonicalRepresentation(
    const TruthTable& table
) {
    CanonicalRepresentation result;

    const auto& rows = table.getRows();
    const auto& outputs = table.getOutputs();

    for (std::size_t row = 0;
         row < rows.size();
         ++row) {

        const int index =
            binaryIndex(rows[row]);

        if (outputs[row] == 1) {
            result.minterms.push_back(index);
        } else {
            result.maxterms.push_back(index);
        }
    }

    return result;
}

std::string canonicalSOP(
    const std::vector<std::string>& variables,
    const std::vector<int>& minterms
) {
    if (minterms.empty()) {
        return "0";
    }

    if (
        minterms.size() ==
        static_cast<std::size_t>(
            1 << variables.size()
        )
    ) {
        return "1";
    }

    std::ostringstream expression;

    for (std::size_t i = 0;
         i < minterms.size();
         ++i) {

        if (i > 0) {
            expression << " + ";
        }

        expression <<
            mintermExpression(
                variables,
                minterms[i]
            );
    }

    return expression.str();
}

std::string canonicalPOS(
    const std::vector<std::string>& variables,
    const std::vector<int>& maxterms
) {
    if (maxterms.empty()) {
        return "1";
    }

    if (
        maxterms.size() ==
        static_cast<std::size_t>(
            1 << variables.size()
        )
    ) {
        return "0";
    }

    std::ostringstream expression;

    for (int index : maxterms) {
        expression <<
            maxtermExpression(
                variables,
                index
            );
    }

    return expression.str();
}


// ============================================================
// 8. CANONICAL FORM EVALUATION
// ============================================================

int evaluateSOP(
    const BooleanVector& inputs,
    const std::vector<int>& minterms
) {
    const int index = binaryIndex(inputs);

    return std::find(
        minterms.begin(),
        minterms.end(),
        index
    ) != minterms.end();
}

int evaluatePOS(
    const BooleanVector& inputs,
    const std::vector<int>& maxterms
) {
    const int index = binaryIndex(inputs);

    // A POS is zero exactly at its listed maxterm indices.
    return std::find(
        maxterms.begin(),
        maxterms.end(),
        index
    ) == maxterms.end();
}


// ============================================================
// 9. FUNCTIONAL EQUIVALENCE
// ============================================================

bool areEquivalent(
    int variableCount,
    const BooleanFunction& first,
    const BooleanFunction& second
) {
    const int rowCount = 1 << variableCount;

    for (int index = 0;
         index < rowCount;
         ++index) {

        BooleanVector inputs =
            indexToBits(index, variableCount);

        if (first(inputs) != second(inputs)) {
            return false;
        }
    }

    return true;
}


// ============================================================
// 10. DON'T-CARE SPECIFICATION
// ============================================================

class BooleanSpecification {
private:
    int variableCount;
    std::set<int> onSet;
    std::set<int> offSet;
    std::set<int> dontCareSet;

public:
    BooleanSpecification(
        int variables,
        std::set<int> on,
        std::set<int> off,
        std::set<int> dontCare
    )
        : variableCount(variables),
          onSet(std::move(on)),
          offSet(std::move(off)),
          dontCareSet(std::move(dontCare)) {

        validate();
    }

    void validate() const {
        if (variableCount <= 0) {
            throw std::invalid_argument(
                "Variable count must be positive."
            );
        }

        const int maximum =
            (1 << variableCount) - 1;

        auto validateSet =
            [maximum](const std::set<int>& values,
                      const std::string& name) {

            for (int value : values) {
                if (value < 0 || value > maximum) {
                    throw std::out_of_range(
                        name + " contains invalid index."
                    );
                }
            }
        };

        validateSet(onSet, "ON-set");
        validateSet(offSet, "OFF-set");
        validateSet(dontCareSet, "Don't-care set");

        for (int value : onSet) {
            if (offSet.count(value) > 0) {
                throw std::invalid_argument(
                    "ON-set and OFF-set overlap."
                );
            }

            if (dontCareSet.count(value) > 0) {
                throw std::invalid_argument(
                    "ON-set and don't-care set overlap."
                );
            }
        }

        for (int value : offSet) {
            if (dontCareSet.count(value) > 0) {
                throw std::invalid_argument(
                    "OFF-set and don't-care set overlap."
                );
            }
        }
    }

    void print() const {
        std::cout << "ON-set: ";

        for (int value : onSet) {
            std::cout << value << " ";
        }

        std::cout << "\nOFF-set: ";

        for (int value : offSet) {
            std::cout << value << " ";
        }

        std::cout << "\nDon't-care set: ";

        for (int value : dontCareSet) {
            std::cout << value << " ";
        }

        std::cout << "\n";
    }
};


// ============================================================
// 11. MINTERM ADJACENCY
// ============================================================

int hammingDistance(
    int left,
    int right,
    int variableCount
) {
    BooleanVector leftBits =
        indexToBits(left, variableCount);

    BooleanVector rightBits =
        indexToBits(right, variableCount);

    int differences = 0;

    for (int i = 0; i < variableCount; ++i) {
        if (leftBits[i] != rightBits[i]) {
            ++differences;
        }
    }

    return differences;
}

std::vector<int> adjacentMinterms(
    int index,
    int variableCount
) {
    std::vector<int> result;

    const int rowCount =
        1 << variableCount;

    for (int candidate = 0;
         candidate < rowCount;
         ++candidate) {

        if (
            candidate != index &&
            hammingDistance(
                index,
                candidate,
                variableCount
            ) == 1
        ) {
            result.push_back(candidate);
        }
    }

    return result;
}


// ============================================================
// 12. QUINE-MCCLUSKEY-STYLE IMPLICANTS
// ============================================================

struct Implicant {
    std::string pattern;
    std::set<int> coveredMinterms;

    bool operator<(const Implicant& other) const {
        return pattern < other.pattern;
    }
};

bool canCombine(
    const Implicant& first,
    const Implicant& second
) {
    if (first.pattern.size() != second.pattern.size()) {
        return false;
    }

    int differences = 0;

    for (std::size_t i = 0;
         i < first.pattern.size();
         ++i) {

        const char left = first.pattern[i];
        const char right = second.pattern[i];

        if (left != right) {
            if (left == '-' || right == '-') {
                return false;
            }

            ++differences;
        }
    }

    return differences == 1;
}

Implicant combineImplicants(
    const Implicant& first,
    const Implicant& second
) {
    if (!canCombine(first, second)) {
        throw std::invalid_argument(
            "Implicants cannot be combined."
        );
    }

    Implicant result = first;

    for (std::size_t i = 0;
         i < result.pattern.size();
         ++i) {

        if (first.pattern[i] != second.pattern[i]) {
            result.pattern[i] = '-';
        }
    }

    result.coveredMinterms.insert(
        second.coveredMinterms.begin(),
        second.coveredMinterms.end()
    );

    return result;
}

std::vector<Implicant> initialImplicants(
    const std::vector<int>& minterms,
    int variableCount
) {
    std::vector<Implicant> result;

    for (int minterm : minterms) {
        BooleanVector bits =
            indexToBits(
                minterm,
                variableCount
            );

        std::string pattern;

        for (int bit : bits) {
            pattern +=
                bit == 1 ? '1' : '0';
        }

        result.push_back(
            {
                pattern,
                {minterm}
            }
        );
    }

    return result;
}


// ============================================================
// 13. INDUSTRY-STYLE CASE STUDY
// ============================================================

/*
 * Scenario:
 *
 * A facility has an electronic activation controller.
 *
 * Inputs:
 *   D = door is confirmed closed
 *   A = operator authorization is valid
 *   E = emergency override is active
 *
 * Output:
 *   S = activation permitted
 *
 * Policy:
 *
 * Normal activation:
 *     D AND A
 *
 * Emergency activation:
 *     E
 *
 * Therefore:
 *     S = DA + E
 *
 * This is intentionally small enough to analyze exhaustively while
 * still representing a real control-policy pattern.
 */

class ActivationController {
public:
    static int evaluate(
        const BooleanVector& inputs
    ) {
        if (inputs.size() != 3) {
            throw std::invalid_argument(
                "Activation controller requires D, A, and E."
            );
        }

        const int doorClosed = inputs[0];
        const int authorized = inputs[1];
        const int emergency = inputs[2];

        validateBit(doorClosed);
        validateBit(authorized);
        validateBit(emergency);

        return
            (doorClosed && authorized) ||
            emergency;
    }

    static std::string decisionDescription(
        const BooleanVector& inputs
    ) {
        const int result =
            evaluate(inputs);

        if (result == 1) {
            return "ACTIVATION PERMITTED";
        }

        return "ACTIVATION BLOCKED";
    }
};


// ============================================================
// 14. SECURITY-ORIENTED VALIDATION
// ============================================================

/*
 * Boolean logic can represent authorization rules, but the Boolean
 * expression itself is not a complete security mechanism.
 *
 * A real security system must also authenticate identities, protect
 * credentials, enforce authorization on the server or trusted device,
 * log decisions, handle failures safely, and prevent tampering.
 *
 * This case study therefore treats Boolean logic as the decision rule,
 * not as the complete security architecture.
 */


// ============================================================
// 15. MAIN PROGRAM
// ============================================================

int main() {
    try {
        std::cout << std::string(78, '=') << "\n";
        std::cout
            << "BOOLEAN FUNCTIONS: TRUTH TABLES, MINTERMS, MAXTERMS\n";
        std::cout << std::string(78, '=') << "\n";


        // --------------------------------------------------------
        // Basic operations
        // --------------------------------------------------------

        std::cout << "\n1. BASIC BOOLEAN OPERATIONS\n";

        for (int a : {0, 1}) {
            for (int b : {0, 1}) {
                std::cout
                    << "A=" << a
                    << " B=" << b
                    << " | NOT A=" << booleanNot(a)
                    << " | A AND B=" << booleanAnd(a, b)
                    << " | A OR B=" << booleanOr(a, b)
                    << " | A XOR B=" << booleanXor(a, b)
                    << " | A XNOR B=" << booleanXnor(a, b)
                    << "\n";
            }
        }


        // --------------------------------------------------------
        // Majority truth table
        // --------------------------------------------------------

        TruthTable majorityTable(
            {"A", "B", "C"},
            majorityFunction
        );

        majorityTable.print(
            "2. MAJORITY FUNCTION: F = AB + AC + BC"
        );


        // --------------------------------------------------------
        // Canonical representations
        // --------------------------------------------------------

        CanonicalRepresentation majority =
            extractCanonicalRepresentation(
                majorityTable
            );

        std::cout
            << "\n3. MAJORITY CANONICAL REPRESENTATION\n";

        std::cout << "Minterms: ";

        for (int value : majority.minterms) {
            std::cout << value << " ";
        }

        std::cout << "\nMaxterms: ";

        for (int value : majority.maxterms) {
            std::cout << value << " ";
        }

        std::cout << "\n";

        std::cout
            << "Canonical SOP: "
            << canonicalSOP(
                majorityTable.getVariables(),
                majority.minterms
            )
            << "\n";

        std::cout
            << "Canonical POS: "
            << canonicalPOS(
                majorityTable.getVariables(),
                majority.maxterms
            )
            << "\n";


        // --------------------------------------------------------
        // Minterm and maxterm listing
        // --------------------------------------------------------

        std::cout
            << "\n4. THREE-VARIABLE MINTERMS AND MAXTERMS\n";

        for (int index = 0; index < 8; ++index) {
            std::cout
                << "m" << index
                << " = "
                << mintermExpression(
                    majorityTable.getVariables(),
                    index
                )
                << " | M" << index
                << " = "
                << maxtermExpression(
                    majorityTable.getVariables(),
                    index
                )
                << "\n";
        }


        // --------------------------------------------------------
        // Canonical equivalence test
        // --------------------------------------------------------

        std::cout
            << "\n5. CANONICAL FORM VERIFICATION\n";

        for (std::size_t row = 0;
             row < majorityTable.getRows().size();
             ++row) {

            const BooleanVector& inputs =
                majorityTable.getRows()[row];

            const int original =
                majorityTable.getOutputs()[row];

            const int sop =
                evaluateSOP(
                    inputs,
                    majority.minterms
                );

            const int pos =
                evaluatePOS(
                    inputs,
                    majority.maxterms
                );

            assert(original == sop);
            assert(original == pos);
        }

        std::cout
            << "SOP and POS produce identical outputs: PASS\n";


        // --------------------------------------------------------
        // De Morgan's laws
        // --------------------------------------------------------

        std::cout
            << "\n6. DE MORGAN'S LAW VERIFICATION\n";

        for (int a : {0, 1}) {
            for (int b : {0, 1}) {
                assert(
                    booleanNot(
                        booleanAnd(a, b)
                    ) ==
                    booleanOr(
                        booleanNot(a),
                        booleanNot(b)
                    )
                );

                assert(
                    booleanNot(
                        booleanOr(a, b)
                    ) ==
                    booleanAnd(
                        booleanNot(a),
                        booleanNot(b)
                    )
                );
            }
        }

        std::cout
            << "Both De Morgan laws verified: PASS\n";


        // --------------------------------------------------------
        // Functional equivalence
        // --------------------------------------------------------

        std::cout
            << "\n7. FUNCTIONAL EQUIVALENCE\n";

        BooleanFunction expressionOne =
            [](const BooleanVector& x) {
                return
                    (x[0] && x[1]) ||
                    (x[0] && x[2]) ||
                    (x[1] && x[2]);
            };

        BooleanFunction expressionTwo =
            [](const BooleanVector& x) {
                return
                    (x[0] && (x[1] || x[2])) ||
                    (x[1] && x[2]);
            };

        std::cout
            << "AB + AC + BC == A(B+C) + BC: "
            << (
                areEquivalent(
                    3,
                    expressionOne,
                    expressionTwo
                )
                ? "TRUE"
                : "FALSE"
            )
            << "\n";


        // --------------------------------------------------------
        // Don't-care specification
        // --------------------------------------------------------

        std::cout
            << "\n8. DON'T-CARE SPECIFICATION\n";

        BooleanSpecification specification(
            3,
            {1, 3, 5},
            {0, 2, 7},
            {4, 6}
        );

        specification.print();


        // --------------------------------------------------------
        // Minterm adjacency
        // --------------------------------------------------------

        std::cout
            << "\n9. MINTERM ADJACENCY\n";

        for (int index = 0; index < 8; ++index) {
            std::cout
                << "m" << index << ": ";

            for (int adjacent :
                 adjacentMinterms(index, 3)) {
                std::cout
                    << adjacent
                    << " ";
            }

            std::cout << "\n";
        }


        // --------------------------------------------------------
        // Quine-McCluskey-style combination
        // --------------------------------------------------------

        std::cout
            << "\n10. IMPLICANT COMBINATION\n";

        std::vector<Implicant> implicants =
            initialImplicants(
                {1, 3, 5, 7},
                3
            );

        for (std::size_t first = 0;
             first < implicants.size();
             ++first) {

            for (std::size_t second = first + 1;
                 second < implicants.size();
                 ++second) {

                if (
                    canCombine(
                        implicants[first],
                        implicants[second]
                    )
                ) {
                    Implicant combined =
                        combineImplicants(
                            implicants[first],
                            implicants[second]
                        );

                    std::cout
                        << implicants[first].pattern
                        << " + "
                        << implicants[second].pattern
                        << " -> "
                        << combined.pattern
                        << "\n";
                }
            }
        }


        // --------------------------------------------------------
        // Industry-style activation controller
        // --------------------------------------------------------

        TruthTable activationTable(
            {"D", "A", "E"},
            ActivationController::evaluate
        );

        activationTable.print(
            "\n11. ACTIVATION CONTROLLER: S = DA + E"
        );

        CanonicalRepresentation activation =
            extractCanonicalRepresentation(
                activationTable
            );

        std::cout
            << "\nCanonical SOP: "
            << canonicalSOP(
                activationTable.getVariables(),
                activation.minterms
            )
            << "\n";

        std::cout
            << "Canonical POS: "
            << canonicalPOS(
                activationTable.getVariables(),
                activation.maxterms
            )
            << "\n";


        // --------------------------------------------------------
        // Decision processing
        // --------------------------------------------------------

        std::cout
            << "\n12. CONTROL DECISIONS\n";

        const std::vector<BooleanVector> scenarios = {
            {0, 0, 0},
            {1, 0, 0},
            {1, 1, 0},
            {0, 0, 1},
            {0, 1, 1}
        };

        for (const auto& scenario : scenarios) {
            std::cout
                << "D=" << scenario[0]
                << " A=" << scenario[1]
                << " E=" << scenario[2]
                << " -> "
                << ActivationController::decisionDescription(
                    scenario
                )
                << "\n";
        }


        // --------------------------------------------------------
        // Edge cases: constant functions
        // --------------------------------------------------------

        std::cout
            << "\n13. CONSTANT FUNCTION EDGE CASES\n";

        TruthTable constantZero(
            {"A", "B"},
            [](const BooleanVector&) {
                return 0;
            }
        );

        TruthTable constantOne(
            {"A", "B"},
            [](const BooleanVector&) {
                return 1;
            }
        );

        CanonicalRepresentation zero =
            extractCanonicalRepresentation(
                constantZero
            );

        CanonicalRepresentation one =
            extractCanonicalRepresentation(
                constantOne
            );

        std::cout
            << "Constant 0 SOP: "
            << canonicalSOP(
                constantZero.getVariables(),
                zero.minterms
            )
            << "\n";

        std::cout
            << "Constant 0 POS: "
            << canonicalPOS(
                constantZero.getVariables(),
                zero.maxterms
            )
            << "\n";

        std::cout
            << "Constant 1 SOP: "
            << canonicalSOP(
                constantOne.getVariables(),
                one.minterms
            )
            << "\n";

        std::cout
            << "Constant 1 POS: "
            << canonicalPOS(
                constantOne.getVariables(),
                one.maxterms
            )
            << "\n";


        // --------------------------------------------------------
        // Complexity
        // --------------------------------------------------------

        std::cout
            << "\n14. BOOLEAN FUNCTION SPACE\n";

        for (int variableCount = 1;
             variableCount <= 5;
             ++variableCount) {

            const std::uint64_t rows =
                1ULL << variableCount;

            const std::uint64_t possibleFunctions =
                1ULL << rows;

            std::cout
                << "Variables: "
                << variableCount
                << ", truth-table rows: "
                << rows
                << ", possible Boolean functions: "
                << possibleFunctions
                << "\n";
        }


        // --------------------------------------------------------
        // Error handling demonstration
        // --------------------------------------------------------

        std::cout
            << "\n15. ERROR HANDLING\n";

        try {
            binaryIndex({1, 0, 2});
        }
        catch (const std::exception& error) {
            std::cout
                << "Invalid input handled: "
                << error.what()
                << "\n";
        }

        try {
            mintermExpression(
                {"A", "B"},
                4
            );
        }
        catch (const std::exception& error) {
            std::cout
                << "Invalid minterm handled: "
                << error.what()
                << "\n";
        }

        try {
            BooleanSpecification invalid(
                2,
                {1},
                {1},
                {}
            );
        }
        catch (const std::exception& error) {
            std::cout
                << "Invalid specification handled: "
                << error.what()
                << "\n";
        }


        // --------------------------------------------------------
        // Final exhaustive consistency test
        // --------------------------------------------------------

        std::cout
            << "\n16. FINAL EXHAUSTIVE CONSISTENCY TEST\n";

        TruthTable testTable(
            {"A", "B", "C"},
            [](const BooleanVector& x) {
                // Example:
                // F = AB + C'
                return
                    (x[0] && x[1]) ||
                    !x[2];
            }
        );

        CanonicalRepresentation testRepresentation =
            extractCanonicalRepresentation(
                testTable
            );

        for (std::size_t row = 0;
             row < testTable.getRows().size();
             ++row) {

            const int expected =
                testTable.getOutputs()[row];

            const int sop =
                evaluateSOP(
                    testTable.getRows()[row],
                    testRepresentation.minterms
                );

            const int pos =
                evaluatePOS(
                    testTable.getRows()[row],
                    testRepresentation.maxterms
                );

            if (
                expected != sop ||
                expected != pos
            ) {
                throw std::runtime_error(
                    "Canonical consistency test failed."
                );
            }
        }

        std::cout
            << "All canonical representation checks: PASS\n";

        std::cout
            << "\nProgram completed successfully.\n";

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
