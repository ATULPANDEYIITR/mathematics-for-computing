#include <algorithm>
#include <cstdint>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

/*
 * Combinations: binomial coefficients, combinations, and Pascal's triangle.
 *
 * Technical case study:
 * A capacity-planning system evaluates possible project committees, audit
 * samples, and allocation patterns. The system uses exact binomial
 * coefficients to determine how many unordered selections are possible,
 * stores reusable Pascal rows, validates constraints, and evaluates
 * combinatorial probabilities.
 *
 * C++17 or later.
 *
 * The program uses unsigned __int128 internally for intermediate exact
 * arithmetic. This permits substantially larger intermediate values than
 * uint64_t, although it is still finite and therefore not an arbitrary-
 * precision solution.
 */

using UInt128 = unsigned __int128;

// ---------------------------------------------------------------------------
// Utility formatting
// ---------------------------------------------------------------------------

std::string toString(UInt128 value) {
    if (value == 0) {
        return "0";
    }

    std::string result;

    while (value > 0) {
        const unsigned digit = static_cast<unsigned>(value % 10);
        result.push_back(static_cast<char>('0' + digit));
        value /= 10;
    }

    std::reverse(result.begin(), result.end());
    return result;
}

void validateNK(std::size_t n, std::size_t k) {
    if (k > n) {
        throw std::invalid_argument("k must not exceed n");
    }
}

// ---------------------------------------------------------------------------
// Exact binomial coefficient
// ---------------------------------------------------------------------------

UInt128 combination(std::size_t n, std::size_t k) {
    validateNK(n, k);

    k = std::min(k, n - k);

    UInt128 result = 1;

    for (std::size_t i = 1; i <= k; ++i) {
        /*
         * This multiplicative recurrence avoids calculating n! and is much
         * less wasteful for a single coefficient.
         *
         * result = result * (n-k+i) / i
         *
         * The mathematical coefficient guarantees exact division at each
         * recurrence step.
         */
        result = (result * static_cast<UInt128>(n - k + i))
                 / static_cast<UInt128>(i);
    }

    return result;
}

// ---------------------------------------------------------------------------
// Pascal triangle
// ---------------------------------------------------------------------------

class PascalTriangle {
private:
    std::vector<std::vector<UInt128>> rows_;

public:
    explicit PascalTriangle(std::size_t rowCount) {
        rows_.reserve(rowCount);

        for (std::size_t n = 0; n < rowCount; ++n) {
            std::vector<UInt128> row(n + 1, 1);

            if (n >= 2) {
                const auto& previous = rows_[n - 1];

                for (std::size_t k = 1; k < n; ++k) {
                    row[k] = previous[k - 1] + previous[k];
                }
            }

            rows_.push_back(std::move(row));
        }
    }

    UInt128 coefficient(std::size_t n, std::size_t k) const {
        validateNK(n, k);

        if (n >= rows_.size()) {
            throw std::out_of_range("requested row is not stored");
        }

        return rows_[n][k];
    }

    const std::vector<UInt128>& row(std::size_t n) const {
        if (n >= rows_.size()) {
            throw std::out_of_range("requested row is not stored");
        }

        return rows_[n];
    }

    std::size_t size() const {
        return rows_.size();
    }

    void print() const {
        if (rows_.empty()) {
            return;
        }

        std::string finalWidth;

        for (UInt128 value : rows_.back()) {
            finalWidth += toString(value) + " ";
        }

        const std::size_t width = finalWidth.size();

        for (const auto& rowValues : rows_) {
            std::string line;

            for (UInt128 value : rowValues) {
                if (!line.empty()) {
                    line += ' ';
                }

                line += toString(value);
            }

            const std::size_t padding =
                line.size() < width ? (width - line.size()) / 2 : 0;

            std::cout << std::string(padding, ' ')
                      << line
                      << '\n';
        }
    }
};

// ---------------------------------------------------------------------------
// Project governance case study
// ---------------------------------------------------------------------------

