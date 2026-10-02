#include <algorithm>
#include <cstdint>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

/*
 * Combinatorics Fundamentals
 *
 * Technical case study:
 * A deployment-platform governance engine estimates how many valid
 * deployment configurations exist before allowing an operations team to
 * choose among them.
 *
 * The system demonstrates:
 *   - Sum rule for mutually exclusive deployment channels
 *   - Product rule for environment/region/window choices
 *   - Dependent choices when resources cannot be reused
 *   - Restricted configurations
 *   - Exact combinatorial calculations
 *   - Inclusion-exclusion for overlapping capability groups
 *   - Validation and failure handling
 *   - Complexity considerations
 *
 * Compile:
 *   g++ -std=c++17 -Wall -Wextra -pedantic combinatorics.cpp -o combinatorics
 */

using Count = std::uint64_t;


// -----------------------------------------------------------------------------
// Validation helpers
// -----------------------------------------------------------------------------

void requireNonNegative(Count value, const std::string& name)
{
    (void)value;
    (void)name;
}

Count checkedAdd(Count left, Count right)
{
    if (right > std::numeric_limits<Count>::max() - left) {
        throw std::overflow_error("Counting addition overflow.");
    }

    return left + right;
}

Count checkedMultiply(Count left, Count right)
{
    if (left != 0 &&
        right > std::numeric_limits<Count>::max() / left) {
        throw std::overflow_error("Counting multiplication overflow.");
    }

    return left * right;
}


// -----------------------------------------------------------------------------
// Fundamental counting rules
// -----------------------------------------------------------------------------

Count sumRule(const std::vector<Count>& alternatives)
{
    Count total = 0;

    for (Count count : alternatives) {
        total = checkedAdd(total, count);
    }

    return total;
}

Count productRule(const std::vector<Count>& stages)
{
    Count total = 1;

    for (Count count : stages) {
        total = checkedMultiply(total, count);
    }

    return total;
}


// -----------------------------------------------------------------------------
// Combinatorial extensions
// -----------------------------------------------------------------------------

Count permutationCount(Count n, Count r)
{
    if (r > n) {
        throw std::invalid_argument("Permutation requires r <= n.");
    }

    Count result = 1;

    for (Count position = 0; position < r; ++position) {
        result = checkedMultiply(result, n - position);
    }

    return result;
}

Count combinationCount(Count n, Count r)
{
    if (r > n) {
        throw std::invalid_argument("Combination requires r <= n.");
    }

    // C(n,r) = C(n,n-r). Using the smaller side reduces multiplication work.
    r = std::min(r, n - r);

    Count result = 1;

    for (Count i = 1; i <= r; ++i) {
        // For the case study's moderate values, the intermediate product
        // fits into uint64_t. A production arbitrary-precision implementation
        // would be required for unrestricted large inputs.
        Count numerator = n - r + i;

        result = checkedMultiply(result, numerator);

        if (result % i != 0) {
            throw std::overflow_error(
                "Intermediate combination arithmetic lost exact divisibility."
            );
        }

        result /= i;
    }

    return result;
}


// -----------------------------------------------------------------------------
// Deployment model
// -----------------------------------------------------------------------------

enum class DeploymentChannel {
    PublicCloud,
    PrivateCloud,
    Edge
};

std::string channelName(DeploymentChannel channel)
{
    switch (channel) {
        case DeploymentChannel::PublicCloud:
            return "Public Cloud";
        case DeploymentChannel::PrivateCloud:
            return "Private Cloud";
        case DeploymentChannel::Edge:
            return "Edge";
    }

    return "Unknown";
}

struct DeploymentChannelModel {
    DeploymentChannel channel;
    Count regions;
    Count environments;
    Count deploymentWindows;
    bool allowsProduction;
};

Count channelConfigurationCount(const DeploymentChannelModel& channel)
{
    if (!channel.allowsProduction) {
        // A channel without production is still useful, but its environment
        // count explicitly excludes production.
    }

    return productRule({
        channel.regions,
        channel.environments,
        channel.deploymentWindows
    });
}


// -----------------------------------------------------------------------------
// Governance engine
// -----------------------------------------------------------------------------

struct RepositoryPolicy {
    bool productionRequiresTwoReviewers;
    bool stagingRequiresOneReviewer;
    bool requireSuccessfulChecks;
    bool prohibitDirectProductionPush;
};

struct DeploymentRequest {
    DeploymentChannel channel;
    std::string environment;
    std::string region;
    std::string window;
    std::set<std::string> reviewers;
    bool checksPassed;
    bool directPush;
};

