import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/*
 * Entropy and Cross-Entropy Enterprise Analytics
 *
 * Java 17 implementation.
 *
 * Domain components:
 * - ProbabilityDistribution
 * - JointDistribution
 * - EntropyService
 * - EvaluationPolicy
 * - EvaluationResult
 * - ClassificationService
 * - Enterprise validation
 * - Immutable probability data
 * - Explicit error handling
 */

public class EntropyAnalytics {

    private static final double EPSILON = 1e-10;

    enum Metric {
        SHANNON_ENTROPY,
        CROSS_ENTROPY,
        KL_DIVERGENCE,
        MUTUAL_INFORMATION,
        CONDITIONAL_ENTROPY
    }

    enum EvaluationStatus {
        VALID,
        INFINITE_LOSS,
        POLICY_REJECTED
    }

    static class ProbabilityException extends RuntimeException {
        ProbabilityException(String message) {
            super(message);
        }
    }

    record ProbabilityDistribution(
            String name,
            Map<String, Double> probabilities
    ) {

        ProbabilityDistribution {
            if (name == null || name.isBlank()) {
                throw new ProbabilityException(
                        "Distribution name is required."
                );
            }

            Objects.requireNonNull(
                    probabilities,
                    "Probability map cannot be null."
            );

            if (probabilities.isEmpty()) {
                throw new ProbabilityException(
                        "Distribution cannot be empty."
                );
            }

            Map<String, Double> copy = new LinkedHashMap<>();
            double total = 0.0;

            for (var entry : probabilities.entrySet()) {
                String event = entry.getKey();
                Double probability = entry.getValue();

                if (event == null || event.isBlank()) {
                    throw new ProbabilityException(
                            "Event name cannot be empty."
                    );
                }

                if (probability == null ||
                        !Double.isFinite(probability) ||
                        probability < 0.0 ||
                        probability > 1.0) {
                    throw new ProbabilityException(
                            "Invalid probability for " + event
                    );
                }

                if (copy.putIfAbsent(event, probability) != null) {
                    throw new ProbabilityException(
                            "Duplicate event: " + event
                    );
                }

                total += probability;
            }

            if (Math.abs(total - 1.0) > EPSILON) {
                throw new ProbabilityException(
                        "Probabilities must sum to one."
                );
            }

            probabilities = Collections.unmodifiableMap(copy);
        }

        double probability(String event) {
            return probabilities.getOrDefault(event, 0.0);
        }

        int size() {
            return probabilities.size();
        }
    }

    record EvaluationPolicy(
            boolean requireFiniteLoss,
            double maximumCrossEntropy,
            boolean rejectZeroPredictions
    ) {

        EvaluationPolicy {
            if (Double.isNaN(maximumCrossEntropy) ||
                    maximumCrossEntropy <= 0.0) {
                throw new ProbabilityException(
                        "Maximum cross-entropy must be positive."
                );
            }
        }

        static EvaluationPolicy standard() {
            return new EvaluationPolicy(
                    true,
                    100.0,
                    true
            );
        }
    }

    record EvaluationResult(
            String actualName,
            String predictedName,
            double entropy,
            double crossEntropy,
            double klDivergence,
            EvaluationStatus status,
            boolean identityVerified
    ) {}

    static class EntropyService {

        private void validateCompatible(
                ProbabilityDistribution p,
                ProbabilityDistribution q
        ) {
            if (!p.probabilities().keySet()
                    .equals(q.probabilities().keySet())) {
                throw new ProbabilityException(
                        "Event sets must match."
                );
            }
        }

        public double entropy(
                ProbabilityDistribution distribution
        ) {
            double result = 0.0;

            for (double p :
                    distribution.probabilities().values()) {

                if (p > 0.0) {
                    result -= p * Math.log(p) / Math.log(2);
                }
            }

            return result;
        }

        public double crossEntropy(
                ProbabilityDistribution actual,
                ProbabilityDistribution predicted
        ) {
            validateCompatible(actual, predicted);

            double result = 0.0;

            for (String event : actual.probabilities().keySet()) {
                double p = actual.probability(event);
                double q = predicted.probability(event);

                if (p == 0.0) {
                    continue;
                }

                if (q == 0.0) {
                    return Double.POSITIVE_INFINITY;
                }

                result -= p * Math.log(q) / Math.log(2);
            }

            return result;
        }

        public double klDivergence(
                ProbabilityDistribution actual,
                ProbabilityDistribution predicted
        ) {
            validateCompatible(actual, predicted);

            double result = 0.0;

            for (String event : actual.probabilities().keySet()) {
                double p = actual.probability(event);
                double q = predicted.probability(event);

                if (p == 0.0) {
                    continue;
                }

                if (q == 0.0) {
                    return Double.POSITIVE_INFINITY;
                }

                result += p * Math.log(p / q) / Math.log(2);
            }

            return Math.max(0.0, result);
        }

