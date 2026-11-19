import java.util.*;
import java.util.function.ToDoubleFunction;

/*
 * Statistical Estimation Enterprise Engine
 *
 * Java 17 implementation:
 * - Immutable estimation records
 * - Point estimation
 * - Confidence intervals
 * - Normal and Student's t distributions
 * - Wilson proportion intervals
 * - Bootstrap estimation
 * - Maximum likelihood estimation
 * - Estimator evaluation and governance
 * - Validation and explicit failure handling
 */

public class StatisticalEstimation {

    enum EstimationMethod {
        ARITHMETIC_MEAN,
        UNBIASED_VARIANCE,
        MAXIMUM_LIKELIHOOD,
        NORMAL_INTERVAL,
        STUDENT_T_INTERVAL,
        WILSON_INTERVAL,
        BOOTSTRAP
    }

    enum EstimationStatus {
        COMPLETED,
        REJECTED,
        FAILED
    }

    static class EstimationException extends RuntimeException {
        public EstimationException(String message) {
            super(message);
        }
    }

    record PointEstimate(
        String parameter,
        double value,
        int sampleSize,
        EstimationMethod method
    ) {
        public PointEstimate {
            Objects.requireNonNull(parameter);
            Objects.requireNonNull(method);

            if (!Double.isFinite(value) || sampleSize < 1) {
                throw new EstimationException(
                    "Invalid point estimate."
                );
            }
        }
    }

    record ConfidenceInterval(
        String parameter,
        double estimate,
        double lower,
        double upper,
        double confidence,
        EstimationMethod method
    ) {
        public ConfidenceInterval {
            Objects.requireNonNull(parameter);
            Objects.requireNonNull(method);

            if (
                !Double.isFinite(lower)
                || !Double.isFinite(upper)
                || lower > upper
                || !(confidence > 0 && confidence < 1)
            ) {
                throw new EstimationException(
                    "Invalid confidence interval."
                );
            }
        }

        double width() {
            return upper - lower;
        }

        boolean contains(double value) {
            return value >= lower && value <= upper;
        }
    }

    record EstimatorEvaluation(
        String name,
        int repetitions,
        double trueValue,
        double average,
        double bias,
        double variance,
        double mse
    ) {}

    record EstimationEvent(
        String requestId,
        EstimationStatus status,
        String description,
        InstantWrapper timestamp
    ) {}

    record InstantWrapper(String value) {}

    interface Estimator {
        PointEstimate estimate(List<Double> observations);
    }

    interface EstimationPolicy {
        void validate(List<Double> observations);
    }

    static final class DefaultEstimationPolicy
        implements EstimationPolicy {

        @Override
        public void validate(List<Double> observations) {
            if (observations == null || observations.isEmpty()) {
                throw new EstimationException(
                    "Observation set cannot be empty."
                );
            }

            for (Double value : observations) {
                if (value == null || !Double.isFinite(value)) {
                    throw new EstimationException(
                        "Observations must be finite numbers."
                    );
                }
            }
        }
    }

    static final class EstimationService {

        private final EstimationPolicy policy;

        private final Map<String, PointEstimate> auditLog =
            new LinkedHashMap<>();

        EstimationService(EstimationPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        PointEstimate estimate(
            String requestId,
            String estimatorName,
            Estimator estimator,
            List<Double> observations
        ) {
            if (
                requestId == null || requestId.isBlank()
                || estimatorName == null || estimatorName.isBlank()
            ) {
                throw new EstimationException(
                    "Request and estimator identifiers are required."
                );
            }

            Objects.requireNonNull(estimator);

            policy.validate(observations);

            if (auditLog.containsKey(requestId)) {
                throw new EstimationException(
                    "Duplicate estimation request identifier."
                );
            }

            PointEstimate result = estimator.estimate(
                List.copyOf(observations)
            );

            auditLog.put(requestId, result);

            return result;
        }

        Map<String, PointEstimate> auditLog() {
            return Collections.unmodifiableMap(auditLog);
        }
    }

    static List<Double> validate(List<Double> data) {
        new DefaultEstimationPolicy().validate(data);
        return List.copyOf(data);
    }

    static double mean(List<Double> data) {
        List<Double> values = validate(data);

        double sum = 0;

        for (double value : values) {
            sum += value;
        }

        return sum / values.size();
    }

    static double variance(
        List<Double> data,
        boolean unbiased
    ) {
        List<Double> values = validate(data);

        if (unbiased && values.size() < 2) {
            throw new EstimationException(
                "At least two observations are required."
            );
        }

        double average = mean(values);

        double sum = 0;

        for (double value : values) {
            sum += Math.pow(value - average, 2);
        }

        return sum / (
            unbiased ? values.size() - 1 : values.size()
        );
    }

