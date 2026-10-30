#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * Advanced Number Theory: C++17
 *
 * Engineering perspective:
 * A 64-bit computational number theory engine using fixed-width
 * arithmetic, STL containers, deterministic Miller-Rabin,
 * Pollard Rho, Tonelli-Shanks, BSGS and Pohlig-Hellman.
 *
 * The supported prime modulus and group order are restricted to
 * signed 64-bit positive integers. Multiplication uses unsigned
 * 128-bit intermediates to prevent overflow.
 */

namespace nt {

using u64 = std::uint64_t;
using u128 = __uint128_t;
using i128 = __int128_t;

constexpr u64 MAX_BSGS_ENTRIES = 2'000'000;

class NumberTheoryError : public std::runtime_error {
public:
    explicit NumberTheoryError(const std::string& message)
        : std::runtime_error(message) {}
};

class ComputationLimitError : public std::runtime_error {
public:
    explicit ComputationLimitError(const std::string& message)
        : std::runtime_error(message) {}
};

void validate_modulus(u64 modulus) {
    if (modulus < 2 ||
        modulus > static_cast<u64>(std::numeric_limits<std::int64_t>::max())) {
        throw NumberTheoryError(
            "Modulus must be between 2 and INT64_MAX."
        );
    }
}

u64 add_mod(u64 a, u64 b, u64 modulus) {
    return static_cast<u64>(
        (static_cast<u128>(a) + b) % modulus
    );
}

u64 multiply_mod(u64 a, u64 b, u64 modulus) {
    return static_cast<u64>(
        (static_cast<u128>(a) * b) % modulus
    );
}

u64 modular_power(u64 base, u64 exponent, u64 modulus) {
    validate_modulus(modulus);

    u64 result = 1 % modulus;
    base %= modulus;

    while (exponent > 0) {
        if (exponent & 1ULL) {
            result = multiply_mod(result, base, modulus);
        }

        base = multiply_mod(base, base, modulus);
        exponent >>= 1ULL;
    }

    return result;
}

i128 extended_gcd(i128 a, i128 b, i128& x, i128& y) {
    i128 old_r = a;
    i128 r = b;

    i128 old_s = 1;
    i128 s = 0;

    i128 old_t = 0;
    i128 t = 1;

    while (r != 0) {
        i128 quotient = old_r / r;

        i128 next_r = old_r - quotient * r;
        old_r = r;
        r = next_r;

        i128 next_s = old_s - quotient * s;
        old_s = s;
        s = next_s;

        i128 next_t = old_t - quotient * t;
        old_t = t;
        t = next_t;
    }

    x = old_s;
    y = old_t;

    return old_r;
}

u64 modular_inverse(u64 value, u64 modulus) {
    validate_modulus(modulus);

    i128 x = 0;
    i128 y = 0;

    i128 gcd_value = extended_gcd(
        static_cast<i128>(value % modulus),
        static_cast<i128>(modulus),
        x,
        y
    );

    if (gcd_value != 1) {
        throw NumberTheoryError(
            "Modular inverse does not exist."
        );
    }

    i128 normalized = x % static_cast<i128>(modulus);

    if (normalized < 0) {
        normalized += static_cast<i128>(modulus);
    }

    return static_cast<u64>(normalized);
}

bool is_prime(u64 n) {
    if (n < 2) return false;

    const std::vector<u64> small_primes = {
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37
    };

    for (u64 prime : small_primes) {
        if (n == prime) return true;
        if (n % prime == 0) return false;
    }

    u64 d = n - 1;
    int s = 0;

    while ((d & 1ULL) == 0) {
        d >>= 1ULL;
        ++s;
    }

    // Deterministic witness set for the full uint64_t range.
    const std::vector<u64> bases = {
        2ULL,
        325ULL,
        9375ULL,
        28178ULL,
        450775ULL,
        9780504ULL,
        1795265022ULL
    };

    for (u64 witness : bases) {
        u64 a = witness % n;

        if (a < 2) continue;

        u64 x = modular_power(a, d, n);

        if (x == 1 || x == n - 1) continue;

        bool passed = false;

        for (int r = 1; r < s; ++r) {
            x = multiply_mod(x, x, n);

            if (x == n - 1) {
                passed = true;
                break;
            }
        }

        if (!passed) return false;
    }

    return true;
}

class Factorizer {
private:
    std::mt19937_64 generator_;