        public double binaryEntropy(double p) {
            if (!Double.isFinite(p) ||
                    p < 0.0 || p > 1.0) {
                throw new ProbabilityException(
                        "Invalid binary probability."
                );
            }

            if (p == 0.0 || p == 1.0) {
                return 0.0;
            }

            return -p * Math.log(p) / Math.log(2)
                    - (1.0 - p) *
                    Math.log(1.0 - p) / Math.log(2);
        }

        public ProbabilityDistribution smooth(
                ProbabilityDistribution distribution,
                double alpha
        ) {
            if (!Double.isFinite(alpha) || alpha <= 0.0) {
                throw new ProbabilityException(
                        "Alpha must be positive."
                );
            }

            double denominator =
                    1.0 + distribution.size() * alpha;

            Map<String, Double> result = new LinkedHashMap<>();

            distribution.probabilities().forEach(
                    (event, probability) ->
                            result.put(
                                    event,
                                    (probability + alpha) / denominator
                            )
            );

            return new ProbabilityDistribution(
                    distribution.name() + "_smoothed",
                    result
            );
        }

        public EvaluationResult evaluate(
                ProbabilityDistribution actual,
                ProbabilityDistribution predicted,
                EvaluationPolicy policy
        ) {
            validateCompatible(actual, predicted);

            double h = entropy(actual);
            double ce = crossEntropy(actual, predicted);
            double kl = klDivergence(actual, predicted);

            boolean zeroPrediction =
                    Double.isInfinite(ce);

            EvaluationStatus status;

            if (zeroPrediction) {
                status = EvaluationStatus.INFINITE_LOSS;
            } else if (
                    ce > policy.maximumCrossEntropy() ||
                    (policy.rejectZeroPredictions() && zeroPrediction) ||
                    (policy.requireFiniteLoss() && !Double.isFinite(ce))
            ) {
                status = EvaluationStatus.POLICY_REJECTED;
            } else {
                status = EvaluationStatus.VALID;
            }

            boolean identity = Double.isFinite(ce) &&
                    Math.abs(ce - h - kl) < 1e-8;

            return new EvaluationResult(
                    actual.name(),
                    predicted.name(),
                    h,
                    ce,
                    kl,
                    status,
                    identity
            );
        }
    }

    static class JointDistribution {

        private final double[][] matrix;
        private final double[] marginalX;
        private final double[] marginalY;

        JointDistribution(double[][] input) {
            if (input == null || input.length == 0 ||
                    input[0] == null || input[0].length == 0) {
                throw new ProbabilityException(
                        "Joint matrix cannot be empty."
                );
            }

            int columns = input[0].length;

            matrix = new double[input.length][columns];
            marginalX = new double[input.length];
            marginalY = new double[columns];

            double total = 0.0;

            for (int i = 0; i < input.length; i++) {
                if (input[i] == null ||
                        input[i].length != columns) {
                    throw new ProbabilityException(
                            "Joint matrix must be rectangular."
                    );
                }

                for (int j = 0; j < columns; j++) {
                    double p = input[i][j];

                    if (!Double.isFinite(p) ||
                            p < 0.0 || p > 1.0) {
                        throw new ProbabilityException(
                                "Invalid joint probability."
                        );
                    }

                    matrix[i][j] = p;
                    marginalX[i] += p;
                    marginalY[j] += p;
                    total += p;
                }
            }

            if (Math.abs(total - 1.0) > EPSILON) {
                throw new ProbabilityException(
                        "Joint probabilities must sum to one."
                );
            }
        }

        private double entropy(double[] values) {
            double result = 0.0;

            for (double p : values) {
                if (p > 0.0) {
                    result -= p * Math.log(p) / Math.log(2);
                }
            }

            return result;
        }

        double entropyX() {
            return entropy(marginalX);
        }

        double entropyY() {
            return entropy(marginalY);
        }

        double jointEntropy() {
            double result = 0.0;

            for (double[] row : matrix) {
                for (double p : row) {
                    if (p > 0.0) {
                        result -= p * Math.log(p) / Math.log(2);
                    }
                }
            }

            return result;
        }

        double conditionalEntropyYGivenX() {
            return Math.max(
                    0.0,
                    jointEntropy() - entropyX()
            );
        }

        double mutualInformation() {
            return Math.max(
                    0.0,
                    entropyX() + entropyY() - jointEntropy()
            );
        }
    }

    static class ClassificationService {

        private final EntropyService entropyService;

        ClassificationService(EntropyService entropyService) {
            this.entropyService = entropyService;
        }

        double negativeLogLikelihood(
                String actualClass,
                ProbabilityDistribution prediction
        ) {
            double probability =
                    prediction.probability(actualClass);

            if (probability == 0.0) {
                return Double.POSITIVE_INFINITY;
            }

            return -Math.log(probability) / Math.log(2);
        }

