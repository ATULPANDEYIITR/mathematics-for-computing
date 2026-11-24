import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

/*
 * Information Theory: Enterprise Information Analysis
 *
 * Java 17 implementation featuring:
 * - Immutable probability distributions
 * - Self-information
 * - Shannon entropy
 * - Conditional and joint entropy
 * - Mutual information
 * - Cross-entropy
 * - KL divergence
 * - Huffman coding
 * - Streaming entropy monitoring
 * - Explicit validation and domain exceptions
 */

public class InformationTheoryEngine {

    private static final double EPSILON = 1e-9;

    public static class InformationTheoryException
            extends IllegalArgumentException {

        public InformationTheoryException(String message) {
            super(message);
        }
    }

    public record Outcome(String name) {
        public Outcome {
            if (name == null || name.isBlank()) {
                throw new InformationTheoryException(
                        "Outcome name cannot be empty."
                );
            }
        }
    }

    public record Observation(String symbol, long timestamp) {
        public Observation {
            if (symbol == null || symbol.isBlank()) {
                throw new InformationTheoryException(
                        "Observation symbol cannot be empty."
                );
            }

            if (timestamp < 0) {
                throw new InformationTheoryException(
                        "Timestamp cannot be negative."
                );
            }
        }
    }

    public record JointOutcome(String x, String y) {
        public JointOutcome {
            if (x == null || y == null ||
                    x.isBlank() || y.isBlank()) {
                throw new InformationTheoryException(
                        "Joint outcome components cannot be empty."
                );
            }
        }
    }

    public record Metric(String name, double value, String unit) {
        public Metric {
            Objects.requireNonNull(name);
            Objects.requireNonNull(unit);

            if (Double.isNaN(value)) {
                throw new InformationTheoryException(
                        "Metric cannot be NaN."
                );
            }
        }
    }

    public static final class ProbabilityDistribution<T> {

        private final Map<T, Double> probabilities;

        public ProbabilityDistribution(Map<T, Double> input) {
            if (input == null || input.isEmpty()) {
                throw new InformationTheoryException(
                        "Distribution cannot be empty."
                );
            }

            Map<T, Double> copy = new LinkedHashMap<>();
            double total = 0.0;

            for (Map.Entry<T, Double> entry : input.entrySet()) {
                T outcome = Objects.requireNonNull(entry.getKey());
                double probability = entry.getValue();

                if (!Double.isFinite(probability) ||
                        probability < 0.0 ||
                        probability > 1.0) {
                    throw new InformationTheoryException(
                            "Invalid probability for " + outcome
                    );
                }

                copy.put(outcome, probability);
                total += probability;
            }

            if (Math.abs(total - 1.0) > EPSILON) {
                throw new InformationTheoryException(
                        "Probabilities must sum to 1. Current sum: " + total
                );
            }

            this.probabilities =
                    Collections.unmodifiableMap(copy);
        }

        public Map<T, Double> values() {
            return probabilities;
        }

        public int outcomeCount() {
            return probabilities.size();
        }

        public double probabilityOf(T outcome) {
            Double probability = probabilities.get(outcome);

            if (probability == null) {
                throw new InformationTheoryException(
                        "Unknown outcome: " + outcome
                );
            }

            return probability;
        }
    }

    public interface InformationMetric {
        double calculate();
    }

    public static final class SelfInformation
            implements InformationMetric {

        private final double probability;
        private final double base;

        public SelfInformation(double probability) {
            this(probability, 2.0);
        }

        public SelfInformation(double probability, double base) {
            if (!Double.isFinite(probability) ||
                    probability < 0 || probability > 1) {
                throw new InformationTheoryException(
                        "Probability must be between 0 and 1."
                );
            }

            if (!Double.isFinite(base) || base <= 0 || base == 1) {
                throw new InformationTheoryException(
                        "Invalid logarithm base."
                );
            }

            this.probability = probability;
            this.base = base;
        }

        @Override
        public double calculate() {
            if (probability == 0) {
                return Double.POSITIVE_INFINITY;
            }

            return -Math.log(probability) / Math.log(base);
        }
    }

