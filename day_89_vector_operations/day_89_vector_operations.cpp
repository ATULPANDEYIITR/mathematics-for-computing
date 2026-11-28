#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

class VectorError : public runtime_error {
public:
    explicit VectorError(const string& message)
        : runtime_error(message) {}
};

class DimensionMismatchError : public VectorError {
public:
    DimensionMismatchError(size_t first, size_t second)
        : VectorError(
            "Dimension mismatch: " + to_string(first) +
            " != " + to_string(second)
        ) {}
};

class ZeroVectorError : public VectorError {
public:
    explicit ZeroVectorError(const string& message)
        : VectorError(message) {}
};

enum class NormType {
    L1,
    L2,
    L_INFINITY
};

struct VectorStatistics {
    double l1;
    double l2;
    double infinity;
};

class Vector {
private:
    vector<double> values;

    void validate() const {
        if (values.empty()) {
            throw VectorError("Vector cannot be empty.");
        }

        for (double value : values) {
            if (!isfinite(value)) {
                throw VectorError(
                    "Vector components must be finite."
                );
            }
        }
    }

    void requireSameDimension(const Vector& other) const {
        if (dimension() != other.dimension()) {
            throw DimensionMismatchError(
                dimension(), other.dimension()
            );
        }
    }

public:
    explicit Vector(vector<double> components)
        : values(move(components)) {
        validate();
    }

    size_t dimension() const {
        return values.size();
    }

    const vector<double>& components() const {
        return values;
    }

    Vector add(const Vector& other) const {
        requireSameDimension(other);

        vector<double> result(dimension());

        for (size_t i = 0; i < dimension(); ++i) {
            result[i] = values[i] + other.values[i];
        }

        return Vector(move(result));
    }

    Vector subtract(const Vector& other) const {
        requireSameDimension(other);

        vector<double> result(dimension());

        for (size_t i = 0; i < dimension(); ++i) {
            result[i] = values[i] - other.values[i];
        }

        return Vector(move(result));
    }

    Vector scale(double scalar) const {
        if (!isfinite(scalar)) {
            throw VectorError("Scalar must be finite.");
        }

        vector<double> result;
        result.reserve(dimension());

        for (double value : values) {
            result.push_back(value * scalar);
        }

        return Vector(move(result));
    }

    double dot(const Vector& other) const {
        requireSameDimension(other);

        // Long double accumulation reduces intermediate precision loss
        // on platforms where long double has extended precision.
        long double result = 0.0L;

        for (size_t i = 0; i < dimension(); ++i) {
            result += static_cast<long double>(values[i]) *
                      static_cast<long double>(other.values[i]);
        }

        if (!isfinite(result) ||
            result > numeric_limits<double>::max() ||
            result < -numeric_limits<double>::max()) {
            throw VectorError("Dot product overflowed.");
        }

        return static_cast<double>(result);
    }

    double l1Norm() const {
        long double result = 0.0L;

        for (double value : values) {
            result += abs(static_cast<long double>(value));
        }

        if (!isfinite(result) ||
            result > numeric_limits<double>::max()) {
            throw VectorError("L1 norm overflowed.");
        }

        return static_cast<double>(result);
    }

    double l2Norm() const {
        // hypot provides a scaled calculation that avoids many
        // intermediate overflow and underflow problems.
        double result = 0.0;

        for (double value : values) {
            result = hypot(result, value);
        }

        if (!isfinite(result)) {
            throw VectorError("L2 norm overflowed.");
        }

        return result;
    }

    double infinityNorm() const {
        double result = 0.0;

        for (double value : values) {
            result = max(result, abs(value));
        }

        return result;
    }

    double norm(NormType type) const {
        switch (type) {
            case NormType::L1:
                return l1Norm();

            case NormType::L2:
                return l2Norm();

            case NormType::L_INFINITY:
                return infinityNorm();
        }

        throw VectorError("Unknown norm type.");
    }

    double pNorm(double p) const {
        if (!isfinite(p) || p < 1.0) {
            throw VectorError("p must be finite and >= 1.");
        }

        if (p == 1.0) return l1Norm();
        if (p == 2.0) return l2Norm();

        double maximum = infinityNorm();

        if (maximum == 0.0) return 0.0;

        long double sum = 0.0L;

        for (double value : values) {
            sum += pow(abs(value) / maximum, p);
        }

        double result = maximum * pow(
            static_cast<double>(sum), 1.0 / p
        );

        if (!isfinite(result)) {
            throw VectorError("p-norm overflowed.");
        }

        return result;
    }

