#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

using Matrix = std::vector<std::vector<long long>>;

// A recurrence of order k has the form
//
//   a_n = c1*a_(n-1) + c2*a_(n-2) + ... + ck*a_(n-k) + f(n)
//
// The program uses a demand-planning case study. A warehouse forecasts future
// demand using a linear recurrence. A zero forcing function produces a
// homogeneous recurrence; a non-zero forcing function models external effects.

class RecurrenceModel {
private:
    std::vector<long long> coefficients;
    std::vector<long long> initialTerms;

public:
    RecurrenceModel(
        std::vector<long long> coefficients,
        std::vector<long long> initialTerms
    )
        : coefficients(std::move(coefficients)),
          initialTerms(std::move(initialTerms)) {

        if (this->coefficients.empty()) {
            throw std::invalid_argument(
                "A recurrence must have at least one coefficient."
            );
        }

        if (this->coefficients.size() != this->initialTerms.size()) {
            throw std::invalid_argument(
                "Recurrence order and initial-term count must match."
            );
        }
    }

    std::size_t order() const {
        return coefficients.size();
    }

    long long nextTerm(
        const std::vector<long long>& history,
        long long forcing
    ) const {
        if (history.size() < order()) {
            throw std::invalid_argument(
                "Insufficient history for recurrence evaluation."
            );
        }

        long long value = forcing;

        for (std::size_t i = 0; i < coefficients.size(); ++i) {
            value += coefficients[i] *
                     history[history.size() - 1 - i];
        }

        return value;
    }

    std::vector<long long> generate(
        std::size_t count,
        const std::function<long long(std::size_t)>& forcing
    ) const {
        std::vector<long long> terms;

        if (count == 0) {
            return terms;
        }

        for (std::size_t i = 0;
             i < count && i < initialTerms.size();
             ++i) {
            terms.push_back(initialTerms[i]);
        }

        while (terms.size() < count) {
            const std::size_t n = terms.size();
            const long long next = nextTerm(terms, forcing(n));

            if (next < 0) {
                throw std::domain_error(
                    "The model generated an invalid negative value."
                );
            }

            terms.push_back(next);
        }

        return terms;
    }
};

Matrix multiplyMatrix(const Matrix& a, const Matrix& b) {
    if (a.empty() || b.empty()) {
        throw std::invalid_argument("Matrices cannot be empty.");
    }

    if (a.front().size() != b.size()) {
        throw std::invalid_argument("Incompatible matrix dimensions.");
    }

    Matrix result(
        a.size(),
        std::vector<long long>(b.front().size(), 0)
    );

    for (std::size_t i = 0; i < a.size(); ++i) {
        for (std::size_t k = 0; k < b.size(); ++k) {
            for (std::size_t j = 0; j < b.front().size(); ++j) {
                result[i][j] += a[i][k] * b[k][j];
            }
        }
    }

    return result;
}

Matrix identityMatrix(std::size_t size) {
    Matrix result(
        size,
        std::vector<long long>(size, 0)
    );

    for (std::size_t i = 0; i < size; ++i) {
        result[i][i] = 1;
    }

    return result;
}

Matrix matrixPower(Matrix base, unsigned long long exponent) {
    if (base.empty() ||
        base.size() != base.front().size()) {
        throw std::invalid_argument(
            "Matrix exponentiation requires a square matrix."
        );
    }

    Matrix result = identityMatrix(base.size());

    while (exponent > 0) {
        if (exponent & 1ULL) {
            result = multiplyMatrix(result, base);
        }

        base = multiplyMatrix(base, base);
        exponent >>= 1ULL;
    }

    return result;
}

Matrix companionMatrix(
    const std::vector<long long>& coefficients
) {
    const std::size_t k = coefficients.size();

    Matrix matrix(
        k,
        std::vector<long long>(k, 0)
    );

    matrix[0] = coefficients;

    for (std::size_t row = 1; row < k; ++row) {
        matrix[row][row - 1] = 1;
    }

    return matrix;
}

long long nthHomogeneousTerm(
    const std::vector<long long>& coefficients,
    const std::vector<long long>& initialTerms,
    unsigned long long n
) {
    const std::size_t k = coefficients.size();

    if (initialTerms.size() != k) {
        throw std::invalid_argument(
            "Initial-term count must equal recurrence order."
        );
    }

    if (n < k) {
        return initialTerms[static_cast<std::size_t>(n)];
    }

    const Matrix transition = companionMatrix(coefficients);
    const Matrix powered = matrixPower(
        transition,
        n - (k - 1)
    );

    Matrix state(
        k,
        std::vector<long long>(1, 0)
    );

    for (std::size_t i = 0; i < k; ++i) {
        state[i][0] = initialTerms[k - 1 - i];
    }

    return multiplyMatrix(powered, state)[0][0];
}

void printTerms(
    const std::string& label,
    const std::vector<long long>& terms
) {
    std::cout << label << ": ";

    for (std::size_t i = 0; i < terms.size(); ++i) {
        if (i != 0) {
            std::cout << ", ";
        }
        std::cout << terms[i];
    }

    std::cout << '\n';
}