struct CommitteeRequest {
    std::size_t availableEngineers;
    std::size_t committeeSize;
    std::string projectName;
};

class CommitteePlanner {
public:
    UInt128 possibleCommittees(const CommitteeRequest& request) const {
        if (request.availableEngineers == 0) {
            throw std::invalid_argument(
                "a project must have at least one available engineer"
            );
        }

        if (request.committeeSize == 0) {
            /*
             * There is exactly one empty committee mathematically. Whether an
             * application permits it is a domain rule, so this planner
             * rejects it explicitly instead of silently assigning meaning.
             */
            throw std::invalid_argument(
                "committee size must be greater than zero"
            );
        }

        if (request.committeeSize > request.availableEngineers) {
            throw std::invalid_argument(
                "committee size cannot exceed available engineers"
            );
        }

        return combination(
            request.availableEngineers,
            request.committeeSize
        );
    }
};

// ---------------------------------------------------------------------------
// Audit sample probability
// ---------------------------------------------------------------------------

struct Fraction {
    UInt128 numerator;
    UInt128 denominator;
};

UInt128 gcd128(UInt128 a, UInt128 b) {
    while (b != 0) {
        UInt128 remainder = a % b;
        a = b;
        b = remainder;
    }

    return a;
}

Fraction reduceFraction(UInt128 numerator, UInt128 denominator) {
    if (denominator == 0) {
        throw std::invalid_argument("fraction denominator cannot be zero");
    }

    const UInt128 divisor = gcd128(numerator, denominator);

    return {
        numerator / divisor,
        denominator / divisor
    };
}

Fraction hypergeometricProbability(
    std::size_t population,
    std::size_t targetItems,
    std::size_t sampleSize,
    std::size_t targetItemsSelected
) {
    if (targetItems > population) {
        throw std::invalid_argument(
            "targetItems cannot exceed population"
        );
    }

    if (sampleSize > population) {
        throw std::invalid_argument(
            "sampleSize cannot exceed population"
        );
    }

    const std::size_t nonTargets = population - targetItems;

    if (targetItemsSelected > targetItems) {
        return {0, 1};
    }

    if (sampleSize < targetItemsSelected) {
        return {0, 1};
    }

    const std::size_t nonTargetsSelected =
        sampleSize - targetItemsSelected;

    if (nonTargetsSelected > nonTargets) {
        return {0, 1};
    }

    /*
     * Every sample of the same size is treated as equally likely.
     *
     * Favorable samples:
     *   choose targetItemsSelected from all target items
     *   choose the remaining positions from non-target items
     *
     * Total samples:
     *   choose sampleSize from the entire population.
     */
    const UInt128 favorable =
        combination(targetItems, targetItemsSelected) *
        combination(nonTargets, nonTargetsSelected);

    const UInt128 total =
        combination(population, sampleSize);

    return reduceFraction(favorable, total);
}

// ---------------------------------------------------------------------------
// Combination generation
// ---------------------------------------------------------------------------

class CombinationGenerator {
public:
    using Selection = std::vector<std::string>;

private:
    const std::vector<std::string>& values_;
    std::size_t targetSize_;
    Selection current_;
    std::vector<Selection> output_;

    void generate(std::size_t start) {
        if (current_.size() == targetSize_) {
            output_.push_back(current_);
            return;
        }

        const std::size_t remaining =
            targetSize_ - current_.size();

        if (values_.size() - start < remaining) {
            return;
        }

        /*
         * Each recursive choice fixes one position in the unordered
         * selection. Increasing start prevents the same committee from being
         * generated in a different order.
         */
        for (std::size_t index = start;
             index <= values_.size() - remaining;
             ++index) {

            current_.push_back(values_[index]);
            generate(index + 1);
            current_.pop_back();
        }
    }

public:
    CombinationGenerator(
        const std::vector<std::string>& values,
        std::size_t targetSize
    )
        : values_(values),
          targetSize_(targetSize) {

        if (targetSize > values.size()) {
            throw std::invalid_argument(
                "selection size cannot exceed input size"
            );
        }
    }

