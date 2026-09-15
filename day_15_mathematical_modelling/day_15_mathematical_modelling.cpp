/*
 * Mathematical Modeling
 * ======================
 *
 * Industry-style C++ case study:
 *
 *     Production Planning and Capacity Optimization System
 *
 * The program translates a manufacturing planning problem into:
 *     - decision variables
 *     - parameters
 *     - assumptions
 *     - constraints
 *     - objective function
 *     - feasibility checks
 *     - integer optimization
 *     - scenario analysis
 *     - sensitivity analysis
 *     - validation
 *
 * Compile:
 *     g++ -std=c++17 -O2 mathematical_modeling.cpp -o mathematical_modeling
 *
 * Run:
 *     ./mathematical_modeling
 *
 * Windows:
 *     mathematical_modeling.exe
 */

#include <algorithm>
#include <cassert>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

// ============================================================================
// 1. BASIC MATHEMATICAL MODEL
// ============================================================================

struct Product {
    string name;

    double sellingPrice;
    double variableCost;

    double laborHours;
    double machineHours;

    int maximumDemand;

    double contributionMargin() const {
        return sellingPrice - variableCost;
    }

    double contribution(int quantity) const {
        return contributionMargin() * quantity;
    }
};

struct ProductionPlan {
    int productAQuantity = 0;
    int productBQuantity = 0;

    double objectiveValue = 0.0;
};

// ============================================================================
// 2. PROBLEM DEFINITION
// ============================================================================

class ProductionPlanningModel {
private:
    Product productA;
    Product productB;

    double laborCapacity;
    double machineCapacity;
    double fixedCost;

public:
    ProductionPlanningModel(
        Product a,
        Product b,
        double labor,
        double machine,
        double fixed
    )
        : productA(std::move(a)),
          productB(std::move(b)),
          laborCapacity(labor),
          machineCapacity(machine),
          fixedCost(fixed) {

        validateParameters();
    }

    void validateParameters() const {
        if (productA.sellingPrice < 0 ||
            productB.sellingPrice < 0) {
            throw invalid_argument(
                "Selling prices cannot be negative."
            );
        }

        if (productA.variableCost < 0 ||
            productB.variableCost < 0) {
            throw invalid_argument(
                "Variable costs cannot be negative."
            );
        }

        if (productA.maximumDemand < 0 ||
            productB.maximumDemand < 0) {
            throw invalid_argument(
                "Demand limits cannot be negative."
            );
        }

        if (laborCapacity < 0 ||
            machineCapacity < 0 ||
            fixedCost < 0) {
            throw invalid_argument(
                "Resource capacities and fixed cost cannot be negative."
            );
        }

        if (productA.contributionMargin() <= 0 ||
            productB.contributionMargin() <= 0) {
            throw invalid_argument(
                "Both products must have positive contribution margins."
            );
        }
    }

    // ========================================================================
    // 3. MATHEMATICAL CONSTRAINTS
    // ========================================================================

    bool isFeasible(int quantityA, int quantityB) const {
        if (quantityA < 0 || quantityB < 0) {
            return false;
        }

        if (quantityA > productA.maximumDemand ||
            quantityB > productB.maximumDemand) {
            return false;
        }

        const double laborUsed =
            quantityA * productA.laborHours +
            quantityB * productB.laborHours;

        const double machineUsed =
            quantityA * productA.machineHours +
            quantityB * productB.machineHours;

        return laborUsed <= laborCapacity + 1e-9 &&
               machineUsed <= machineCapacity + 1e-9;
    }

    double laborUsed(int quantityA, int quantityB) const {
        return quantityA * productA.laborHours +
               quantityB * productB.laborHours;
    }

    double machineUsed(int quantityA, int quantityB) const {
        return quantityA * productA.machineHours +
               quantityB * productB.machineHours;
    }

    // ========================================================================
    // 4. OBJECTIVE FUNCTION
    // ========================================================================

