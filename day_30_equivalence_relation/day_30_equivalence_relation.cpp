#include <algorithm>
#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * Technical case study:
 *
 * A data-processing service receives records describing the same logical
 * entity from different systems. Two records are considered equivalent when
 * they share a normalized identity key. The service must:
 *
 * - verify that the relation is an equivalence relation;
 * - construct equivalence classes;
 * - interpret those classes as a partition;
 * - build a quotient representation in which each class becomes one logical
 *   entity;
 * - support operations on quotient elements;
 * - update classes efficiently as new equivalences are discovered.
 *
 * The implementation also uses congruence modulo n as a mathematical
 * quotient example and disjoint-set union for incremental class maintenance.
 */

template <typename T>
class EquivalenceRelation {
public:
    using Relation = std::function<bool(const T&, const T&)>;
    using Class = std::set<T>;

    EquivalenceRelation(
        std::vector<T> elements,
        Relation relation,
        std::string name
    )
        : elements_(std::move(elements)),
          relation_(std::move(relation)),
          name_(std::move(name)) {
        std::sort(elements_.begin(), elements_.end());
        elements_.erase(
            std::unique(elements_.begin(), elements_.end()),
            elements_.end()
        );
    }

    bool is_reflexive() const {
        for (const auto& x : elements_) {
            if (!relation_(x, x)) {
                return false;
            }
        }
        return true;
    }

    bool is_symmetric() const {
        for (const auto& x : elements_) {
            for (const auto& y : elements_) {
                if (relation_(x, y) && !relation_(y, x)) {
                    return false;
                }
            }
        }
        return true;
    }

    bool is_transitive() const {
        for (const auto& x : elements_) {
            for (const auto& y : elements_) {
                if (!relation_(x, y)) {
                    continue;
                }

                for (const auto& z : elements_) {
                    if (relation_(y, z) && !relation_(x, z)) {
                        return false;
                    }
                }
            }
        }
        return true;
    }

    bool is_equivalence() const {
        return is_reflexive() && is_symmetric() && is_transitive();
    }

    Class equivalence_class(const T& element) const {
        if (!std::binary_search(elements_.begin(), elements_.end(), element)) {
            throw std::invalid_argument("Element is outside the relation domain.");
        }

        Class result;

        for (const auto& other : elements_) {
            if (relation_(element, other)) {
                result.insert(other);
            }
        }

        return result;
    }

    std::vector<Class> classes() const {
        if (!is_equivalence()) {
            throw std::logic_error(
                "Equivalence classes cannot form a partition because the "
                "relation is not an equivalence relation."
            );
        }

        std::vector<Class> result;
        std::set<T> assigned;

        for (const auto& element : elements_) {
            if (assigned.contains(element)) {
                continue;
            }

            Class current = equivalence_class(element);
            assigned.insert(current.begin(), current.end());
            result.push_back(std::move(current));
        }

        return result;
    }

    const std::string& name() const {
        return name_;
    }

private:
    std::vector<T> elements_;
    Relation relation_;
    std::string name_;
};

template <typename T>
void print_class(const std::set<T>& class_set) {
    std::cout << "{ ";

    bool first = true;
    for (const auto& value : class_set) {
        if (!first) {
            std::cout << ", ";
        }

        std::cout << value;
        first = false;
    }

    std::cout << " }";
}

template <typename T>
void print_relation_report(const EquivalenceRelation<T>& relation) {
    std::cout << "\n=== " << relation.name() << " ===\n";
    std::cout << "Reflexive: " << std::boolalpha
              << relation.is_reflexive() << '\n';
    std::cout << "Symmetric: " << relation.is_symmetric() << '\n';
    std::cout << "Transitive: " << relation.is_transitive() << '\n';
    std::cout << "Equivalence relation: " << relation.is_equivalence() << '\n';

    if (relation.is_equivalence()) {
        std::cout << "Equivalence classes:\n";

        for (const auto& class_set : relation.classes()) {
            std::cout << "  ";
            print_class(class_set);
            std::cout << '\n';
        }
    }
}

