#include <algorithm>
#include <cassert>
#include <cstdint>
#include <exception>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

/*
 * Euclidean Algorithm: Repository Integrity Key Service
 *
 * The program models an arithmetic service that can generate a Bézout
 * certificate for two integers. The certificate contains coefficients
 * x and y satisfying:
 *
 *     a*x + b*y = gcd(a,b)
 *
 * The same certificate can establish modular inverses when gcd(a,m)=1.
 *
 * The case study uses signed 64-bit integers and explicitly detects the
 * only problematic absolute-value case: INT64_MIN.
 */

struct ExtendedGCDResult {
    std::int64_t a{};
    std::int64_t b{};
    std::int64_t gcd{};
    std::int64_t x{};
    std::int64_t y{};

    __int128 bezoutValue() const {
        return static_cast<__int128>(a) * x +
               static_cast<__int128>(b) * y;
    }

    bool valid() const {
        return bezoutValue() == gcd;
    }
};

struct DiophantineSolution {
    std::int64_t x{};
    std::int64_t y{};
    std::int64_t gcd{};
};

class EuclideanAlgorithm {
private:
    static std::uint64_t magnitude(std::int64_t value) {
        /*
         * Converting after negation would overflow for INT64_MIN.
         * This expression obtains its magnitude safely in unsigned space.
         */
        if (value >= 0) {
            return static_cast<std::uint64_t>(value);
        }

        return static_cast<std::uint64_t>(-(value + 1)) + 1ULL;
    }

    static std::int64_t checkedToSigned(std::uint64_t value) {
        if (value > static_cast<std::uint64_t>(
                        std::numeric_limits<std::int64_t>::max())) {
            throw std::overflow_error("result does not fit int64_t");
        }

        return static_cast<std::int64_t>(value);
    }

public:
    static std::int64_t gcd(std::int64_t a, std::int64_t b) {
        std::uint64_t x = magnitude(a);
        std::uint64_t y = magnitude(b);

        while (y != 0) {
            const std::uint64_t remainder = x % y;
            x = y;
            y = remainder;
        }

        return checkedToSigned(x);
    }

    static ExtendedGCDResult extendedGCD(
        std::int64_t a,
        std::int64_t b
    ) {
        /*
         * Coefficients are maintained as __int128 internally. This avoids
         * intermediate overflow for valid int64 input pairs. The final
         * coefficients are required to fit int64_t for this API.
         */
        std::uint64_t oldR = magnitude(a);
        std::uint64_t r = magnitude(b);

        __int128 oldS = 1;
        __int128 s = 0;
        __int128 oldT = 0;
        __int128 t = 1;

        while (r != 0) {
            const std::uint64_t quotient = oldR / r;

            const std::uint64_t nextR = oldR % r;
            oldR = r;
            r = nextR;

            const __int128 nextS =
                oldS - static_cast<__int128>(quotient) * s;
            oldS = s;
            s = nextS;

            const __int128 nextT =
                oldT - static_cast<__int128>(quotient) * t;
            oldT = t;
            t = nextT;
        }

        if (a < 0) {
            oldS = -oldS;
        }

        if (b < 0) {
            oldT = -oldT;
        }

        if (oldS < std::numeric_limits<std::int64_t>::min() ||
            oldS > std::numeric_limits<std::int64_t>::max() ||
            oldT < std::numeric_limits<std::int64_t>::min() ||
            oldT > std::numeric_limits<std::int64_t>::max()) {
            throw std::overflow_error(
                "Bézout coefficient does not fit int64_t"
            );
        }

        ExtendedGCDResult result{
            a,
            b,
            checkedToSigned(oldR),
            static_cast<std::int64_t>(oldS),
            static_cast<std::int64_t>(oldT)
        };

        if (!result.valid()) {
            throw std::logic_error("Bézout invariant violated");
        }

        return result;
    }

    static std::int64_t positiveModulo(
        std::int64_t value,
        std::int64_t modulus
    ) {
        if (modulus <= 1) {
            throw std::invalid_argument(
                "modulus must be greater than one"
            );
        }

        const std::int64_t remainder = value % modulus;
        return remainder < 0 ? remainder + modulus : remainder;
    }

    static std::int64_t modularInverse(
        std::int64_t value,
        std::int64_t modulus
    ) {
        if (modulus <= 1) {
            throw std::invalid_argument(
                "modulus must be greater than one"
            );
        }

        const ExtendedGCDResult result =
            extendedGCD(value, modulus);

        if (result.gcd != 1) {
            throw std::domain_error(
                "modular inverse does not exist"
            );
        }

        return positiveModulo(result.x, modulus);
    }

