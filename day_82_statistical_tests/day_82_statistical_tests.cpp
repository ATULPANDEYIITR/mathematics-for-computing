#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

class StatisticalError : public runtime_error {
public:
    explicit StatisticalError(const string& message)
        : runtime_error(message) {}
};

enum class TestCategory {
    T_TEST,
    Z_TEST,
    CHI_SQUARE,
    ANOVA
};

struct TestResult {
    string name;
    double statistic;
    double pValue;
    double degreesOfFreedom;
    double alpha;
    double effectSize;
    bool hasEffectSize;

    bool rejectNull() const {
        return pValue < alpha;
    }
};

class StatisticalEngine {
private:
    static constexpr double EPS = 1e-300;

    static void validateAlpha(double alpha) {
        if (!(alpha > 0 && alpha < 1)) {
            throw StatisticalError("Alpha must be between zero and one.");
        }
    }

    static vector<double> validateSample(
        const vector<double>& values,
        const string& name
    ) {
        if (values.size() < 2) {
            throw StatisticalError(name + " needs at least two observations.");
        }

        for (double x : values) {
            if (!isfinite(x)) {
                throw StatisticalError(name + " contains non-finite data.");
            }
        }

        return values;
    }

    static double mean(const vector<double>& values) {
        return accumulate(values.begin(), values.end(), 0.0)
            / static_cast<double>(values.size());
    }

    static double variance(const vector<double>& values) {
        const double avg = mean(values);
        double sum = 0;

        for (double x : values) {
            sum += (x - avg) * (x - avg);
        }

        return sum / (values.size() - 1);
    }

    static double betaFraction(double a, double b, double x) {
        const double qab = a + b;
        const double qap = a + 1;
        const double qam = a - 1;

        double c = 1;
        double d = 1 - qab * x / qap;

        if (abs(d) < EPS) d = EPS;

        d = 1 / d;
        double h = d;

        for (int m = 1; m <= 10000; ++m) {
            const int m2 = 2 * m;

            double aa = m * (b - m) * x
                / ((qam + m2) * (a + m2));

            d = 1 + aa * d;
            if (abs(d) < EPS) d = EPS;

            c = 1 + aa / c;
            if (abs(c) < EPS) c = EPS;

            d = 1 / d;
            h *= d * c;

            aa = -(a + m) * (qab + m) * x
                / ((a + m2) * (qap + m2));

            d = 1 + aa * d;
            if (abs(d) < EPS) d = EPS;

            c = 1 + aa / c;
            if (abs(c) < EPS) c = EPS;

            d = 1 / d;
            const double delta = d * c;
            h *= delta;

            if (abs(delta - 1) < 3e-14) {
                return h;
            }
        }

        throw StatisticalError("Beta continued fraction failed.");
    }

    static double betaRegularized(double x, double a, double b) {
        if (a <= 0 || b <= 0 || x < 0 || x > 1) {
            throw StatisticalError("Invalid beta distribution parameters.");
        }

        if (x == 0) return 0;
        if (x == 1) return 1;

        const double bt = exp(
            lgamma(a + b) - lgamma(a) - lgamma(b)
            + a * log(x) + b * log1p(-x)
        );

        double result;

        if (x < (a + 1) / (a + b + 2)) {
            result = bt * betaFraction(a, b, x) / a;
        } else {
            result = 1 - bt * betaFraction(b, a, 1 - x) / b;
        }

        return clamp(result, 0.0, 1.0);
    }

    static double gammaQ(double a, double x) {
        if (a <= 0 || x < 0) {
            throw StatisticalError("Invalid gamma parameters.");
        }

        if (x == 0) return 1;

        const double gln = lgamma(a);

        if (x < a + 1) {
            double ap = a;
            double term = 1 / a;
            double sum = term;

            for (int i = 0; i < 10000; ++i) {
                ap += 1;
                term *= x / ap;
                sum += term;

                if (abs(term) < abs(sum) * 3e-14) {
                    const double p = sum * exp(
                        -x + a * log(x) - gln
                    );

                    return clamp(1 - p, 0.0, 1.0);
                }
            }

            throw StatisticalError("Gamma series failed.");
        }

        double b = x + 1 - a;
        double c = 1e300;
        double d = 1 / b;
        double h = d;

        for (int i = 1; i <= 10000; ++i) {
            const double an = -i * (i - a);
            b += 2;

            d = an * d + b;
            if (abs(d) < EPS) d = EPS;

            c = b + an / c;
            if (abs(c) < EPS) c = EPS;

            d = 1 / d;
            const double delta = d * c;
            h *= delta;

            if (abs(delta - 1) < 3e-14) {
                return clamp(
                    exp(-x + a * log(x) - gln) * h,
                    0.0,
                    1.0
                );
            }
        }

        throw StatisticalError("Gamma continued fraction failed.");
    }

    static double normalCDF(double z) {
        return 0.5 * erfc(-z / sqrt(2));
    }

    static double normalP(double z) {
        return erfc(abs(z) / sqrt(2));
    }

