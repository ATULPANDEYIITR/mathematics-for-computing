import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/*
 * Euclidean Algorithm: Enterprise Arithmetic Policy Engine
 *
 * The program models an enterprise service that issues arithmetic
 * certificates. The certificate records gcd(a,b), together with
 * coefficients x and y satisfying:
 *
 *     ax + by = gcd(a,b)
 *
 * The same domain model supports modular inverse validation and
 * integer linear-equation solving.
 *
 * BigInteger is used because enterprise services should not silently
 * overflow when identifiers or cryptographic parameters exceed the
 * primitive integer range.
 */

public class EuclideanAlgorithmEnterprise {

    enum OperationStatus {
        SUCCESS,
        REJECTED
    }

    enum FailureReason {
        NONE,
        INVALID_MODULUS,
        NO_MODULAR_INVERSE,
        UNSOLVABLE_EQUATION
    }

    record BezoutCertificate(
            BigInteger a,
            BigInteger b,
            BigInteger gcd,
            BigInteger x,
            BigInteger y) {

        BezoutCertificate {
            Objects.requireNonNull(a);
            Objects.requireNonNull(b);
            Objects.requireNonNull(gcd);
            Objects.requireNonNull(x);
            Objects.requireNonNull(y);

            if (gcd.signum() < 0) {
                throw new IllegalArgumentException(
                        "gcd must be non-negative");
            }
        }

        BigInteger evaluate() {
            return a.multiply(x).add(b.multiply(y));
        }

        boolean valid() {
            return evaluate().equals(gcd);
        }
    }

    record ServiceResult<T>(
            OperationStatus status,
            T value,
            FailureReason failureReason,
            String message) {

        static <T> ServiceResult<T> success(T value) {
            return new ServiceResult<>(
                    OperationStatus.SUCCESS,
                    value,
                    FailureReason.NONE,
                    "Operation completed");
        }

        static <T> ServiceResult<T> rejected(
                FailureReason reason,
                String message) {

            return new ServiceResult<>(
                    OperationStatus.REJECTED,
                    null,
                    reason,
                    message);
        }
    }

    record DiophantineSolution(
            BigInteger x,
            BigInteger y,
            BigInteger gcd) {

        BigInteger evaluate(
                BigInteger a,
                BigInteger b) {

            return a.multiply(x).add(b.multiply(y));
        }
    }

    static final class ArithmeticEngine {

        private ArithmeticEngine() {
        }

        static BigInteger gcd(
                BigInteger a,
                BigInteger b) {

            Objects.requireNonNull(a);
            Objects.requireNonNull(b);

            return a.abs().gcd(b.abs());
        }

        static BezoutCertificate extendedGcd(
                BigInteger a,
                BigInteger b) {

            Objects.requireNonNull(a);
            Objects.requireNonNull(b);

            BigInteger oldR = a.abs();
            BigInteger r = b.abs();

            BigInteger oldS = BigInteger.ONE;
            BigInteger s = BigInteger.ZERO;

            BigInteger oldT = BigInteger.ZERO;
            BigInteger t = BigInteger.ONE;

            while (!r.equals(BigInteger.ZERO)) {
                BigInteger quotient = oldR.divide(r);

                BigInteger nextR =
                        oldR.subtract(
                                quotient.multiply(r));

                BigInteger nextS =
                        oldS.subtract(
                                quotient.multiply(s));

                BigInteger nextT =
                        oldT.subtract(
                                quotient.multiply(t));

                oldR = r;
                r = nextR;

                oldS = s;
                s = nextS;

                oldT = t;
                t = nextT;
            }

            if (a.signum() < 0) {
                oldS = oldS.negate();
            }

            if (b.signum() < 0) {
                oldT = oldT.negate();
            }

            BezoutCertificate certificate =
                    new BezoutCertificate(
                            a,
                            b,
                            oldR,
                            oldS,
                            oldT);

            if (!certificate.valid()) {
                throw new IllegalStateException(
                        "Bézout invariant violated");
            }

            return certificate;
        }