    public static final class Entropy<T>
            implements InformationMetric {

        private final ProbabilityDistribution<T> distribution;

        public Entropy(ProbabilityDistribution<T> distribution) {
            this.distribution = Objects.requireNonNull(distribution);
        }

        @Override
        public double calculate() {
            double result = 0;

            for (double probability :
                    distribution.values().values()) {

                if (probability > 0) {
                    result -= probability * Math.log(probability) /
                            Math.log(2);
                }
            }

            return result;
        }

        public double normalized() {
            if (distribution.outcomeCount() == 1) {
                return 0;
            }

            return calculate() /
                    (Math.log(distribution.outcomeCount()) / Math.log(2));
        }

        public double maximum() {
            return Math.log(distribution.outcomeCount()) /
                    Math.log(2);
        }

        public double uncertaintyGap() {
            return maximum() - calculate();
        }
    }

    public static final class JointInformation {

        private final ProbabilityDistribution<JointOutcome> joint;

        public JointInformation(
                ProbabilityDistribution<JointOutcome> joint
        ) {
            this.joint = Objects.requireNonNull(joint);
        }

        public <K> ProbabilityDistribution<K> marginal(
                java.util.function.Function<JointOutcome, K> extractor
        ) {
            Map<K, Double> result = new LinkedHashMap<>();

            joint.values().forEach((outcome, probability) ->
                    result.merge(
                            extractor.apply(outcome),
                            probability,
                            Double::sum
                    )
            );

            return new ProbabilityDistribution<>(result);
        }

        public double jointEntropy() {
            return new Entropy<>(joint).calculate();
        }

        public double conditionalEntropyYGivenX() {
            return conditionalEntropy(true);
        }

        public double conditionalEntropyXGivenY() {
            return conditionalEntropy(false);
        }

        private double conditionalEntropy(boolean conditionOnX) {
            Map<String, Map<String, Double>> groups =
                    new LinkedHashMap<>();

            for (var entry : joint.values().entrySet()) {
                JointOutcome outcome = entry.getKey();

                String condition = conditionOnX
                        ? outcome.x()
                        : outcome.y();

                String target = conditionOnX
                        ? outcome.y()
                        : outcome.x();

                groups.computeIfAbsent(
                        condition,
                        ignored -> new LinkedHashMap<>()
                ).merge(target, entry.getValue(), Double::sum);
            }

            double result = 0;

            for (Map<String, Double> group : groups.values()) {
                double groupProbability =
                        group.values().stream()
                                .mapToDouble(Double::doubleValue)
                                .sum();

                Map<String, Double> conditional =
                        new LinkedHashMap<>();

                group.forEach((symbol, probability) ->
                        conditional.put(
                                symbol,
                                probability / groupProbability
                        )
                );

                ProbabilityDistribution<String> distribution =
                        new ProbabilityDistribution<>(conditional);

                result += groupProbability *
                        new Entropy<>(distribution).calculate();
            }

            return result;
        }

        public double mutualInformation() {
            double hx = new Entropy<>(
                    marginal(JointOutcome::x)
            ).calculate();

            double hy = new Entropy<>(
                    marginal(JointOutcome::y)
            ).calculate();

            return Math.max(
                    0,
                    hx + hy - jointEntropy()
            );
        }
    }

    public static final class DistributionComparison {

        public static <T> double crossEntropy(
                ProbabilityDistribution<T> actual,
                ProbabilityDistribution<T> predicted
        ) {
            validateMatchingOutcomes(actual, predicted);

            double result = 0;

            for (T symbol : actual.values().keySet()) {
                double p = actual.probabilityOf(symbol);
                double q = predicted.probabilityOf(symbol);

                if (p == 0) continue;
                if (q == 0) return Double.POSITIVE_INFINITY;

                result -= p * Math.log(q) / Math.log(2);
            }

            return result;
        }

        public static <T> double klDivergence(
                ProbabilityDistribution<T> actual,
                ProbabilityDistribution<T> predicted
        ) {
            validateMatchingOutcomes(actual, predicted);

            double result = 0;

            for (T symbol : actual.values().keySet()) {
                double p = actual.probabilityOf(symbol);
                double q = predicted.probabilityOf(symbol);

                if (p == 0) continue;
                if (q == 0) return Double.POSITIVE_INFINITY;

                result += p * Math.log(p / q) / Math.log(2);
            }

            return Math.max(0, result);
        }