    Vector normalize() const {
        double magnitude = l2Norm();

        if (magnitude == 0.0) {
            throw ZeroVectorError(
                "Cannot normalize a zero vector."
            );
        }

        return scale(1.0 / magnitude);
    }

    double cosineSimilarity(const Vector& other) const {
        requireSameDimension(other);

        double firstNorm = l2Norm();
        double secondNorm = other.l2Norm();

        if (firstNorm == 0.0 || secondNorm == 0.0) {
            throw ZeroVectorError(
                "Cosine similarity is undefined for zero vectors."
            );
        }

        // Sequential division reduces denominator overflow risk.
        double result = dot(other) / firstNorm / secondNorm;

        return clamp(result, -1.0, 1.0);
    }

    double distance(const Vector& other) const {
        return subtract(other).l2Norm();
    }

    bool isOrthogonal(
        const Vector& other,
        double tolerance = 1e-10
    ) const {
        if (!isfinite(tolerance) || tolerance < 0.0) {
            throw VectorError("Invalid tolerance.");
        }

        return abs(dot(other)) <= tolerance;
    }

    VectorStatistics statistics() const {
        return {
            l1Norm(),
            l2Norm(),
            infinityNorm()
        };
    }

    void display(const string& label) const {
        cout << label << " = [";

        for (size_t i = 0; i < dimension(); ++i) {
            cout << values[i];

            if (i + 1 < dimension()) {
                cout << ", ";
            }
        }

        cout << "]\n";
    }
};

class VectorCalculator {
public:
    static void demonstrate(const Vector& first,
                            const Vector& second) {
        cout << "\nVECTOR CALCULATOR\n";

        first.display("First vector");
        second.display("Second vector");

        first.add(second).display("Addition");
        first.subtract(second).display("Subtraction");
        first.scale(3.0).display("Scalar multiplication");

        cout << "Dot product: " << first.dot(second) << '\n';

        VectorStatistics stats = first.statistics();

        cout << "L1 norm: " << stats.l1 << '\n';
        cout << "L2 norm: " << stats.l2 << '\n';
        cout << "L-infinity norm: "
             << stats.infinity << '\n';

        cout << "L3 norm: " << first.pNorm(3.0) << '\n';

        first.normalize().display("Normalized first vector");

        cout << "Euclidean distance: "
             << first.distance(second) << '\n';

        cout << "Cosine similarity: "
             << first.cosineSimilarity(second) << '\n';

        cout << "Orthogonal: "
             << boolalpha
             << first.isOrthogonal(second)
             << '\n';
    }
};

int main() {
    try {
        cout << fixed << setprecision(6);

        Vector first({3.0, 4.0});
        Vector second({4.0, 3.0});

        VectorCalculator::demonstrate(first, second);

        cout << "\nHIGH-DIMENSIONAL CALCULATION\n";

        vector<double> components(10000);

        iota(components.begin(), components.end(), 1.0);

        Vector highDimensional(move(components));

        cout << "Dimension: "
             << highDimensional.dimension() << '\n';

        cout << "L2 norm: "
             << highDimensional.l2Norm() << '\n';

        cout << "\nEDGE CASES\n";

        Vector zero({0.0, 0.0});

        cout << "Zero-vector L2 norm: "
             << zero.l2Norm() << '\n';

        try {
            zero.normalize();
        } catch (const ZeroVectorError& error) {
            cout << "Normalization rejected: "
                 << error.what() << '\n';
        }

        try {
            first.add(Vector({1.0, 2.0, 3.0}));
        } catch (const DimensionMismatchError& error) {
            cout << "Addition rejected: "
                 << error.what() << '\n';
        }

        try {
            first.scale(numeric_limits<double>::infinity());
        } catch (const VectorError& error) {
            cout << "Scalar rejected: "
                 << error.what() << '\n';
        }

        cout << "\nVALIDATION\n";

        if (first.add(second).components() !=
            vector<double>({7.0, 7.0})) {
            throw VectorError("Addition assertion failed.");
        }

        if (abs(first.dot(second) - 24.0) > 1e-12) {
            throw VectorError("Dot product assertion failed.");
        }

        if (abs(first.l2Norm() - 5.0) > 1e-12) {
            throw VectorError("Norm assertion failed.");
        }

        if (abs(first.normalize().l2Norm() - 1.0) > 1e-12) {
            throw VectorError("Normalization assertion failed.");
        }

        if (!Vector({1.0, 0.0}).isOrthogonal(
                Vector({0.0, 1.0}))) {
            throw VectorError("Orthogonality assertion failed.");
        }

        cout << "All assertions passed.\n";

    } catch (const exception& error) {
        cerr << "Execution failed: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