    static double standardDeviation(List<Double> data) {
        return Math.sqrt(variance(data, true));
    }

    static double proportion(List<Integer> data) {
        if (data == null || data.isEmpty()) {
            throw new EstimationException(
                "Binary observations cannot be empty."
            );
        }

        long successes = 0;

        for (Integer value : data) {
            if (value == null || (value != 0 && value != 1)) {
                throw new EstimationException(
                    "Proportion estimation requires binary data."
                );
            }

            successes += value;
        }

        return (double) successes / data.size();
    }

    static double normalQuantile(double p) {
        if (!(p > 0 && p < 1)) {
            throw new EstimationException("Invalid probability.");
        }

        double[] a = {
            -39.69683028665376,
            220.9460984245205,
            -275.9285104469687,
            138.3577518672690,
            -30.66479806614716,
            2.506628277459239
        };

        double[] b = {
            -54.47609879822406,
            161.5858368580409,
            -155.6989798598866,
            66.80131188771972,
            -13.28068155288572
        };

        double[] c = {
            -0.007784894002430293,
            -0.3223964580411365,
            -2.400758277161838,
            -2.549732539343734,
            4.374664141464968,
            2.938163982698783
        };

        double[] d = {
            0.007784695709041462,
            0.3224671290700398,
            2.445134137142996,
            3.754408661907416
        };

        double low = 0.02425;
        double high = 1 - low;

        if (p < low || p > high) {
            double q = Math.sqrt(
                -2 * Math.log(p < low ? p : 1 - p)
            );

            double numerator = 0;
            double denominator = 1;

            for (int i = 0; i < 6; i++) {
                numerator += c[i] * Math.pow(q, 5 - i);
            }

            for (int i = 0; i < 4; i++) {
                denominator += d[i] * Math.pow(q, 3 - i);
            }

            double result = numerator / denominator;

            return p < low ? result : -result;
        }

        double q = p - 0.5;
        double r = q * q;

        double numerator = 0;
        double denominator = 1;

        for (int i = 0; i < 6; i++) {
            numerator += a[i] * q * Math.pow(r, 2 - i);
        }

        for (int i = 0; i < 5; i++) {
            denominator += b[i] * Math.pow(r, 2 - i);
        }

        return numerator / denominator;
    }

    static double betaFraction(
        double a,
        double b,
        double x
    ) {
        double tiny = 1e-300;
        double qab = a + b;
        double qap = a + 1;
        double qam = a - 1;

        double c = 1;
        double d = 1 - qab * x / qap;

        if (Math.abs(d) < tiny) d = tiny;

        d = 1 / d;

        double h = d;

        for (int m = 1; m <= 300; m++) {
            int m2 = 2 * m;

            double aa = m * (b - m) * x
                / ((qam + m2) * (a + m2));

            d = 1 + aa * d;
            if (Math.abs(d) < tiny) d = tiny;

            c = 1 + aa / c;
            if (Math.abs(c) < tiny) c = tiny;

            d = 1 / d;
            h *= d * c;

            aa = -(a + m) * (qab + m) * x
                / ((a + m2) * (qap + m2));

            d = 1 + aa * d;
            if (Math.abs(d) < tiny) d = tiny;

            c = 1 + aa / c;
            if (Math.abs(c) < tiny) c = tiny;

            d = 1 / d;

            double delta = d * c;
            h *= delta;

            if (Math.abs(delta - 1) < 3e-14) {
                return h;
            }
        }

        throw new EstimationException(
            "Incomplete beta did not converge."
        );
    }

    static double regularizedBeta(
        double x,
        double a,
        double b
    ) {
        if (x <= 0) return 0;
        if (x >= 1) return 1;

        double logBt =
            logGamma(a + b)
            - logGamma(a)
            - logGamma(b)
            + a * Math.log(x)
            + b * Math.log1p(-x);

        double bt = Math.exp(logBt);

        if (x < (a + 1) / (a + b + 2)) {
            return bt * betaFraction(a, b, x) / a;
        }

        return 1 - bt * betaFraction(b, a, 1 - x) / b;
    }

    static double logGamma(double z) {
        double[] coefficients = {
            676.5203681218851,
            -1259.1392167224028,
            771.3234287776531,
            -176.6150291621406,
            12.507343278686905,
            -0.13857109526572012,
            9.984369578019572e-6,
            1.5056327351493116e-7
        };

        if (z < 0.5) {
            return Math.log(Math.PI)
                - Math.log(Math.sin(Math.PI * z))
                - logGamma(1 - z);
        }

        z -= 1;

        double x = 0.99999999999980993;

        for (int i = 0; i < coefficients.length; i++) {
            x += coefficients[i] / (z + i + 1);
        }

        double t = z + coefficients.length - 0.5;

        return 0.5 * Math.log(2 * Math.PI)
            + (z + 0.5) * Math.log(t)
            - t
            + Math.log(x);
    }