struct EvaluationResult {
    bool accepted;
    std::string reason;
};

class DeploymentGovernanceEngine {
public:
    explicit DeploymentGovernanceEngine(RepositoryPolicy policy)
        : policy_(policy)
    {
    }

    EvaluationResult evaluate(
        const DeploymentRequest& request
    ) const
    {
        if (request.environment.empty() ||
            request.region.empty() ||
            request.window.empty()) {
            return {
                false,
                "Environment, region, and deployment window are required."
            };
        }

        if (request.directPush &&
            request.environment == "production" &&
            policy_.prohibitDirectProductionPush) {
            return {
                false,
                "Direct production pushes are prohibited by policy."
            };
        }

        if (policy_.requireSuccessfulChecks &&
            !request.checksPassed) {
            return {
                false,
                "Required validation checks have not passed."
            };
        }

        if (request.environment == "production" &&
            policy_.productionRequiresTwoReviewers &&
            request.reviewers.size() < 2) {
            return {
                false,
                "Production requires at least two distinct reviewers."
            };
        }

        if (request.environment == "staging" &&
            policy_.stagingRequiresOneReviewer &&
            request.reviewers.empty()) {
            return {
                false,
                "Staging requires at least one reviewer."
            };
        }

        return {
            true,
            "Deployment configuration satisfies the governance policy."
        };
    }

private:
    RepositoryPolicy policy_;
};


// -----------------------------------------------------------------------------
// Counting a governance configuration space
// -----------------------------------------------------------------------------

Count countGovernedConfigurations(
    const std::vector<DeploymentChannelModel>& channels
)
{
    // The channel is an exclusive alternative. Therefore the total number
    // of complete configurations is the sum of each channel's internal
    // product count.
    Count total = 0;

    for (const auto& channel : channels) {
        Count channelCount = channelConfigurationCount(channel);

        std::cout
            << "  "
            << channelName(channel.channel)
            << ": "
            << channelCount
            << " configurations\n";

        total = checkedAdd(total, channelCount);
    }

    return total;
}


// -----------------------------------------------------------------------------
// Reviewer assignment model
// -----------------------------------------------------------------------------

Count countReviewerAssignments(
    Count availableReviewers,
    Count requiredReviewers
)
{
    // Reviewers occupy distinct roles. The first role has n choices, the
    // second has n-1, and so on. This is a dependent product.
    return permutationCount(
        availableReviewers,
        requiredReviewers
    );
}


// -----------------------------------------------------------------------------
// Capability overlap
// -----------------------------------------------------------------------------

Count countCapabilityUnion(
    Count platformEngineers,
    Count securityEngineers,
    Count engineersWithBoth
)
{
    if (engineersWithBoth > platformEngineers ||
        engineersWithBoth > securityEngineers) {
        throw std::invalid_argument(
            "Intersection cannot exceed either capability group."
        );
    }

    // The intersection is subtracted once because direct addition counts it
    // twice.
    return platformEngineers +
           securityEngineers -
           engineersWithBoth;
}


// -----------------------------------------------------------------------------
// Practical scenario
// -----------------------------------------------------------------------------

