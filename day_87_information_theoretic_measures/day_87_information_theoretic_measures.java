import java.util.*;
import java.util.stream.Collectors;

/*
 * Information-Theoretic Measures
 *
 * Enterprise-oriented categorical feature analysis.
 *
 * Java 17
 * Standard library only.
 *
 * Implements:
 * - Shannon entropy
 * - Conditional entropy
 * - Joint entropy
 * - Mutual information
 * - Information gain
 * - Normalized mutual information
 * - Feature ranking
 * - Feature selection
 * - Immutable domain records
 * - Analysis service
 * - Validation and failure handling
 */

public class InformationTheoryEnterprise {

    private static final double EPSILON = 1e-12;

    public enum Measure {
        ENTROPY,
        CONDITIONAL_ENTROPY,
        JOINT_ENTROPY,
        MUTUAL_INFORMATION,
        INFORMATION_GAIN,
        NORMALIZED_MUTUAL_INFORMATION
    }

    public enum AnalysisStatus {
        CREATED,
        VALIDATED,
        COMPLETED,
        FAILED
    }

    public static class InformationTheoryException
            extends RuntimeException {

        public InformationTheoryException(String message) {
            super(message);
        }
    }

    public static class ValidationException
            extends InformationTheoryException {

        public ValidationException(String message) {
            super(message);
        }
    }

    public record ProbabilityEntry(
            String category,
            long count,
            double probability
    ) {

        public ProbabilityEntry {
            Objects.requireNonNull(category);

            if (count < 0) {
                throw new ValidationException(
                    "Count cannot be negative."
                );
            }

            if (
                !Double.isFinite(probability) ||
                probability < 0 ||
                probability > 1
            ) {
                throw new ValidationException(
                    "Invalid probability."
                );
            }
        }
    }

    public record FeatureScore(
            String feature,
            double targetEntropy,
            double conditionalEntropy,
            double mutualInformation,
            double informationGain,
            double normalizedMutualInformation
    ) {

        public FeatureScore {
            Objects.requireNonNull(feature);

            if (
                !Double.isFinite(informationGain) ||
                informationGain < -EPSILON
            ) {
                throw new ValidationException(
                    "Invalid information gain."
                );
            }
        }
    }

    public record AnalysisReport(
            String datasetName,
            int observationCount,
            double targetEntropy,
            List<FeatureScore> scores,
            AnalysisStatus status
    ) {

        public AnalysisReport {
            Objects.requireNonNull(datasetName);
            Objects.requireNonNull(scores);
            Objects.requireNonNull(status);

            scores = List.copyOf(scores);

            if (observationCount <= 0) {
                throw new ValidationException(
                    "Observation count must be positive."
                );
            }
        }
    }

    public record Dataset(
            String name,
            List<String> target,
            Map<String, List<String>> features
    ) {

        public Dataset {
            if (name == null || name.isBlank()) {
                throw new ValidationException(
                    "Dataset name cannot be empty."
                );
            }

            target = List.copyOf(
                Objects.requireNonNull(target)
            );

            if (target.isEmpty()) {
                throw new ValidationException(
                    "Target cannot be empty."
                );
            }

            Map<String, List<String>> copied =
                new LinkedHashMap<>();

            Objects.requireNonNull(features).forEach(
                (feature, values) -> {

                    if (
                        feature == null ||
                        feature.isBlank() ||
                        values == null
                    ) {
                        throw new ValidationException(
                            "Invalid feature definition."
                        );
                    }

                    List<String> immutableValues =
                        List.copyOf(values);

                    if (
                        immutableValues.size() != target.size()
                    ) {
                        throw new ValidationException(
                            "Feature dimensions do not match target."
                        );
                    }

                    copied.put(
                        feature,
                        immutableValues
                    );
                }
            );

            if (copied.isEmpty()) {
                throw new ValidationException(
                    "Dataset requires at least one feature."
                );
            }

            features = Collections.unmodifiableMap(copied);
        }
    }

    public static final class ProbabilityModel {

        private final Map<String, Double> probabilities;