    static double studentTCDF(double t, int degrees) {
        double x = degrees / (degrees + t * t);

        double beta = regularizedBeta(
            x,
            degrees / 2.0,
            0.5
        );

        return t >= 0 ? 1 - beta / 2 : beta / 2;
    }

    static double studentTQuantile(double p, int degrees) {
        if (degrees < 1 || !(p > 0 && p < 1)) {
            throw new EstimationException(
                "Invalid Student's t parameters."
            );
        }

        if (p == 0.5) return 0;

        if (p < 0.5) {
            return -studentTQuantile(1 - p, degrees);
        }

        double lower = 0;
        double upper = 1;

        while (studentTCDF(upper, degrees) < p) {
            upper *= 2;

            if (upper > 1e12) {
                throw new EstimationException(
                    "Unable to bracket t quantile."
                );
            }
        }

        for (int i = 0; i < 150; i++) {
            double middle = (lower + upper) / 2;

            if (studentTCDF(middle, degrees) < p) {
                lower = middle;
            } else {
                upper = middle;
            }
        }

        return (lower + upper) / 2;
    }

    static ConfidenceInterval meanInterval(
        List<Double> data,
        double confidence,
        boolean useStudentT
    ) {
        List<Double> values = validate(data);

        if (!(confidence > 0 && confidence < 1)) {
            throw new EstimationException(
                "Invalid confidence level."
            );
        }

        if (values.size() < 2) {
            throw new EstimationException(
                "At least two observations are required."
            );
        }

        double estimate = mean(values);

        double standardError = standardDeviation(values)
            / Math.sqrt(values.size());

        double critical = useStudentT
            ? studentTQuantile(
                (1 + confidence) / 2,
                values.size() - 1
            )
            : normalQuantile((1 + confidence) / 2);

        double margin = critical * standardError;

        return new ConfidenceInterval(
            "population_mean",
            estimate,
            estimate - margin,
            estimate + margin,
            confidence,
            useStudentT
                ? EstimationMethod.STUDENT_T_INTERVAL
                : EstimationMethod.NORMAL_INTERVAL
        );
    }

    static ConfidenceInterval wilsonInterval(
        List<Integer> data,
        double confidence
    ) {
        if (!(confidence > 0 && confidence < 1)) {
            throw new EstimationException(
                "Invalid confidence level."
            );
        }

        double p = proportion(data);
        double n = data.size();

        double z = normalQuantile((1 + confidence) / 2);
        double z2 = z * z;

        double denominator = 1 + z2 / n;

        double center = (
            p + z2 / (2 * n)
        ) / denominator;

        double margin = z * Math.sqrt(
            p * (1 - p) / n + z2 / (4 * n * n)
        ) / denominator;

        return new ConfidenceInterval(
            "population_proportion",
            p,
            Math.max(0, center - margin),
            Math.min(1, center + margin),
            confidence,
            EstimationMethod.WILSON_INTERVAL
        );
    }

    static ConfidenceInterval bootstrapInterval(
        List<Double> data,
        double confidence,
        int repetitions,
        long seed
    ) {
        List<Double> values = validate(data);

        if (!(confidence > 0 && confidence < 1)) {
            throw new EstimationException(
                "Invalid confidence level."
            );
        }

        if (repetitions < 100) {
            throw new EstimationException(
                "At least 100 repetitions are required."
            );
        }

        Random random = new Random(seed);

        List<Double> estimates = new ArrayList<>(repetitions);

        for (int i = 0; i < repetitions; i++) {
            List<Double> sample = new ArrayList<>(values.size());

            for (int j = 0; j < values.size(); j++) {
                sample.add(
                    values.get(random.nextInt(values.size()))
                );
            }

            estimates.add(mean(sample));
        }

        Collections.sort(estimates);

        double alpha = 1 - confidence;

        int lowerIndex = (int) Math.floor(
            alpha / 2 * repetitions
        );

        int upperIndex = Math.min(
            repetitions - 1,
            (int) Math.floor(
                (1 - alpha / 2) * repetitions
            )
        );

        return new ConfidenceInterval(
            "population_mean",
            mean(values),
            estimates.get(lowerIndex),
            estimates.get(upperIndex),
            confidence,
            EstimationMethod.BOOTSTRAP
        );
    }

    static PointEstimate exponentialMLE(List<Double> data) {
        List<Double> values = validate(data);

        for (double value : values) {
            if (value < 0) {
                throw new EstimationException(
                    "Exponential observations cannot be negative."
                );
            }
        }

        double average = mean(values);

        if (average <= 0) {
            throw new EstimationException(
                "MLE is undefined for an all-zero sample."
            );
        }

        return new PointEstimate(
            "exponential_rate",
            1 / average,
            values.size(),
            EstimationMethod.MAXIMUM_LIKELIHOOD
        );
    }