    u64 random_between(u64 low, u64 high) {
        std::uniform_int_distribution<u64> distribution(low, high);
        return distribution(generator_);
    }

    u64 rho(u64 n) {
        if (n % 2 == 0) return 2;
        if (n % 3 == 0) return 3;

        while (true) {
            u64 x = random_between(2, n - 2);
            u64 y = x;
            u64 c = random_between(1, n - 1);
            u64 divisor = 1;

            auto f = [n, c](u64 value) {
                return add_mod(
                    multiply_mod(value, value, n),
                    c,
                    n
                );
            };

            for (int iteration = 0;
                 iteration < 250000;
                 ++iteration) {

                x = f(x);
                y = f(f(y));

                u64 difference = x > y ? x - y : y - x;
                divisor = std::gcd(difference, n);

                if (divisor == 1) continue;
                if (divisor != n) return divisor;

                break;
            }
        }
    }

    void factor_recursive(
        u64 n,
        std::map<u64, int>& factors
    ) {
        if (n == 1) return;

        if (is_prime(n)) {
            ++factors[n];
            return;
        }

        u64 divisor = rho(n);

        if (divisor == 1 || divisor == n) {
            throw NumberTheoryError("Factorization failed.");
        }

        factor_recursive(divisor, factors);
        factor_recursive(n / divisor, factors);
    }

public:
    explicit Factorizer(u64 seed = std::random_device{}())
        : generator_(seed) {}

    std::map<u64, int> factor(u64 n) {
        if (n == 0) {
            throw NumberTheoryError(
                "Zero does not have a finite prime factorization."
            );
        }

        std::map<u64, int> result;
        factor_recursive(n, result);
        return result;
    }
};

int legendre_symbol(u64 a, u64 p) {
    if (p <= 2 || !is_prime(p)) {
        throw NumberTheoryError(
            "Legendre symbol requires an odd prime modulus."
        );
    }

    a %= p;

    if (a == 0) return 0;

    u64 result = modular_power(a, (p - 1) / 2, p);

    return result == 1 ? 1 : -1;
}

struct SquareRootResult {
    u64 prime;
    u64 value;
    std::vector<u64> roots;