        private static <T> void validateMatchingOutcomes(
                ProbabilityDistribution<T> actual,
                ProbabilityDistribution<T> predicted
        ) {
            Objects.requireNonNull(actual);
            Objects.requireNonNull(predicted);

            if (!actual.values().keySet().equals(
                    predicted.values().keySet()
            )) {
                throw new InformationTheoryException(
                        "Outcome sets must match."
                );
            }
        }
    }

    public static final class HuffmanCoder {

        private static final class Node {
            double probability;
            String symbol;
            Node left;
            Node right;
            long order;

            Node(double probability, String symbol, long order) {
                this.probability = probability;
                this.symbol = symbol;
                this.order = order;
            }
        }

        private final Map<String, String> codes =
                new LinkedHashMap<>();

        public HuffmanCoder(
                ProbabilityDistribution<String> distribution
        ) {
            PriorityQueue<Node> queue = new PriorityQueue<>(
                    Comparator.comparingDouble((Node n) -> n.probability)
                            .thenComparingLong(n -> n.order)
            );

            AtomicLong sequence = new AtomicLong();

            distribution.values().forEach((symbol, probability) ->
                    queue.add(new Node(
                            probability,
                            symbol,
                            sequence.getAndIncrement()
                    ))
            );

            if (queue.size() == 1) {
                Node only = queue.remove();
                codes.put(only.symbol, "0");
                return;
            }

            while (queue.size() > 1) {
                Node left = queue.remove();
                Node right = queue.remove();

                Node parent = new Node(
                        left.probability + right.probability,
                        null,
                        sequence.getAndIncrement()
                );

                parent.left = left;
                parent.right = right;

                queue.add(parent);
            }

            buildCodes(queue.remove(), "");
        }

        private void buildCodes(Node node, String prefix) {
            if (node.symbol != null) {
                codes.put(node.symbol, prefix);
                return;
            }

            buildCodes(node.left, prefix + "0");
            buildCodes(node.right, prefix + "1");
        }

        public Map<String, String> codes() {
            return Collections.unmodifiableMap(codes);
        }

        public String encode(List<String> message) {
            StringBuilder encoded = new StringBuilder();

            for (String symbol : message) {
                String code = codes.get(symbol);

                if (code == null) {
                    throw new InformationTheoryException(
                            "Unknown symbol: " + symbol
                    );
                }

                encoded.append(code);
            }

            return encoded.toString();
        }

        public double expectedLength(
                ProbabilityDistribution<String> distribution
        ) {
            double result = 0;

            for (var entry : distribution.values().entrySet()) {
                String code = codes.get(entry.getKey());

                if (code == null) {
                    throw new InformationTheoryException(
                            "Missing source code."
                    );
                }

                result += entry.getValue() * code.length();
            }

            return result;
        }
    }

    public static final class StreamingEntropyService {

        private final Map<String, Long> frequencies =
                new LinkedHashMap<>();

        private long count;

        public synchronized Metric observe(Observation observation) {
            Objects.requireNonNull(observation);

            frequencies.merge(
                    observation.symbol(),
                    1L,
                    Long::sum
            );

            count++;

            Map<String, Double> probabilities =
                    new LinkedHashMap<>();

            frequencies.forEach((symbol, frequency) ->
                    probabilities.put(
                            symbol,
                            (double) frequency / count
                    )
            );

            ProbabilityDistribution<String> distribution =
                    new ProbabilityDistribution<>(probabilities);

            return new Metric(
                    "stream_entropy",
                    new Entropy<>(distribution).calculate(),
                    "bits"
            );
        }

        public synchronized long observationCount() {
            return count;
        }

        public synchronized void reset() {
            frequencies.clear();
            count = 0;
        }
    }

    private static void printMetric(String name, double value) {
        System.out.printf("%-28s %.4f bits%n", name, value);
    }

