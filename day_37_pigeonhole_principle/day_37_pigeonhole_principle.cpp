#include <algorithm>
#include <cmath>
#include <cstdint>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

/*
 * Pigeonhole Principle Case Study:
 * Repository Artifact Distribution and Collision Analysis
 *
 * The program models a large software artifact service that assigns objects
 * to finite storage partitions. The same reasoning applies to hash buckets,
 * cache partitions, database shards, finite identifiers, and modular
 * classification.
 *
 * The mathematical guarantee is:
 *
 *     maximum bucket occupancy >= ceil(objects / buckets)
 *
 * The program separates:
 * - deterministic guarantees from probabilistic observations,
 * - theoretical lower bounds from actual distributions,
 * - finite representation spaces from collision-resolution mechanisms.
 */

namespace pigeonhole {

std::size_t guaranteedOccupancy(
    std::size_t objects,
    std::size_t containers
) {
    if (containers == 0) {
        throw std::invalid_argument("container count must be positive");
    }

    if (objects == 0) {
        return 0;
    }

    return (objects + containers - 1) / containers;
}

std::size_t objectsForTarget(
    std::size_t containers,
    std::size_t target
) {
    if (containers == 0) {
        throw std::invalid_argument("container count must be positive");
    }

    if (target == 0) {
        throw std::invalid_argument("target must be positive");
    }

    return containers * (target - 1) + 1;
}

std::vector<std::size_t> balancedDistribution(
    std::size_t objects,
    std::size_t containers
) {
    if (containers == 0) {
        throw std::invalid_argument("container count must be positive");
    }

    std::vector<std::size_t> distribution(containers, 0);

    for (std::size_t i = 0; i < objects; ++i) {
        ++distribution[i % containers];
    }

    return distribution;
}

std::size_t maximumOccupancy(
    const std::vector<std::size_t>& distribution
) {
    if (distribution.empty()) {
        return 0;
    }

    return *std::max_element(
        distribution.begin(),
        distribution.end()
    );
}

} // namespace pigeonhole

class PartitionStore {
public:
    explicit PartitionStore(std::size_t partitionCount)
        : partitions_(partitionCount) {
        if (partitionCount == 0) {
            throw std::invalid_argument(
                "partition count must be positive"
            );
        }
    }

    std::size_t assign(
        const std::string& artifactId
    ) {
        std::size_t partition =
            std::hash<std::string>{}(artifactId) % partitions_.size();

        partitions_[partition].push_back(artifactId);

        return partition;
    }

    const std::vector<std::vector<std::string>>& partitions() const {
        return partitions_;
    }

private:
    std::vector<std::vector<std::string>> partitions_;
};

void printDistribution(
    const std::vector<std::size_t>& distribution
) {
    for (std::size_t index = 0; index < distribution.size(); ++index) {
        std::cout
            << "Partition " << index
            << ": " << distribution[index]
            << " object(s)\n";
    }
}

void basicPrincipleCase() {
    std::cout << "\n=== Basic Pigeonhole Principle ===\n";

    const std::size_t developers = 13;
    const std::size_t weekdays = 7;

    const std::size_t guaranteed =
        pigeonhole::guaranteedOccupancy(
            developers,
            weekdays
        );

    std::cout
        << developers
        << " developers assigned to "
        << weekdays
        << " weekdays guarantees a day containing at least "
        << guaranteed
        << " developers.\n";
}

void generalizedCase() {
    std::cout << "\n=== Generalized Principle ===\n";

    const std::size_t objects = 1001;
    const std::size_t containers = 16;

    const std::size_t guaranteed =
        pigeonhole::guaranteedOccupancy(
            objects,
            containers
        );

    std::cout
        << objects
        << " objects across "
        << containers
        << " containers guarantees occupancy of at least "
        << guaranteed
        << ".\n";

    const std::size_t target = 70;

    std::cout
        << "Objects needed to guarantee a container with "
        << target
        << " objects: "
        << pigeonhole::objectsForTarget(
            containers,
            target
        )
        << "\n";
}