template <typename T>
bool validate_partition(
    const std::set<T>& universe,
    const std::vector<std::set<T>>& blocks,
    std::string& error
) {
    if (blocks.empty()) {
        error = "A partition of a nonempty universe needs at least one block.";
        return false;
    }

    std::set<T> union_of_blocks;

    for (const auto& block : blocks) {
        if (block.empty()) {
            error = "A partition cannot contain an empty block.";
            return false;
        }

        for (const auto& element : block) {
            if (!universe.contains(element)) {
                error = "A block contains an element outside the universe.";
                return false;
            }

            if (!union_of_blocks.insert(element).second) {
                error = "Distinct blocks must be pairwise disjoint.";
                return false;
            }
        }
    }

    if (union_of_blocks != universe) {
        error = "The blocks do not cover the complete universe.";
        return false;
    }

    error.clear();
    return true;
}

class DisjointSet {
public:
    explicit DisjointSet(std::size_t size)
        : parent_(size), rank_(size, 0) {
        std::iota(parent_.begin(), parent_.end(), 0);
    }

    std::size_t find(std::size_t value) {
        if (value >= parent_.size()) {
            throw std::out_of_range("Disjoint-set index is outside the domain.");
        }

        if (parent_[value] != value) {
            parent_[value] = find(parent_[value]);
        }

        return parent_[value];
    }

    bool unite(std::size_t left, std::size_t right) {
        std::size_t left_root = find(left);
        std::size_t right_root = find(right);

        if (left_root == right_root) {
            return false;
        }

        if (rank_[left_root] < rank_[right_root]) {
            std::swap(left_root, right_root);
        }

        parent_[right_root] = left_root;

        if (rank_[left_root] == rank_[right_root]) {
            ++rank_[left_root];
        }

        return true;
    }

    std::map<std::size_t, std::set<std::size_t>> classes() {
        std::map<std::size_t, std::set<std::size_t>> result;

        for (std::size_t value = 0; value < parent_.size(); ++value) {
            result[find(value)].insert(value);
        }

        return result;
    }

private:
    std::vector<std::size_t> parent_;
    std::vector<std::size_t> rank_;
};

struct CustomerRecord {
    int id;
    std::string source;
    std::string external_id;
    std::string normalized_email;
};

class IdentityQuotient {
public:
    explicit IdentityQuotient(std::vector<CustomerRecord> records)
        : records_(std::move(records)) {
        build();
    }

    const std::map<std::string, std::set<int>>& classes() const {
        return classes_;
    }

    std::string canonical_identity(const std::string& key) const {
        auto it = classes_.find(key);

        if (it == classes_.end()) {
            throw std::out_of_range("Unknown quotient element.");
        }

        return key;
    }

private:
    void build() {
        for (const auto& record : records_) {
            classes_[record.normalized_email].insert(record.id);
        }
    }

    std::vector<CustomerRecord> records_;
    std::map<std::string, std::set<int>> classes_;
};

class ResidueClass {
public:
    ResidueClass(long long value, long long modulus)
        : modulus_(modulus) {
        if (modulus <= 0) {
            throw std::invalid_argument("Modulus must be positive.");
        }

        value_ = ((value % modulus_) + modulus_) % modulus_;
    }

    ResidueClass add(const ResidueClass& other) const {
        ensure_same_modulus(other);
        return ResidueClass(value_ + other.value_, modulus_);
    }

    ResidueClass multiply(const ResidueClass& other) const {
        ensure_same_modulus(other);
        return ResidueClass(value_ * other.value_, modulus_);
    }

    bool operator==(const ResidueClass& other) const {
        return modulus_ == other.modulus_ && value_ == other.value_;
    }

    long long representative() const {
        return value_;
    }

    long long modulus() const {
        return modulus_;
    }

private:
    void ensure_same_modulus(const ResidueClass& other) const {
        if (modulus_ != other.modulus_) {
            throw std::invalid_argument(
                "Operations between different quotient structures are invalid."
            );
        }
    }

    long long value_;
    long long modulus_;
};

