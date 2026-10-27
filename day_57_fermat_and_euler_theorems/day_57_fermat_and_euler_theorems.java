import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class FermatEulerTheorems {

    enum Theorem {
        FERMAT_LITTLE,
        EULER
    }

    record ModularEvaluation(
            long base,
            long modulus,
            long phi,
            boolean coprime,
            boolean valid
    ) {}

    static final class NumberTheoryException extends Exception {
        NumberTheoryException(String message) {
            super(message);
        }
    }

    static final class NumberTheoryService {

        long gcd(long a, long b) {
            a = Math.abs(a);
            b = Math.abs(b);

            while (b != 0) {
                long remainder = a % b;
                a = b;
                b = remainder;
            }

            return a;
        }

        long modPow(long base, long exponent, long modulus)
                throws NumberTheoryException {
            if (modulus <= 0) {
                throw new NumberTheoryException("modulus must be positive");
            }
            if (exponent < 0) {
                throw new NumberTheoryException("exponent must be non-negative");
            }

            long result = 1 % modulus;
            base = Math.floorMod(base, modulus);

            while (exponent > 0) {
                if ((exponent & 1L) != 0) {
                    result = Math.floorMod(result * base, modulus);
                }

                base = Math.floorMod(base * base, modulus);
                exponent >>= 1;
            }

            return result;
        }

        boolean isPrime(long n) {
            if (n < 2) return false;
            if (n == 2) return true;
            if ((n & 1L) == 0) return false;

            for (long divisor = 3; divisor <= n / divisor; divisor += 2) {
                if (n % divisor == 0) return false;
            }

            return true;
        }

        long phi(long n) throws NumberTheoryException {
            if (n <= 0) {
                throw new NumberTheoryException("n must be positive");
            }

            long result = n;
            long value = n;

            if (value % 2 == 0) {
                result -= result / 2;
                while (value % 2 == 0) {
                    value /= 2;
                }
            }

            for (long factor = 3; factor <= value / factor; factor += 2) {
                if (value % factor == 0) {
                    result -= result / factor;
                    while (value % factor == 0) {
                        value /= factor;
                    }
                }
            }

            if (value > 1) {
                result -= result / value;
            }

            return result;
        }

        boolean verifyFermat(long a, long p)
                throws NumberTheoryException {
            if (!isPrime(p)) {
                throw new NumberTheoryException(
                        "Fermat's little theorem requires a prime modulus"
                );
            }

            if (a % p == 0) {
                return false;
            }

            return modPow(a, p - 1, p) == 1;
        }

        boolean verifyEuler(long a, long n)
                throws NumberTheoryException {
            if (gcd(a, n) != 1) {
                return false;
            }

            return modPow(a, phi(n), n) == 1;
        }

        long modularInverse(long a, long modulus)
                throws NumberTheoryException {
            if (modulus <= 1) {
                throw new NumberTheoryException(
                        "modulus must be greater than one"
                );
            }

            long oldR = Math.floorMod(a, modulus);
            long r = modulus;
            long oldS = 1;
            long s = 0;

            while (r != 0) {
                long quotient = oldR / r;

                long nextR = oldR - quotient * r;
                oldR = r;
                r = nextR;

                long nextS = oldS - quotient * s;
                oldS = s;
                s = nextS;
            }

            if (oldR != 1) {
                throw new NumberTheoryException(
                        "modular inverse does not exist"
                );
            }

            return Math.floorMod(oldS, modulus);
        }

        long inverseUsingEuler(long a, long n)
                throws NumberTheoryException {
            if (gcd(a, n) != 1) {
                throw new NumberTheoryException(
                        "a and n must be coprime"
                );
            }

            return modPow(a, phi(n) - 1, n);
        }

        ModularEvaluation evaluate(Theorem theorem, long a, long n)
                throws NumberTheoryException {
            Objects.requireNonNull(theorem, "theorem");

            boolean coprime = gcd(a, n) == 1;
            boolean valid;

            if (theorem == Theorem.FERMAT_LITTLE) {
                valid = verifyFermat(a, n);
            } else {
                valid = verifyEuler(a, n);
            }

            return new ModularEvaluation(
                    a,
                    n,
                    phi(n),
                    coprime,
                    valid
            );
        }
    }

    static final class RepositoryGovernanceService {
        private final NumberTheoryService numberTheory;

        RepositoryGovernanceService(NumberTheoryService numberTheory) {
            this.numberTheory = numberTheory;
        }

        List<ModularEvaluation> evaluatePolicy(
                List<Long> moduli,
                long base
        ) throws NumberTheoryException {
            List<ModularEvaluation> evaluations = new ArrayList<>();

            for (long modulus : moduli) {
                if (numberTheory.gcd(base, modulus) != 1) {
                    evaluations.add(new ModularEvaluation(
                            base,
                            modulus,
                            numberTheory.phi(modulus),
                            false,
                            false
                    ));
                    continue;
                }

                evaluations.add(new ModularEvaluation(
                        base,
                        modulus,
                        numberTheory.phi(modulus),
                        true,
                        numberTheory.verifyEuler(base, modulus)
                ));
            }

            return List.copyOf(evaluations);
        }
    }

    static final class RsaStyleWorkflow {
        private final NumberTheoryService service;
        private final long n;
        private final long publicExponent;
        private final long privateExponent;

        RsaStyleWorkflow(
                NumberTheoryService service,
                long p,
                long q,
                long publicExponent
        ) throws NumberTheoryException {
            if (!service.isPrime(p) || !service.isPrime(q)) {
                throw new NumberTheoryException(
                        "RSA-style example requires prime factors"
                );
            }

            this.service = service;
            this.n = Math.multiplyExact(p, q);

            long phiN = Math.multiplyExact(p - 1, q - 1);

            if (service.gcd(publicExponent, phiN) != 1) {
                throw new NumberTheoryException(
                        "public exponent must be coprime to phi(n)"
                );
            }

            this.publicExponent = publicExponent;
            this.privateExponent =
                    service.modularInverse(publicExponent, phiN);
        }

        long encrypt(long message) throws NumberTheoryException {
            if (message < 0 || message >= n) {
                throw new NumberTheoryException(
                        "message must satisfy 0 <= message < n"
                );
            }

            return service.modPow(message, publicExponent, n);
        }

        long decrypt(long ciphertext) throws NumberTheoryException {
            if (ciphertext < 0 || ciphertext >= n) {
                throw new NumberTheoryException(
                        "ciphertext must satisfy 0 <= ciphertext < n"
                );
            }

            return service.modPow(ciphertext, privateExponent, n);
        }

        long modulus() {
            return n;
        }

        long privateExponent() {
            return privateExponent;
        }
    }

    public static void main(String[] args) {
        NumberTheoryService service = new NumberTheoryService();

        try {
            System.out.println("=== Euler Phi Function ===");

            List.of(1L, 2L, 5L, 8L, 12L, 36L)
                    .forEach(n -> {
                        try {
                            System.out.println(
                                    "phi(" + n + ") = " + service.phi(n)
                            );
                        } catch (NumberTheoryException e) {
                            throw new RuntimeException(e);
                        }
                    });

            System.out.println("\n=== Fermat's Little Theorem ===");

            List.of(5L, 7L, 11L, 13L).forEach(p -> {
                try {
                    boolean valid = service.verifyFermat(3, p);
                    long value = service.modPow(3, p - 1, p);

                    System.out.println(
                            "3^(" + (p - 1) + ") mod " + p
                                    + " = " + value
                                    + " -> " + (valid ? "VALID" : "INVALID")
                    );
                } catch (NumberTheoryException e) {
                    throw new RuntimeException(e);
                }
            });

            System.out.println("\n=== Euler's Theorem ===");

            List.of(
                    new long[]{5, 8},
                    new long[]{5, 9},
                    new long[]{7, 12},
                    new long[]{11, 15}
            ).forEach(pair -> {
                try {
                    ModularEvaluation result =
                            service.evaluate(
                                    Theorem.EULER,
                                    pair[0],
                                    pair[1]
                            );

                    System.out.println(result);
                } catch (NumberTheoryException e) {
                    throw new RuntimeException(e);
                }
            });

            System.out.println("\n=== Enterprise Policy Evaluation ===");

            RepositoryGovernanceService governance =
                    new RepositoryGovernanceService(service);

            List<ModularEvaluation> policyResults =
                    governance.evaluatePolicy(
                            List.of(8L, 9L, 10L, 12L, 15L),
                            5
                    );

            policyResults.forEach(System.out::println);

            System.out.println("\n=== Modular Inverse ===");

            for (long[] pair : List.of(
                    new long[]{3, 10},
                    new long[]{7, 40},
                    new long[]{11, 26}
            )) {
                long direct = service.modularInverse(pair[0], pair[1]);
                long euler = service.inverseUsingEuler(pair[0], pair[1]);

                System.out.println(
                        pair[0] + "^-1 mod " + pair[1]
                                + " = " + direct
                                + " using Euler = " + euler
                );

                if (direct != euler) {
                    throw new NumberTheoryException(
                            "inverse calculation mismatch"
                    );
                }
            }

            System.out.println("\n=== RSA-Style Workflow ===");

            RsaStyleWorkflow rsa =
                    new RsaStyleWorkflow(service, 61, 53, 17);

            long message = 65;
            long ciphertext = rsa.encrypt(message);
            long recovered = rsa.decrypt(ciphertext);

            System.out.println("n = " + rsa.modulus());
            System.out.println("private exponent d = "
                    + rsa.privateExponent());
            System.out.println("message = " + message);
            System.out.println("ciphertext = " + ciphertext);
            System.out.println("recovered = " + recovered);

            if (message != recovered) {
                throw new NumberTheoryException(
                        "RSA-style recovery failed"
                );
            }

            System.out.println("\n=== Failure States ===");

            try {
                service.modularInverse(6, 15);
            } catch (NumberTheoryException e) {
                System.out.println(
                        "Rejected non-invertible value: "
                                + e.getMessage()
                );
            }

            try {
                service.verifyFermat(3, 15);
            } catch (NumberTheoryException e) {
                System.out.println(
                        "Rejected composite modulus: "
                                + e.getMessage()
                );
            }

            System.out.println("\nPerformance: modular exponentiation "
                    + "requires O(log exponent) iterations. Phi calculation "
                    + "uses trial division by candidate prime factors and "
                    + "is intended for educational and moderate-size inputs.");

            System.out.println("Security: textbook RSA arithmetic is not a "
                    + "secure cryptosystem. Production implementations need "
                    + "validated cryptographic providers, secure key sizes, "
                    + "padding, randomness, and side-channel protection.");

        } catch (NumberTheoryException | ArithmeticException e) {
            System.err.println("Fatal error: " + e.getMessage());
            System.exit(1);
        }
    }
}