    bool is_residue() const {
        return !roots.empty();
    }
};

SquareRootResult tonelli_shanks(u64 a, u64 p) {
    validate_modulus(p);

    if (!is_prime(p)) {
        throw NumberTheoryError("Modulus must be prime.");
    }

    a %= p;

    if (p == 2) {
        return {p, a, {a}};
    }

    if (a == 0) {
        return {p, a, {0}};
    }

    if (legendre_symbol(a, p) != 1) {
        return {p, a, {}};
    }

    if (p % 4 == 3) {
        u64 root = modular_power(a, (p + 1) / 4, p);
        u64 other = (p - root) % p;

        std::vector<u64> roots = {root};

        if (other != root) roots.push_back(other);

        std::sort(roots.begin(), roots.end());

        return {p, a, roots};
    }

    u64 q = p - 1;
    int s = 0;

    while (q % 2 == 0) {
        q /= 2;
        ++s;
    }

    u64 z = 2;

    while (legendre_symbol(z, p) != -1) {
        ++z;
    }

    u64 c = modular_power(z, q, p);
    u64 x = modular_power(a, (q + 1) / 2, p);
    u64 t = modular_power(a, q, p);
    int m = s;

    while (t != 1) {
        int i = 1;
        u64 temporary = multiply_mod(t, t, p);

        while (i < m && temporary != 1) {
            temporary = multiply_mod(temporary, temporary, p);
            ++i;
        }

        if (i == m) {
            throw NumberTheoryError(
                "Tonelli-Shanks invariant failed."
            );
        }

        u64 exponent = 1ULL << (m - i - 1);
        u64 b = modular_power(c, exponent, p);
        u64 b_squared = multiply_mod(b, b, p);

        x = multiply_mod(x, b, p);
        t = multiply_mod(t, b_squared, p);
        c = b_squared;
        m = i;
    }

    u64 other = (p - x) % p;

    std::vector<u64> roots = {x};

    if (other != x) roots.push_back(other);

    std::sort(roots.begin(), roots.end());

    for (u64 root : roots) {
        if (multiply_mod(root, root, p) != a) {
            throw NumberTheoryError(
                "Square root verification failed."
            );
        }
    }

    return {p, a, roots};
}

u64 exact_multiplicative_order(
    u64 base,
    u64 p,
    const std::map<u64, int>& factors
) {
    if (!is_prime(p) || base % p == 0) {
        throw NumberTheoryError("Invalid multiplicative group element.");
    }

    u64 order = p - 1;

    for (const auto& [prime, exponent] : factors) {
        (void) exponent;

        while (
            order % prime == 0 &&
            modular_power(base, order / prime, p) == 1
        ) {
            order /= prime;
        }
    }

    return order;
}

u64 ceil_sqrt(u64 value) {
    u64 result = static_cast<u64>(
        std::sqrt(static_cast<long double>(value))
    );

    while (
        static_cast<u128>(result) * result < value
    ) {
        ++result;
    }

    while (
        result > 0 &&
        static_cast<u128>(result - 1) * (result - 1) >= value
    ) {
        --result;
    }

    return result;
}

std::optional<u64> baby_step_giant_step(
    u64 base,
    u64 target,
    u64 p,
    u64 order,
    u64 max_entries = MAX_BSGS_ENTRIES
) {
    if (order == 0 || !is_prime(p)) {
        throw NumberTheoryError("Invalid BSGS parameters.");
    }

    base %= p;
    target %= p;

    u64 m = ceil_sqrt(order);

    if (m > max_entries) {
        throw ComputationLimitError(
            "BSGS memory limit exceeded."
        );
    }

    std::unordered_map<u64, u64> baby_steps;
    baby_steps.reserve(static_cast<std::size_t>(m * 2));

    u64 value = 1;

    for (u64 j = 0; j < m; ++j) {
        baby_steps.emplace(value, j);
        value = multiply_mod(value, base, p);
    }

    u64 factor = modular_inverse(
        modular_power(base, m, p),
        p
    );

    u64 gamma = target;
    u64 giant_count = (order + m - 1) / m;

    for (u64 i = 0; i <= giant_count; ++i) {
        auto found = baby_steps.find(gamma);

        if (found != baby_steps.end()) {
            u128 candidate =
                static_cast<u128>(i) * m + found->second;

            if (candidate < order) {
                u64 exponent = static_cast<u64>(candidate);

                if (
                    modular_power(base, exponent, p) == target
                ) {
                    return exponent;
                }
            }
        }

        gamma = multiply_mod(gamma, factor, p);
    }

    return std::nullopt;
}

u64 chinese_remainder(
    const std::vector<u64>& residues,
    const std::vector<u64>& moduli
) {
    if (
        residues.empty() ||
        residues.size() != moduli.size()
    ) {
        throw NumberTheoryError("Invalid CRT arguments.");
    }

    u64 result = 0;
    u64 product = 1;

    for (std::size_t i = 0; i < residues.size(); ++i) {
        const u64 modulus = moduli[i];

        if (
            modulus <= 1 ||
            std::gcd(product, modulus) != 1
        ) {
            throw NumberTheoryError(
                "CRT moduli must be pairwise coprime."
            );
        }

        u64 current = result % modulus;

        u64 delta = (
            residues[i] >= current
            ? residues[i] - current
            : modulus - (current - residues[i])
        ) % modulus;

        u64 inverse = modular_inverse(
            product % modulus,
            modulus
        );

        u64 correction = multiply_mod(
            delta,
            inverse,
            modulus
        );

        u128 combined =
            static_cast<u128>(result) +
            static_cast<u128>(product) * correction;

        u128 next_product =
            static_cast<u128>(product) * modulus;

        if (
            next_product >
            static_cast<u128>(
                std::numeric_limits<std::int64_t>::max()
            )
        ) {
            throw ComputationLimitError(
                "CRT result exceeds supported 64-bit range."
            );
        }

        product = static_cast<u64>(next_product);
        result = static_cast<u64>(combined % product);
    }

    return result;
}

std::optional<u64> pohlig_hellman(
    u64 base,
    u64 target,
    u64 p,
    u64 order,
    const std::map<u64, int>& factors,
    u64 max_entries = MAX_BSGS_ENTRIES
) {
    if (!is_prime(p) || order == 0 || order > p - 1) {
        throw NumberTheoryError("Invalid discrete logarithm group.");
    }

    base %= p;
    target %= p;

    if (base == 0) {
        throw NumberTheoryError("Base cannot be zero.");
    }

    if (modular_power(base, order, p) != 1) {
        throw NumberTheoryError("Group order is incorrect.");
    }

    u64 product = 1;

    for (const auto& [prime, exponent] : factors) {
        for (int i = 0; i < exponent; ++i) {
            product *= prime;
        }

        if (
            modular_power(base, order / prime, p) == 1
        ) {
            throw NumberTheoryError(
                "Base does not have the supplied exact order."
            );
        }
    }

    if (product != order) {
        throw NumberTheoryError(
            "Prime factorization does not reconstruct group order."
        );
    }

    if (modular_power(target, order, p) != 1) {
        return std::nullopt;
    }

    std::vector<u64> residues;
    std::vector<u64> moduli;

    for (const auto& [q, exponent] : factors) {
        u64 prime_power = 1;

        for (int i = 0; i < exponent; ++i) {
            prime_power *= q;
        }

        u64 subgroup_base = modular_power(
            base,
            order / prime_power,
            p
        );

        u64 subgroup_target = modular_power(
            target,
            order / prime_power,
            p
        );

        u64 digit_base = modular_power(
            subgroup_base,
            prime_power / q,
            p
        );

        u64 partial = 0;
        u64 q_power = 1;

        for (int k = 0; k < exponent; ++k) {
            u64 inverse_partial = modular_inverse(
                modular_power(subgroup_base, partial, p),
                p
            );

            u64 correction = multiply_mod(
                subgroup_target,
                inverse_partial,
                p
            );

            u64 digit_target = modular_power(
                correction,
                prime_power / (q_power * q),
                p
            );

            auto digit = baby_step_giant_step(
                digit_base,
                digit_target,
                p,
                q,
                max_entries
            );

            if (!digit.has_value()) {
                return std::nullopt;
            }

            partial += digit.value() * q_power;
            q_power *= q;
        }

        residues.push_back(partial);
        moduli.push_back(prime_power);
    }

    u64 answer = chinese_remainder(residues, moduli) % order;

    if (modular_power(base, answer, p) != target) {
        throw NumberTheoryError(
            "Pohlig-Hellman verification failed."
        );
    }

    return answer;
}

} // namespace nt