    std::vector<Selection> generateAll() {
        output_.clear();
        current_.clear();
        generate(0);
        return output_;
    }
};

// ---------------------------------------------------------------------------
// Binomial theorem
// ---------------------------------------------------------------------------

long long checkedPower(long long base, std::size_t exponent) {
    long long result = 1;

    for (std::size_t i = 0; i < exponent; ++i) {
        if (base != 0 &&
            (result > std::numeric_limits<long long>::max() / base ||
             result < std::numeric_limits<long long>::min() / base)) {
            throw std::overflow_error("power exceeds long long range");
        }

        result *= base;
    }

    return result;
}

long long evaluateBinomialExpansion(
    long long a,
    long long b,
    std::size_t n
) {
    long long total = 0;

    for (std::size_t k = 0; k <= n; ++k) {
        const UInt128 coefficient = combination(n, k);

        /*
         * This demonstration deliberately converts the coefficient to
         * unsigned long long only after checking the range. A production
         * arbitrary-size numeric implementation would keep every term in an
         * arbitrary-precision representation.
         */
        if (coefficient >
            static_cast<UInt128>(
                std::numeric_limits<unsigned long long>::max()
            )) {
            throw std::overflow_error(
                "binomial coefficient exceeds demonstration range"
            );
        }

        const auto coefficient64 =
            static_cast<unsigned long long>(coefficient);

        const long long left =
            checkedPower(a, n - k);

        const long long right =
            checkedPower(b, k);

        const __int128 term =
            static_cast<__int128>(coefficient64) *
            static_cast<__int128>(left) *
            static_cast<__int128>(right);

        const __int128 newTotal =
            static_cast<__int128>(total) + term;

        if (newTotal >
                static_cast<__int128>(
                    std::numeric_limits<long long>::max()
                ) ||
            newTotal <
                static_cast<__int128>(
                    std::numeric_limits<long long>::min()
                )) {
            throw std::overflow_error(
                "binomial expansion exceeds long long range"
            );
        }

        total = static_cast<long long>(newTotal);
    }

    return total;
}

// ---------------------------------------------------------------------------
// Identity validation
// ---------------------------------------------------------------------------

bool verifySymmetry(std::size_t limit) {
    for (std::size_t n = 0; n <= limit; ++n) {
        for (std::size_t k = 0; k <= n; ++k) {
            if (combination(n, k) != combination(n, n - k)) {
                return false;
            }
        }
    }

    return true;
}

bool verifyPascalIdentity(std::size_t limit) {
    for (std::size_t n = 1; n <= limit; ++n) {
        for (std::size_t k = 1; k < n; ++k) {
            const UInt128 left = combination(n, k);

            const UInt128 right =
                combination(n - 1, k - 1) +
                combination(n - 1, k);

            if (left != right) {
                return false;
            }
        }
    }

    return true;
}

bool verifyRowSums(std::size_t limit) {
    UInt128 expected = 1;

    for (std::size_t n = 0; n <= limit; ++n) {
        UInt128 sum = 0;

        for (std::size_t k = 0; k <= n; ++k) {
            sum += combination(n, k);
        }

        if (sum != expected) {
            return false;
        }

        expected *= 2;
    }

    return true;
}

// ---------------------------------------------------------------------------
// Main case study
// ---------------------------------------------------------------------------

