#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

/*
 * Linear Algebra Foundations
 *
 * C++17 implementation of:
 * - Real scalars
 * - Coordinate vectors
 * - Vector spaces R^n
 * - Vector arithmetic
 * - Linear combinations
 * - Matrix rank
 * - Linear independence
 * - Basis verification
 *
 * Gaussian elimination uses partial pivoting.
 */

namespace linear_algebra {

constexpr double EPSILON = 1e-9;

class LinearAlgebraError : public std::runtime_error {
public:
    explicit LinearAlgebraError(const std::string& message)
        : std::runtime_error(message) {}
};

class DimensionError : public LinearAlgebraError {
public:
    explicit DimensionError(const std::string& message)
        : LinearAlgebraError(message) {}
};

class ScalarError : public LinearAlgebraError {
public:
    explicit ScalarError(const std::string& message)
        : LinearAlgebraError(message) {}
};

void validateScalar(double value) {
    if (!std::isfinite(value)) {
        throw ScalarError("Scalar must be finite.");
    }
}

class Scalar {
private:
    double value_;

public:
    explicit Scalar(double value) : value_(value) {
        validateScalar(value);
    }

    double value() const {
        return value_;
    }

    Scalar operator+(const Scalar& other) const {
        return Scalar(value_ + other.value_);
    }

    Scalar operator*(const Scalar& other) const {
        return Scalar(value_ * other.value_);
    }
};

class Vector {
private:
    std::vector<double> components_;

    void validate() const {
        if (components_.empty()) {
            throw DimensionError(
                "A vector must contain at least one component."
            );
        }

        for (double value : components_) {
            validateScalar(value);
        }
    }

    void checkDimension(const Vector& other) const {
        if (dimension() != other.dimension()) {
            throw DimensionError(
                "Vector dimensions are incompatible."
            );
        }
    }

public:
    explicit Vector(std::vector<double> components)
        : components_(std::move(components)) {
        validate();
    }

    std::size_t dimension() const {
        return components_.size();
    }

    const std::vector<double>& components() const {
        return components_;
    }

    double operator[](std::size_t index) const {
        return components_.at(index);
    }

    Vector operator+(const Vector& other) const {
        checkDimension(other);

        std::vector<double> result(dimension());

        for (std::size_t i = 0; i < dimension(); ++i) {
            result[i] = components_[i] + other.components_[i];
        }

        return Vector(std::move(result));
    }

    Vector operator-(const Vector& other) const {
        checkDimension(other);

        std::vector<double> result(dimension());

        for (std::size_t i = 0; i < dimension(); ++i) {
            result[i] = components_[i] - other.components_[i];
        }

        return Vector(std::move(result));
    }

    Vector operator-() const {
        std::vector<double> result;

        for (double value : components_) {
            result.push_back(-value);
        }

        return Vector(std::move(result));
    }

    Vector scale(double scalar) const {
        validateScalar(scalar);

        std::vector<double> result;

        for (double value : components_) {
            result.push_back(value * scalar);
        }

        return Vector(std::move(result));
    }

    double dot(const Vector& other) const {
        checkDimension(other);

        double result = 0.0;

        for (std::size_t i = 0; i < dimension(); ++i) {
            result += components_[i] * other.components_[i];
        }

        return result;
    }

    double norm() const {
        return std::sqrt(dot(*this));
    }

    Vector normalized() const {
        const double magnitude = norm();

        if (magnitude <= EPSILON) {
            throw LinearAlgebraError(
                "The zero vector cannot be normalized."
            );
        }

        return scale(1.0 / magnitude);
    }

    bool isZero() const {
        return std::all_of(
            components_.begin(),
            components_.end(),
            [](double value) {
                return std::abs(value) <= EPSILON;
            }
        );
    }

    bool approximatelyEquals(const Vector& other) const {
        checkDimension(other);

        for (std::size_t i = 0; i < dimension(); ++i) {
            if (
                std::abs(components_[i] - other.components_[i])
                > EPSILON
            ) {
                return false;
            }
        }

        return true;
    }

    void print() const {
        std::cout << "(";

        for (std::size_t i = 0; i < dimension(); ++i) {
            std::cout << components_[i];

            if (i + 1 < dimension()) {
                std::cout << ", ";
            }
        }

        std::cout << ")";
    }
};

class VectorSpace {
private:
    std::size_t dimension_;

public:
    explicit VectorSpace(std::size_t dimension)
        : dimension_(dimension) {
        if (dimension == 0) {
            throw DimensionError(
                "Vector-space dimension must be positive."
            );
        }
    }