    double objective(int quantityA, int quantityB) const {
        if (!isFeasible(quantityA, quantityB)) {
            throw invalid_argument(
                "Cannot evaluate objective for an infeasible plan."
            );
        }

        /*
         * Profit:
         *
         *     P(x,y)
         *       = contribution_A*x
         *       + contribution_B*y
         *       - fixedCost
         *
         * The fixed cost does not change which feasible plan maximizes
         * contribution if it is constant across all plans.
         */
        return
            productA.contribution(quantityA) +
            productB.contribution(quantityB) -
            fixedCost;
    }

    // ========================================================================
    // 5. BRUTE-FORCE INTEGER OPTIMIZATION
    // ========================================================================

    ProductionPlan optimize() const {
        ProductionPlan best;
        best.objectiveValue =
            -numeric_limits<double>::infinity();

        /*
         * The search space is bounded by demand limits and resource
         * constraints. Because the decision variables are integer-valued,
         * every candidate production plan is explicitly evaluated.
         *
         * Complexity:
         *
         *     O(D_A * D_B)
         *
         * in the worst case, where D_A and D_B are demand bounds.
         *
         * This is appropriate for a small educational model. Large-scale
         * production systems would normally use integer programming,
         * branch-and-bound, dynamic programming, or specialized solvers.
         */
        for (int quantityA = 0;
             quantityA <= productA.maximumDemand;
             ++quantityA) {

            for (int quantityB = 0;
                 quantityB <= productB.maximumDemand;
                 ++quantityB) {

                if (!isFeasible(quantityA, quantityB)) {
                    continue;
                }

                const double value =
                    objective(quantityA, quantityB);

                if (value > best.objectiveValue) {
                    best.productAQuantity = quantityA;
                    best.productBQuantity = quantityB;
                    best.objectiveValue = value;
                }
            }
        }

        return best;
    }

    // ========================================================================
    // 6. SCENARIO ANALYSIS
    // ========================================================================

    ProductionPlan optimizeScenario(
        double priceMultiplier,
        double costMultiplier
    ) const {
        if (priceMultiplier <= 0 ||
            costMultiplier <= 0) {
            throw invalid_argument(
                "Scenario multipliers must be positive."
            );
        }

        ProductionPlan best;
        best.objectiveValue =
            -numeric_limits<double>::infinity();

        for (int quantityA = 0;
             quantityA <= productA.maximumDemand;
             ++quantityA) {

            for (int quantityB = 0;
                 quantityB <= productB.maximumDemand;
                 ++quantityB) {

                if (!isFeasible(quantityA, quantityB)) {
                    continue;
                }

                const double contributionA =
                    quantityA *
                    (
                        productA.sellingPrice * priceMultiplier -
                        productA.variableCost * costMultiplier
                    );

                const double contributionB =
                    quantityB *
                    (
                        productB.sellingPrice * priceMultiplier -
                        productB.variableCost * costMultiplier
                    );

                const double profit =
                    contributionA +
                    contributionB -
                    fixedCost;

                if (profit > best.objectiveValue) {
                    best.productAQuantity = quantityA;
                    best.productBQuantity = quantityB;
                    best.objectiveValue = profit;
                }
            }
        }

        return best;
    }

    // ========================================================================
    // 7. SENSITIVITY ANALYSIS
    // ========================================================================

    double profitWithChangedPriceA(
        const ProductionPlan& plan,
        double newPrice
    ) const {
        if (newPrice < 0) {
            throw invalid_argument(
                "New price cannot be negative."
            );
        }

        const double contributionA =
            (newPrice - productA.variableCost) *
            plan.productAQuantity;

        const double contributionB =
            productB.contribution(plan.productBQuantity);

        return contributionA + contributionB - fixedCost;
    }

    // ========================================================================
    // 8. REPORTING
    // ========================================================================

    void printPlan(
        const ProductionPlan& plan,
        const string& label
    ) const {
        cout << "\n" << label << "\n";
        cout << string(60, '-') << "\n";

        cout << "Product A quantity: "
             << plan.productAQuantity << "\n";

        cout << "Product B quantity: "
             << plan.productBQuantity << "\n";

        cout << fixed << setprecision(2);

        cout << "Labor used: "
             << laborUsed(
                    plan.productAQuantity,
                    plan.productBQuantity
                )
             << " / "
             << laborCapacity
             << "\n";

        cout << "Machine used: "
             << machineUsed(
                    plan.productAQuantity,
                    plan.productBQuantity
                )
             << " / "
             << machineCapacity
             << "\n";

        cout << "Profit: "
             << plan.objectiveValue
             << "\n";
    }

