import java.math.BigInteger;
import java.security.SecureRandom;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.TreeMap;

/*
 * Advanced Number Theory: Java 17
 *
 * Enterprise-oriented computational number theory service.
 *
 * Features:
 * - Arbitrary-precision modular arithmetic
 * - Probabilistic primality validation
 * - Pollard Rho factorization
 * - Legendre symbols
 * - Tonelli-Shanks square roots
 * - Exact multiplicative-order calculation
 * - Baby-Step Giant-Step
 * - Pohlig-Hellman
 * - Chinese Remainder Theorem
 * - Immutable parameter objects
 * - Computation policies
 * - Explicit discrete-log job state transitions
 */

public class NumberTheoryWorkbench {

    private static final BigInteger TWO = BigInteger.TWO;
    private static final BigInteger THREE = BigInteger.valueOf(3);

    private static final int DEFAULT_CERTAINTY = 100;
    private static final long DEFAULT_BSGS_LIMIT = 2_000_000L;

    private static final List<BigInteger> SMALL_PRIMES = List.of(
        TWO,
        THREE,
        BigInteger.valueOf(5),
        BigInteger.valueOf(7),
        BigInteger.valueOf(11),
        BigInteger.valueOf(13),
        BigInteger.valueOf(17),
        BigInteger.valueOf(19),
        BigInteger.valueOf(23),
        BigInteger.valueOf(29),
        BigInteger.valueOf(31),
        BigInteger.valueOf(37)
    );

    public static class NumberTheoryException extends RuntimeException {
        public NumberTheoryException(String message) {
            super(message);
        }
    }

    public static class ComputationLimitException
            extends RuntimeException {
        public ComputationLimitException(String message) {
            super(message);
        }
    }

    public enum JobStatus {
        PENDING,
        RUNNING,
        SOLVED,
        NO_SOLUTION,
        FAILED
    }

    public enum ResidueClassification {
        ZERO,
        QUADRATIC_RESIDUE,
        QUADRATIC_NONRESIDUE
    }

    public record ComputationPolicy(
        int primalityCertainty,
        long maximumBabySteps,
        int maximumPollardIterations
    ) {
        public ComputationPolicy {
            if (primalityCertainty < 10) {
                throw new IllegalArgumentException(
                    "Primality certainty must be at least 10."
                );
            }

            if (maximumBabySteps < 1) {
                throw new IllegalArgumentException(
                    "Baby-step limit must be positive."
                );
            }

            if (maximumPollardIterations < 1) {
                throw new IllegalArgumentException(
                    "Pollard iteration limit must be positive."
                );
            }
        }

        public static ComputationPolicy standard() {
            return new ComputationPolicy(
                DEFAULT_CERTAINTY,
                DEFAULT_BSGS_LIMIT,
                250_000
            );
        }
    }

    public record PrimeField(BigInteger modulus) {
        public PrimeField {
            Objects.requireNonNull(modulus);

            if (modulus.compareTo(TWO) < 0) {
                throw new NumberTheoryException(
                    "Prime modulus must be at least two."
                );
            }

            if (!modulus.isProbablePrime(100)) {
                throw new NumberTheoryException(
                    "Field modulus failed primality validation."
                );
            }
        }

        public BigInteger reduce(BigInteger value) {
            return value.mod(modulus);
        }

        public BigInteger multiply(
                BigInteger left,
                BigInteger right) {
            return left.multiply(right).mod(modulus);
        }

        public BigInteger power(
                BigInteger base,
                BigInteger exponent) {
            if (exponent.signum() < 0) {
                throw new NumberTheoryException(
                    "Negative exponents are not supported."
                );
            }

            return base.modPow(exponent, modulus);
        }
    }