        static ServiceResult<BigInteger> modularInverse(
                BigInteger value,
                BigInteger modulus) {

            if (modulus.compareTo(BigInteger.ONE) <= 0) {
                return ServiceResult.rejected(
                        FailureReason.INVALID_MODULUS,
                        "Modulus must be greater than one");
            }

            BezoutCertificate certificate =
                    extendedGcd(value, modulus);

            if (!certificate.gcd()
                    .equals(BigInteger.ONE)) {

                return ServiceResult.rejected(
                        FailureReason.NO_MODULAR_INVERSE,
                        "Inputs are not coprime");
            }

            return ServiceResult.success(
                    certificate.x()
                            .mod(modulus));
        }

        static ServiceResult<DiophantineSolution>
        solveEquation(
                BigInteger a,
                BigInteger b,
                BigInteger c) {

            if (a.signum() == 0 &&
                    b.signum() == 0) {

                if (c.signum() == 0) {
                    return ServiceResult.success(
                            new DiophantineSolution(
                                    BigInteger.ZERO,
                                    BigInteger.ZERO,
                                    BigInteger.ZERO));
                }

                return ServiceResult.rejected(
                        FailureReason.UNSOLVABLE_EQUATION,
                        "0x + 0y = nonzero c has no solution");
            }

            BezoutCertificate certificate =
                    extendedGcd(a, b);

            BigInteger g = certificate.gcd();

            if (!c.mod(g).equals(BigInteger.ZERO)) {
                return ServiceResult.rejected(
                        FailureReason.UNSOLVABLE_EQUATION,
                        "gcd(a,b) does not divide c");
            }

            BigInteger multiplier =
                    c.divide(g);

            DiophantineSolution solution =
                    new DiophantineSolution(
                            certificate.x()
                                    .multiply(multiplier),
                            certificate.y()
                                    .multiply(multiplier),
                            g);

            return ServiceResult.success(solution);
        }
    }

    interface Policy {
        boolean accepts(BezoutCertificate certificate);
    }

    static final class BezoutIntegrityPolicy
            implements Policy {

        @Override
        public boolean accepts(
                BezoutCertificate certificate) {

            return certificate != null &&
                    certificate.gcd().signum() >= 0 &&
                    certificate.valid();
        }
    }

    static final class ArithmeticAuditLog {

        private final List<String> entries =
                new ArrayList<>();

        void record(String event) {
            entries.add(event);
        }

        void print() {
            entries.forEach(
                    entry -> System.out.println(
                            "[AUDIT] " + entry));
        }
    }

    static void demonstrateGcd() {
        System.out.println("GCD");
        System.out.println("---");

        BigInteger a = BigInteger.valueOf(1071);
        BigInteger b = BigInteger.valueOf(462);

        BigInteger result =
                ArithmeticEngine.gcd(a, b);

        System.out.println(
                "gcd(1071, 462) = " + result);
    }

    static void demonstrateCertificate(
            ArithmeticAuditLog audit) {

        System.out.println(
                "\nBézout certificate");

        BigInteger a =
                BigInteger.valueOf(240);

        BigInteger b =
                BigInteger.valueOf(46);

        BezoutCertificate certificate =
                ArithmeticEngine.extendedGcd(a, b);

        Policy integrityPolicy =
                new BezoutIntegrityPolicy();

        boolean accepted =
                integrityPolicy.accepts(certificate);

        audit.record(
                "Certificate evaluated: " +
                        (accepted ? "accepted" : "rejected"));

        System.out.println(
                "gcd = " + certificate.gcd());

        System.out.println(
                "x = " + certificate.x());

        System.out.println(
                "y = " + certificate.y());

        System.out.println(
                "240x + 46y = " +
                        certificate.evaluate());

        System.out.println(
                "policy result = " +
                        (accepted ? "ACCEPT" : "REJECT"));
    }

    static void demonstrateModularInverse(
            ArithmeticAuditLog audit) {

        System.out.println(
                "\nModular inverse");

        BigInteger value =
                BigInteger.valueOf(17);

        BigInteger modulus =
                BigInteger.valueOf(3120);

        ServiceResult<BigInteger> result =
                ArithmeticEngine.modularInverse(
                        value,
                        modulus);

        if (result.status() ==
                OperationStatus.SUCCESS) {

            BigInteger inverse = result.value();

            audit.record(
                    "Modular inverse generated");

            System.out.println(
                    "17^(-1) mod 3120 = " +
                            inverse);

            System.out.println(
                    "verification = " +
                            value.multiply(inverse)
                                    .mod(modulus));
        } else {
            System.out.println(
                    "Rejected: " +
                            result.message());
        }
    }