void storagePartitionCase() {
    std::cout
        << "\n=== Storage Partition Case Study ===\n";

    const std::size_t artifactCount = 53;
    const std::size_t partitionCount = 8;

    const auto theoretical =
        pigeonhole::balancedDistribution(
            artifactCount,
            partitionCount
        );

    std::cout << "Best possible balanced distribution:\n";
    printDistribution(theoretical);

    const std::size_t bound =
        pigeonhole::guaranteedOccupancy(
            artifactCount,
            partitionCount
        );

    std::cout
        << "Theoretical minimum possible value of the largest "
        << "partition: "
        << bound
        << "\n";

    std::cout
        << "Actual maximum in this balanced assignment: "
        << pigeonhole::maximumOccupancy(theoretical)
        << "\n";
}

void actualHashDistributionCase() {
    std::cout
        << "\n=== Actual Hash-Based Distribution ===\n";

    const std::size_t artifactCount = 100;
    const std::size_t partitionCount = 7;

    PartitionStore store(partitionCount);

    for (std::size_t i = 0; i < artifactCount; ++i) {
        store.assign(
            "build-artifact-" + std::to_string(i)
        );
    }

    std::vector<std::size_t> distribution;

    for (const auto& partition : store.partitions()) {
        distribution.push_back(partition.size());
    }

    printDistribution(distribution);

    const std::size_t bound =
        pigeonhole::guaranteedOccupancy(
            artifactCount,
            partitionCount
        );

    std::cout
        << "Pigeonhole guarantee: some partition has at least "
        << bound
        << " artifact(s).\n";

    std::cout
        << "Observed maximum: "
        << pigeonhole::maximumOccupancy(distribution)
        << "\n";

    /*
     * The bound is deterministic. The observed maximum depends on the hash
     * function and input distribution. A good hash can improve balance but
     * cannot defeat the finite-space counting argument.
     */
}

void modularArithmeticCase() {
    std::cout << "\n=== Modular Arithmetic Case ===\n";

    const std::size_t modulus = 9;
    const std::size_t integerCount = 50;

    std::map<std::size_t, std::vector<std::size_t>> residueGroups;

    for (std::size_t value = 0; value < integerCount; ++value) {
        residueGroups[value % modulus].push_back(value);
    }

    for (const auto& [residue, values] : residueGroups) {
        std::cout << "Residue " << residue << ": ";

        for (std::size_t value : values) {
            std::cout << value << ' ';
        }

        std::cout << '\n';
    }

    std::cout
        << "At least "
        << pigeonhole::guaranteedOccupancy(
            integerCount,
            modulus
        )
        << " integers must share one residue class.\n";
}

void finiteIdentifierCase() {
    std::cout << "\n=== Finite Identifier Space ===\n";

    const std::size_t alphabetSize = 16;
    const std::size_t identifierLength = 4;

    std::size_t identifierSpace = 1;

    for (std::size_t i = 0; i < identifierLength; ++i) {
        identifierSpace *= alphabetSize;
    }

    std::cout
        << "Identifier space: "
        << identifierSpace
        << "\n";

    std::cout
        << "Assignments required to force a duplicate: "
        << identifierSpace + 1
        << "\n";
}

void bitPatternCase() {
    std::cout << "\n=== Finite Bit Pattern Space ===\n";

    const std::size_t bitWidth = 10;
    const std::size_t patterns = std::size_t{1} << bitWidth;
    const std::size_t logicalStates = patterns + 1;

    std::cout
        << bitWidth
        << "-bit representation has "
        << patterns
        << " possible patterns.\n";

    std::cout
        << logicalStates
        << " distinct logical states cannot all receive unique "
        << bit patterns.\n";

    std::cout
        << "At least two logical states must share a representation "
        << "if the mapping is total.\n";
}