    static EstimatorEvaluation evaluateMean(
        double trueValue,
        int repetitions,
        int sampleSize,
        long seed
    ) {
        if (
            !Double.isFinite(trueValue)
            || repetitions < 2
            || sampleSize < 1
        ) {
            throw new EstimationException(
                "Invalid simulation parameters."
            );
        }

        Random random = new Random(seed);

        List<Double> estimates = new ArrayList<>(repetitions);

        for (int i = 0; i < repetitions; i++) {
            List<Double> sample = new ArrayList<>(sampleSize);

            for (int j = 0; j < sampleSize; j++) {
                sample.add(
                    trueValue + 2 * random.nextGaussian()
                );
            }

            estimates.add(mean(sample));
        }

        double average = mean(estimates);

        double bias = average - trueValue;

        double estimatorVariance = variance(estimates, false);

        double mse = estimates.stream()
            .mapToDouble(value -> Math.pow(value - trueValue, 2))
            .average()
            .orElseThrow();

        return new EstimatorEvaluation(
            "sample_mean",
            repetitions,
            trueValue,
            average,
            bias,
            estimatorVariance,
            mse
        );
    }

    static void runTests() {
        List<Double> sample = List.of(10.0, 12.0, 13.0, 15.0, 16.0);

        assert Math.abs(mean(sample) - 13.2) < 1e-9;

        assert Math.abs(variance(sample, true) - 5.7) < 1e-9;

        ConfidenceInterval interval = meanInterval(
            sample,
            0.95,
            true
        );

        assert interval.contains(13.2);

        assert Math.abs(
            proportion(List.of(1, 0, 1, 1)) - 0.75
        ) < 1e-9;

        assert studentTQuantile(0.975, 9) > 2.2;
        assert studentTQuantile(0.975, 9) < 2.3;

        boolean rejected = false;

        try {
            variance(List.of(5.0), true);
        } catch (EstimationException exception) {
            rejected = true;
        }

        assert rejected;

        System.out.println("All Java tests passed.");
    }

    public static void main(String[] args) {
        try {
            List<Double> observations = List.of(
                48.2, 51.1, 49.5, 52.3, 47.8,
                50.6, 53.0, 49.9, 51.7, 48.9,
                52.1, 50.3
            );

            System.out.println("\nSTATISTICAL ESTIMATION");
            System.out.println("==============================");

            EstimationService service = new EstimationService(
                new DefaultEstimationPolicy()
            );

            PointEstimate estimate = service.estimate(
                "REQ-001",
                "arithmetic_mean",
                data -> new PointEstimate(
                    "population_mean",
                    mean(data),
                    data.size(),
                    EstimationMethod.ARITHMETIC_MEAN
                ),
                observations
            );

            System.out.println("\nPOINT ESTIMATION");
            System.out.println(estimate);

            System.out.println("\nVARIANCE ESTIMATION");

            System.out.println(
                new PointEstimate(
                    "population_variance",
                    variance(observations, true),
                    observations.size(),
                    EstimationMethod.UNBIASED_VARIANCE
                )
            );

            System.out.println("\nINTERVAL ESTIMATION");

            System.out.println(
                meanInterval(observations, 0.95, true)
            );

            System.out.println(
                meanInterval(observations, 0.95, false)
            );

            System.out.println(
                bootstrapInterval(
                    observations,
                    0.95,
                    5000,
                    42
                )
            );

            System.out.println("\nPROPORTION ESTIMATION");

            List<Integer> outcomes = List.of(
                1, 1, 0, 1, 0, 1, 1, 0, 1, 1,
                0, 1, 0, 1, 1, 1, 0, 1, 0, 1
            );

            System.out.println(
                "Proportion: " + proportion(outcomes)
            );

            System.out.println(
                wilsonInterval(outcomes, 0.95)
            );

            System.out.println("\nMAXIMUM LIKELIHOOD");

            System.out.println(
                exponentialMLE(
                    List.of(1.2, 0.8, 2.1, 1.5, 0.9, 1.7)
                )
            );

            System.out.println("\nESTIMATOR EVALUATION");

            System.out.println(
                evaluateMean(50.0, 2000, 30, 42)
            );

            System.out.println("\nAUDIT RECORDS");

            System.out.println(service.auditLog());

            runTests();

        } catch (EstimationException exception) {
            System.err.println(
                "Estimation rejected: " + exception.getMessage()
            );

            System.exit(1);
        } catch (Exception exception) {
            System.err.println(
                "Unexpected failure: " + exception.getMessage()
            );

            System.exit(2);
        }
    }
}