    // ========================================================================
    // 9. MODEL DOCUMENTATION
    // ========================================================================

    void printModelDefinition() const {
        cout << "\nMATHEMATICAL MODEL\n";
        cout << string(60, '=') << "\n";

        cout << "Decision variables:\n";
        cout << "  x = units of " << productA.name << "\n";
        cout << "  y = units of " << productB.name << "\n";

        cout << "\nObjective:\n";
        cout << "  maximize contribution profit\n";

        cout << "\nConstraints:\n";
        cout << "  labor_A*x + labor_B*y <= labor capacity\n";
        cout << "  machine_A*x + machine_B*y <= machine capacity\n";
        cout << "  0 <= x <= demand_A\n";
        cout << "  0 <= y <= demand_B\n";
        cout << "  x and y are integers\n";

        cout << "\nAssumptions:\n";
        cout << "  - unit prices are constant within a scenario\n";
        cout << "  - variable costs are constant per unit\n";
        cout << "  - resource consumption is linear\n";
        cout << "  - products are indivisible\n";
        cout << "  - fixed cost is independent of production quantity\n";
        cout << "  - demand limits are known\n";
    }
};

// ============================================================================
// 10. VALIDATION UTILITIES
// ============================================================================

void requireClose(
    double actual,
    double expected,
    double tolerance,
    const string& message
) {
    if (fabs(actual - expected) > tolerance) {
        throw runtime_error(
            message +
            " | actual=" + to_string(actual) +
            " expected=" + to_string(expected)
        );
    }
}

void runModelTests(
    const ProductionPlanningModel& model
) {
    cout << "\nRUNNING MODEL TESTS\n";
    cout << string(60, '-') << "\n";

    assert(model.isFeasible(0, 0));
    assert(!model.isFeasible(-1, 0));

    ProductionPlan best = model.optimize();

    assert(best.productAQuantity >= 0);
    assert(best.productBQuantity >= 0);

    assert(
        model.isFeasible(
            best.productAQuantity,
            best.productBQuantity
        )
    );

    requireClose(
        model.objective(0, 0),
        -18000.0,
        1e-9,
        "Zero-production profit test failed"
    );

    cout << "All model tests passed.\n";
}

// ============================================================================
// 11. EDGE CASE DEMONSTRATION
// ============================================================================

void demonstrateEdgeCases(
    const ProductionPlanningModel& model
) {
    cout << "\nEDGE CASES\n";
    cout << string(60, '-') << "\n";

    vector<pair<int, int>> testPlans = {
        {0, 0},
        {1, 0},
        {0, 1},
        {-1, 0},
        {1000, 1000}
    };

    for (const auto& [x, y] : testPlans) {
        cout << "Plan (" << x << ", " << y << "): ";

        if (model.isFeasible(x, y)) {
            cout << "feasible, profit="
                 << fixed << setprecision(2)
                 << model.objective(x, y)
                 << "\n";
        } else {
            cout << "infeasible\n";
        }
    }
}

// ============================================================================
// 12. SENSITIVITY REPORT
// ============================================================================

void demonstrateSensitivity(
    const ProductionPlanningModel& model,
    const ProductionPlan& bestPlan
) {
    cout << "\nPRICE SENSITIVITY FOR PRODUCT A\n";
    cout << string(60, '-') << "\n";

    vector<double> prices = {
        60.0,
        70.0,
        80.0,
        90.0,
        100.0
    };

    for (double price : prices) {
        double profit =
            model.profitWithChangedPriceA(
                bestPlan,
                price
            );

        cout << "Price A = "
             << fixed << setprecision(2)
             << price
             << ", profit = "
             << profit
             << "\n";
    }
}

// ============================================================================
// 13. SCENARIO REPORT
// ============================================================================