    public record Factorization(
        BigInteger number,
        Map<BigInteger, Integer> primePowers
    ) {
        public Factorization {
            Objects.requireNonNull(number);
            Objects.requireNonNull(primePowers);

            if (number.signum() <= 0) {
                throw new NumberTheoryException(
                    "Factorized number must be positive."
                );
            }

            primePowers = Collections.unmodifiableMap(
                new TreeMap<>(primePowers)
            );

            BigInteger product = BigInteger.ONE;

            for (Map.Entry<BigInteger, Integer> entry
                    : primePowers.entrySet()) {

                BigInteger prime = entry.getKey();
                int exponent = entry.getValue();

                if (
                    exponent <= 0 ||
                    !prime.isProbablePrime(100)
                ) {
                    throw new NumberTheoryException(
                        "Invalid prime-power factor."
                    );
                }

                product = product.multiply(
                    prime.pow(exponent)
                );
            }

            if (!product.equals(number)) {
                throw new NumberTheoryException(
                    "Factorization does not reconstruct the input."
                );
            }
        }
    }

    public record SquareRootResult(
        BigInteger value,
        BigInteger modulus,
        List<BigInteger> roots,
        ResidueClassification classification
    ) {
        public SquareRootResult {
            roots = List.copyOf(roots);
        }

        public boolean isResidue() {
            return classification !=
                ResidueClassification.QUADRATIC_NONRESIDUE;
        }
    }

    public record DiscreteLogResult(
        BigInteger exponent,
        BigInteger groupOrder,
        String algorithm
    ) {}

    /*
     * A job has an explicit lifecycle.
     * Terminal states cannot transition to another state.
     */
    public static final class DiscreteLogJob {
        private final String jobId;
        private final BigInteger base;
        private final BigInteger target;
        private final BigInteger order;

        private JobStatus status = JobStatus.PENDING;
        private DiscreteLogResult result;
        private String failureReason;

        public DiscreteLogJob(
                String jobId,
                BigInteger base,
                BigInteger target,
                BigInteger order) {

            if (jobId == null || jobId.isBlank()) {
                throw new NumberTheoryException(
                    "Job identifier cannot be blank."
                );
            }

            this.jobId = jobId;
            this.base = Objects.requireNonNull(base);
            this.target = Objects.requireNonNull(target);
            this.order = Objects.requireNonNull(order);

            if (order.compareTo(BigInteger.ONE) <= 0) {
                throw new NumberTheoryException(
                    "Group order must exceed one."
                );
            }
        }

        private void transition(JobStatus next) {
            boolean valid = switch (status) {
                case PENDING -> next == JobStatus.RUNNING;
                case RUNNING -> next == JobStatus.SOLVED
                    || next == JobStatus.NO_SOLUTION
                    || next == JobStatus.FAILED;
                default -> false;
            };

            if (!valid) {
                throw new NumberTheoryException(
                    "Invalid job transition: " +
                    status + " -> " + next
                );
            }

            status = next;
        }

        public void markSolved(DiscreteLogResult result) {
            transition(JobStatus.SOLVED);
            this.result = Objects.requireNonNull(result);
        }

        public void markNoSolution() {
            transition(JobStatus.NO_SOLUTION);
        }

        public void markFailed(String reason) {
            transition(JobStatus.FAILED);
            this.failureReason = reason;
        }

        public void start() {
            transition(JobStatus.RUNNING);
        }

        public String jobId() {
            return jobId;
        }

        public BigInteger base() {
            return base;
        }

        public BigInteger target() {
            return target;
        }

        public BigInteger order() {
            return order;
        }

        public JobStatus status() {
            return status;
        }

        public Optional<DiscreteLogResult> result() {
            return Optional.ofNullable(result);
        }

        public Optional<String> failureReason() {
            return Optional.ofNullable(failureReason);
        }
    }

    public static final class FactorizationService {
        private final SecureRandom random = new SecureRandom();
        private final ComputationPolicy policy;

