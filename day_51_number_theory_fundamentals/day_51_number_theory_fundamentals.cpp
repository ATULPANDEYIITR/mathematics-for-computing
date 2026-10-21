#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

/*
 * Topic: Number Theory Fundamentals
 *
 * Case study:
 * A repository-quality numerical analysis service classifies identifiers,
 * validates divisibility rules, calculates factors, and evaluates common
 * divisors used to partition resources into equal groups.
 *
 * C++17, standard library only.
 */

class NumberTheoryError : public std::invalid_argument {
public:
    explicit NumberTheoryError(const std::string& message)
        : std::invalid_argument(message) {}
};

class NumberTheory {
public:
    static bool divides(long long divisor, long long value) {
        if (divisor == 0) {
            throw NumberTheoryError("zero cannot be used as a divisor");
        }
        return value % divisor == 0;
    }

    static std::vector<long long> divisors(long long n) {
        validatePositive(n);

        std::vector<long long> result;

        // Use i <= n / i rather than i * i <= n to avoid multiplication
        // overflow when n is close to LLONG_MAX.
        for (long long i = 1; i <= n / i; ++i) {
            if (n % i == 0) {
                result.push_back(i);

                const long long paired = n / i;
                if (paired != i) {
                    result.push_back(paired);
                }
            }
        }

        std::sort(result.begin(), result.end());
        return result;
    }

    static bool isPrime(long long n) {
        if (n < 2) {
            return false;
        }

        if (n == 2) {
            return true;
        }

        if (n % 2 == 0) {
            return false;
        }

        // The n / candidate form prevents candidate*candidate overflow.
        for (long long candidate = 3;
             candidate <= n / candidate;
             candidate += 2) {
            if (n % candidate == 0) {
                return false;
            }
        }

        return true;
    }

    static bool isComposite(long long n) {
        validatePositive(n);
        return n > 1 && !isPrime(n);
    }

    static std::map<long long, int> primeFactorization(long long n) {
        validatePositive(n);

        std::map<long long, int> factors;
        long long remaining = n;

        while (remaining % 2 == 0 && remaining > 1) {
            ++factors[2];
            remaining /= 2;
        }

        for (long long candidate = 3;
             candidate <= remaining / candidate;
             candidate += 2) {
            while (remaining % candidate == 0) {
                ++factors[candidate];
                remaining /= candidate;
            }
        }

        if (remaining > 1) {
            ++factors[remaining];
        }

        return factors;
    }

    static long long gcd(long long a, long long b) {
        // std::gcd handles signs, but explicitly rejecting (0,0) makes the
        // domain rule visible instead of silently relying on a convention.
        if (a == 0 && b == 0) {
            throw NumberTheoryError("gcd(0, 0) is undefined");
        }

        a = std::llabs(a);
        b = std::llabs(b);

        // Euclid's algorithm has logarithmic iteration count in the size
        // of its inputs and avoids factor enumeration.
        while (b != 0) {
            const long long remainder = a % b;
            a = b;
            b = remainder;
        }

        return a;
    }

    static long long gcdMany(const std::vector<long long>& values) {
        if (values.empty()) {
            throw NumberTheoryError("at least one value is required");
        }

        long long result = 0;
        for (const long long value : values) {
            result = gcd(result, value);
        }

        return result;
    }

    static long long lcm(long long a, long long b) {
        if (a == 0 || b == 0) {
            return 0;
        }

        const long long divisor = gcd(a, b);
        const long long reduced = a / divisor;

        // This check prevents signed overflow before multiplication.
        if (reduced > 0 && b > 0 &&
            reduced > std::numeric_limits<long long>::max() / b) {
            throw NumberTheoryError("LCM exceeds long long range");
        }

        if (reduced < 0 && b > 0 &&
            reduced < std::numeric_limits<long long>::min() / b) {
            throw NumberTheoryError("LCM exceeds long long range");
        }

        if (reduced > 0 && b < 0 &&
            reduced > std::numeric_limits<long long>::min() / b) {
            throw NumberTheoryError("LCM exceeds long long range");
        }

        if (reduced < 0 && b < 0 &&
            reduced < std::numeric_limits<long long>::max() / b) {
            throw NumberTheoryError("LCM exceeds long long range");
        }

        return std::llabs(reduced * b);
    }

