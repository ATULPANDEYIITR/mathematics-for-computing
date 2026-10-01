#include <algorithm>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

class Poset {
public:
    using Element = std::string;
    using Pair = std::pair<Element, Element>;

private:
    std::set<Element> elements_;
    std::set<Pair> relation_;

public:
    Poset(
        std::set<Element> elements,
        std::set<Pair> relation
    )
        : elements_(std::move(elements)),
          relation_(std::move(relation)) {
        validate();
    }

    bool leq(const Element& a, const Element& b) const {
        return relation_.contains({a, b});
    }

    bool strictLess(const Element& a, const Element& b) const {
        return a != b && leq(a, b);
    }

    bool comparable(const Element& a, const Element& b) const {
        return leq(a, b) || leq(b, a);
    }

    bool isChain(const std::vector<Element>& subset) const {
        std::set<Element> unique(subset.begin(), subset.end());

        if (unique.size() != subset.size()) {
            return false;
        }

        for (const auto& element : unique) {
            if (!elements_.contains(element)) {
                return false;
            }
        }

        for (auto first = unique.begin(); first != unique.end(); ++first) {
            auto second = first;
            ++second;

            for (; second != unique.end(); ++second) {
                if (!comparable(*first, *second)) {
                    return false;
                }
            }
        }

        return true;
    }

    bool isAntichain(const std::vector<Element>& subset) const {
        std::set<Element> unique(subset.begin(), subset.end());

        if (unique.size() != subset.size()) {
            return false;
        }

        for (const auto& element : unique) {
            if (!elements_.contains(element)) {
                return false;
            }
        }

        for (auto first = unique.begin(); first != unique.end(); ++first) {
            auto second = first;
            ++second;

            for (; second != unique.end(); ++second) {
                if (comparable(*first, *second)) {
                    return false;
                }
            }
        }

        return true;
    }

    std::vector<Element> minimalElements() const {
        std::vector<Element> result;

        for (const auto& candidate : elements_) {
            bool hasLowerElement = false;

            for (const auto& other : elements_) {
                if (strictLess(other, candidate)) {
                    hasLowerElement = true;
                    break;
                }
            }

            if (!hasLowerElement) {
                result.push_back(candidate);
            }
        }

        return result;
    }

    std::vector<Element> maximalElements() const {
        std::vector<Element> result;

        for (const auto& candidate : elements_) {
            bool hasUpperElement = false;

            for (const auto& other : elements_) {
                if (strictLess(candidate, other)) {
                    hasUpperElement = true;
                    break;
                }
            }

            if (!hasUpperElement) {
                result.push_back(candidate);
            }
        }

        return result;
    }

    std::vector<Pair> coverRelations() const {
        std::vector<Pair> covers;

        for (const auto& [lower, upper] : relation_) {
            if (!strictLess(lower, upper)) {
                continue;
            }

            bool intermediate = false;

            for (const auto& middle : elements_) {
                if (
                    middle != lower &&
                    middle != upper &&
                    strictLess(lower, middle) &&
                    strictLess(middle, upper)
                ) {
                    intermediate = true;
                    break;
                }
            }

            if (!intermediate) {
                covers.push_back({lower, upper});
            }
        }

        return covers;
    }

    std::vector<std::vector<Element>> layers() const {
        std::set<Element> remaining = elements_;
        std::vector<std::vector<Element>> result;

        while (!remaining.empty()) {
            std::vector<Element> layer;

            for (const auto& candidate : remaining) {
                bool hasLowerRemaining = false;

                for (const auto& other : remaining) {
                    if (strictLess(other, candidate)) {
                        hasLowerRemaining = true;
                        break;
                    }
                }

                if (!hasLowerRemaining) {
                    layer.push_back(candidate);
                }
            }

            if (layer.empty()) {
                throw std::logic_error("Unable to layer a cyclic relation.");
            }

            for (const auto& element : layer) {
                remaining.erase(element);
            }

            result.push_back(layer);
        }

        return result;
    }