        public FactorizationService(ComputationPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        public Factorization factor(BigInteger number) {
            if (number.signum() <= 0) {
                throw new NumberTheoryException(
                    "Factorization requires a positive integer."
                );
            }

            TreeMap<BigInteger, Integer> factors =
                new TreeMap<>();

            ArrayDeque<BigInteger> pending =
                new ArrayDeque<>();

            pending.push(number);

            while (!pending.isEmpty()) {
                BigInteger current = pending.pop();

                if (current.equals(BigInteger.ONE)) {
                    continue;
                }

                if (
                    current.isProbablePrime(
                        policy.primalityCertainty()
                    )
                ) {
                    factors.merge(current, 1, Integer::sum);
                    continue;
                }

                BigInteger divisor = pollardRho(current);

                if (
                    divisor.equals(BigInteger.ONE) ||
                    divisor.equals(current)
                ) {
                    throw new NumberTheoryException(
                        "Pollard Rho failed to find a proper factor."
                    );
                }

                pending.push(divisor);
                pending.push(current.divide(divisor));
            }

            return new Factorization(number, factors);
        }

        private BigInteger randomBelow(BigInteger limit) {
            if (limit.signum() <= 0) {
                throw new IllegalArgumentException(
                    "Random bound must be positive."
                );
            }

            BigInteger value;

            do {
                value = new BigInteger(
                    limit.bitLength(),
                    random
                );
            } while (value.compareTo(limit) >= 0);

            return value;
        }

        private BigInteger pollardRho(BigInteger n) {
            if (n.mod(TWO).equals(BigInteger.ZERO)) {
                return TWO;
            }

            if (n.mod(THREE).equals(BigInteger.ZERO)) {
                return THREE;
            }

            while (true) {
                BigInteger x = randomBelow(n.subtract(TWO))
                    .add(TWO);

                BigInteger y = x;

                BigInteger c = randomBelow(
                    n.subtract(BigInteger.ONE)
                ).add(BigInteger.ONE);

                BigInteger divisor = BigInteger.ONE;

                for (
                    int iteration = 0;
                    iteration < policy.maximumPollardIterations();
                    iteration++
                ) {
                    x = rhoFunction(x, c, n);

                    y = rhoFunction(
                        rhoFunction(y, c, n),
                        c,
                        n
                    );

                    divisor = x.subtract(y)
                        .abs()
                        .gcd(n);

                    if (divisor.equals(BigInteger.ONE)) {
                        continue;
                    }

                    if (!divisor.equals(n)) {
                        return divisor;
                    }

                    break;
                }
            }
        }

        private BigInteger rhoFunction(
                BigInteger x,
                BigInteger c,
                BigInteger n) {

            return x.multiply(x)
                .add(c)
                .mod(n);
        }
    }

    public static final class ArithmeticService {
        private final ComputationPolicy policy;
        private final FactorizationService factorizationService;

        public ArithmeticService(ComputationPolicy policy) {
            this.policy = policy;

            this.factorizationService =
                new FactorizationService(policy);
        }

        public Factorization factor(BigInteger n) {
            return factorizationService.factor(n);
        }

        public int legendreSymbol(
                BigInteger value,
                PrimeField field) {

            BigInteger p = field.modulus();

            if (p.equals(TWO)) {
                throw new NumberTheoryException(
                    "The Legendre symbol requires an odd prime."
                );
            }

            BigInteger a = value.mod(p);

            if (a.equals(BigInteger.ZERO)) {
                return 0;
            }

            return a.modPow(
                p.subtract(BigInteger.ONE).shiftRight(1),
                p
            ).equals(BigInteger.ONE) ? 1 : -1;
        }