bool validateSequence(
    const std::vector<long long>& sequence,
    const RecurrenceModel& model,
    const std::function<long long(std::size_t)>& forcing
) {
    if (sequence.size() < model.order()) {
        return false;
    }

    for (std::size_t n = model.order();
         n < sequence.size();
         ++n) {

        std::vector<long long> history(
            sequence.begin(),
            sequence.begin() + n
        );

        const long long expected =
            model.nextTerm(history, forcing(n));

        if (expected != sequence[n]) {
            std::cout
                << "Validation failure at n=" << n
                << ": expected " << expected
                << ", observed " << sequence[n]
                << '\n';

            return false;
        }
    }

    return true;
}

// The case study represents a distribution center whose weekly demand follows
// a second-order linear model. Historical demand contributes through the
// recurrence, while a promotion or seasonal effect is represented separately
// as the forcing function.
//
// Homogeneous model:
//   D_n = D_(n-1) + D_(n-2)
//
// Non-homogeneous model:
//   D_n = D_(n-1) + D_(n-2) + campaign(n)
//
// Keeping the forcing term separate makes the mathematical distinction explicit.
void demandPlanningCaseStudy() {
    std::cout
        << "\n=== Distribution Center Demand Model ===\n";

    RecurrenceModel homogeneous(
        {1, 1},
        {120, 180}
    );

    const auto noExternalEffect =
        [](std::size_t) -> long long {
            return 0;
        };

    const auto normalDemand =
        homogeneous.generate(10, noExternalEffect);

    printTerms(
        "Homogeneous demand sequence",
        normalDemand
    );

    const auto campaignEffect =
        [](std::size_t n) -> long long {
            if (n % 4 == 0) {
                return 30;
            }

            return 0;
        };

    const auto campaignDemand =
        homogeneous.generate(10, campaignEffect);

    printTerms(
        "Non-homogeneous campaign sequence",
        campaignDemand
    );

    std::cout
        << "Homogeneous validation: "
        << std::boolalpha
        << validateSequence(
            normalDemand,
            homogeneous,
            noExternalEffect
        )
        << '\n';

    std::cout
        << "Campaign validation: "
        << validateSequence(
            campaignDemand,
            homogeneous,
            campaignEffect
        )
        << '\n';

    auto corrupted = campaignDemand;
    corrupted[6] += 100;

    std::cout
        << "Corrupted campaign sequence valid: "
        << validateSequence(
            corrupted,
            homogeneous,
            campaignEffect
        )
        << '\n';
}

void characteristicEquationCaseStudy() {
    std::cout
        << "\n=== Characteristic Equation ===\n";

    // For
    //
    //   a_n = 3a_(n-1) - 2a_(n-2)
    //
    // substitute a_n = r^n:
    //
    //   r^2 - 3r + 2 = 0
    //
    // which factors into:
    //
    //   (r - 1)(r - 2) = 0.
    //
    // Therefore the homogeneous solution has the structure
    //
    //   a_n = A*1^n + B*2^n.
    //
    // The program evaluates the same recurrence directly and through its
    // companion matrix.

    const std::vector<long long> coefficients = {3, -2};
    const std::vector<long long> initialTerms = {1, 3};

    RecurrenceModel model(
        coefficients,
        initialTerms
    );

    const auto sequence = model.generate(
        8,
        [](std::size_t) -> long long {
            return 0;
        }
    );

    printTerms(
        "Characteristic-equation recurrence",
        sequence
    );

    for (unsigned long long n : {10, 20, 30}) {
        std::cout
            << "a_" << n << " using matrix exponentiation = "
            << nthHomogeneousTerm(
                coefficients,
                initialTerms,
                n
            )
            << '\n';
    }
}

void edgeCaseDemonstration() {
    std::cout
        << "\n=== Edge Cases ===\n";

    try {
        RecurrenceModel invalid({}, {});
    } catch (const std::exception& error) {
        std::cout
            << "Empty coefficient list rejected: "
            << error.what()
            << '\n';
    }

    try {
        RecurrenceModel invalid({1, 1}, {1});
    } catch (const std::exception& error) {
        std::cout
            << "Mismatched initial terms rejected: "
            << error.what()
            << '\n';
    }

    try {
        matrixPower({{1, 2, 3}}, 4);
    } catch (const std::exception& error) {
        std::cout
            << "Non-square matrix rejected: "
            << error.what()
            << '\n';
    }
}

int main() {
    try {
        std::cout
            << "RECURRENCE RELATIONS ENGINE\n"
            << "C++17 case study\n";

        demandPlanningCaseStudy();
        characteristicEquationCaseStudy();
        edgeCaseDemonstration();

        std::cout
            << "\nComplexity notes:\n"
            << "Direct recurrence generation evaluates each term once.\n"
            << "For fixed order k, this is O(n*k) arithmetic operations.\n"
            << "Companion-matrix exponentiation reduces the number of matrix "
               "multiplication stages to O(log n).\n"
            << "For large exact integer terms, arithmetic width can become "
               "the dominant practical constraint.\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }
}