    static double tP(double t, double df) {
        return betaRegularized(
            df / (df + t * t),
            df / 2,
            0.5
        );
    }

    static double chiSquareP(double x, double df) {
        return gammaQ(df / 2, x / 2);
    }

    static double fP(double f, double df1, double df2) {
        return betaRegularized(
            df2 / (df2 + df1 * f),
            df2 / 2,
            df1 / 2
        );
    }

    static double inverseCDF(
        double (*function)(double),
        double probability
    ) {
        double low = 0;
        double high = 10;

        for (int i = 0; i < 150; ++i) {
            const double mid = (low + high) / 2;

            if (function(mid) < probability) {
                low = mid;
            } else {
                high = mid;
            }
        }

        return (low + high) / 2;
    }

    static double normalCritical(double alpha) {
        return inverseCDF(normalCDF, 1 - alpha / 2);
    }

public:
    static TestResult oneSampleT(
        const vector<double>& input,
        double reference,
        double alpha = 0.05
    ) {
        validateAlpha(alpha);
        const auto x = validateSample(input, "Sample");

        const double avg = mean(x);
        const double sd = sqrt(variance(x));
        const double se = sd / sqrt(x.size());

        if (se == 0) {
            throw StatisticalError("Zero sample variance.");
        }

        const double t = (avg - reference) / se;
        const double df = x.size() - 1;

        return {
            "One-sample t-test",
            t,
            tP(t, df),
            df,
            alpha,
            (avg - reference) / sd,
            true
        };
    }

    static TestResult independentWelchT(
        const vector<double>& first,
        const vector<double>& second,
        double alpha = 0.05
    ) {
        validateAlpha(alpha);

        const auto a = validateSample(first, "First group");
        const auto b = validateSample(second, "Second group");

        const double va = variance(a);
        const double vb = variance(b);
        const double difference = mean(a) - mean(b);

        const double x = va / a.size();
        const double y = vb / b.size();
        const double se2 = x + y;

        if (se2 == 0) {
            throw StatisticalError("Zero combined variance.");
        }

        const double df = se2 * se2 / (
            x * x / (a.size() - 1)
            + y * y / (b.size() - 1)
        );

        const double t = difference / sqrt(se2);

        return {
            "Welch independent t-test",
            t,
            tP(t, df),
            df,
            alpha,
            0,
            false
        };
    }

    static TestResult pairedT(
        const vector<double>& before,
        const vector<double>& after,
        double alpha = 0.05
    ) {
        if (before.size() != after.size()) {
            throw StatisticalError("Paired samples must have equal lengths.");
        }

        vector<double> differences;

        for (size_t i = 0; i < before.size(); ++i) {
            differences.push_back(after[i] - before[i]);
        }

        TestResult result = oneSampleT(differences, 0, alpha);
        result.name = "Paired t-test";

        return result;
    }

    static TestResult zTest(
        double sampleMean,
        double populationMean,
        double populationSD,
        size_t sampleSize,
        double alpha = 0.05
    ) {
        validateAlpha(alpha);

        if (populationSD <= 0 || sampleSize == 0) {
            throw StatisticalError("Invalid population parameters.");
        }

        const double se = populationSD / sqrt(sampleSize);
        const double z = (sampleMean - populationMean) / se;

        return {
            "One-sample z-test",
            z,
            normalP(z),
            0,
            alpha,
            (sampleMean - populationMean) / populationSD,
            true
        };
    }

    static TestResult chiSquareIndependence(
        const vector<vector<double>>& table,
        double alpha = 0.05
    ) {
        validateAlpha(alpha);

        if (table.size() < 2 || table[0].size() < 2) {
            throw StatisticalError("Contingency table must be at least 2x2.");
        }

        const size_t rows = table.size();
        const size_t cols = table[0].size();

        vector<double> rowTotals(rows, 0);
        vector<double> colTotals(cols, 0);

        double total = 0;

        for (size_t i = 0; i < rows; ++i) {
            if (table[i].size() != cols) {
                throw StatisticalError("Non-rectangular contingency table.");
            }

            for (size_t j = 0; j < cols; ++j) {
                const double value = table[i][j];

                if (!isfinite(value) || value < 0) {
                    throw StatisticalError("Invalid frequency.");
                }

                rowTotals[i] += value;
                colTotals[j] += value;
                total += value;
            }
        }

        if (total <= 0) {
            throw StatisticalError("Contingency table is empty.");
        }

        double statistic = 0;

        for (size_t i = 0; i < rows; ++i) {
            for (size_t j = 0; j < cols; ++j) {
                const double expected = rowTotals[i] * colTotals[j] / total;

                if (expected <= 0) {
                    throw StatisticalError("Zero expected frequency.");
                }

                statistic += pow(table[i][j] - expected, 2) / expected;
            }
        }

        const double df = (rows - 1) * (cols - 1);

        const double cramerV = sqrt(
            statistic / (total * min(rows - 1, cols - 1))
        );

        return {
            "Chi-square independence test",
            statistic,
            chiSquareP(statistic, df),
            df,
            alpha,
            cramerV,
            true
        };
    }