void duplicateDetectionCase() {
    std::cout << "\n=== Duplicate Detection ===\n";

    const std::vector<std::string> keys = {
        "REQ-001",
        "REQ-002",
        "REQ-003",
        "REQ-004",
        "REQ-002",
        "REQ-005"
    };

    std::unordered_map<std::string, std::size_t> firstSeen;

    for (std::size_t index = 0; index < keys.size(); ++index) {
        const auto& key = keys[index];

        auto [iterator, inserted] =
            firstSeen.emplace(key, index);

        if (!inserted) {
            std::cout
                << "Duplicate key " << key
                << " found at positions "
                << iterator->second
                << " and "
                << index
                << ".\n";
            break;
        }
    }
}

void targetOccupancyCase() {
    std::cout << "\n=== Target Occupancy Threshold ===\n";

    const std::size_t partitions = 12;
    const std::size_t target = 10;

    const std::size_t required =
        pigeonhole::objectsForTarget(
            partitions,
            target
        );

    std::cout
        << required
        << " objects are required to force at least one of "
        << partitions
        << " partitions to contain "
        << target
        << " objects.\n";
}

void probabilityVersusGuaranteeCase() {
    std::cout
        << "\n=== Probability Versus Guarantee ===\n";

    std::mt19937 generator(20261007);
    std::uniform_int_distribution<int> distribution(0, 364);

    const int people = 23;
    const int days = 365;
    const int trials = 3000;

    int collisionTrials = 0;

    for (int trial = 0; trial < trials; ++trial) {
        std::set<int> occupied;

        for (int person = 0; person < people; ++person) {
            occupied.insert(distribution(generator));
        }

        if (static_cast<int>(occupied.size()) < people) {
            ++collisionTrials;
        }
    }

    const double frequency =
        static_cast<double>(collisionTrials) /
        static_cast<double>(trials);

    std::cout
        << "Observed collision frequency for "
        << people
        << " random assignments to "
        << days
        << " days: "
        << std::fixed
        << std::setprecision(3)
        << frequency
        << "\n";

    std::cout
        << "For 366 people and 365 days, a collision is guaranteed "
        << "without probability calculations.\n";
}

void edgeCaseValidation() {
    std::cout << "\n=== Validation and Edge Cases ===\n";

    const std::vector<std::pair<std::size_t, std::size_t>> valid = {
        {0, 5},
        {1, 1},
        {5, 5},
        {6, 5},
        {100, 7}
    };

    for (const auto& [objects, containers] : valid) {
        std::cout
            << objects
            << " objects / "
            << containers
            << " containers -> "
            << pigeonhole::guaranteedOccupancy(
                objects,
                containers
            )
            << "\n";
    }

    try {
        pigeonhole::guaranteedOccupancy(10, 0);
    } catch (const std::exception& error) {
        std::cout
            << "Rejected invalid input: "
            << error.what()
            << "\n";
    }
}

void complexityCase() {
    std::cout << "\n=== Complexity ===\n";

    std::cout
        << "Direct ceil(n/k) calculation: O(1) time and O(1) space.\n";

    std::cout
        << "Explicit occupancy counting: O(n) time and O(k) space.\n";

    std::cout
        << "Hash-based duplicate detection: expected O(n) time and O(n) "
        << "additional space.\n";

    std::cout
        << "The mathematical principle itself does not require enumerating "
        << "all assignments.\n";
}

int main() {
    try {
        std::cout
            << "PIGEONHOLE PRINCIPLE: COMPUTING CASE STUDY\n";

        basicPrincipleCase();
        generalizedCase();
        storagePartitionCase();
        actualHashDistributionCase();
        modularArithmeticCase();
        finiteIdentifierCase();
        bitPatternCase();
        duplicateDetectionCase();
        targetOccupancyCase();
        probabilityVersusGuaranteeCase();
        edgeCaseValidation();
        complexityCase();

        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }
}