        public SquareRootResult squareRoots(
                BigInteger value,
                PrimeField field) {

            BigInteger p = field.modulus();
            BigInteger a = value.mod(p);

            if (p.equals(TWO)) {
                return new SquareRootResult(
                    a,
                    p,
                    List.of(a),
                    ResidueClassification.QUADRATIC_RESIDUE
                );
            }

            int symbol = legendreSymbol(a, field);

            if (symbol == -1) {
                return new SquareRootResult(
                    a,
                    p,
                    List.of(),
                    ResidueClassification.QUADRATIC_NONRESIDUE
                );
            }

            if (a.equals(BigInteger.ZERO)) {
                return new SquareRootResult(
                    a,
                    p,
                    List.of(BigInteger.ZERO),
                    ResidueClassification.ZERO
                );
            }

            BigInteger root;

            if (p.mod(BigInteger.valueOf(4)).equals(THREE)) {
                root = a.modPow(
                    p.add(BigInteger.ONE).shiftRight(2),
                    p
                );
            } else {
                root = tonelliShanks(a, p);
            }

            BigInteger other = p.subtract(root).mod(p);

            List<BigInteger> roots = new ArrayList<>();
            roots.add(root);

            if (!other.equals(root)) {
                roots.add(other);
            }

            roots.sort(BigInteger::compareTo);

            for (BigInteger candidate : roots) {
                if (
                    !candidate.multiply(candidate)
                        .mod(p)
                        .equals(a)
                ) {
                    throw new NumberTheoryException(
                        "Square-root verification failed."
                    );
                }
            }

            return new SquareRootResult(
                a,
                p,
                roots,
                ResidueClassification.QUADRATIC_RESIDUE
            );
        }

        private BigInteger tonelliShanks(
                BigInteger a,
                BigInteger p) {

            BigInteger q = p.subtract(BigInteger.ONE);
            int s = 0;

            while (!q.testBit(0)) {
                q = q.shiftRight(1);
                s++;
            }

            BigInteger z = TWO;

            while (legendreSymbol(z, new PrimeField(p)) != -1) {
                z = z.add(BigInteger.ONE);
            }

            BigInteger c = z.modPow(q, p);
            BigInteger x = a.modPow(
                q.add(BigInteger.ONE).shiftRight(1),
                p
            );

            BigInteger t = a.modPow(q, p);
            int m = s;

            while (!t.equals(BigInteger.ONE)) {
                int i = 1;
                BigInteger temporary = t.multiply(t).mod(p);

                while (
                    i < m &&
                    !temporary.equals(BigInteger.ONE)
                ) {
                    temporary = temporary.multiply(temporary).mod(p);
                    i++;
                }

                if (i == m) {
                    throw new NumberTheoryException(
                        "Tonelli-Shanks invariant failed."
                    );
                }

                BigInteger exponent = BigInteger.ONE.shiftLeft(m - i - 1);
                BigInteger b = c.modPow(exponent, p);
                BigInteger bSquared = b.multiply(b).mod(p);

                x = x.multiply(b).mod(p);
                t = t.multiply(bSquared).mod(p);
                c = bSquared;
                m = i;
            }

            return x;
        }

        public BigInteger multiplicativeOrder(
                BigInteger base,
                PrimeField field) {

            BigInteger p = field.modulus();

            base = base.mod(p);

            if (base.equals(BigInteger.ZERO)) {
                throw new NumberTheoryException(
                    "Zero has no multiplicative order."
                );
            }

            BigInteger order = p.subtract(BigInteger.ONE);

            Factorization factorization = factor(order);

            for (BigInteger prime :
                    factorization.primePowers().keySet()) {

                while (
                    order.mod(prime).equals(BigInteger.ZERO) &&
                    base.modPow(order.divide(prime), p)
                        .equals(BigInteger.ONE)
                ) {
                    order = order.divide(prime);
                }
            }

            return order;
        }