    const std::set<Element>& elements() const {
        return elements_;
    }

private:
    void validate() const {
        for (const auto& element : elements_) {
            if (!relation_.contains({element, element})) {
                throw std::invalid_argument(
                    "Relation is not reflexive at " + element
                );
            }
        }

        for (const auto& [a, b] : relation_) {
            if (!elements_.contains(a) || !elements_.contains(b)) {
                throw std::invalid_argument(
                    "Relation contains an unknown element."
                );
            }

            if (a != b && relation_.contains({b, a})) {
                throw std::invalid_argument(
                    "Relation violates antisymmetry."
                );
            }
        }

        for (const auto& [a, b] : relation_) {
            for (const auto& c : elements_) {
                if (relation_.contains({b, c}) &&
                    !relation_.contains({a, c})) {
                    throw std::invalid_argument(
                        "Relation violates transitivity."
                    );
                }
            }
        }
    }
};


/*
 * Case study:
 *
 * A software delivery organization has repository artifacts whose release
 * order is constrained by dependencies. The governance engine must determine
 * which artifacts can proceed independently and which are ordered.
 *
 * The dependency relation is converted into a poset where A <= B means that
 * A is required before B. The Hasse diagram stores only immediate
 * dependencies, eliminating edges that are implied transitively.
 */
class ReleaseGovernance {
public:
    using Task = std::string;

private:
    std::map<Task, std::set<Task>> prerequisites_;
    std::set<Task> completed_;

public:
    explicit ReleaseGovernance(
        std::map<Task, std::set<Task>> prerequisites
    )
        : prerequisites_(std::move(prerequisites)) {
        for (const auto& [task, prerequisites] : prerequisites_) {
            (void)task;

            for (const auto& prerequisite : prerequisites) {
                if (!prerequisites_.contains(prerequisite)) {
                    prerequisites_[prerequisite] = {};
                }
            }
        }

        validateAcyclic();
    }

    std::vector<Task> readyTasks() const {
        std::vector<Task> ready;

        for (const auto& [task, prerequisites] : prerequisites_) {
            if (completed_.contains(task)) {
                continue;
            }

            bool satisfied = std::all_of(
                prerequisites.begin(),
                prerequisites.end(),
                [this](const Task& prerequisite) {
                    return completed_.contains(prerequisite);
                }
            );

            if (satisfied) {
                ready.push_back(task);
            }
        }

        return ready;
    }

    void complete(const Task& task) {
        if (!prerequisites_.contains(task)) {
            throw std::invalid_argument("Unknown task: " + task);
        }

        const auto ready = readyTasks();

        if (std::find(ready.begin(), ready.end(), task) == ready.end()) {
            throw std::logic_error(
                "Task " + task + " is not ready because a prerequisite "
                "is incomplete."
            );
        }

        completed_.insert(task);
    }

    Poset asPoset() const {
        std::set<Poset::Element> elements;

        for (const auto& [task, prerequisites] : prerequisites_) {
            elements.insert(task);

            for (const auto& prerequisite : prerequisites) {
                elements.insert(prerequisite);
            }
        }

        std::set<Poset::Pair> relation;

        for (const auto& element : elements) {
            relation.insert({element, element});
        }

        /*
         * Each prerequisite edge is expanded through graph reachability.
         * This creates the transitive partial order rather than merely
         * storing direct dependency edges.
         */
        for (const auto& start : elements) {
            std::queue<Task> pending;
            std::set<Task> visited;

            auto direct = prerequisites_.find(start);

            if (direct != prerequisites_.end()) {
                for (const auto& prerequisite : direct->second) {
                    pending.push(prerequisite);
                }
            }

            while (!pending.empty()) {
                const Task current = pending.front();
                pending.pop();

                if (!visited.insert(current).second) {
                    continue;
                }

                relation.insert({current, start});

                auto next = prerequisites_.find(current);
                if (next != prerequisites_.end()) {
                    for (const auto& prerequisite : next->second) {
                        pending.push(prerequisite);
                    }
                }
            }
        }

        return Poset(elements, relation);
    }

private:
    void validateAcyclic() const {
        enum class State {
            Unvisited,
            Visiting,
            Visited
        };

        std::map<Task, State> states;

        for (const auto& [task, prerequisites] : prerequisites_) {
            (void)prerequisites;
            states[task] = State::Unvisited;
        }

        std::function<void(const Task&)> visit =
            [&](const Task& task) {
                if (states[task] == State::Visiting) {
                    throw std::invalid_argument(
                        "Dependency cycle detected at " + task
                    );
                }

                if (states[task] == State::Visited) {
                    return;
                }

                states[task] = State::Visiting;

                for (const auto& prerequisite :
                     prerequisites_.at(task)) {
                    visit(prerequisite);
                }

                states[task] = State::Visited;
            };

        for (const auto& [task, prerequisites] : prerequisites_) {
            (void)prerequisites;
            visit(task);
        }
    }
};