    static void demonstrateEquation(
            ArithmeticAuditLog audit) {

        System.out.println(
                "\nLinear Diophantine equation");

        BigInteger a =
                BigInteger.valueOf(35);

        BigInteger b =
                BigInteger.valueOf(15);

        BigInteger c =
                BigInteger.valueOf(10);

        ServiceResult<DiophantineSolution> result =
                ArithmeticEngine.solveEquation(
                        a,
                        b,
                        c);

        if (result.status() ==
                OperationStatus.SUCCESS) {

            DiophantineSolution solution =
                    result.value();

            audit.record(
                    "Diophantine equation accepted");

            System.out.println(
                    "35x + 15y = 10");

            System.out.println(
                    "x = " + solution.x());

            System.out.println(
                    "y = " + solution.y());

            System.out.println(
                    "verification = " +
                            solution.evaluate(a, b));
        } else {
            audit.record(
                    "Diophantine equation rejected");

            System.out.println(
                    "Rejected: " +
                            result.message());
        }
    }

    static void demonstrateFailures() {
        System.out.println(
                "\nFailure states");

        ServiceResult<BigInteger> inverse =
                ArithmeticEngine.modularInverse(
                        BigInteger.valueOf(6),
                        BigInteger.valueOf(15));

        System.out.println(
                "inverse(6,15): " +
                        inverse.status() +
                        " / " +
                        inverse.failureReason());

        ServiceResult<DiophantineSolution> equation =
                ArithmeticEngine.solveEquation(
                        BigInteger.valueOf(6),
                        BigInteger.valueOf(10),
                        BigInteger.valueOf(7));

        System.out.println(
                "6x + 10y = 7: " +
                        equation.status() +
                        " / " +
                        equation.failureReason());
    }

    static void runSelfTests() {
        List<BigInteger[]> cases = List.of(
                new BigInteger[]{
                        BigInteger.ZERO,
                        BigInteger.ZERO
                },
                new BigInteger[]{
                        BigInteger.ZERO,
                        BigInteger.ONE
                },
                new BigInteger[]{
                        BigInteger.valueOf(48),
                        BigInteger.valueOf(18)
                },
                new BigInteger[]{
                        BigInteger.valueOf(-48),
                        BigInteger.valueOf(18)
                },
                new BigInteger[]{
                        BigInteger.valueOf(1071),
                        BigInteger.valueOf(462)
                }
        );

        for (BigInteger[] pair : cases) {
            BezoutCertificate certificate =
                    ArithmeticEngine.extendedGcd(
                            pair[0],
                            pair[1]);

            if (!certificate.valid()) {
                throw new AssertionError(
                        "Bézout validation failed");
            }

            if (!certificate.gcd().equals(
                    ArithmeticEngine.gcd(
                            pair[0],
                            pair[1]))) {
                throw new AssertionError(
                        "GCD validation failed");
            }
        }

        ServiceResult<BigInteger> inverse =
                ArithmeticEngine.modularInverse(
                        BigInteger.valueOf(3),
                        BigInteger.valueOf(11));

        if (!BigInteger.valueOf(4)
                .equals(inverse.value())) {
            throw new AssertionError(
                    "Inverse validation failed");
        }

        System.out.println(
                "\nSelf-tests: PASS");
    }

    public static void main(String[] args) {
        ArithmeticAuditLog audit =
                new ArithmeticAuditLog();

        System.out.println(
                "Euclidean Algorithm Enterprise Engine");
        System.out.println(
                "=====================================");

        demonstrateGcd();
        demonstrateCertificate(audit);
        demonstrateModularInverse(audit);
        demonstrateEquation(audit);
        demonstrateFailures();

        System.out.println(
                "\nAudit log");

        audit.print();

        runSelfTests();
    }
}