    std::size_t dimension() const {
        return dimension_;
    }

    void validate(const Vector& vector) const {
        if (vector.dimension() != dimension_) {
            throw DimensionError(
                "Vector does not belong to the specified space."
            );
        }
    }

    Vector zero() const {
        return Vector(
            std::vector<double>(dimension_, 0.0)
        );
    }

    Vector add(
        const Vector& first,
        const Vector& second
    ) const {
        validate(first);
        validate(second);

        return first + second;
    }

    Vector scalarMultiply(
        double scalar,
        const Vector& vector
    ) const {
        validate(vector);
        return vector.scale(scalar);
    }

    Vector linearCombination(
        const std::vector<Vector>& vectors,
        const std::vector<double>& coefficients
    ) const {
        if (vectors.size() != coefficients.size()) {
            throw LinearAlgebraError(
                "Vector and coefficient counts must match."
            );
        }

        Vector result = zero();

        for (std::size_t i = 0; i < vectors.size(); ++i) {
            validate(vectors[i]);
            validateScalar(coefficients[i]);

            result = result + vectors[i].scale(coefficients[i]);
        }

        return result;
    }
};

/*
 * Calculate matrix rank when vectors are matrix columns.
 *
 * Partial pivoting improves numerical stability.
 * Complexity: O(m*n*min(m,n)).
 */
std::size_t matrixRank(
    const std::vector<Vector>& vectors
) {
    if (vectors.empty()) {
        return 0;
    }

    const std::size_t rows = vectors.front().dimension();
    const std::size_t columns = vectors.size();

    for (const auto& vector : vectors) {
        if (vector.dimension() != rows) {
            throw DimensionError(
                "All vectors must have equal dimensions."
            );
        }
    }

    std::vector<std::vector<double>> matrix(
        rows,
        std::vector<double>(columns, 0.0)
    );

    for (std::size_t row = 0; row < rows; ++row) {
        for (std::size_t col = 0; col < columns; ++col) {
            matrix[row][col] = vectors[col][row];
        }
    }

    std::size_t rank = 0;

    for (
        std::size_t col = 0;
        col < columns && rank < rows;
        ++col
    ) {
        std::size_t pivot = rank;

        for (std::size_t row = rank + 1; row < rows; ++row) {
            if (
                std::abs(matrix[row][col]) >
                std::abs(matrix[pivot][col])
            ) {
                pivot = row;
            }
        }

        if (std::abs(matrix[pivot][col]) <= EPSILON) {
            continue;
        }

        std::swap(matrix[rank], matrix[pivot]);

        const double pivotValue = matrix[rank][col];

        for (std::size_t row = rank + 1; row < rows; ++row) {
            const double factor =
                matrix[row][col] / pivotValue;

            for (std::size_t j = col; j < columns; ++j) {
                matrix[row][j] -=
                    factor * matrix[rank][j];
            }
        }

        ++rank;
    }

    return rank;
}

bool linearlyIndependent(
    const std::vector<Vector>& vectors
) {
    return matrixRank(vectors) == vectors.size();
}

bool isBasis(
    const std::vector<Vector>& vectors,
    const VectorSpace& space
) {
    for (const auto& vector : vectors) {
        space.validate(vector);
    }

    return (
        vectors.size() == space.dimension() &&
        linearlyIndependent(vectors)
    );
}

void printVector(
    const std::string& label,
    const Vector& vector
) {
    std::cout << label;
    vector.print();
    std::cout << "\n";
}

} // namespace linear_algebra

