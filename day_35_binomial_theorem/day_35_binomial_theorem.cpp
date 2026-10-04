#include <algorithm>
#include <cmath>
#include <cstdint>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * Binomial Theorem Case Study
 *
 * Scenario:
 * A symbolic mathematics service receives requests to analyze expressions
 * of the form (a + bx)^n. It must:
 *
 * - expand finite integer powers;
 * - extract individual coefficients without constructing every term;
 * - validate binomial identities;
 * - combine polynomial expressions;
 * - evaluate merge-like "calculation policies" for exact versus approximate
 *   arithmetic;
 * - support generalized real exponents through a convergent series.
 *
 * The implementation deliberately uses C++17 standard-library facilities only.
 *
 * Note:
 * The standard C++ library does not provide an arbitrary-precision integer.
 * Therefore the finite exact implementation uses unsigned long long and
 * detects overflow before multiplication. This is a real constraint that
 * distinguishes this implementation from languages with arbitrary-precision
 * integers.
 */

using U64 = unsigned long long;

class BinomialError : public std::runtime_error {
public:
    explicit BinomialError(const std::string& message)
        : std::runtime_error(message) {}
};

// -----------------------------------------------------------------------------
// Safe integer arithmetic
// -----------------------------------------------------------------------------

U64 checkedMultiply(U64 left, U64 right) {
    if (left != 0 && right > std::numeric_limits<U64>::max() / left) {
        throw BinomialError("unsigned integer overflow");
    }

    return left * right;
}

U64 checkedAdd(U64 left, U64 right) {
    if (right > std::numeric_limits<U64>::max() - left) {
        throw BinomialError("unsigned integer addition overflow");
    }

    return left + right;
}

// -----------------------------------------------------------------------------
// Binomial coefficient engine
// -----------------------------------------------------------------------------

U64 binomialCoefficient(unsigned n, unsigned k) {
    if (k > n) {
        return 0;
    }

    // C(n,k) = C(n,n-k), so calculate the smaller side.
    k = std::min(k, n - k);

    U64 result = 1;

    for (unsigned i = 1; i <= k; ++i) {
        /*
         * The mathematical recurrence is:
         *
         * C(n,i) = C(n,i-1) * (n-i+1) / i
         *
         * The intermediate multiplication may overflow even when the final
         * coefficient fits. For a robust arbitrary-range production service,
         * boost::multiprecision::cpp_int would be appropriate. This case study
         * instead exposes overflow as a controlled failure.
         */
        const U64 factor = static_cast<U64>(n - i + 1);
        const U64 numerator = checkedMultiply(result, factor);

        if (numerator % i != 0) {
            throw BinomialError("internal exact-division invariant failed");
        }

        result = numerator / i;
    }

    return result;
}

// -----------------------------------------------------------------------------
// Polynomial model
// -----------------------------------------------------------------------------

class Polynomial {
private:
    std::vector<long double> coefficients_;

    void normalize() {
        while (coefficients_.size() > 1 &&
               std::fabs(coefficients_.back()) < 1e-18L) {
            coefficients_.pop_back();
        }

        if (coefficients_.empty()) {
            coefficients_.push_back(0.0L);
        }
    }

public:
    explicit Polynomial(std::vector<long double> coefficients)
        : coefficients_(std::move(coefficients)) {
        normalize();
    }

    static Polynomial binomial(unsigned n, long double a, long double b) {
        std::vector<long double> coefficients(n + 1);

        for (unsigned k = 0; k <= n; ++k) {
            const U64 combination = binomialCoefficient(n, k);

            coefficients[k] =
                static_cast<long double>(combination) *
                std::pow(a, static_cast<long double>(n - k)) *
                std::pow(b, static_cast<long double>(k));
        }

        return Polynomial(std::move(coefficients));
    }

    const std::vector<long double>& coefficients() const {
        return coefficients_;
    }