        public ProbabilityModel(
                Map<String, Double> probabilities
        ) {

            if (
                probabilities == null ||
                probabilities.isEmpty()
            ) {
                throw new ValidationException(
                    "Probability model cannot be empty."
                );
            }

            Map<String, Double> copy =
                new LinkedHashMap<>();

            double total = 0;

            for (var entry : probabilities.entrySet()) {

                String category = entry.getKey();
                Double probability = entry.getValue();

                if (
                    category == null ||
                    probability == null ||
                    !Double.isFinite(probability) ||
                    probability < 0
                ) {
                    throw new ValidationException(
                        "Invalid probability entry."
                    );
                }

                copy.put(category, probability);
                total += probability;
            }

            if (Math.abs(total - 1.0) > EPSILON) {
                throw new ValidationException(
                    "Probability values must sum to 1."
                );
            }

            this.probabilities =
                Collections.unmodifiableMap(copy);
        }

        public Map<String, Double> probabilities() {
            return probabilities;
        }
    }

    public static final class InformationCalculator {

        private InformationCalculator() {}

        private static void validateBase(double base) {

            if (
                !Double.isFinite(base) ||
                base <= 0 ||
                Math.abs(base - 1.0) < EPSILON
            ) {
                throw new ValidationException(
                    "Invalid logarithm base."
                );
            }
        }

        private static void validateColumns(
                List<String> first,
                List<String> second
        ) {

            if (
                first == null ||
                second == null ||
                first.isEmpty() ||
                first.size() != second.size()
            ) {
                throw new ValidationException(
                    "Columns must be non-empty and equally sized."
                );
            }

            if (
                first.stream().anyMatch(Objects::isNull) ||
                second.stream().anyMatch(Objects::isNull)
            ) {
                throw new ValidationException(
                    "Null observations are not supported."
                );
            }
        }

        public static Map<String, Long> counts(
                List<String> values
        ) {

            if (
                values == null ||
                values.isEmpty() ||
                values.stream().anyMatch(Objects::isNull)
            ) {
                throw new ValidationException(
                    "Invalid categorical observations."
                );
            }

            return values.stream().collect(
                Collectors.groupingBy(
                    value -> value,
                    LinkedHashMap::new,
                    Collectors.counting()
                )
            );
        }

        public static double entropy(
                List<String> values
        ) {

            return entropy(values, 2.0);
        }

        public static double entropy(
                List<String> values,
                double base
        ) {

            validateBase(base);

            Map<String, Long> frequencies =
                counts(values);

            double total = values.size();
            double result = 0;

            for (long count : frequencies.values()) {

                double probability = count / total;

                result -= probability *
                    Math.log(probability) / Math.log(base);
            }

            return result;
        }

        public static double jointEntropy(
                List<String> x,
                List<String> y
        ) {

            validateColumns(x, y);

            List<String> joint = new ArrayList<>();

            for (int i = 0; i < x.size(); i++) {

                // Length-prefixing avoids ambiguous concatenation.
                String a = x.get(i);
                String b = y.get(i);

                joint.add(
                    a.length() + ":" + a +
                    b.length() + ":" + b
                );
            }

            return entropy(joint);
        }

        public static double conditionalEntropy(
                List<String> target,
                List<String> condition
        ) {

            validateColumns(target, condition);

            Map<String, List<String>> groups =
                new HashMap<>();

            for (int i = 0; i < target.size(); i++) {

                groups.computeIfAbsent(
                    condition.get(i),
                    ignored -> new ArrayList<>()
                ).add(target.get(i));
            }

            double result = 0;
            double total = target.size();

            for (List<String> group : groups.values()) {

                double weight = group.size() / total;

                result += weight * entropy(group);
            }

            return result;
        }

        public static double mutualInformation(
                List<String> x,
                List<String> y
        ) {

            validateColumns(x, y);

            return Math.max(
                0,
                entropy(y) - conditionalEntropy(y, x)
            );
        }

        public static double informationGain(
                List<String> target,
                List<String> feature
        ) {

            return mutualInformation(feature, target);
        }

        public static double normalizedMutualInformation(
                List<String> x,
                List<String> y
        ) {

            validateColumns(x, y);

            double hx = entropy(x);
            double hy = entropy(y);

            if (hx + hy <= EPSILON) {
                return 1.0;
            }

            return 2 * mutualInformation(x, y) /
                (hx + hy);
        }