    static TestResult goodnessOfFit(
        const vector<double>& observed,
        const vector<double>& expected,
        double alpha = 0.05
    ) {
        validateAlpha(alpha);

        if (observed.size() != expected.size() || observed.size() < 2) {
            throw StatisticalError("Frequency arrays must have equal lengths.");
        }

        double statistic = 0;
        double total = 0;

        for (size_t i = 0; i < observed.size(); ++i) {
            if (observed[i] < 0 || expected[i] <= 0
                || !isfinite(observed[i]) || !isfinite(expected[i])) {
                throw StatisticalError("Invalid observed or expected frequency.");
            }

            statistic += pow(observed[i] - expected[i], 2) / expected[i];
            total += observed[i];
        }

        const double df = observed.size() - 1;

        return {
            "Chi-square goodness-of-fit",
            statistic,
            chiSquareP(statistic, df),
            df,
            alpha,
            sqrt(statistic / total),
            true
        };
    }

    static TestResult anova(
        const vector<vector<double>>& groups,
        double alpha = 0.05
    ) {
        validateAlpha(alpha);

        if (groups.size() < 2) {
            throw StatisticalError("ANOVA requires at least two groups.");
        }

        size_t totalN = 0;
        double grandTotal = 0;

        for (size_t i = 0; i < groups.size(); ++i) {
            validateSample(groups[i], "ANOVA group");

            totalN += groups[i].size();
            grandTotal += accumulate(
                groups[i].begin(), groups[i].end(), 0.0
            );
        }

        const double grandMean = grandTotal / totalN;

        double ssBetween = 0;
        double ssWithin = 0;

        for (const auto& group : groups) {
            const double avg = mean(group);

            ssBetween += group.size() * pow(avg - grandMean, 2);

            for (double x : group) {
                ssWithin += pow(x - avg, 2);
            }
        }

        const double df1 = groups.size() - 1;
        const double df2 = totalN - groups.size();

        const double msWithin = ssWithin / df2;

        if (msWithin == 0) {
            throw StatisticalError("Within-group variance is zero.");
        }

        const double f = (ssBetween / df1) / msWithin;
        const double etaSquared = ssBetween / (ssBetween + ssWithin);

        return {
            "One-way ANOVA",
            f,
            fP(f, df1, df2),
            df2,
            alpha,
            etaSquared,
            true
        };
    }
};


class GovernanceEngine {
private:
    vector<TestResult> results;

public:
    void submit(const TestResult& result) {
        if (!isfinite(result.statistic)
            || !isfinite(result.pValue)
            || result.pValue < 0
            || result.pValue > 1) {
            throw StatisticalError("Invalid test result.");
        }

        results.push_back(result);
    }

    void printReport() const {
        cout << "\nSTATISTICAL EXPERIMENT REPORT\n";

        cout << left
             << setw(34) << "Test"
             << setw(14) << "Statistic"
             << setw(14) << "P-value"
             << "Decision\n";

        cout << string(80, '-') << '\n';

        for (const auto& result : results) {
            cout << left
                 << setw(34) << result.name
                 << setw(14) << fixed << setprecision(5) << result.statistic
                 << setw(14) << result.pValue
                 << (result.rejectNull() ? "Reject H0" : "Fail to reject H0")
                 << '\n';
        }
    }

    void applyBonferroni() const {
        cout << "\nBONFERRONI-ADJUSTED P-VALUES\n";

        const size_t count = results.size();

        for (const auto& result : results) {
            const double adjusted = min(1.0, result.pValue * count);

            cout << result.name
                 << ": " << adjusted << '\n';
        }
    }
};


int main() {
    try {
        StatisticalEngine engine;
        GovernanceEngine report;

        report.submit(
            engine.oneSampleT(
                {51, 53, 49, 52, 55, 50, 54, 52},
                50
            )
        );

        report.submit(
            engine.independentWelchT(
                {68, 70, 72, 65, 71, 69, 67},
                {75, 78, 74, 80, 77, 76, 79}
            )
        );

        report.submit(
            engine.pairedT(
                {70, 72, 68, 75, 71, 69},
                {74, 76, 72, 78, 75, 73}
            )
        );

        report.submit(
            engine.zTest(102, 100, 10, 100)
        );

        report.submit(
            engine.chiSquareIndependence({
                {40, 20},
                {30, 50}
            })
        );

        report.submit(
            engine.goodnessOfFit(
                {45, 55, 50, 50},
                {50, 50, 50, 50}
            )
        );

        report.submit(
            engine.anova({
                {18, 20, 19, 21, 17},
                {24, 25, 23, 26, 22},
                {29, 30, 28, 31, 27}
            })
        );

        report.printReport();
        report.applyBonferroni();

        if (abs(StatisticalEngine::oneSampleT(
            {10, 11, 12, 13}, 11
        ).pValue - 1.0) > 1e-10) {
            throw StatisticalError("Symmetry validation failed.");
        }

        cout << "\nNumerical validation passed.\n";

    } catch (const exception& error) {
        cerr << "Statistical execution error: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