int main() {
    try {
        std::cout << "COMBINATIONS AND BINOMIAL COEFFICIENTS\n";
        std::cout << "=====================================\n\n";

        std::cout << "=== Project committee planning ===\n";

        CommitteePlanner planner;

        const CommitteeRequest request{
            12,
            4,
            "Distributed Data Platform"
        };

        const UInt128 committeeCount =
            planner.possibleCommittees(request);

        std::cout << request.projectName
                  << " has "
                  << request.availableEngineers
                  << " eligible engineers and requires "
                  << request.committeeSize
                  << " members.\n";

        std::cout << "Possible unordered committees: "
                  << toString(committeeCount)
                  << "\n\n";

        std::cout << "=== Pascal's triangle ===\n";

        PascalTriangle triangle(9);
        triangle.print();

        std::cout << "\nCoefficient lookup C(50,25): "
                  << toString(triangle.size() > 50
                                  ? triangle.coefficient(50, 25)
                                  : combination(50, 25))
                  << "\n";

        std::cout << "\n=== Concrete committee generation ===\n";

        const std::vector<std::string> engineers{
            "Aarav",
            "Meera",
            "Kabir",
            "Isha",
            "Rohan"
        };

        CombinationGenerator generator(engineers, 3);
        const auto committees = generator.generateAll();

        std::cout << "Generated "
                  << committees.size()
                  << " committees:\n";

        for (const auto& committee : committees) {
            std::cout << "  {";

            for (std::size_t i = 0; i < committee.size(); ++i) {
                if (i > 0) {
                    std::cout << ", ";
                }

                std::cout << committee[i];
            }

            std::cout << "}\n";
        }

        std::cout << "\n=== Audit sampling probability ===\n";

        /*
         * Twenty records exist in a population. Five are classified as
         * high-risk. Four records are audited without replacement. The
         * probability below is for exactly two high-risk records.
         */
        const Fraction auditProbability =
            hypergeometricProbability(
                20,
                5,
                4,
                2
            );

        std::cout << "P(exactly 2 high-risk records) = "
                  << toString(auditProbability.numerator)
                  << "/"
                  << toString(auditProbability.denominator)
                  << "\n";

        std::cout << "\n=== Binomial theorem ===\n";

        const long long direct =
            checkedPower(2 + 3, 5);

        const long long expansion =
            evaluateBinomialExpansion(2, 3, 5);

        std::cout << "(2 + 3)^5 directly = "
                  << direct
                  << "\n";

        std::cout << "Binomial expansion = "
                  << expansion
                  << "\n";

        std::cout << "\n=== Identity validation ===\n";

        std::cout << "Symmetry identity: "
                  << (verifySymmetry(30) ? "PASS" : "FAIL")
                  << "\n";

        std::cout << "Pascal recurrence: "
                  << (verifyPascalIdentity(30) ? "PASS" : "FAIL")
                  << "\n";

        std::cout << "Row sum identity: "
                  << (verifyRowSums(30) ? "PASS" : "FAIL")
                  << "\n";

        std::cout << "\n=== Boundary and failure behavior ===\n";

        std::cout << "C(10,0) = "
                  << toString(combination(10, 0))
                  << "\n";

        std::cout << "C(10,10) = "
                  << toString(combination(10, 10))
                  << "\n";

        try {
            combination(5, 8);
        } catch (const std::exception& error) {
            std::cout << "Invalid C(5,8) rejected: "
                      << error.what()
                      << "\n";
        }

        try {
            CommitteeRequest invalid{
                4,
                7,
                "Invalid Project"
            };

            planner.possibleCommittees(invalid);
        } catch (const std::exception& error) {
            std::cout << "Invalid committee request rejected: "
                      << error.what()
                      << "\n";
        }

        std::cout << "\n=== Complexity and design characteristics ===\n";

        std::cout
            << "A single coefficient uses O(min(k,n-k)) multiplicative steps.\n";

        std::cout
            << "A stored Pascal triangle through row n requires O(n^2) "
               "coefficient storage.\n";

        std::cout
            << "Generating all k-element selections has output-sensitive "
               "complexity because C(n,k) selections may need to be emitted.\n";

        std::cout
            << "The program uses explicit validation because an invalid k "
               "would otherwise create meaningless combinatorial results.\n";

        std::cout
            << "Unsigned __int128 extends the exact integer range but does "
               "not eliminate overflow for arbitrarily large coefficients.\n";

        std::cout
            << "Production systems requiring unbounded exact coefficients "
               "should use an arbitrary-precision integer implementation.\n";

    } catch (const std::exception& error) {
        std::cerr << "Fatal error: "
                  << error.what()
                  << '\n';

        return 1;
    }

    return 0;
}
