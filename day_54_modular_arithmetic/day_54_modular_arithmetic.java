import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/**
 * Enterprise-style modular arithmetic service.
 * Compile: javac ModularArithmeticApp.java
 * Run: java ModularArithmeticApp
 */
public class ModularArithmeticApp {

    public enum Operation {
        NORMALIZE, CONGRUENCE, ADD, MULTIPLY, POWER, INVERSE
    }

    public enum Outcome {
        SUCCESS, INVALID_REQUEST, NON_INVERTIBLE
    }

    public record ArithmeticRequest(
            Operation operation,
            BigInteger left,
            BigInteger right,
            BigInteger exponent,
            BigInteger modulus
    ) {
        public ArithmeticRequest {
            Objects.requireNonNull(operation, "Operation is required.");
            Objects.requireNonNull(left, "Left operand is required.");
            Objects.requireNonNull(modulus, "Modulus is required.");

            if (modulus.signum() <= 0) {
                throw new IllegalArgumentException("Modulus must be positive.");
            }

            switch (operation) {
                case CONGRUENCE, ADD, MULTIPLY ->
                    Objects.requireNonNull(right, "Right operand is required.");
                case POWER ->
                    Objects.requireNonNull(exponent, "Exponent is required.");
                case NORMALIZE, INVERSE -> {
                    // These operations use only the left operand.
                }
            }
        }
    }

    public record ArithmeticResult(
            Outcome outcome,
            BigInteger value,
            String message
    ) {}

    public interface ArithmeticPolicy {
        boolean accepts(ArithmeticRequest request);

        String rejectionReason();
    }

    /**
     * Policy limits prevent untrusted callers from submitting computations
     * with excessively large operands or moduli.
     */
    public record ResourcePolicy(
            int maximumOperandBits,
            int maximumModulusBits,
            int maximumExponentBits
    ) implements ArithmeticPolicy {

        public ResourcePolicy {
            if (maximumOperandBits < 1
                    || maximumModulusBits < 1
                    || maximumExponentBits < 1) {
                throw new IllegalArgumentException(
                        "Resource limits must be positive.");
            }
        }

        @Override
        public boolean accepts(ArithmeticRequest request) {
            if (request.left().abs().bitLength() > maximumOperandBits
                    || request.modulus().bitLength() > maximumModulusBits) {
                return false;
            }

            if (request.right() != null
                    && request.right().abs().bitLength() > maximumOperandBits) {
                return false;
            }

            return request.exponent() == null
                    || request.exponent().abs().bitLength()
                    <= maximumExponentBits;
        }

        @Override
        public String rejectionReason() {
            return "Request exceeds configured operand or exponent limits.";
        }
    }

    public static final class ModularArithmeticService {
        private final List<ArithmeticPolicy> policies;

        public ModularArithmeticService(List<ArithmeticPolicy> policies) {
            this.policies = List.copyOf(policies);
        }

        public ArithmeticResult execute(ArithmeticRequest request) {
            Objects.requireNonNull(request, "Request is required.");

            // Every policy must accept the request; one rejection is decisive.
            for (ArithmeticPolicy policy : policies) {
                if (!policy.accepts(request)) {
                    return new ArithmeticResult(
                            Outcome.INVALID_REQUEST,
                            null,
                            policy.rejectionReason()
                    );
                }
            }

            BigInteger modulus = request.modulus();
            BigInteger left = request.left().mod(modulus);

            try {
                BigInteger result = switch (request.operation()) {
                    case NORMALIZE -> left;

                    case CONGRUENCE -> left.equals(
                            request.right().mod(modulus))
                            ? BigInteger.ONE
                            : BigInteger.ZERO;

                    case ADD -> left.add(
                            request.right().mod(modulus)).mod(modulus);

                    case MULTIPLY -> left.multiply(
                            request.right().mod(modulus)).mod(modulus);

                    case POWER -> power(left, request.exponent(), modulus);

                    case INVERSE -> {
                        if (modulus.equals(BigInteger.ONE)) {
                            throw new ArithmeticException(
                                    "Modular inverse requires modulus > 1.");
                        }
                        yield left.modInverse(modulus);
                    }
                };

                return new ArithmeticResult(
                        Outcome.SUCCESS, result, "Operation completed.");
            } catch (ArithmeticException exception) {
                return new ArithmeticResult(
                        Outcome.NON_INVERTIBLE,
                        null,
                        exception.getMessage() == null
                                ? "Arithmetic operation failed."
                                : exception.getMessage()
                );
            }
        }