    Polynomial multiply(const Polynomial& other) const {
        std::vector<long double> result(
            coefficients_.size() + other.coefficients_.size() - 1,
            0.0L
        );

        /*
         * Polynomial multiplication is a discrete convolution:
         * coefficient[i+j] receives coefficient[i] * coefficient[j].
         *
         * This is O(degree_left * degree_right), which is appropriate for
         * the moderate symbolic degrees used by this service.
         */
        for (std::size_t i = 0; i < coefficients_.size(); ++i) {
            for (std::size_t j = 0; j < other.coefficients_.size(); ++j) {
                result[i + j] += coefficients_[i] * other.coefficients_[j];
            }
        }

        return Polynomial(std::move(result));
    }

    long double evaluate(long double x) const {
        // Horner evaluation reduces repeated powers and uses O(degree) work.
        long double result = 0.0L;

        for (auto it = coefficients_.rbegin();
             it != coefficients_.rend();
             ++it) {
            result = result * x + *it;
        }

        return result;
    }

    std::string toString(const std::string& variable = "x") const {
        std::ostringstream output;
        output << std::setprecision(8);

        bool first = true;

        for (std::size_t power = 0; power < coefficients_.size(); ++power) {
            const long double coefficient = coefficients_[power];

            if (std::fabs(coefficient) < 1e-18L) {
                continue;
            }

            if (!first) {
                output << (coefficient < 0 ? " - " : " + ");
            } else if (coefficient < 0) {
                output << "-";
            }

            const long double magnitude = std::fabs(coefficient);

            if (power == 0) {
                output << magnitude;
            } else {
                if (std::fabs(magnitude - 1.0L) > 1e-18L) {
                    output << magnitude;
                }

                output << variable;

                if (power > 1) {
                    output << "^" << power;
                }
            }

            first = false;
        }

        return first ? "0" : output.str();
    }
};

// -----------------------------------------------------------------------------
// Generalized binomial series
// -----------------------------------------------------------------------------

long double generalizedCoefficient(long double alpha, unsigned k) {
    long double coefficient = 1.0L;

    for (unsigned j = 0; j < k; ++j) {
        coefficient *= (alpha - static_cast<long double>(j));
        coefficient /= static_cast<long double>(j + 1);
    }

    return coefficient;
}

long double generalizedBinomialSeries(
    long double alpha,
    long double x,
    unsigned terms
) {
    if (terms == 0) {
        throw BinomialError("terms must be greater than zero");
    }

    /*
     * For non-integer alpha, the standard generalized expansion
     *
     * (1+x)^alpha = sum C(alpha,k)x^k
     *
     * converges for |x| < 1.
     */
    const bool integerExponent =
        std::fabs(alpha - std::round(alpha)) < 1e-15L;

    if (!integerExponent && std::fabs(x) >= 1.0L) {
        throw BinomialError(
            "non-integer generalized binomial series requires |x| < 1"
        );
    }

    long double coefficient = 1.0L;
    long double power = 1.0L;
    long double sum = 1.0L;

    for (unsigned k = 1; k < terms; ++k) {
        coefficient *= alpha - static_cast<long double>(k - 1);
        coefficient /= static_cast<long double>(k);

        power *= x;
        sum += coefficient * power;
    }

    return sum;
}

// -----------------------------------------------------------------------------
// Identity validation
// -----------------------------------------------------------------------------

bool verifyPascalIdentity(unsigned n, unsigned k) {
    if (n == 0 || k > n) {
        throw BinomialError("invalid Pascal identity parameters");
    }

    return binomialCoefficient(n, k) ==
           binomialCoefficient(n - 1, k - 1) +
           binomialCoefficient(n - 1, k);
}

bool verifySymmetry(unsigned n, unsigned k) {
    if (k > n) {
        throw BinomialError("invalid symmetry parameters");
    }

    return binomialCoefficient(n, k) ==
           binomialCoefficient(n, n - k);
}

