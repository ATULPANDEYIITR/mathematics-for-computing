#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using u64 = std::uint64_t;
using u128 = unsigned __int128;

bool isPrime(u64 n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;

    for (u64 divisor = 3; divisor <= n / divisor; divisor += 2) {
        if (n % divisor == 0) return false;
    }
    return true;
}

std::map<u64, unsigned> primeFactorization(u64 n) {
    if (n < 2) {
        throw std::invalid_argument("factorization requires n >= 2");
    }

    std::map<u64, unsigned> factors;

    while (n % 2 == 0) {
        ++factors[2];
        n /= 2;
    }

    for (u64 divisor = 3; divisor <= n / divisor; divisor += 2) {
        while (n % divisor == 0) {
            ++factors[divisor];
            n /= divisor;
        }
    }

    if (n > 1) {
        ++factors[n];
    }

    return factors;
}

std::string formatFactors(const std::map<u64, unsigned>& factors) {
    std::string result;
    bool first = true;

    for (const auto& [prime, exponent] : factors) {
        if (!first) result += " x ";
        first = false;

        result += std::to_string(prime);

        if (exponent > 1) {
            result += "^" + std::to_string(exponent);
        }
    }

    return result;
}

std::vector<u64> sieve(u64 limit) {
    if (limit < 2) return {};

    // A byte per candidate keeps the implementation simple and avoids
    // bit-level complexity while remaining compact for normal limits.
    std::vector<bool> composite(limit + 1, false);

    for (u64 candidate = 2; candidate <= limit / candidate; ++candidate) {
        if (!composite[candidate]) {
            for (u64 multiple = candidate * candidate;
                 multiple <= limit;
                 multiple += candidate) {
                composite[multiple] = true;
            }
        }
    }

    std::vector<u64> primes;
    for (u64 n = 2; n <= limit; ++n) {
        if (!composite[n]) primes.push_back(n);
    }

    return primes;
}

std::vector<u64> segmentedSieve(u64 low, u64 high) {
    if (low > high) {
        throw std::invalid_argument("low must be <= high");
    }

    if (high < 2) return {};
    low = std::max<u64>(low, 2);

    const u64 root = static_cast<u64>(std::sqrt(static_cast<long double>(high)));
    const auto basePrimes = sieve(root);

    const u64 length = high - low + 1;
    std::vector<bool> composite(length, false);

    for (u64 prime : basePrimes) {
        u64 first = std::max<u64>(
            prime * prime,
            ((low + prime - 1) / prime) * prime
        );

        for (u64 multiple = first; multiple <= high; multiple += prime) {
            composite[multiple - low] = true;
        }
    }

    std::vector<u64> primes;

    for (u64 offset = 0; offset < length; ++offset) {
        if (!composite[offset]) {
            primes.push_back(low + offset);
        }
    }

    return primes;
}

struct PrimeDistribution {
    std::vector<u64> primes;
    u64 largestGap{};
    double averageGap{};
};

PrimeDistribution analyzeDistribution(const std::vector<u64>& primes) {
    PrimeDistribution result;
    result.primes = primes;

    if (primes.size() < 2) {
        return result;
    }

    u64 gapSum = 0;

    for (std::size_t i = 1; i < primes.size(); ++i) {
        const u64 gap = primes[i] - primes[i - 1];
        result.largestGap = std::max(result.largestGap, gap);
        gapSum += gap;
    }

    result.averageGap =
        static_cast<double>(gapSum) /
        static_cast<double>(primes.size() - 1);

    return result;
}

bool verifyFactorization(
    u64 original,
    const std::map<u64, unsigned>& factors
) {
    u128 reconstructed = 1;

    for (const auto& [prime, exponent] : factors) {
        if (!isPrime(prime) || exponent == 0) {
            return false;
        }

        for (unsigned i = 0; i < exponent; ++i) {
            reconstructed *= prime;

            // The expected examples fit u64. This guard prevents an
            // accidental overflow from silently validating bad data.
            if (reconstructed > original) {
                return false;
            }
        }
    }

    return reconstructed == original;
}

void runTests() {
    if (isPrime(1) || !isPrime(2) || !isPrime(97) || isPrime(91)) {
        throw std::runtime_error("primality tests failed");
    }

    const auto factors = primeFactorization(360);

    if (formatFactors(factors) != "2^3 x 3^2 x 5") {
        throw std::runtime_error("factorization formatting failed");
    }

    if (!verifyFactorization(360, factors)) {
        throw std::runtime_error("factorization verification failed");
    }

    if (sieve(10) != std::vector<u64>{2, 3, 5, 7}) {
        throw std::runtime_error("sieve test failed");
    }

    if (segmentedSieve(100, 120) !=
        std::vector<u64>{101, 103, 107, 109, 113}) {
        throw std::runtime_error("segmented sieve test failed");
    }
}

int main() {
    try {
        runTests();

        const std::vector<u64> values{
            84,
            360,
            9973,
            1000000
        };

        std::cout << "Prime factorization\n";
        std::cout << "-------------------\n";

        for (u64 value : values) {
            const auto factors = primeFactorization(value);
            std::cout << value << " = "
                      << formatFactors(factors) << '\n';
        }

        const u64 limit = 100000;
        const auto primes = sieve(limit);
        const auto distribution = analyzeDistribution(primes);

        std::cout << "\nPrime distribution\n";
        std::cout << "------------------\n";
        std::cout << "pi(" << limit << ") = "
                  << primes.size() << '\n';

        std::cout << std::fixed << std::setprecision(6);
        std::cout << "Empirical density = "
                  << static_cast<double>(primes.size()) / limit
                  << '\n';

        std::cout << "1 / ln(n) = "
                  << 1.0 / std::log(static_cast<double>(limit))
                  << '\n';

        std::cout << "Average prime gap = "
                  << distribution.averageGap << '\n';

        std::cout << "Largest prime gap = "
                  << distribution.largestGap << '\n';

        std::cout << "\nSegmented sieve\n";
        std::cout << "---------------\n";

        const auto interval = segmentedSieve(1'000'000, 1'000'200);

        for (u64 prime : interval) {
            std::cout << prime << ' ';
        }
        std::cout << '\n';

        std::cout << "\nFactorization verification\n";
        std::cout << "--------------------------\n";

        for (u64 value : values) {
            const auto factors = primeFactorization(value);
            std::cout << value << ": "
                      << (verifyFactorization(value, factors)
                              ? "valid"
                              : "invalid")
                      << '\n';
        }

        // The segmented sieve uses O(sqrt(high)) base storage plus
        // O(high-low+1) interval storage, unlike a full sieve up to high.
        const auto largeInterval = segmentedSieve(10'000'000, 10'001'000);

        std::cout << "\nPrimes in [10,000,000, 10,001,000]: "
                  << largeInterval.size() << '\n';
    }
    catch (const std::exception& error) {
        std::cerr << "Prime analysis failed: "
                  << error.what() << '\n';
        return 1;
    }

    return 0;
}