        public static double conditionalMutualInformation(
                List<String> x,
                List<String> y,
                List<String> z
        ) {

            validateColumns(x, y);
            validateColumns(x, z);

            if (
                x.size() != y.size() ||
                x.size() != z.size()
            ) {
                throw new ValidationException(
                    "All three columns must have equal lengths."
                );
            }

            Map<String, List<String>> yzGroups =
                new HashMap<>();

            Map<String, List<String>> xzGroups =
                new HashMap<>();

            for (int i = 0; i < x.size(); i++) {

                String zValue = z.get(i);

                yzGroups.computeIfAbsent(
                    zValue,
                    ignored -> new ArrayList<>()
                ).add(y.get(i));

                String xzKey =
                    x.get(i).length() + ":" + x.get(i) +
                    zValue.length() + ":" + zValue;

                xzGroups.computeIfAbsent(
                    xzKey,
                    ignored -> new ArrayList<>()
                ).add(y.get(i));
            }

            double hYGivenZ = conditionalEntropy(y, z);

            double hYGivenXZ = 0;
            double total = x.size();

            for (List<String> group : xzGroups.values()) {
                hYGivenXZ +=
                    group.size() / total * entropy(group);
            }

            return Math.max(
                0,
                hYGivenZ - hYGivenXZ
            );
        }
    }

    public static final class FeatureAnalysisService {

        private final Dataset dataset;

        public FeatureAnalysisService(Dataset dataset) {
            this.dataset = Objects.requireNonNull(dataset);
        }

        public AnalysisReport analyze() {

            double targetEntropy =
                InformationCalculator.entropy(dataset.target());

            List<FeatureScore> scores =
                new ArrayList<>();

            for (
                Map.Entry<String, List<String>> entry :
                dataset.features().entrySet()
            ) {

                String featureName = entry.getKey();
                List<String> feature = entry.getValue();

                double conditional =
                    InformationCalculator.conditionalEntropy(
                        dataset.target(),
                        feature
                    );

                double mutualInformation =
                    InformationCalculator.mutualInformation(
                        feature,
                        dataset.target()
                    );

                double gain = Math.max(
                    0,
                    targetEntropy - conditional
                );

                double nmi =
                    InformationCalculator.normalizedMutualInformation(
                        feature,
                        dataset.target()
                    );

                scores.add(
                    new FeatureScore(
                        featureName,
                        targetEntropy,
                        conditional,
                        mutualInformation,
                        gain,
                        nmi
                    )
                );
            }

            scores.sort(
                Comparator
                    .comparingDouble(
                        FeatureScore::informationGain
                    )
                    .reversed()
                    .thenComparing(FeatureScore::feature)
            );

            return new AnalysisReport(
                dataset.name(),
                dataset.target().size(),
                targetEntropy,
                scores,
                AnalysisStatus.COMPLETED
            );
        }

        public List<String> selectFeatures(
                double minimumGain
        ) {

            if (
                !Double.isFinite(minimumGain) ||
                minimumGain < 0
            ) {
                throw new ValidationException(
                    "Minimum gain must be non-negative."
                );
            }

            return analyze().scores().stream()
                .filter(
                    score ->
                        score.informationGain() >= minimumGain
                )
                .map(FeatureScore::feature)
                .toList();
        }
    }

    private static Dataset createExampleDataset() {

        List<String> target = List.of(
            "No", "No", "Yes", "Yes",
            "Yes", "No", "Yes", "No",
            "Yes", "Yes", "Yes", "Yes",
            "Yes", "No"
        );

        Map<String, List<String>> features =
            new LinkedHashMap<>();

        features.put(
            "Outlook",
            List.of(
                "Sunny", "Sunny", "Overcast", "Rain",
                "Rain", "Rain", "Overcast", "Sunny",
                "Sunny", "Rain", "Sunny", "Overcast",
                "Overcast", "Rain"
            )
        );

        features.put(
            "Temperature",
            List.of(
                "Hot", "Hot", "Hot", "Mild",
                "Cool", "Cool", "Cool", "Mild",
                "Cool", "Mild", "Mild", "Mild",
                "Hot", "Mild"
            )
        );

        features.put(
            "Humidity",
            List.of(
                "High", "High", "High", "High",
                "Normal", "Normal", "Normal", "High",
                "Normal", "Normal", "Normal", "High",
                "Normal", "High"
            )
        );

        features.put(
            "Wind",
            List.of(
                "Weak", "Strong", "Weak", "Weak",
                "Weak", "Strong", "Strong", "Weak",
                "Weak", "Weak", "Strong", "Strong",
                "Weak", "Strong"
            )
        );

        return new Dataset(
            "Weather Classification",
            target,
            features
        );
    }