void demonstrateScenarios(
    const ProductionPlanningModel& model
) {
    cout << "\nSCENARIO ANALYSIS\n";
    cout << string(60, '-') << "\n";

    struct Scenario {
        string name;
        double priceMultiplier;
        double costMultiplier;
    };

    vector<Scenario> scenarios = {
        {"Pessimistic", 0.90, 1.10},
        {"Base",        1.00, 1.00},
        {"Optimistic",  1.10, 0.90}
    };

    for (const auto& scenario : scenarios) {
        ProductionPlan plan =
            model.optimizeScenario(
                scenario.priceMultiplier,
                scenario.costMultiplier
            );

        cout << scenario.name
             << ": A=" << plan.productAQuantity
             << ", B=" << plan.productBQuantity
             << ", profit=" << fixed
             << setprecision(2)
             << plan.objectiveValue
             << "\n";
    }
}

// ============================================================================
// 14. RESOURCE UTILIZATION
// ============================================================================

void explainResourceTradeOffs(
    const ProductionPlanningModel& model,
    const ProductionPlan& plan
) {
    cout << "\nRESOURCE UTILIZATION AND TRADE-OFFS\n";
    cout << string(60, '-') << "\n";

    const double labor =
        model.laborUsed(
            plan.productAQuantity,
            plan.productBQuantity
        );

    const double machine =
        model.machineUsed(
            plan.productAQuantity,
            plan.productBQuantity
        );

    cout << "The selected plan is constrained by finite resources.\n";
    cout << "Labor utilization: "
         << labor
         << "\n";

    cout << "Machine utilization: "
         << machine
         << "\n";

    cout << "\nThe objective function determines which feasible "
            "resource allocation is preferred.\n";

    cout << "A resource constraint may become a bottleneck when "
            "additional production of either product is impossible "
            "without violating that constraint.\n";
}

// ============================================================================
// 15. MAIN CASE STUDY
// ============================================================================

int main() {
    try {
        cout << "MATHEMATICAL MODELING CASE STUDY\n";
        cout << string(78, '=') << "\n";

        /*
         * Realistic manufacturing scenario:
         *
         * Product A:
         *     selling price = 80
         *     variable cost = 30
         *     labor = 2 hours
         *     machine = 3 hours
         *     demand limit = 1000
         *
         * Product B:
         *     selling price = 100
         *     variable cost = 40
         *     labor = 3 hours
         *     machine = 2 hours
         *     demand limit = 1000
         *
         * Factory:
         *     labor capacity = 100 hours
         *     machine capacity = 90 hours
         *     fixed cost = 18000
         *
         * Mathematical model:
         *
         *     maximize:
         *
         *       P(x,y) =
         *          (80-30)x + (100-40)y - 18000
         *
         *     subject to:
         *
         *       2x + 3y <= 100
         *       3x + 2y <= 90
         *       0 <= x <= 1000
         *       0 <= y <= 1000
         *       x,y ∈ Z
         */

        Product productA{
            "Product A",
            80.0,
            30.0,
            2.0,
            3.0,
            1000
        };

        Product productB{
            "Product B",
            100.0,
            40.0,
            3.0,
            2.0,
            1000
        };

        ProductionPlanningModel model(
            productA,
            productB,
            100.0,
            90.0,
            18000.0
        );

        model.printModelDefinition();

        ProductionPlan best = model.optimize();

        model.printPlan(
            best,
            "OPTIMAL INTEGER PRODUCTION PLAN"
        );

        explainResourceTradeOffs(model, best);

        demonstrateSensitivity(model, best);

        demonstrateScenarios(model);

        demonstrateEdgeCases(model);

        runModelTests(model);

        cout << "\nINTERPRETATION\n";
        cout << string(60, '-') << "\n";

        cout << "The computed solution is optimal only relative to the "
                "mathematical model and its assumptions.\n";

        cout << "Changing demand, prices, costs, resource capacities, "
                "or the objective can change the recommended plan.\n";

        cout << "The model is therefore a decision-support representation "
                "rather than a complete description of the real factory.\n";

        cout << "\nCASE STUDY COMPLETED SUCCESSFULLY\n";

        return 0;
    }
    catch (const exception& error) {
        cerr << "\nMODEL EXECUTION ERROR: "
             << error.what()
             << "\n";

        return 1;
    }
}