bool verifyHockeyStick(unsigned n, unsigned k) {
    if (k > n) {
        throw BinomialError("require n >= k");
    }

    U64 sum = 0;

    for (unsigned row = k; row <= n; ++row) {
        sum = checkedAdd(sum, binomialCoefficient(row, k));
    }

    return sum == binomialCoefficient(n + 1, k + 1);
}

bool verifyVandermonde(unsigned r, unsigned s, unsigned n) {
    if (n > r + s) {
        return binomialCoefficient(r + s, n) == 0;
    }

    U64 sum = 0;

    for (unsigned k = 0; k <= n; ++k) {
        if (k <= r && n - k <= s) {
            const U64 left = binomialCoefficient(r, k);
            const U64 right = binomialCoefficient(s, n - k);

            sum = checkedAdd(sum, checkedMultiply(left, right));
        }
    }

    return sum == binomialCoefficient(r + s, n);
}

// -----------------------------------------------------------------------------
// Domain case study: risk of approximation versus exact symbolic arithmetic
// -----------------------------------------------------------------------------

enum class CalculationMode {
    ExactInteger,
    FloatingPointApproximation,
    GeneralizedSeries
};

struct ExpansionRequest {
    unsigned exponent;
    long double a;
    long double b;
    CalculationMode mode;
    unsigned seriesTerms = 20;
};

class ExpansionService {
public:
    Polynomial process(const ExpansionRequest& request) const {
        if (request.exponent > 100000) {
            throw BinomialError(
                "exponent exceeds the service safety limit"
            );
        }

        if (request.mode == CalculationMode::ExactInteger) {
            /*
             * Exact mode is only meaningful for integral coefficients.
             * This example checks representability before converting.
             */
            if (std::floor(request.a) != request.a ||
                std::floor(request.b) != request.b) {
                throw BinomialError(
                    "exact integer mode requires integral a and b"
                );
            }
        }

        if (request.mode == CalculationMode::GeneralizedSeries) {
            throw BinomialError(
                "generalized mode belongs to scalar series evaluation, "
                "not finite polynomial construction"
            );
        }

        return Polynomial::binomial(
            request.exponent,
            request.a,
            request.b
        );
    }
};

// -----------------------------------------------------------------------------
// Combinatorial application
// -----------------------------------------------------------------------------

U64 binaryStringsWithExactOnes(unsigned length, unsigned ones) {
    if (ones > length) {
        return 0;
    }

    /*
     * Each valid string corresponds to selecting which `ones` positions
     * contain 1. The remaining positions necessarily contain 0.
     */
    return binomialCoefficient(length, ones);
}

// -----------------------------------------------------------------------------
// Demonstration
// -----------------------------------------------------------------------------

void printRow(const std::vector<U64>& row) {
    for (const U64 value : row) {
        std::cout << value << " ";
    }

    std::cout << "\n";
}