        public Optional<BigInteger> babyStepGiantStep(
                BigInteger base,
                BigInteger target,
                BigInteger modulus,
                BigInteger order) {

            if (order.signum() <= 0) {
                throw new NumberTheoryException(
                    "Group order must be positive."
                );
            }

            BigInteger m = order.sqrt();

            if (!m.multiply(m).equals(order)) {
                m = m.add(BigInteger.ONE);
            }

            if (
                m.compareTo(BigInteger.valueOf(
                    policy.maximumBabySteps()
                )) > 0
            ) {
                throw new ComputationLimitException(
                    "Baby-Step Giant-Step memory budget exceeded."
                );
            }

            int tableSize = m.intValueExact();

            base = base.mod(modulus);
            target = target.mod(modulus);

            Map<BigInteger, Integer> babySteps =
                new LinkedHashMap<>(tableSize * 2);

            BigInteger value = BigInteger.ONE;

            for (int j = 0; j < tableSize; j++) {
                babySteps.putIfAbsent(value, j);
                value = value.multiply(base).mod(modulus);
            }

            BigInteger giantFactor = base.modPow(m, modulus)
                .modInverse(modulus);

            BigInteger gamma = target;

            BigInteger giantCount =
                order.add(m).subtract(BigInteger.ONE).divide(m);

            long iterations = giantCount.longValueExact();

            for (long i = 0; i <= iterations; i++) {
                Integer baby = babySteps.get(gamma);

                if (baby != null) {
                    BigInteger candidate = m
                        .multiply(BigInteger.valueOf(i))
                        .add(BigInteger.valueOf(baby));

                    if (
                        candidate.compareTo(order) < 0 &&
                        base.modPow(candidate, modulus)
                            .equals(target)
                    ) {
                        return Optional.of(candidate);
                    }
                }

                gamma = gamma.multiply(giantFactor).mod(modulus);
            }

            return Optional.empty();
        }

        private BigInteger chineseRemainder(
                List<BigInteger> residues,
                List<BigInteger> moduli) {

            if (
                residues.isEmpty() ||
                residues.size() != moduli.size()
            ) {
                throw new NumberTheoryException(
                    "Invalid Chinese Remainder input."
                );
            }

            BigInteger result = BigInteger.ZERO;
            BigInteger product = BigInteger.ONE;

            for (int i = 0; i < residues.size(); i++) {
                BigInteger modulus = moduli.get(i);

                if (
                    modulus.compareTo(BigInteger.ONE) <= 0 ||
                    !product.gcd(modulus).equals(BigInteger.ONE)
                ) {
                    throw new NumberTheoryException(
                        "CRT moduli must be pairwise coprime."
                    );
                }

                BigInteger correction = residues.get(i)
                    .subtract(result)
                    .multiply(product.modInverse(modulus))
                    .mod(modulus);

                result = result.add(
                    product.multiply(correction)
                );

                product = product.multiply(modulus);
                result = result.mod(product);
            }

            return result;
        }