    static std::string classify(long long n) {
        if (n < 0) return "negative integer";
        if (n == 0) return "zero";
        if (n == 1) return "unit";
        return isPrime(n) ? "prime" : "composite";
    }

private:
    static void validatePositive(long long n) {
        if (n <= 0) {
            throw NumberTheoryError("value must be positive");
        }
    }
};

struct RepositoryIdentifier {
    long long id;
    std::string owner;
    std::string repository;

    void validate() const {
        if (id <= 0) {
            throw NumberTheoryError("repository identifier must be positive");
        }

        if (owner.empty() || repository.empty()) {
            throw NumberTheoryError("owner and repository must not be empty");
        }
    }
};

class GovernancePartitionPlanner {
public:
    explicit GovernancePartitionPlanner(
        std::vector<RepositoryIdentifier> identifiers)
        : identifiers_(std::move(identifiers)) {}

    void printAnalysis() const {
        for (const auto& identifier : identifiers_) {
            identifier.validate();

            const auto factors = NumberTheory::primeFactorization(identifier.id);
            const auto allDivisors = NumberTheory::divisors(identifier.id);

            std::cout << identifier.owner << "/" << identifier.repository
                      << " [" << identifier.id << "]\n";
            std::cout << "  classification: "
                      << NumberTheory::classify(identifier.id) << "\n";
            std::cout << "  divisors: ";

            for (std::size_t i = 0; i < allDivisors.size(); ++i) {
                if (i != 0) std::cout << ", ";
                std::cout << allDivisors[i];
            }
            std::cout << "\n";

            std::cout << "  prime factorization: ";
            bool first = true;
            for (const auto& [prime, exponent] : factors) {
                if (!first) std::cout << " * ";
                first = false;
                std::cout << prime;
                if (exponent > 1) {
                    std::cout << "^" << exponent;
                }
            }
            std::cout << "\n";
        }
    }

private:
    std::vector<RepositoryIdentifier> identifiers_;
};

int main() {
    try {
        std::cout << "NUMBER THEORY FUNDAMENTALS\n";
        std::cout << std::string(72, '=') << "\n\n";

        GovernancePartitionPlanner planner({
            {84, "platform", "release-service"},
            {97, "security", "policy-engine"},
            {360, "data", "warehouse-loader"},
            {600851475143LL, "research", "factor-analysis"}
        });

        planner.printAnalysis();

        std::cout << "\nDIVISIBILITY VALIDATION\n";
        std::cout << std::boolalpha;
        std::cout << "7 divides 84: "
                  << NumberTheory::divides(7, 84) << "\n";
        std::cout << "5 divides 84: "
                  << NumberTheory::divides(5, 84) << "\n";

        std::cout << "\nGCD FOR EQUAL PARTITIONING\n";
        const std::vector<long long> resourceCounts{84, 126, 210};
        const long long groupSize = NumberTheory::gcdMany(resourceCounts);

        std::cout << "resource counts: ";
        for (const auto value : resourceCounts) {
            std::cout << value << " ";
        }
        std::cout << "\nmaximum equal group size: " << groupSize << "\n";

        std::cout << "groups per resource set: ";
        for (const auto value : resourceCounts) {
            std::cout << value / groupSize << " ";
        }
        std::cout << "\n";

        std::cout << "\nCOPRIMALITY\n";
        std::cout << "gcd(35, 64): "
                  << NumberTheory::gcd(35, 64) << "\n";
        std::cout << "lcm(12, 18): "
                  << NumberTheory::lcm(12, 18) << "\n";

        std::cout << "\nFAILURE CONDITIONS\n";

        try {
            NumberTheory::divides(0, 84);
        } catch (const NumberTheoryError& error) {
            std::cout << "invalid divisor rejected: "
                      << error.what() << "\n";
        }

        try {
            NumberTheory::gcd(0, 0);
        } catch (const NumberTheoryError& error) {
            std::cout << "undefined GCD rejected: "
                      << error.what() << "\n";
        }

        /*
         * Complexity:
         * - gcd: O(log(min(|a|, |b|)))
         * - primality by trial division: O(sqrt(n))
         * - divisor enumeration: O(sqrt(n)) time and O(d(n)) space
         * - trial factorization: potentially O(sqrt(n)) divisions
         *
         * For cryptographic-scale integers, deterministic trial division is
         * inappropriate; specialized big-integer algorithms are required.
         */
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
