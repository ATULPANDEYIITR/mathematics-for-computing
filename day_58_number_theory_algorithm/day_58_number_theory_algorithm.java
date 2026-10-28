import java.math.BigInteger;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

public class NumberTheoryEnterprise {

    enum OperationState {
        RECEIVED,
        VALIDATED,
        EXECUTED,
        REJECTED
    }

    record ModularRequest(
            long requestId,
            long base,
            long exponent,
            long modulus
    ) {}

    record EvaluationResult(
            long requestId,
            OperationState state,
            String message,
            Long result
    ) {}

    interface NumberTheoryPolicy {
        void validate(ModularRequest request);
    }

    static final class InputValidationPolicy implements NumberTheoryPolicy {
        @Override
        public void validate(ModularRequest request) {
            Objects.requireNonNull(request, "Request cannot be null.");

            if (request.exponent() < 0) {
                throw new ValidationException(
                        "Exponent must be non-negative."
                );
            }

            if (request.modulus() <= 0) {
                throw new ValidationException(
                        "Modulus must be positive."
                );
            }
        }
    }

    static final class ValidationException extends RuntimeException {
        ValidationException(String message) {
            super(message);
        }
    }

    static final class ModularArithmeticService {
        private final NumberTheoryPolicy policy;

        ModularArithmeticService(NumberTheoryPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        EvaluationResult evaluate(ModularRequest request) {
            OperationState state = OperationState.RECEIVED;

            try {
                policy.validate(request);
                state = OperationState.VALIDATED;

                long result = modPow(
                        request.base(),
                        request.exponent(),
                        request.modulus()
                );

                state = OperationState.EXECUTED;

                return new EvaluationResult(
                        request.requestId(),
                        state,
                        "Modular exponentiation completed.",
                        result
                );
            } catch (ValidationException | ArithmeticException error) {
                return new EvaluationResult(
                        request.requestId(),
                        OperationState.REJECTED,
                        error.getMessage(),
                        null
                );
            }
        }
    }

    static long gcd(long a, long b) {
        a = Math.abs(a);
        b = Math.abs(b);

        while (b != 0) {
            long remainder = a % b;
            a = b;
            b = remainder;
        }

        return a;
    }

    static long modPow(long base, long exponent, long modulus) {
        if (modulus <= 0) {
            throw new ValidationException("Modulus must be positive.");
        }

        if (exponent < 0) {
            throw new ValidationException(
                    "Exponent must be non-negative."
            );
        }

        /*
         * BigInteger avoids signed long overflow during multiplication.
         * The domain model still exposes long values for ordinary requests.
         */
        BigInteger m = BigInteger.valueOf(modulus);
        BigInteger b = BigInteger.valueOf(base).mod(m);
        BigInteger result = BigInteger.ONE.mod(m);
        long e = exponent;

        while (e > 0) {
            if ((e & 1L) != 0) {
                result = result.multiply(b).mod(m);
            }

            b = b.multiply(b).mod(m);
            e >>>= 1;
        }

        return result.longValueExact();
    }

    static BigInteger modPow(
            BigInteger base,
            BigInteger exponent,
            BigInteger modulus
    ) {
        if (modulus.signum() <= 0) {
            throw new ValidationException("Modulus must be positive.");
        }

        if (exponent.signum() < 0) {
            throw new ValidationException(
                    "Exponent must be non-negative."
            );
        }

        BigInteger result = BigInteger.ONE.mod(modulus);
        BigInteger b = base.mod(modulus);
        BigInteger e = exponent;

        while (e.signum() > 0) {
            if (e.testBit(0)) {
                result = result.multiply(b).mod(modulus);
            }

            b = b.multiply(b).mod(modulus);
            e = e.shiftRight(1);
        }

        return result;
    }

    static boolean isPrime(BigInteger n) {
        if (n == null || n.compareTo(BigInteger.TWO) < 0) {
            return false;
        }

        return n.isProbablePrime(40);
    }

    static Map<BigInteger, Integer> factorize(long value) {
        if (value <= 0) {
            throw new ValidationException(
                    "Factorization requires a positive integer."
            );
        }

        long remaining = value;
        Map<BigInteger, Integer> factors = new LinkedHashMap<>();

        int exponent = 0;

        while (remaining % 2 == 0 && remaining > 1) {
            remaining /= 2;
            exponent++;
        }

        if (exponent > 0) {
            factors.put(BigInteger.TWO, exponent);
        }

        for (long divisor = 3;
             divisor <= remaining / divisor;
             divisor += 2) {

            exponent = 0;

            while (remaining % divisor == 0) {
                remaining /= divisor;
                exponent++;
            }

            if (exponent > 0) {
                factors.put(
                        BigInteger.valueOf(divisor),
                        exponent
                );
            }
        }

        if (remaining > 1) {
            BigInteger prime = BigInteger.valueOf(remaining);
            factors.merge(prime, 1, Integer::sum);
        }

        return factors;
    }