        public Optional<BigInteger> pohligHellman(
                BigInteger base,
                BigInteger target,
                PrimeField field,
                BigInteger order) {

            BigInteger p = field.modulus();

            base = base.mod(p);
            target = target.mod(p);

            if (base.equals(BigInteger.ZERO)) {
                throw new NumberTheoryException(
                    "Base cannot be zero."
                );
            }

            if (
                order.signum() <= 0 ||
                order.compareTo(p.subtract(BigInteger.ONE)) > 0
            ) {
                throw new NumberTheoryException(
                    "Invalid subgroup order."
                );
            }

            if (!base.modPow(order, p).equals(BigInteger.ONE)) {
                throw new NumberTheoryException(
                    "Base does not satisfy the supplied order."
                );
            }

            Factorization factorization = factor(order);

            for (BigInteger prime :
                    factorization.primePowers().keySet()) {

                if (
                    base.modPow(order.divide(prime), p)
                        .equals(BigInteger.ONE)
                ) {
                    throw new NumberTheoryException(
                        "Supplied order is not exact."
                    );
                }
            }

            if (
                !target.modPow(order, p)
                    .equals(BigInteger.ONE)
            ) {
                return Optional.empty();
            }

            List<BigInteger> residues = new ArrayList<>();
            List<BigInteger> moduli = new ArrayList<>();

            for (Map.Entry<BigInteger, Integer> entry :
                    factorization.primePowers().entrySet()) {

                BigInteger q = entry.getKey();
                int exponent = entry.getValue();
                BigInteger primePower = q.pow(exponent);

                BigInteger g = base.modPow(
                    order.divide(primePower),
                    p
                );

                BigInteger h = target.modPow(
                    order.divide(primePower),
                    p
                );

                BigInteger digitBase = g.modPow(
                    primePower.divide(q),
                    p
                );

                BigInteger partial = BigInteger.ZERO;
                BigInteger qPower = BigInteger.ONE;

                for (int k = 0; k < exponent; k++) {
                    BigInteger inversePartial = g.modPow(
                        partial,
                        p
                    ).modInverse(p);

                    BigInteger correction = h.multiply(
                        inversePartial
                    ).mod(p);

                    BigInteger digitTarget = correction.modPow(
                        primePower.divide(qPower.multiply(q)),
                        p
                    );

                    Optional<BigInteger> digit =
                        babyStepGiantStep(
                            digitBase,
                            digitTarget,
                            p,
                            q
                        );

                    if (digit.isEmpty()) {
                        return Optional.empty();
                    }

                    partial = partial.add(
                        digit.get().multiply(qPower)
                    );

                    qPower = qPower.multiply(q);
                }

                residues.add(partial);
                moduli.add(primePower);
            }

            BigInteger answer = chineseRemainder(
                residues,
                moduli
            ).mod(order);

            if (!base.modPow(answer, p).equals(target)) {
                throw new NumberTheoryException(
                    "Pohlig-Hellman result failed verification."
                );
            }

            return Optional.of(answer);
        }
    }

    /*
     * The service controls state transitions and prevents invalid
     * mathematical results from entering the completed-job state.
     */
    public static final class DiscreteLogService {
        private final ArithmeticService arithmetic;

        public DiscreteLogService(ArithmeticService arithmetic) {
            this.arithmetic = Objects.requireNonNull(arithmetic);
        }

        public DiscreteLogJob execute(
                DiscreteLogJob job,
                PrimeField field) {

            Objects.requireNonNull(job);
            Objects.requireNonNull(field);

            job.start();

            try {
                Optional<BigInteger> result =
                    arithmetic.pohligHellman(
                        job.base(),
                        job.target(),
                        field,
                        job.order()
                    );

                if (result.isEmpty()) {
                    job.markNoSolution();
                } else {
                    job.markSolved(
                        new DiscreteLogResult(
                            result.get(),
                            job.order(),
                            "Pohlig-Hellman"
                        )
                    );
                }

            } catch (RuntimeException exception) {
                job.markFailed(exception.getMessage());
                throw exception;
            }

            return job;
        }
    }