        double batchCrossEntropy(
                List<ProbabilityDistribution> actual,
                List<ProbabilityDistribution> predicted
        ) {
            if (actual.size() != predicted.size() ||
                    actual.isEmpty()) {
                throw new ProbabilityException(
                        "Batch dimensions must match and be non-empty."
                );
            }

            double total = 0.0;

            for (int i = 0; i < actual.size(); i++) {
                double loss = entropyService.crossEntropy(
                        actual.get(i),
                        predicted.get(i)
                );

                if (!Double.isFinite(loss)) {
                    return Double.POSITIVE_INFINITY;
                }

                total += loss;
            }

            return total / actual.size();
        }
    }

    private static ProbabilityDistribution distribution(
            String name,
            double... values
    ) {
        Map<String, Double> map = new LinkedHashMap<>();

        for (int i = 0; i < values.length; i++) {
            map.put("class_" + i, values[i]);
        }

        return new ProbabilityDistribution(name, map);
    }

    private static void runTests(EntropyService service) {
        var uniform = distribution("uniform", 0.5, 0.5);

        if (Math.abs(service.entropy(uniform) - 1.0) > EPSILON) {
            throw new AssertionError("Uniform entropy test failed.");
        }

        if (Math.abs(service.binaryEntropy(0.5) - 1.0) > EPSILON) {
            throw new AssertionError("Binary entropy test failed.");
        }

        var p = distribution("p", 0.5, 0.3, 0.2);
        var q = distribution("q", 0.4, 0.4, 0.2);

        var result = service.evaluate(
                p,
                q,
                EvaluationPolicy.standard()
        );

        if (!result.identityVerified()) {
            throw new AssertionError(
                    "Cross-entropy identity failed."
            );
        }

        if (service.klDivergence(p, p) > EPSILON) {
            throw new AssertionError(
                    "KL identity failed."
            );
        }

        var joint = new JointDistribution(
                new double[][]{
                        {0.4, 0.1},
                        {0.1, 0.4}
                }
        );

        if (joint.mutualInformation() <= 0.0) {
            throw new AssertionError(
                    "Mutual information test failed."
            );
        }

        var smoothed = service.smooth(
                distribution("sparse", 1.0, 0.0),
                0.1
        );

        if (smoothed.probability("class_1") <= 0.0) {
            throw new AssertionError(
                    "Smoothing test failed."
            );
        }

        System.out.println("All tests passed.");
    }

    public static void main(String[] args) {
        try {
            EntropyService service = new EntropyService();

            ProbabilityDistribution actual =
                    distribution(
                            "observed_classes",
                            0.50, 0.30, 0.20
                    );

            ProbabilityDistribution predicted =
                    distribution(
                            "predicted_classes",
                            0.40, 0.40, 0.20
                    );

            EvaluationResult result = service.evaluate(
                    actual,
                    predicted,
                    EvaluationPolicy.standard()
            );

            System.out.println(
                    "ENTROPY AND CROSS-ENTROPY ANALYTICS"
            );

            System.out.println("-----------------------------------");

            System.out.printf(
                    "Shannon entropy: %.6f bits%n",
                    result.entropy()
            );

            System.out.printf(
                    "Cross-entropy: %.6f bits%n",
                    result.crossEntropy()
            );

            System.out.printf(
                    "KL divergence: %.6f bits%n",
                    result.klDivergence()
            );

            System.out.println("Status: " + result.status());

            System.out.println(
                    "Identity verified: " +
                            result.identityVerified()
            );

            System.out.println("\nBINARY ENTROPY");

            for (double p :
                    new double[]{0, 0.1, 0.25, 0.5, 0.75, 1}) {
                System.out.printf(
                        "p=%.2f H(X)=%.6f bits%n",
                        p,
                        service.binaryEntropy(p)
                );
            }

            System.out.println("\nJOINT DISTRIBUTION");

            JointDistribution joint = new JointDistribution(
                    new double[][]{
                            {0.4, 0.1},
                            {0.1, 0.4}
                    }
            );

            System.out.printf(
                    "H(X,Y): %.6f%n",
                    joint.jointEntropy()
            );

            System.out.printf(
                    "H(X): %.6f%n",
                    joint.entropyX()
            );

            System.out.printf(
                    "H(Y): %.6f%n",
                    joint.entropyY()
            );

            System.out.printf(
                    "H(Y|X): %.6f%n",
                    joint.conditionalEntropyYGivenX()
            );

            System.out.printf(
                    "I(X;Y): %.6f%n",
                    joint.mutualInformation()
            );

            System.out.println("\nCLASSIFICATION");

            ClassificationService classifier =
                    new ClassificationService(service);

            System.out.printf(
                    "Negative log-likelihood: %.6f bits%n",
                    classifier.negativeLogLikelihood(
                            "class_1",
                            distribution(
                                    "classifier",
                                    0.15, 0.70, 0.15
                            )
                    )
            );

            System.out.println("\nPROBABILITY SMOOTHING");

            System.out.println(
                    service.smooth(
                            distribution("sparse", 1.0, 0.0, 0.0),
                            0.1
                    ).probabilities()
            );

            System.out.println("\nVALIDATION");

            runTests(service);

        } catch (ProbabilityException exception) {
            System.err.println(
                    "Validation failure: " + exception.getMessage()
            );
            System.exit(1);
        }
    }
}