int main() {
    using namespace linear_algebra;

    try {
        std::cout << std::fixed << std::setprecision(4);

        std::cout << "LINEAR ALGEBRA FOUNDATIONS\n";
        std::cout << std::string(55, '=') << "\n";

        // 1. Scalars
        std::cout << "\n1. SCALARS\n";

        Scalar alpha(3.0);
        Scalar beta(2.0);

        std::cout << "alpha + beta = "
                  << (alpha + beta).value() << "\n";

        std::cout << "alpha * beta = "
                  << (alpha * beta).value() << "\n";

        // 2. Vector construction
        std::cout << "\n2. VECTOR NOTATION\n";

        Vector u({2.0, 3.0});
        Vector v({4.0, 1.0});

        printVector("u = ", u);
        printVector("v = ", v);

        std::cout << "Dimension = " << u.dimension() << "\n";

        printVector("u + v = ", u + v);
        printVector("u - v = ", u - v);
        printVector("-u = ", -u);

        // 3. Scalar multiplication
        std::cout << "\n3. SCALAR MULTIPLICATION\n";

        printVector("3u = ", u.scale(3.0));
        printVector("(-2)u = ", u.scale(-2.0));
        printVector("0u = ", u.scale(0.0));

        // 4. Dot product and norm
        std::cout << "\n4. DOT PRODUCT AND NORM\n";

        std::cout << "u . v = " << u.dot(v) << "\n";
        std::cout << "||u|| = " << u.norm() << "\n";

        printVector("Unit vector = ", u.normalized());

        // 5. Vector space
        std::cout << "\n5. VECTOR SPACE R^2\n";

        VectorSpace space2(2);

        printVector("Zero vector = ", space2.zero());

        printVector(
            "Additive identity = ",
            space2.add(u, space2.zero())
        );

        printVector(
            "Additive inverse = ",
            space2.add(u, -u)
        );

        // 6. Linear combination
        std::cout << "\n6. LINEAR COMBINATION\n";

        printVector(
            "2u + 3v = ",
            space2.linearCombination(
                {u, v},
                {2.0, 3.0}
            )
        );

        // 7. Basis and rank
        std::cout << "\n7. BASIS AND LINEAR INDEPENDENCE\n";

        Vector e1({1.0, 0.0});
        Vector e2({0.0, 1.0});

        std::vector<Vector> standardBasis = {e1, e2};

        std::cout << "Standard basis rank = "
                  << matrixRank(standardBasis) << "\n";

        std::cout << "Is basis of R^2 = "
                  << std::boolalpha
                  << isBasis(standardBasis, space2)
                  << "\n";

        std::vector<Vector> dependent = {
            Vector({1.0, 2.0}),
            Vector({2.0, 4.0})
        };

        std::cout << "Dependent set rank = "
                  << matrixRank(dependent) << "\n";

        std::cout << "Dependent set independent = "
                  << linearlyIndependent(dependent)
                  << "\n";

        // 8. Higher-dimensional example
        std::cout << "\n8. VECTOR SPACE R^3\n";

        VectorSpace space3(3);

        Vector a({1.0, 0.0, 0.0});
        Vector b({0.0, 1.0, 0.0});
        Vector c({0.0, 0.0, 1.0});

        std::vector<Vector> basis3 = {a, b, c};

        std::cout << "Basis rank = "
                  << matrixRank(basis3) << "\n";

        std::cout << "Is basis of R^3 = "
                  << isBasis(basis3, space3) << "\n";

        // 9. Error handling
        std::cout << "\n9. VALIDATION AND FAILURE HANDLING\n";

        try {
            Vector invalid({1.0, 2.0, 3.0});
            space2.validate(invalid);
        } catch (const DimensionError& error) {
            std::cout << "Dimension error: "
                      << error.what() << "\n";
        }

        try {
            Vector zero = space2.zero();
            zero.normalized();
        } catch (const LinearAlgebraError& error) {
            std::cout << "Normalization error: "
                      << error.what() << "\n";
        }

        try {
            Vector invalid({std::numeric_limits<double>::infinity()});
        } catch (const ScalarError& error) {
            std::cout << "Scalar error: "
                      << error.what() << "\n";
        }

        // 10. Assertions
        std::cout << "\n10. VALIDATION TESTS\n";

        if (!(u + v).approximatelyEquals(Vector({6.0, 4.0}))) {
            throw LinearAlgebraError("Vector addition test failed.");
        }

        if (u.dot(v) != 11.0) {
            throw LinearAlgebraError("Dot product test failed.");
        }

        if (matrixRank(standardBasis) != 2) {
            throw LinearAlgebraError("Rank test failed.");
        }

        if (!isBasis(standardBasis, space2)) {
            throw LinearAlgebraError("Basis test failed.");
        }

        if (matrixRank(dependent) != 1) {
            throw LinearAlgebraError("Dependent vector test failed.");
        }

        if (!space2.zero().isZero()) {
            throw LinearAlgebraError("Zero vector test failed.");
        }

        std::cout << "All validation tests passed.\n";

    } catch (const std::exception& error) {
        std::cerr << "Application failure: "
                  << error.what() << "\n";

        return 1;
    }

    return 0;
}