void printVector(
    const std::vector<std::string>& values
) {
    std::cout << "[";
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i > 0) {
            std::cout << ", ";
        }
        std::cout << values[i];
    }
    std::cout << "]\n";
}


void demonstratePoset() {
    std::cout << "PARTIAL ORDER CASE STUDY\n\n";

    /*
     * The system models a release pipeline:
     *
     * architecture
     *      |
     * implementation
     *      |
     *  +---+-----------+
     *  |               |
     * unit-tests    security-review
     *  +-------+-------+
     *          |
     *      release-candidate
     *
     * unit-tests and security-review are incomparable: neither is below the
     * other in the dependency order.
     */
    ReleaseGovernance governance({
        {"architecture", {}},
        {"implementation", {"architecture"}},
        {"unit-tests", {"implementation"}},
        {"security-review", {"implementation"}},
        {"release-candidate", {"unit-tests", "security-review"}},
        {"production-release", {"release-candidate"}}
    });

    std::cout << "Initial ready tasks: ";
    printVector(governance.readyTasks());

    governance.complete("architecture");

    std::cout << "After architecture: ";
    printVector(governance.readyTasks());

    governance.complete("implementation");

    std::cout << "After implementation: ";
    printVector(governance.readyTasks());

    const Poset poset = governance.asPoset();

    std::cout << "\nHasse diagram cover relations:\n";

    for (const auto& [lower, upper] : poset.coverRelations()) {
        std::cout << "  " << lower << " -> " << upper << "\n";
    }

    std::cout << "\nLayers:\n";

    const auto layers = poset.layers();

    for (std::size_t level = 0; level < layers.size(); ++level) {
        std::cout << "  level " << level << ": ";
        printVector(layers[level]);
    }

    const std::vector<std::string> independent = {
        "unit-tests",
        "security-review"
    };

    std::cout << "\nIndependent release checks form an antichain: "
              << std::boolalpha
              << poset.isAntichain(independent)
              << "\n";

    const std::vector<std::string> ordered = {
        "architecture",
        "implementation",
        "unit-tests"
    };

    std::cout << "Architecture -> implementation -> unit-tests is a chain: "
              << poset.isChain(ordered)
              << "\n";

    std::cout << "\nMinimal elements: ";
    printVector(poset.minimalElements());

    std::cout << "Maximal elements: ";
    printVector(poset.maximalElements());
}


void demonstrateFailures() {
    std::cout << "\nVALIDATION AND FAILURE MODES\n";

    try {
        Poset invalid(
            {"A", "B"},
            {
                {"A", "A"},
                {"B", "B"},
                {"A", "B"},
                {"B", "A"}
            }
        );

        (void)invalid;
    } catch (const std::exception& error) {
        std::cout << "Antisymmetry rejection: "
                  << error.what() << "\n";
    }

    try {
        Poset invalid(
            {"A", "B", "C"},
            {
                {"A", "A"},
                {"B", "B"},
                {"C", "C"},
                {"A", "B"},
                {"B", "C"}
            }
        );

        (void)invalid;
    } catch (const std::exception& error) {
        std::cout << "Transitivity rejection: "
                  << error.what() << "\n";
    }

    try {
        ReleaseGovernance cyclic({
            {"compile", {"test"}},
            {"test", {"compile"}}
        });

        (void)cyclic;
    } catch (const std::exception& error) {
        std::cout << "Cycle rejection: "
                  << error.what() << "\n";
    }

    try {
        ReleaseGovernance governance({
            {"compile", {}},
            {"test", {"compile"}}
        });

        governance.complete("test");
    } catch (const std::exception& error) {
        std::cout << "Invalid progression rejection: "
                  << error.what() << "\n";
    }
}


int main() {
    try {
        demonstratePoset();
        demonstrateFailures();
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