class RepositoryNumberTheoryCaseStudy {
private:
    nt::Factorizer factorizer_;

public:
    void run() {
        using namespace nt;

        std::cout << "ADVANCED NUMBER THEORY ENGINE\n";
        std::cout << "=============================\n";

        // Work with a prime field and its multiplicative group.
        const u64 p = 1019;
        const u64 base = 2;
        const u64 order_of_full_group = p - 1;

        if (!is_prime(p)) {
            throw NumberTheoryError("Invalid field modulus.");
        }

        auto order_factors = factorizer_.factor(order_of_full_group);

        const u64 actual_order = exact_multiplicative_order(
            base,
            p,
            order_factors
        );

        std::cout << "\nPRIME-FIELD PARAMETERS\n";
        std::cout << "Prime modulus: " << p << '\n';
        std::cout << "Group order: " << order_of_full_group << '\n';
        std::cout << "Generator: " << base << '\n';
        std::cout << "Exact element order: " << actual_order << '\n';

        // Integer factorization.
        const u64 number = 600851475143ULL;
        auto factors = factorizer_.factor(number);

        std::cout << "\nPOLLARD RHO FACTORIZATION\n";
        std::cout << number << " = ";

        bool first = true;

        for (const auto& [prime, exponent] : factors) {
            if (!first) std::cout << " * ";
            first = false;

            std::cout << prime;

            if (exponent > 1) {
                std::cout << "^" << exponent;
            }
        }

        std::cout << '\n';

        // Quadratic residue analysis.
        const u64 value = 56 * 56;

        std::cout << "\nQUADRATIC RESIDUES\n";
        std::cout << "Value modulo p: " << value % p << '\n';
        std::cout << "Legendre symbol: "
                  << legendre_symbol(value, p) << '\n';

        SquareRootResult root_result = tonelli_shanks(
            value,
            p
        );

        std::cout << "Tonelli-Shanks roots: ";

        for (u64 root : root_result.roots) {
            std::cout << root << ' ';
        }

        std::cout << '\n';

        SquareRootResult nonresidue = tonelli_shanks(2, p);

        std::cout << "Nonresidue roots: "
                  << nonresidue.roots.size() << '\n';

        // Discrete logarithm experiment.
        const u64 secret_exponent = 137;

        const u64 public_value = modular_power(
            base,
            secret_exponent,
            p
        );

        std::cout << "\nPOHLIG-HELLMAN EXPERIMENT\n";
        std::cout << "Public value: " << public_value << '\n';

        auto recovered = pohlig_hellman(
            base,
            public_value,
            p,
            actual_order,
            factorizer_.factor(actual_order)
        );

        if (!recovered.has_value()) {
            throw NumberTheoryError("Discrete logarithm not found.");
        }

        std::cout << "Recovered exponent: "
                  << recovered.value() << '\n';

        std::cout << "Verification: "
                  << modular_power(base, recovered.value(), p)
                  << " == " << public_value << '\n';

        // Negative case: zero is outside the multiplicative group.
        auto impossible = pohlig_hellman(
            base,
            0,
            p,
            actual_order,
            factorizer_.factor(actual_order)
        );

        std::cout << "Zero target has solution: "
                  << (impossible.has_value() ? "yes" : "no")
                  << '\n';
    }
};