    static BigInteger modularInverse(
            BigInteger value,
            BigInteger modulus
    ) {
        if (modulus.signum() <= 0) {
            throw new ValidationException(
                    "Modulus must be positive."
            );
        }

        try {
            return value.modInverse(modulus);
        } catch (ArithmeticException error) {
            throw new ValidationException(
                    "Modular inverse does not exist."
            );
        }
    }

    static BigInteger eulerTotient(BigInteger n) {
        if (n.signum() <= 0) {
            throw new ValidationException(
                    "Totient requires a positive integer."
            );
        }

        BigInteger result = n;

        BigInteger remaining = n;
        BigInteger divisor = BigInteger.TWO;

        while (divisor.multiply(divisor).compareTo(remaining) <= 0) {
            if (remaining.mod(divisor).signum() == 0) {
                result = result.subtract(
                        result.divide(divisor)
                );

                while (remaining.mod(divisor).signum() == 0) {
                    remaining = remaining.divide(divisor);
                }
            }

            divisor = divisor.equals(BigInteger.TWO)
                    ? BigInteger.valueOf(3)
                    : divisor.add(BigInteger.TWO);
        }

        if (remaining.compareTo(BigInteger.ONE) > 0) {
            result = result.subtract(
                    result.divide(remaining)
            );
        }

        return result;
    }

    static void require(boolean condition, String message) {
        if (!condition) {
            throw new IllegalStateException(message);
        }
    }

    public static void main(String[] args) {
        System.out.println("NUMBER THEORY ENTERPRISE MODEL");
        System.out.println("=".repeat(70));

        System.out.println("\n1. GCD");
        System.out.println("gcd(252, 105) = " + gcd(252, 105));
        require(gcd(252, 105) == 21, "GCD invariant failed.");

        System.out.println("\n2. Policy-driven modular computation");

        NumberTheoryPolicy policy = new InputValidationPolicy();
        ModularArithmeticService service =
                new ModularArithmeticService(policy);

        List<ModularRequest> requests = List.of(
                new ModularRequest(1001, 3, 100, 13),
                new ModularRequest(1002, 7, 0, 26),
                new ModularRequest(1003, 5, -1, 17),
                new ModularRequest(1004, 2, 20, 0)
        );

        for (ModularRequest request : requests) {
            EvaluationResult result = service.evaluate(request);

            System.out.printf(
                    "request=%d state=%s result=%s message=%s%n",
                    result.requestId(),
                    result.state(),
                    result.result(),
                    result.message()
            );
        }

        System.out.println("\n3. Large integer fast exponentiation");

        BigInteger largeBase =
                new BigInteger("123456789012345678901234567890");

        BigInteger largeExponent =
                new BigInteger("987654321");

        BigInteger modulus =
                new BigInteger("1000000007");

        BigInteger largeResult =
                modPow(largeBase, largeExponent, modulus);

        System.out.println("result = " + largeResult);

        System.out.println("\n4. Primality policy");
        List<BigInteger> candidates = List.of(
                BigInteger.ONE,
                BigInteger.TWO,
                BigInteger.valueOf(17),
                BigInteger.valueOf(97),
                BigInteger.valueOf(100),
                new BigInteger("104729")
        );

        candidates.stream()
                .map(n -> n + " -> " + (isPrime(n) ? "prime" : "composite"))
                .forEach(System.out::println);

        System.out.println("\n5. Factorization");

        Map<BigInteger, Integer> factors = factorize(360);

        factors.forEach((prime, exponent) ->
                System.out.println(
                        "prime=" + prime +
                        ", exponent=" + exponent
                )
        );

        require(
                factors.get(BigInteger.TWO) == 3,
                "Factorization of 360 is incorrect."
        );

        System.out.println("\n6. Euler's totient");
        BigInteger phi = eulerTotient(BigInteger.valueOf(36));
        System.out.println("phi(36) = " + phi);
        require(phi.equals(BigInteger.valueOf(12)), "Totient failed.");

        System.out.println("\n7. Modular inverse");

        BigInteger inverse = modularInverse(
                BigInteger.valueOf(7),
                BigInteger.valueOf(26)
        );

        System.out.println("7^-1 mod 26 = " + inverse);

        require(
                BigInteger.valueOf(7)
                        .multiply(inverse)
                        .mod(BigInteger.valueOf(26))
                        .equals(BigInteger.ONE),
                "Inverse validation failed."
        );

        System.out.println("\n8. Edge-case validation");

        try {
            modularInverse(
                    BigInteger.valueOf(6),
                    BigInteger.valueOf(15)
            );
            throw new IllegalStateException(
                    "Invalid inverse was accepted."
            );
        } catch (ValidationException expected) {
            System.out.println("Rejected: " + expected.getMessage());
        }

        try {
            factorize(0);
            throw new IllegalStateException(
                    "Invalid factorization input was accepted."
            );
        } catch (ValidationException expected) {
            System.out.println("Rejected: " + expected.getMessage());
        }

        System.out.println("\nAll enterprise workflow checks passed.");
    }
}