        private static BigInteger power(
                BigInteger base,
                BigInteger exponent,
                BigInteger modulus
        ) {
            if (modulus.equals(BigInteger.ONE)) {
                return BigInteger.ZERO;
            }

            if (exponent.signum() < 0) {
                base = base.modInverse(modulus);
                exponent = exponent.negate();
            }

            return base.modPow(exponent, modulus);
        }
    }

    private static ArithmeticRequest request(
            Operation operation,
            String left,
            String right,
            String exponent,
            String modulus
    ) {
        return new ArithmeticRequest(
                operation,
                new BigInteger(left),
                right == null ? null : new BigInteger(right),
                exponent == null ? null : new BigInteger(exponent),
                new BigInteger(modulus)
        );
    }

    private static void runTests(ModularArithmeticService service) {
        ArithmeticResult normalized = service.execute(request(
                Operation.NORMALIZE, "-17", null, null, "5"));
        require(normalized.value().equals(BigInteger.valueOf(3)),
                "Normalization failed.");

        ArithmeticResult congruence = service.execute(request(
                Operation.CONGRUENCE, "17", "2", null, "5"));
        require(congruence.value().equals(BigInteger.ONE),
                "Congruence failed.");

        ArithmeticResult product = service.execute(request(
                Operation.MULTIPLY, "123456", "789012", null, "97"));
        require(product.value().equals(BigInteger.valueOf(
                123456L * 789012L % 97L)), "Multiplication failed.");

        ArithmeticResult power = service.execute(request(
                Operation.POWER, "3", null, "100", "7"));
        require(power.value().equals(BigInteger.valueOf(4)),
                "Exponentiation failed.");

        ArithmeticResult negativePower = service.execute(request(
                Operation.POWER, "3", null, "-1", "11"));
        require(negativePower.value().equals(BigInteger.valueOf(4)),
                "Negative exponent failed.");

        ArithmeticResult invalidInverse = service.execute(request(
                Operation.INVERSE, "6", null, null, "9"));
        require(invalidInverse.outcome() == Outcome.NON_INVERTIBLE,
                "Non-invertible value was accepted.");

        ArithmeticResult invalidResourceRequest = service.execute(request(
                Operation.POWER, "3", null, "999999999999999999999", "17"));
        require(invalidResourceRequest.outcome() == Outcome.INVALID_REQUEST,
                "Resource policy failed.");
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new IllegalStateException(message);
        }
    }

    public static void main(String[] args) {
        List<ArithmeticPolicy> policies = new ArrayList<>();
        policies.add(new ResourcePolicy(256, 256, 128));

        ModularArithmeticService service =
                new ModularArithmeticService(policies);

        runTests(service);
        System.out.println("All Java 17 modular arithmetic tests passed.");

        List<ArithmeticRequest> requests = List.of(
                request(Operation.ADD, "123", "-45", null, "17"),
                request(Operation.MULTIPLY, "123456", "789012", null, "97"),
                request(Operation.POWER, "3", null, "100", "17"),
                request(Operation.INVERSE, "5", null, null, "17"),
                request(Operation.INVERSE, "6", null, null, "9")
        );

        for (ArithmeticRequest item : requests) {
            ArithmeticResult result = service.execute(item);
            System.out.printf(
                    "%s | result=%s | outcome=%s | %s%n",
                    item.operation(),
                    result.value(),
                    result.outcome(),
                    result.message()
            );
        }
    }
}