void run_tests() {
    using namespace nt;

    assert(modular_power(7, 128, 13) == 9);
    assert(modular_inverse(3, 11) == 4);

    assert(is_prime(1019));
    assert(!is_prime(104060));

    assert(legendre_symbol(0, 1019) == 0);
    assert(legendre_symbol(2, 1019) == -1);
    assert(legendre_symbol(56 * 56, 1019) == 1);

    auto roots = tonelli_shanks(56 * 56, 1019);

    assert(roots.roots.size() == 2);
    assert(roots.roots[0] == 56);
    assert(roots.roots[1] == 963);

    assert(tonelli_shanks(2, 1019).roots.empty());

    Factorizer factorizer(42);

    auto factors = factorizer.factor(600851475143ULL);

    u128 product = 1;

    for (const auto& [prime, exponent] : factors) {
        assert(is_prime(prime));

        for (int i = 0; i < exponent; ++i) {
            product *= prime;
        }
    }

    assert(product == 600851475143ULL);

    const u64 order = 1018;
    const u64 target = modular_power(2, 137, 1019);

    auto answer = pohlig_hellman(
        2,
        target,
        1019,
        order,
        factorizer.factor(order)
    );

    assert(answer.has_value());
    assert(answer.value() == 137);

    assert(!pohlig_hellman(
        2,
        0,
        1019,
        order,
        factorizer.factor(order)
    ).has_value());
}


int main() {
    try {
        run_tests();

        RepositoryNumberTheoryCaseStudy case_study;
        case_study.run();

        std::cout << "\nAll C++17 verification checks passed.\n";

        std::cout
            << "Security notice: this implementation is not "
            << "constant-time cryptographic software.\n";

        return 0;

    } catch (const std::exception& error) {
        std::cerr << "Execution error: "
                  << error.what() << '\n';

        return 1;
    }
}