    private static void runTests(
            ArithmeticService arithmetic,
            PrimeField field) {

        BigInteger p = field.modulus();

        if (!BigInteger.valueOf(1019).equals(p)) {
            throw new AssertionError("Unexpected test field.");
        }

        if (!BigInteger.valueOf(9).equals(
                BigInteger.valueOf(7).modPow(
                    BigInteger.valueOf(128),
                    BigInteger.valueOf(13)
                ))) {
            throw new AssertionError("Modular power failure.");
        }

        if (!BigInteger.valueOf(4).equals(
                BigInteger.valueOf(3).modInverse(
                    BigInteger.valueOf(11)
                ))) {
            throw new AssertionError("Modular inverse failure.");
        }

        if (arithmetic.legendreSymbol(
                BigInteger.valueOf(2), field) != -1) {
            throw new AssertionError("Legendre test failure.");
        }

        if (arithmetic.legendreSymbol(
                BigInteger.ZERO, field) != 0) {
            throw new AssertionError("Zero symbol failure.");
        }

        SquareRootResult roots = arithmetic.squareRoots(
            BigInteger.valueOf(56 * 56),
            field
        );

        if (
            !roots.roots().equals(List.of(
                BigInteger.valueOf(56),
                BigInteger.valueOf(963)
            ))
        ) {
            throw new AssertionError("Tonelli-Shanks failure.");
        }

        if (!arithmetic.squareRoots(
                BigInteger.TWO, field).roots().isEmpty()) {
            throw new AssertionError(
                "A nonresidue produced a square root."
            );
        }

        Factorization factorization = arithmetic.factor(
            BigInteger.valueOf(600851475143L)
        );

        if (
            !factorization.primePowers().values().stream()
                .allMatch(exponent -> exponent > 0)
        ) {
            throw new AssertionError("Factorization validation failed.");
        }

        BigInteger order = arithmetic.multiplicativeOrder(
            BigInteger.TWO,
            field
        );

        if (!order.equals(BigInteger.valueOf(1018))) {
            throw new AssertionError("Multiplicative order failure.");
        }

        BigInteger target = BigInteger.TWO.modPow(
            BigInteger.valueOf(137),
            p
        );

        Optional<BigInteger> answer =
            arithmetic.pohligHellman(
                BigInteger.TWO,
                target,
                field,
                order
            );

        if (
            answer.isEmpty() ||
            !answer.get().equals(BigInteger.valueOf(137))
        ) {
            throw new AssertionError("Discrete logarithm failure.");
        }

        if (arithmetic.pohligHellman(
                BigInteger.TWO,
                BigInteger.ZERO,
                field,
                order
            ).isPresent()) {
            throw new AssertionError(
                "Invalid zero target was accepted."
            );
        }
    }

    public static void main(String[] args) {
        try {
            ComputationPolicy policy =
                ComputationPolicy.standard();

            ArithmeticService arithmetic =
                new ArithmeticService(policy);

            PrimeField field = new PrimeField(
                BigInteger.valueOf(1019)
            );

            runTests(arithmetic, field);

            DiscreteLogService discreteLogService =
                new DiscreteLogService(arithmetic);

            BigInteger generator = BigInteger.TWO;
            BigInteger secret = BigInteger.valueOf(137);

            BigInteger order = arithmetic.multiplicativeOrder(
                generator,
                field
            );

            BigInteger publicValue = generator.modPow(
                secret,
                field.modulus()
            );

            System.out.println("ADVANCED NUMBER THEORY");
            System.out.println("======================");

            System.out.println(
                "Prime field: F_" + field.modulus()
            );

            System.out.println(
                "Generator: " + generator
            );

            System.out.println(
                "Exact multiplicative order: " + order
            );

            System.out.println("\nFACTORIZATION");

            Factorization factors = arithmetic.factor(
                BigInteger.valueOf(600851475143L)
            );

            factors.primePowers().forEach((prime, exponent) ->
                System.out.println(prime + "^" + exponent)
            );

            System.out.println("\nQUADRATIC RESIDUES");

            SquareRootResult squareRoots =
                arithmetic.squareRoots(
                    BigInteger.valueOf(56 * 56),
                    field
                );

            System.out.println(
                "Classification: " + squareRoots.classification()
            );

            System.out.println(
                "Roots: " + squareRoots.roots()
            );

            System.out.println("\nDISCRETE LOGARITHM SERVICE");

            DiscreteLogJob job = new DiscreteLogJob(
                "NT-DLOG-001",
                generator,
                publicValue,
                order
            );

            DiscreteLogJob completed =
                discreteLogService.execute(job, field);

            System.out.println("Job ID: " + completed.jobId());
            System.out.println("State: " + completed.status());

            completed.result().ifPresent(result -> {
                System.out.println(
                    "Recovered exponent: " + result.exponent()
                );

                System.out.println(
                    "Algorithm: " + result.algorithm()
                );
            });

            System.out.println(
                "\nAll Java 17 verification checks passed."
            );

            System.out.println(
                "Security note: BigInteger arithmetic is not "
                + "guaranteed to be constant-time."
            );

        } catch (RuntimeException exception) {
            System.err.println(
                "Computation failed: " + exception.getMessage()
            );

            System.exitCode = 1;
        }
    }
}