void runCaseStudy()
{
    std::cout << "============================================================\n";
    std::cout << "COMBINATORICS GOVERNANCE ENGINE\n";
    std::cout << "============================================================\n\n";

    RepositoryPolicy policy{
        true,   // Production requires two reviewers.
        true,   // Staging requires one reviewer.
        true,   // Validation checks are mandatory.
        true    // Direct production pushes are prohibited.
    };

    DeploymentGovernanceEngine engine(policy);

    std::vector<DeploymentChannelModel> channels{
        {
            DeploymentChannel::PublicCloud,
            4,  // regions
            3,  // environments
            5,  // deployment windows
            true
        },
        {
            DeploymentChannel::PrivateCloud,
            2,
            2,
            4,
            true
        },
        {
            DeploymentChannel::Edge,
            6,
            1,
            3,
            false
        }
    };

    std::cout << "Channel-specific configuration counts:\n";

    Count totalConfigurations =
        countGovernedConfigurations(channels);

    std::cout
        << "\nTotal configurations across exclusive channels: "
        << totalConfigurations
        << "\n";

    std::cout << "\nReviewer assignment counts:\n";

    Count twoReviewerAssignments =
        countReviewerAssignments(6, 2);

    std::cout
        << "  Ordered assignments of two distinct reviewers from six: "
        << twoReviewerAssignments
        << "\n";

    std::cout << "\nCapability overlap:\n";

    Count engineersWithPlatformOrSecurity =
        countCapabilityUnion(
            80,
            65,
            35
        );

    std::cout
        << "  Engineers with platform or security capability: "
        << engineersWithPlatformOrSecurity
        << "\n";

    std::cout << "\nPolicy evaluation:\n";

    DeploymentRequest acceptedRequest{
        DeploymentChannel::PublicCloud,
        "production",
        "India",
        "night",
        {"reviewer-a", "reviewer-b"},
        true,
        false
    };

    EvaluationResult acceptedResult =
        engine.evaluate(acceptedRequest);

    std::cout
        << "  Valid production request: "
        << (acceptedResult.accepted ? "accepted" : "rejected")
        << "\n";
    std::cout
        << "  Reason: "
        << acceptedResult.reason
        << "\n";

    DeploymentRequest rejectedRequest{
        DeploymentChannel::PublicCloud,
        "production",
        "India",
        "night",
        {"reviewer-a"},
        true,
        false
    };

    EvaluationResult rejectedResult =
        engine.evaluate(rejectedRequest);

    std::cout
        << "\n  Production request with one reviewer: "
        << (rejectedResult.accepted ? "accepted" : "rejected")
        << "\n";
    std::cout
        << "  Reason: "
        << rejectedResult.reason
        << "\n";

    DeploymentRequest failedChecksRequest{
        DeploymentChannel::PrivateCloud,
        "staging",
        "Europe",
        "morning",
        {"reviewer-c"},
        false,
        false
    };

    EvaluationResult failedChecksResult =
        engine.evaluate(failedChecksRequest);

    std::cout
        << "\n  Staging request with failed checks: "
        << (failedChecksResult.accepted ? "accepted" : "rejected")
        << "\n";
    std::cout
        << "  Reason: "
        << failedChecksResult.reason
        << "\n";

    DeploymentRequest directPushRequest{
        DeploymentChannel::PublicCloud,
        "production",
        "US",
        "night",
        {"reviewer-a", "reviewer-b"},
        true,
        true
    };

    EvaluationResult directPushResult =
        engine.evaluate(directPushRequest);

    std::cout
        << "\n  Direct production push: "
        << (directPushResult.accepted ? "accepted" : "rejected")
        << "\n";
    std::cout
        << "  Reason: "
        << directPushResult.reason
        << "\n";
}


// -----------------------------------------------------------------------------
// Verification
// -----------------------------------------------------------------------------

void runTests()
{
    std::cout << "\n============================================================\n";
    std::cout << "VERIFICATION\n";
    std::cout << "============================================================\n";

    if (sumRule({3, 4, 5}) != 12) {
        throw std::runtime_error("Sum rule verification failed.");
    }

    if (productRule({3, 4, 5}) != 60) {
        throw std::runtime_error("Product rule verification failed.");
    }

    if (permutationCount(5, 2) != 20) {
        throw std::runtime_error("Permutation verification failed.");
    }

    if (combinationCount(5, 2) != 10) {
        throw std::runtime_error("Combination verification failed.");
    }

    if (countCapabilityUnion(70, 50, 20) != 100) {
        throw std::runtime_error(
            "Inclusion-exclusion verification failed."
        );
    }

    bool invalidPermutationRejected = false;

    try {
        (void)permutationCount(3, 5);
    }
    catch (const std::invalid_argument&) {
        invalidPermutationRejected = true;
    }

    if (!invalidPermutationRejected) {
        throw std::runtime_error(
            "Invalid permutation input was not rejected."
        );
    }

    bool overflowDetected = false;

    try {
        (void)productRule({
            std::numeric_limits<Count>::max(),
            2
        });
    }
    catch (const std::overflow_error&) {
        overflowDetected = true;
    }

    if (!overflowDetected) {
        throw std::runtime_error(
            "Counting overflow was not detected."
        );
    }

    std::cout << "All verification tests passed.\n";
}


// -----------------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------------

int main()
{
    try {
        runCaseStudy();
        runTests();

        std::cout << "\nComplexity characteristics:\n";
        std::cout
            << "  Product-rule evaluation is O(k) for k stages.\n";
        std::cout
            << "  P(n,r) calculation is O(r) with iterative multiplication.\n";
        std::cout
            << "  C(n,r) calculation is O(min(r,n-r)) for moderate values.\n";
        std::cout
            << "  Counting formulas avoid enumerating every configuration.\n";

        std::cout << "\nThe case study completed successfully.\n";

        return 0;
    }
    catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }
}