std::ostream& operator<<(std::ostream& output, const ResidueClass& value) {
    output << '[' << value.representative() << "]_" << value.modulus();
    return output;
}

void demonstrate_basic_equivalence() {
    std::vector<int> domain;
    for (int value = -8; value <= 8; ++value) {
        domain.push_back(value);
    }

    constexpr int modulus = 4;

    EquivalenceRelation<int> congruence(
        domain,
        [](int x, int y) {
            return (x - y) % modulus == 0;
        },
        "integer congruence modulo 4"
    );

    print_relation_report(congruence);

    std::cout << "\nSpecific equivalence classes:\n";

    for (int representative : {-7, -2, 0, 1, 6}) {
        std::cout << '[' << representative << "]_4 = ";
        print_class(congruence.equivalence_class(representative));
        std::cout << '\n';
    }
}

void demonstrate_partition_to_relation() {
    std::set<int> universe{1, 2, 3, 4, 5, 6, 7, 8, 9};

    std::vector<std::set<int>> partition{
        {1, 4, 7},
        {2, 5, 8},
        {3, 6, 9}
    };

    std::string error;

    const bool valid =
        validate_partition(universe, partition, error);

    std::cout << "\n=== Partition as the source of an equivalence relation ===\n";
    std::cout << "Partition valid: " << std::boolalpha << valid << '\n';

    if (!valid) {
        std::cout << "Reason: " << error << '\n';
        return;
    }

    auto same_block =
        [partition](const int& left, const int& right) {
            for (const auto& block : partition) {
                if (block.contains(left) && block.contains(right)) {
                    return true;
                }
            }

            return false;
        };

    EquivalenceRelation<int> induced(
        std::vector<int>(universe.begin(), universe.end()),
        same_block,
        "relation induced by partition"
    );

    std::cout << "Induced relation is an equivalence relation: "
              << induced.is_equivalence() << '\n';

    for (const auto& [left, right] :
         std::vector<std::pair<int, int>>{{1, 7}, {1, 2}, {5, 8}, {6, 9}}) {
        std::cout << left << " R " << right << ": "
                  << induced.equivalence_class(left).contains(right)
                  << '\n';
    }
}

void demonstrate_customer_identity_quotient() {
    /*
     * The business system receives multiple records for the same customer.
     * The normalized email is the key defining equivalence. The quotient
     * collapses duplicate representations into one logical identity.
     */
    std::vector<CustomerRecord> records{
        {101, "CRM", "C-1001", "asha@example.com"},
        {102, "Billing", "B-7741", "asha@example.com"},
        {103, "Support", "S-4402", "asha@example.com"},
        {104, "CRM", "C-1002", "ravi@example.com"},
        {105, "Billing", "B-7742", "ravi@example.com"},
        {106, "CRM", "C-1003", "mina@example.com"}
    };

    IdentityQuotient quotient(records);

    std::cout << "\n=== Customer identity quotient ===\n";
    std::cout << "Input records: " << records.size() << '\n';
    std::cout << "Logical quotient elements: "
              << quotient.classes().size() << '\n';

    for (const auto& [identity, members] : quotient.classes()) {
        std::cout << "Logical identity " << identity << ": records { ";

        bool first = true;
        for (int id : members) {
            if (!first) {
                std::cout << ", ";
            }

            std::cout << id;
            first = false;
        }

        std::cout << " }\n";
    }
}

void demonstrate_quotient_operations() {
    std::cout << "\n=== Well-defined operations on Z/5Z ===\n";

    ResidueClass a(2, 5);
    ResidueClass a_prime(7, 5);
    ResidueClass b(3, 5);
    ResidueClass b_prime(13, 5);

    std::cout << a << " == " << a_prime << ": "
              << (a == a_prime) << '\n';

    std::cout << b << " == " << b_prime << ": "
              << (b == b_prime) << '\n';

    ResidueClass first_sum = a.add(b);
    ResidueClass second_sum = a_prime.add(b_prime);

    ResidueClass first_product = a.multiply(b);
    ResidueClass second_product = a_prime.multiply(b_prime);

    std::cout << a << " + " << b << " = " << first_sum << '\n';
    std::cout << a_prime << " + " << b_prime
              << " = " << second_sum << '\n';

    std::cout << "Addition independent of representatives: "
              << (first_sum == second_sum) << '\n';

    std::cout << a << " * " << b << " = " << first_product << '\n';
    std::cout << a_prime << " * " << b_prime
              << " = " << second_product << '\n';

    std::cout << "Multiplication independent of representatives: "
              << (first_product == second_product) << '\n';
}