    static DiophantineSolution solveLinearDiophantine(
        std::int64_t a,
        std::int64_t b,
        std::int64_t c
    ) {
        if (a == 0 && b == 0) {
            if (c == 0) {
                return {0, 0, 0};
            }

            throw std::domain_error("equation has no solution");
        }

        const ExtendedGCDResult result =
            extendedGCD(a, b);

        if (c % result.gcd != 0) {
            throw std::domain_error(
                "gcd(a,b) does not divide c"
            );
        }

        const __int128 multiplier =
            static_cast<__int128>(c) / result.gcd;

        const __int128 x =
            static_cast<__int128>(result.x) * multiplier;

        const __int128 y =
            static_cast<__int128>(result.y) * multiplier;

        if (x < std::numeric_limits<std::int64_t>::min() ||
            x > std::numeric_limits<std::int64_t>::max() ||
            y < std::numeric_limits<std::int64_t>::min() ||
            y > std::numeric_limits<std::int64_t>::max()) {
            throw std::overflow_error(
                "Diophantine solution does not fit int64_t"
            );
        }

        return {
            static_cast<std::int64_t>(x),
            static_cast<std::int64_t>(y),
            result.gcd
        };
    }
};

class GovernanceAudit {
private:
    std::vector<std::string> events;

public:
    void record(const std::string& event) {
        events.push_back(event);
    }

    void print() const {
        for (const auto& event : events) {
            std::cout << "[AUDIT] " << event << '\n';
        }
    }
};

static std::string toString(__int128 value) {
    if (value == 0) {
        return "0";
    }

    bool negative = value < 0;
    if (negative) {
        value = -value;
    }

    std::string result;

    while (value > 0) {
        result.push_back(
            static_cast<char>('0' + value % 10)
        );
        value /= 10;
    }

    if (negative) {
        result.push_back('-');
    }

    std::reverse(result.begin(), result.end());
    return result;
}

static void runCase(
    GovernanceAudit& audit,
    std::int64_t a,
    std::int64_t b
) {
    const auto result =
        EuclideanAlgorithm::extendedGCD(a, b);

    audit.record(
        "Certificate generated for (" +
        std::to_string(a) + ", " +
        std::to_string(b) + ")"
    );

    std::cout << "a = " << a
              << ", b = " << b << '\n';

    std::cout << "gcd = " << result.gcd << '\n';
    std::cout << "x = " << result.x << '\n';
    std::cout << "y = " << result.y << '\n';

    std::cout
        << "a*x + b*y = "
        << toString(result.bezoutValue())
        << '\n';

    std::cout
        << "certificate valid = "
        << std::boolalpha
        << result.valid()
        << "\n\n";
}

static void runTests() {
    const std::vector<std::pair<std::int64_t, std::int64_t>> cases{
        {0, 0},
        {0, 42},
        {42, 0},
        {48, 18},
        {-48, 18},
        {48, -18},
        {-48, -18},
        {1071, 462},
        {270, 192}
    };

    for (const auto& [a, b] : cases) {
        const auto result =
            EuclideanAlgorithm::extendedGCD(a, b);

        assert(result.gcd == EuclideanAlgorithm::gcd(a, b));
        assert(result.valid());
    }

    assert(EuclideanAlgorithm::modularInverse(3, 11) == 4);

    const auto solution =
        EuclideanAlgorithm::solveLinearDiophantine(35, 15, 10);

    assert(
        35 * solution.x +
        15 * solution.y ==
        10
    );

    bool rejected = false;

    try {
        EuclideanAlgorithm::modularInverse(6, 15);
    } catch (const std::domain_error&) {
        rejected = true;
    }

    assert(rejected);

    rejected = false;

    try {
        EuclideanAlgorithm::solveLinearDiophantine(6, 10, 7);
    } catch (const std::domain_error&) {
        rejected = true;
    }

    assert(rejected);

    std::cout << "Self-tests: PASS\n";
}

int main() {
    try {
        GovernanceAudit audit;

        std::cout << "Euclidean Algorithm Governance Certificate\n";
        std::cout << "==========================================\n\n";

        runCase(audit, 1071, 462);
        runCase(audit, 240, 46);

        std::cout << "Modular inverse\n";
        std::cout << "---------------\n";

        const auto inverse =
            EuclideanAlgorithm::modularInverse(17, 3120);

        std::cout << "inverse(17 mod 3120) = "
                  << inverse << '\n';

        std::cout << "verification = "
                  << (17LL * inverse) % 3120
                  << "\n\n";

        std::cout << "Linear Diophantine equation\n";
        std::cout << "---------------------------\n";

        const auto solution =
            EuclideanAlgorithm::solveLinearDiophantine(
                35,
                15,
                10
            );

        std::cout << "35x + 15y = 10\n";
        std::cout << "x = " << solution.x << '\n';
        std::cout << "y = " << solution.y << '\n';
        std::cout << "gcd = " << solution.gcd << '\n';

        std::cout << "\nFailure conditions\n";
        std::cout << "------------------\n";

        try {
            EuclideanAlgorithm::modularInverse(6, 15);
        } catch (const std::exception& ex) {
            std::cout << "Rejected inverse: "
                      << ex.what() << '\n';
        }

        try {
            EuclideanAlgorithm::solveLinearDiophantine(
                6,
                10,
                7
            );
        } catch (const std::exception& ex) {
            std::cout << "Rejected equation: "
                      << ex.what() << '\n';
        }

        std::cout << "\nAudit trail\n";
        std::cout << "-----------\n";
        audit.print();

        std::cout << '\n';
        runTests();
    } catch (const std::exception& ex) {
        std::cerr << "Fatal error: "
                  << ex.what()
                  << '\n';
        return 1;
    }

    return 0;
}