int main() {
    try {
        std::cout << std::string(72, '=') << "\n";
        std::cout << "BINOMIAL THEOREM - C++17 CASE STUDY\n";
        std::cout << std::string(72, '=') << "\n";

        std::cout << "\nFinite expansion\n";

        Polynomial first = Polynomial::binomial(5, 1.0L, 1.0L);
        std::cout << "(1+x)^5 = " << first.toString() << "\n";

        Polynomial scaled = Polynomial::binomial(4, 2.0L, 3.0L);
        std::cout << "(2+3x)^4 = " << scaled.toString() << "\n";

        std::cout << "\nIndividual coefficient extraction\n";

        std::cout << "[x^4](1+x)^10 = "
                  << binomialCoefficient(10, 4)
                  << "\n";

        std::cout << "[x^3](2+5x)^7 = "
                  << static_cast<unsigned long long>(
                         binomialCoefficient(7, 3)
                     ) *
                         static_cast<unsigned long long>(std::pow(2.0, 4)) *
                         static_cast<unsigned long long>(std::pow(5.0, 3))
                  << "\n";

        std::cout << "\nPascal triangle\n";

        for (unsigned row = 0; row < 8; ++row) {
            std::vector<U64> values;

            for (unsigned k = 0; k <= row; ++k) {
                values.push_back(binomialCoefficient(row, k));
            }

            printRow(values);
        }

        std::cout << "\nIdentity validation\n";
        std::cout << "Pascal: "
                  << std::boolalpha
                  << verifyPascalIdentity(15, 6)
                  << "\n";

        std::cout << "Symmetry: "
                  << verifySymmetry(15, 6)
                  << "\n";

        std::cout << "Hockey-stick: "
                  << verifyHockeyStick(15, 6)
                  << "\n";

        std::cout << "Vandermonde: "
                  << verifyVandermonde(8, 7, 6)
                  << "\n";

        std::cout << "\nPolynomial multiplication\n";

        Polynomial p1({1.0L, 2.0L});
        Polynomial p2({3.0L, 4.0L, 1.0L});

        Polynomial product = p1.multiply(p2);

        std::cout << "(1+2x)(3+4x+x^2) = "
                  << product.toString()
                  << "\n";

        std::cout << "Product evaluated at x=2: "
                  << product.evaluate(2.0L)
                  << "\n";

        std::cout << "\nEnterprise-style expansion service\n";

        ExpansionService service;

        ExpansionRequest request{
            6,
            2.0L,
            3.0L,
            CalculationMode::ExactInteger
        };

        Polynomial serviceResult = service.process(request);

        std::cout << "Accepted request: "
                  << serviceResult.toString()
                  << "\n";

        std::cout << "\nGeneralized binomial approximation\n";

        const long double generalized =
            generalizedBinomialSeries(
                0.5L,
                0.25L,
                25
            );

        std::cout << std::setprecision(15)
                  << "(1.25)^(1/2) by series = "
                  << generalized
                  << "\n";

        std::cout << "Reference sqrt(1.25) = "
                  << std::sqrt(1.25L)
                  << "\n";

        std::cout << "\nCombinatorial application\n";

        std::cout
            << "12-bit strings with exactly 5 ones = "
            << binaryStringsWithExactOnes(12, 5)
            << "\n";

        std::cout << "\nFailure handling\n";

        try {
            service.process({
                5,
                2.5L,
                3.0L,
                CalculationMode::ExactInteger
            });
        } catch (const std::exception& error) {
            std::cout << "Rejected invalid exact request: "
                      << error.what()
                      << "\n";
        }

        try {
            std::cout << "C(100000,50000) = "
                      << binomialCoefficient(100000, 50000)
                      << "\n";
        } catch (const std::exception& error) {
            std::cout << "Large exact coefficient rejected safely: "
                      << error.what()
                      << "\n";
        }

        try {
            generalizedBinomialSeries(0.5L, 1.1L, 20);
        } catch (const std::exception& error) {
            std::cout << "Invalid generalized-series domain: "
                      << error.what()
                      << "\n";
        }

        std::cout << "\nDesign observations\n";
        std::cout
            << "Finite polynomial expansion is O(n) in the number of "
               "generated terms, while naive polynomial multiplication "
               "is O(degree_left * degree_right).\n";

        std::cout
            << "Horner evaluation is O(n) and avoids explicitly computing "
               "each power of x.\n";

        std::cout
            << "The standard library's lack of arbitrary-precision integers "
               "is an explicit production constraint in this implementation. "
               "Overflow detection prevents silently corrupted coefficients.\n";

        std::cout
            << "Generalized expansions require convergence-domain validation "
               "when the exponent is non-integer.\n";

        return 0;
    }
    catch (const std::exception& error) {
        std::cerr << "Fatal calculation error: "
                  << error.what()
                  << "\n";
        return 1;
    }
}