void demonstrate_non_equivalence() {
    std::vector<int> domain{1, 2, 3};

    EquivalenceRelation<int> less_than(
        domain,
        [](int x, int y) {
            return x < y;
        },
        "strict less-than"
    );

    EquivalenceRelation<int> different_parity(
        domain,
        [](int x, int y) {
            return (x % 2) != (y % 2);
        },
        "different parity"
    );

    print_relation_report(less_than);
    print_relation_report(different_parity);
}

void demonstrate_union_find() {
    /*
     * When equivalences arrive incrementally, rebuilding every class from
     * the original relation can be expensive. Disjoint-set union maintains
     * the current partition using path compression and union by rank.
     */
    std::cout << "\n=== Incremental partition maintenance ===\n";

    DisjointSet dsu(10);

    const std::vector<std::pair<std::size_t, std::size_t>> relationships{
        {0, 3},
        {3, 6},
        {1, 4},
        {4, 7},
        {2, 5},
        {5, 8},
        {8, 9}
    };

    for (const auto& [left, right] : relationships) {
        dsu.unite(left, right);
    }

    for (const auto& [representative, members] : dsu.classes()) {
        std::cout << "Representative " << representative << ": ";

        print_class(members);
        std::cout << '\n';
    }

    std::cout << "0 and 6 equivalent: "
              << (dsu.find(0) == dsu.find(6)) << '\n';

    std::cout << "1 and 8 equivalent: "
              << (dsu.find(1) == dsu.find(8)) << '\n';
}

void demonstrate_partition_failure() {
    std::cout << "\n=== Partition validation failures ===\n";

    std::set<int> universe{1, 2, 3, 4, 5, 6};

    const std::vector<std::vector<std::set<int>>> candidates{
        {
            {1, 2},
            {2, 3},
            {4, 5, 6}
        },
        {
            {1, 2},
            {3, 4}
        },
        {
            {1, 2},
            {},
            {3, 4, 5, 6}
        }
    };

    for (const auto& candidate : candidates) {
        std::string error;

        bool valid =
            validate_partition(universe, candidate, error);

        std::cout << "Valid: " << valid;

        if (!valid) {
            std::cout << " | Reason: " << error;
        }

        std::cout << '\n';
    }
}

int main() {
    std::cout << "EQUIVALENCE RELATIONS, CLASSES, PARTITIONS, AND QUOTIENT STRUCTURES\n";
    std::cout << std::string(78, '=') << '\n';

    demonstrate_basic_equivalence();
    demonstrate_partition_to_relation();
    demonstrate_customer_identity_quotient();
    demonstrate_quotient_operations();
    demonstrate_non_equivalence();
    demonstrate_union_find();
    demonstrate_partition_failure();

    std::cout << "\n=== Final verification ===\n";

    std::vector<int> verification_domain;
    for (int value = 0; value < 12; ++value) {
        verification_domain.push_back(value);
    }

    EquivalenceRelation<int> modulo_three(
        verification_domain,
        [](int x, int y) {
            return (x - y) % 3 == 0;
        },
        "congruence modulo 3"
    );

    if (!modulo_three.is_equivalence()) {
        throw std::logic_error(
            "Modulo-three congruence failed equivalence verification."
        );
    }

    if (modulo_three.classes().size() != 3) {
        throw std::logic_error(
            "The quotient Z/3Z should contain three equivalence classes."
        );
    }

    std::cout << "Modulo-three relation verified as reflexive, symmetric, "
                 "and transitive.\n";
    std::cout << "The quotient contains three classes.\n";
    std::cout << "All case-study checks passed.\n";

    return 0;
}