    public static void main(String[] args) {

        System.out.println("INFORMATION THEORY ENGINE");
        System.out.println("=".repeat(60));

        Map<String, Double> sourceValues = new LinkedHashMap<>();

        sourceValues.put("A", 0.50);
        sourceValues.put("B", 0.25);
        sourceValues.put("C", 0.125);
        sourceValues.put("D", 0.125);

        ProbabilityDistribution<String> source =
                new ProbabilityDistribution<>(sourceValues);

        System.out.println("\n1. SELF-INFORMATION");

        source.values().forEach((symbol, probability) ->
                printMetric(
                        symbol,
                        new SelfInformation(probability).calculate()
                )
        );

        Entropy<String> sourceEntropy = new Entropy<>(source);

        System.out.println("\n2. SHANNON ENTROPY");

        printMetric("Entropy", sourceEntropy.calculate());
        printMetric("Maximum entropy", sourceEntropy.maximum());

        System.out.printf(
                "Normalized entropy: %.4f%n",
                sourceEntropy.normalized()
        );

        System.out.println("\n3. JOINT INFORMATION");

        Map<JointOutcome, Double> jointValues =
                new LinkedHashMap<>();

        jointValues.put(new JointOutcome("Sunny", "Hot"), 0.30);
        jointValues.put(new JointOutcome("Sunny", "Cold"), 0.20);
        jointValues.put(new JointOutcome("Rainy", "Hot"), 0.10);
        jointValues.put(new JointOutcome("Rainy", "Cold"), 0.40);

        JointInformation joint = new JointInformation(
                new ProbabilityDistribution<>(jointValues)
        );

        printMetric("H(X,Y)", joint.jointEntropy());
        printMetric("H(X|Y)", joint.conditionalEntropyXGivenY());
        printMetric("H(Y|X)", joint.conditionalEntropyYGivenX());
        printMetric("I(X;Y)", joint.mutualInformation());

        System.out.println("\n4. DISTRIBUTION COMPARISON");

        ProbabilityDistribution<String> actual =
                new ProbabilityDistribution<>(
                        Map.of("A", 0.50, "B", 0.30, "C", 0.20)
                );

        ProbabilityDistribution<String> predicted =
                new ProbabilityDistribution<>(
                        Map.of("A", 0.40, "B", 0.40, "C", 0.20)
                );

        printMetric(
                "Cross-entropy",
                DistributionComparison.crossEntropy(actual, predicted)
        );

        printMetric(
                "KL divergence",
                DistributionComparison.klDivergence(actual, predicted)
        );

        System.out.println("\n5. HUFFMAN CODING");

        HuffmanCoder coder = new HuffmanCoder(source);

        coder.codes().forEach(
                (symbol, code) ->
                        System.out.println(symbol + " -> " + code)
        );

        printMetric(
                "Expected code length",
                coder.expectedLength(source)
        );

        System.out.println(
                "Encoded message: " +
                coder.encode(List.of("A", "B", "C", "D"))
        );

        System.out.println("\n6. STREAMING ENTROPY");

        StreamingEntropyService stream =
                new StreamingEntropyService();

        String[] observations = {
                "success", "success", "failure",
                "success", "failure", "success"
        };

        long timestamp = 1;

        for (String symbol : observations) {
            Metric metric = stream.observe(
                    new Observation(symbol, timestamp++)
            );

            System.out.printf(
                    "Count=%d, H=%.4f bits%n",
                    stream.observationCount(),
                    metric.value()
            );
        }

        System.out.println("\n7. EDGE CASES");

        printMetric(
                "Certain event",
                new SelfInformation(1.0).calculate()
        );

        System.out.println(
                "Impossible event: " +
                new SelfInformation(0.0).calculate()
        );

        ProbabilityDistribution<String> deterministic =
                new ProbabilityDistribution<>(
                        Map.of("fixed", 1.0)
                );

        printMetric(
                "Deterministic entropy",
                new Entropy<>(deterministic).calculate()
        );

        System.out.println("\n8. VALIDATION");

        try {
            new ProbabilityDistribution<>(
                    Map.of("A", 0.7, "B", 0.7)
            );
        } catch (InformationTheoryException exception) {
            System.out.println(
                    "Invalid input rejected: " + exception.getMessage()
            );
        }

        System.out.println("\n9. MATHEMATICAL INVARIANTS");

        if (Math.abs(sourceEntropy.calculate() - 1.75) > EPSILON) {
            throw new IllegalStateException("Entropy invariant failed.");
        }

        if (DistributionComparison.klDivergence(actual, actual) > EPSILON) {
            throw new IllegalStateException("KL invariant failed.");
        }

        if (coder.expectedLength(source) + EPSILON <
                sourceEntropy.calculate()) {
            throw new IllegalStateException("Coding bound failed.");
        }

        System.out.println("All mathematical invariants passed.");
    }
}