    private static void runTests() {

        List<String> x = List.of("0", "0", "1", "1");
        List<String> y = List.of("0", "0", "1", "1");

        if (
            Math.abs(
                InformationCalculator.entropy(x) - 1.0
            ) > EPSILON
        ) {
            throw new AssertionError("Entropy test failed.");
        }

        if (
            Math.abs(
                InformationCalculator.mutualInformation(x, y)
                - 1.0
            ) > EPSILON
        ) {
            throw new AssertionError("MI test failed.");
        }

        if (
            Math.abs(
                InformationCalculator.conditionalEntropy(y, x)
            ) > EPSILON
        ) {
            throw new AssertionError(
                "Conditional entropy test failed."
            );
        }

        List<String> independent =
            List.of("0", "1", "0", "1");

        if (
            Math.abs(
                InformationCalculator.mutualInformation(
                    x,
                    independent
                )
            ) > EPSILON
        ) {
            throw new AssertionError(
                "Independence test failed."
            );
        }

        if (
            Math.abs(
                InformationCalculator.jointEntropy(x, y) - 1
            ) > EPSILON
        ) {
            throw new AssertionError(
                "Joint entropy test failed."
            );
        }

        boolean failedCorrectly = false;

        try {
            new ProbabilityModel(
                Map.of("A", 0.8, "B", 0.8)
            );
        } catch (ValidationException expected) {
            failedCorrectly = true;
        }

        if (!failedCorrectly) {
            throw new AssertionError(
                "Invalid probability model was accepted."
            );
        }

        System.out.println(
            "All mathematical and domain validation tests passed."
        );
    }

    private static void printReport(
            AnalysisReport report
    ) {

        System.out.println("\nENTERPRISE INFORMATION ANALYSIS");
        System.out.println("Dataset: " + report.datasetName());
        System.out.println(
            "Observations: " + report.observationCount()
        );
        System.out.printf(
            "Target entropy: %.5f bits%n",
            report.targetEntropy()
        );

        System.out.println(
            "\nFeature               H(Y)       H(Y|X)       MI       IG       NMI"
        );

        System.out.println(
            "-----------------------------------------------------------------------"
        );

        for (FeatureScore score : report.scores()) {

            System.out.printf(
                "%-18s %8.5f %11.5f %9.5f %8.5f %8.5f%n",
                score.feature(),
                score.targetEntropy(),
                score.conditionalEntropy(),
                score.mutualInformation(),
                score.informationGain(),
                score.normalizedMutualInformation()
            );
        }

        if (!report.scores().isEmpty()) {

            System.out.println(
                "\nBest initial split: " +
                report.scores().getFirst().feature()
            );
        }
    }

    public static void main(String[] args) {

        try {

            runTests();

            Dataset dataset = createExampleDataset();

            FeatureAnalysisService service =
                new FeatureAnalysisService(dataset);

            AnalysisReport report = service.analyze();

            printReport(report);

            System.out.println(
                "\nSelected features: " +
                service.selectFeatures(0.05)
            );

            double conditionalMI =
                InformationCalculator.conditionalMutualInformation(
                    List.of("A", "A", "B", "B"),
                    List.of("X", "Y", "X", "Y"),
                    List.of("Z", "Z", "W", "W")
                );

            System.out.printf(
                "Conditional mutual information: %.5f bits%n",
                conditionalMI
            );

        } catch (InformationTheoryException exception) {

            System.err.println(
                "Domain error: " + exception.getMessage()
            );

            System.exit(1);

        } catch (Exception exception) {

            System.err.println(
                "Unexpected execution failure: " +
                exception.getMessage()
            );

            System.exit(2);
        }
    }
}
