/*
 * Recurrence Proofs: Industry-Style Algorithm Analysis Case Study
 *
 * Modern standard:
 *     C++17 or later
 *
 * Scenario:
 *     A document-processing service receives large collections of records.
 *     The service must sort records, search indexed records, calculate
 *     recursively defined metrics, and reason about the running time of the
 *     algorithms.
 *
 * The program develops the system in stages:
 *
 *     1. Recursive mathematical definitions
 *     2. Recurrence-defined metrics
 *     3. Recursive binary search
 *     4. Merge sort and its recurrence
 *     5. Quicksort and partition-dependent recurrences
 *     6. Memoization for overlapping subproblems
 *     7. Structural recursion over a tree
 *     8. Induction-oriented correctness checks
 *     9. Recurrence-tree measurements
 *    10. Master-Theorem classification
 *
 * The executable checks are finite computational validations. They do not
 * replace mathematical proofs over infinite domains. Formal induction is
 * represented explicitly in comments and through functions that verify the
 * relevant algebraic transformation for finite test ranges.
 */

#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstddef>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using std::cout;
using std::endl;
using std::size_t;
using std::string;
using std::vector;


// ============================================================================
// Section 1: Validation utilities
// ============================================================================

void requireNonNegative(int value, const string& parameterName)
{
    if (value < 0)
    {
        throw std::invalid_argument(parameterName + " must be non-negative");
    }
}


// ============================================================================
// Section 2: Recursive mathematical definitions
// ============================================================================

long long factorial(int n)
{
    /*
     * Recursive definition:
     *
     *     0! = 1
     *     n! = n(n-1)! for n >= 1
     *
     * The function uses long long. Very large factorials overflow this type,
     * which is an intentional example of a practical implementation limit.
     */
    requireNonNegative(n, "n");

    if (n == 0)
    {
        return 1;
    }

    return static_cast<long long>(n) * factorial(n - 1);
}


long long fibonacciRecursive(int n)
{
    /*
     *     F(0) = 0
     *     F(1) = 1
     *     F(n) = F(n-1) + F(n-2)
     *
     * This direct implementation has exponential recursive work.
     */
    requireNonNegative(n, "n");

    if (n < 2)
    {
        return n;
    }

    return fibonacciRecursive(n - 1) + fibonacciRecursive(n - 2);
}


long long fibonacciMemoized(
    int n,
    std::map<int, long long>& memo)
{
    /*
     * Memoization preserves the mathematical recurrence while preventing
     * repeated evaluation of identical subproblems.
     */
    requireNonNegative(n, "n");

    auto found = memo.find(n);
    if (found != memo.end())
    {
        return found->second;
    }

    if (n < 2)
    {
        memo[n] = n;
        return n;
    }

    memo[n] =
        fibonacciMemoized(n - 1, memo) +
        fibonacciMemoized(n - 2, memo);

    return memo[n];
}


long long fibonacciIterative(int n)
{
    requireNonNegative(n, "n");

    long long previous = 0;
    long long current = 1;

    for (int index = 0; index < n; ++index)
    {
        const long long next = previous + current;
        previous = current;
        current = next;
    }

    return previous;
}


// ============================================================================
// Section 3: Recurrence-defined business metric
// ============================================================================

long long cumulativeWork(int n)
{
    /*
     * Model a batch-processing metric:
     *
     *     W(0) = 0
     *     W(n) = W(n-1) + n
     *
     * Therefore:
     *
     *     W(n) = n(n+1)/2
     *
     * This recurrence occurs whenever the nth stage adds n units of work.
     */
    requireNonNegative(n, "n");

    if (n == 0)
    {
        return 0;
    }

    return cumulativeWork(n - 1) + n;
}


long long cumulativeWorkClosedForm(int n)
{
    requireNonNegative(n, "n");

    return static_cast<long long>(n) * (n + 1) / 2;
}


// ============================================================================
// Section 4: Towers of Hanoi recurrence
// ============================================================================

long long hanoiMoveCount(int n)
{
    /*
     *     H(0) = 0
     *     H(n) = 2H(n-1) + 1
     *
     * Solving the recurrence gives:
     *
     *     H(n) = 2^n - 1
     */
    requireNonNegative(n, "n");

    if (n == 0)
    {
        return 0;
    }

    return 2 * hanoiMoveCount(n - 1) + 1;
}


long long hanoiClosedForm(int n)
{
    requireNonNegative(n, "n");

    return (1LL << n) - 1;
}


// ============================================================================
// Section 5: Recursive binary search
// ============================================================================

int binarySearchRecursive(
    const vector<int>& values,
    int target,
    int left,
    int right)
{
    /*
     * At each recursive step, approximately half of the search interval is
     * discarded:
     *
     *     T(n) = T(n/2) + O(1)
     *
     * Repeated expansion gives:
     *
     *     T(n) = O(log n)
     */
    if (left > right)
    {
        return -1;
    }

    const int middle = left + (right - left) / 2;

    if (values[middle] == target)
    {
        return middle;
    }

    if (values[middle] < target)
    {
        return binarySearchRecursive(
            values,
            target,
            middle + 1,
            right
        );
    }

    return binarySearchRecursive(
        values,
        target,
        left,
        middle - 1
    );
}


int binarySearchRecursive(
    const vector<int>& values,
    int target)
{
    if (values.empty())
    {
        return -1;
    }

    return binarySearchRecursive(
        values,
        target,
        0,
        static_cast<int>(values.size()) - 1
    );
}


// ============================================================================
// Section 6: Merge operation
// ============================================================================

vector<int> mergeSorted(
    const vector<int>& left,
    const vector<int>& right)
{
    /*
     * The merge phase examines each element at most once.
     *
     * Merge cost:
     *
     *     Theta(n)
     *
     * where n is the combined size of left and right.
     */
    vector<int> result;
    result.reserve(left.size() + right.size());

    size_t leftIndex = 0;
    size_t rightIndex = 0;

    while (leftIndex < left.size() &&
           rightIndex < right.size())
    {
        if (left[leftIndex] <= right[rightIndex])
        {
            result.push_back(left[leftIndex]);
            ++leftIndex;
        }
        else
        {
            result.push_back(right[rightIndex]);
            ++rightIndex;
        }
    }

    while (leftIndex < left.size())
    {
        result.push_back(left[leftIndex]);
        ++leftIndex;
    }

    while (rightIndex < right.size())
    {
        result.push_back(right[rightIndex]);
        ++rightIndex;
    }

    return result;
}


// ============================================================================
// Section 7: Merge sort
// ============================================================================

vector<int> mergeSort(const vector<int>& values)
{
    /*
     * Divide-and-conquer recurrence:
     *
     *     T(n) = 2T(n/2) + Theta(n)
     *
     * The recursion tree has logarithmic depth. Each level performs Theta(n)
     * total merging work, producing:
     *
     *     T(n) = Theta(n log n)
     *
     * The implementation creates temporary vectors, so auxiliary memory is
     * also O(n), excluding recursion-stack considerations.
     */
    if (values.size() <= 1)
    {
        return values;
    }

    const size_t middle = values.size() / 2;

    vector<int> left(
        values.begin(),
        values.begin() + static_cast<std::ptrdiff_t>(middle)
    );

    vector<int> right(
        values.begin() + static_cast<std::ptrdiff_t>(middle),
        values.end()
    );

    left = mergeSort(left);
    right = mergeSort(right);

    return mergeSorted(left, right);
}


// ============================================================================
// Section 8: Quicksort
// ============================================================================

int partitionValues(
    vector<int>& values,
    int low,
    int high)
{
    const int pivot = values[high];

    int smallerIndex = low - 1;

    for (int index = low; index < high; ++index)
    {
        if (values[index] <= pivot)
        {
            ++smallerIndex;
            std::swap(
                values[smallerIndex],
                values[index]
            );
        }
    }

    std::swap(
        values[smallerIndex + 1],
        values[high]
    );

    return smallerIndex + 1;
}


void quickSortRecursive(
    vector<int>& values,
    int low,
    int high)
{
    /*
     * The recurrence depends on partition quality.
     *
     * Balanced partition:
     *
     *     T(n) = 2T(n/2) + Theta(n)
     *           = Theta(n log n)
     *
     * Worst-case partition:
     *
     *     T(n) = T(n-1) + Theta(n)
     *           = Theta(n^2)
     *
     * This distinction is central when using recurrence relations for
     * real algorithms: the recurrence may depend on the input distribution.
     */
    if (low >= high)
    {
        return;
    }

    const int pivotIndex =
        partitionValues(values, low, high);

    quickSortRecursive(
        values,
        low,
        pivotIndex - 1
    );

    quickSortRecursive(
        values,
        pivotIndex + 1,
        high
    );
}


vector<int> quickSort(const vector<int>& values)
{
    vector<int> result = values;

    if (!result.empty())
    {
        quickSortRecursive(
            result,
            0,
            static_cast<int>(result.size()) - 1
        );
    }

    return result;
}


// ============================================================================
// Section 9: Recursive tree model
// ============================================================================

struct TreeNode
{
    int value;
    TreeNode* left;
    TreeNode* right;

    explicit TreeNode(
        int nodeValue,
        TreeNode* nodeLeft = nullptr,
        TreeNode* nodeRight = nullptr)
        : value(nodeValue),
          left(nodeLeft),
          right(nodeRight)
    {
    }
};


int treeSize(const TreeNode* node)
{
    /*
     * Structural recursive definition:
     *
     *     size(empty) = 0
     *     size(node) = 1 + size(left) + size(right)
     */
    if (node == nullptr)
    {
        return 0;
    }

    return 1 +
           treeSize(node->left) +
           treeSize(node->right);
}


int treeHeight(const TreeNode* node)
{
    /*
     *     height(empty) = 0
     *     height(node) =
     *         1 + max(height(left), height(right))
     */
    if (node == nullptr)
    {
        return 0;
    }

    return 1 + std::max(
        treeHeight(node->left),
        treeHeight(node->right)
    );
}


int leafCount(const TreeNode* node)
{
    if (node == nullptr)
    {
        return 0;
    }

    if (node->left == nullptr &&
        node->right == nullptr)
    {
        return 1;
    }

    return leafCount(node->left) +
           leafCount(node->right);
}


int internalNodeCount(const TreeNode* node)
{
    if (node == nullptr)
    {
        return 0;
    }

    if (node->left == nullptr &&
        node->right == nullptr)
    {
        return 0;
    }

    return 1 +
           internalNodeCount(node->left) +
           internalNodeCount(node->right);
}


bool verifyTreeIdentity(const TreeNode* node)
{
    /*
     * Structural proposition:
     *
     *     number of nodes =
     *     number of leaves + number of internal nodes
     *
     * A structural induction proof considers the empty tree and then the
     * recursive construction of a larger tree from subtrees.
     */
    return treeSize(node) ==
           leafCount(node) +
           internalNodeCount(node);
}


void deleteTree(TreeNode* node)
{
    /*
     * Memory management follows the same recursive structure as the tree.
     */
    if (node == nullptr)
    {
        return;
    }

    deleteTree(node->left);
    deleteTree(node->right);
    delete node;
}


TreeNode* createSampleTree()
{
    return new TreeNode(
        10,
        new TreeNode(
            5,
            new TreeNode(2),
            new TreeNode(7)
        ),
        new TreeNode(
            15,
            nullptr,
            new TreeNode(20)
        )
    );
}


// ============================================================================
// Section 10: Strong induction example
// ============================================================================

bool canComposeFromTwoAndThree(
    int n,
    std::map<int, bool>& memo)
{
    /*
     * A number is constructible from 2s and 3s if it can be reduced to zero by
     * repeatedly subtracting 2 or 3.
     *
     * The recursive relation is:
     *
     *     P(n) = P(n-2) OR P(n-3)
     *
     * This is naturally associated with strong induction because the proof may
     * refer to multiple previously established cases.
     */
    if (n < 0)
    {
        return false;
    }

    if (n == 0)
    {
        return true;
    }

    auto found = memo.find(n);
    if (found != memo.end())
    {
        return found->second;
    }

    memo[n] =
        canComposeFromTwoAndThree(n - 2, memo) ||
        canComposeFromTwoAndThree(n - 3, memo);

    return memo[n];
}


// ============================================================================
// Section 11: Recurrence-tree evaluator
// ============================================================================

long long recurrenceTreeCost(
    int n,
    int branchingFactor = 2,
    int shrinkFactor = 2,
    long long work = 1)
{
    /*
     * Evaluate:
     *
     *     T(n) = bT(floor(n/s)) + c
     *
     * for small n.
     *
     * This function is intentionally simple. Its purpose is to make a
     * recurrence tree executable rather than to replace asymptotic analysis.
     */
    if (n <= 1)
    {
        return work;
    }

    if (branchingFactor <= 0)
    {
        throw std::invalid_argument(
            "branchingFactor must be positive"
        );
    }

    if (shrinkFactor < 2)
    {
        throw std::invalid_argument(
            "shrinkFactor must be at least 2"
        );
    }

    const int smaller =
        std::max(1, n / shrinkFactor);

    return branchingFactor *
               recurrenceTreeCost(
                   smaller,
                   branchingFactor,
                   shrinkFactor,
                   work
               ) +
           work;
}


// ============================================================================
// Section 12: Master-Theorem classifier
// ============================================================================

enum class MasterCase
{
    Case1,
    Case2,
    Case3
};


MasterCase classifyMasterTheorem(
    int a,
    int b,
    double d)
{
    /*
     * For:
     *
     *     T(n) = aT(n/b) + Theta(n^d)
     *
     * let:
     *
     *     p = log_b(a)
     *
     * Case 1:
     *     d < p
     *
     * Case 2:
     *     d = p
     *
     * Case 3:
     *     d > p
     *
     * Case 3 also requires the theorem's regularity condition.
     */
    if (a <= 0)
    {
        throw std::invalid_argument("a must be positive");
    }

    if (b <= 1)
    {
        throw std::invalid_argument("b must be greater than 1");
    }

    const double p =
        std::log(static_cast<double>(a)) /
        std::log(static_cast<double>(b));

    const double epsilon = 1e-12;

    if (d < p - epsilon)
    {
        return MasterCase::Case1;
    }

    if (std::abs(d - p) <= epsilon)
    {
        return MasterCase::Case2;
    }

    return MasterCase::Case3;
}


string masterCaseToString(MasterCase value)
{
    switch (value)
    {
        case MasterCase::Case1:
            return "Case 1";
        case MasterCase::Case2:
            return "Case 2";
        case MasterCase::Case3:
            return "Case 3";
    }

    return "Unknown";
}


// ============================================================================
// Section 13: Substitution-style recurrence evaluation
// ============================================================================

long long mergeSortRecurrenceCost(
    int n,
    std::map<int, long long>& memo)
{
    /*
     * Toy recurrence:
     *
     *     T(n) = 2T(floor(n/2)) + n
     *
     * T(1) = 1.
     *
     * This exact integer recurrence is used to test candidate upper bounds on
     * finite values of n.
     */
    if (n <= 1)
    {
        return 1;
    }

    auto found = memo.find(n);
    if (found != memo.end())
    {
        return found->second;
    }

    const long long result =
        2 *
            mergeSortRecurrenceCost(
                n / 2,
                memo
            ) +
        n;

    memo[n] = result;
    return result;
}


bool verifyMergeSortUpperBound(
    int n,
    double constant = 2.0)
{
    std::map<int, long long> memo;

    const long long actual =
        mergeSortRecurrenceCost(n, memo);

    const double bound =
        constant *
        static_cast<double>(n) *
        std::log2(static_cast<double>(n) + 1.0);

    return static_cast<double>(actual) <= bound;
}


// ============================================================================
// Section 14: Induction-oriented proof checks
// ============================================================================

bool verifyTriangularInduction(int limit)
{
    /*
     * Proposition:
     *
     *     P(n): W(n) = n(n+1)/2
     *
     * Base case:
     *
     *     W(0) = 0
     *
     * Inductive step:
     *
     *     Assume W(n) = n(n+1)/2.
     *
     *     W(n+1)
     *       = W(n) + (n+1)
     *       = n(n+1)/2 + (n+1)
     *       = (n+1)(n+2)/2.
     *
     * The loop checks the algebraic transformation for a finite range.
     */
    if (cumulativeWork(0) != 0)
    {
        return false;
    }

    for (int n = 0; n <= limit; ++n)
    {
        const long long assumed =
            static_cast<long long>(n) *
            (n + 1) /
            2;

        const long long derivedNext =
            assumed + (n + 1);

        const long long expectedNext =
            static_cast<long long>(n + 1) *
            (n + 2) /
            2;

        if (derivedNext != expectedNext)
        {
            return false;
        }
    }

    return true;
}


bool verifyPowerOfTwoInduction(int limit)
{
    /*
     * Proposition:
     *
     *     P(n): 2^n satisfies the recurrence P(n+1)=2P(n).
     *
     * Base:
     *
     *     2^0 = 1.
     *
     * Step:
     *
     *     2^(n+1)
     *       = 2 * 2^n.
     */
    if (1 != 1)
    {
        return false;
    }

    long long current = 1;

    for (int n = 0; n < limit; ++n)
    {
        const long long derivedNext = 2 * current;
        const long long expectedNext =
            1LL << (n + 1);

        if (derivedNext != expectedNext)
        {
            return false;
        }

        current = derivedNext;
    }

    return true;
}


bool verifyStrongInduction(
    int limit)
{
    std::map<int, bool> memo;

    /*
     * Base cases:
     *
     *     2 = 2
     *     3 = 3
     *     4 = 2 + 2
     *
     * Once those are known, every larger value can be reduced by 2, giving
     * another valid previously established case.
     */
    for (int n = 2; n <= limit; ++n)
    {
        if (!canComposeFromTwoAndThree(n, memo))
        {
            return false;
        }
    }

    return true;
}


// ============================================================================
// Section 15: Application model
// ============================================================================

struct DocumentRecord
{
    int id;
    string category;
    int priority;
};


class DocumentIndex
{
private:
    vector<DocumentRecord> records;

public:
    /*
     * Insert records into the index.
     *
     * The vector is later sorted by id. Keeping insertion separate from sorting
     * makes the system's lifecycle explicit.
     */
    void add(DocumentRecord record)
    {
        if (record.id < 0)
        {
            throw std::invalid_argument(
                "document id must be non-negative"
            );
        }

        if (record.priority < 0)
        {
            throw std::invalid_argument(
                "document priority must be non-negative"
            );
        }

        if (record.category.empty())
        {
            throw std::invalid_argument(
                "document category cannot be empty"
            );
        }

        records.push_back(std::move(record));
    }


    void build()
    {
        /*
         * std::sort is an introspective sorting implementation in standard
         * library implementations. The exact internal strategy is
         * implementation-dependent, but comparison sorting is commonly
         * analyzed around O(n log n).
         */
        std::sort(
            records.begin(),
            records.end(),
            [](const DocumentRecord& left,
               const DocumentRecord& right)
            {
                return left.id < right.id;
            }
        );
    }


    std::optional<DocumentRecord> findById(int id) const
    {
        /*
         * The records are sorted by id, allowing binary search.
         *
         * Recurrence:
         *
         *     T(n) = T(n/2) + O(1)
         *
         *     => O(log n)
         */
        int left = 0;
        int right =
            static_cast<int>(records.size()) - 1;

        while (left <= right)
        {
            const int middle =
                left + (right - left) / 2;

            if (records[middle].id == id)
            {
                return records[middle];
            }

            if (records[middle].id < id)
            {
                left = middle + 1;
            }
            else
            {
                right = middle - 1;
            }
        }

        return std::nullopt;
    }


    const vector<DocumentRecord>& allRecords() const
    {
        return records;
    }


    long long cumulativePriorityWork() const
    {
        /*
         * This intentionally applies a recurrence-like cumulative calculation:
         *
         *     W(0) = 0
         *     W(k) = W(k-1) + priority_k
         *
         * The implementation is iterative because the same mathematical
         * recurrence does not require a recursive call stack.
         */
        long long total = 0;

        for (const DocumentRecord& record : records)
        {
            total += record.priority;
        }

        return total;
    }
};


// ============================================================================
// Section 16: Performance measurements
// ============================================================================

void printComplexityTable()
{
    cout << "\nCOMPLEXITY MODELS\n";
    cout << "------------------------------------------------------------\n";

    cout << std::left
         << std::setw(22) << "Algorithm"
         << std::setw(32) << "Recurrence"
         << "Growth"
         << '\n';

    cout << std::setw(22) << "Binary search"
         << std::setw(32) << "T(n)=T(n/2)+Theta(1)"
         << "Theta(log n)"
         << '\n';

    cout << std::setw(22) << "Merge sort"
         << std::setw(32) << "T(n)=2T(n/2)+Theta(n)"
         << "Theta(n log n)"
         << '\n';

    cout << std::setw(22) << "Naive Fibonacci"
         << std::setw(32) << "T(n)=T(n-1)+T(n-2)+Theta(1)"
         << "Exponential"
         << '\n';

    cout << std::setw(22) << "Towers of Hanoi"
         << std::setw(32) << "H(n)=2H(n-1)+1"
         << "Theta(2^n)"
         << '\n';

    cout << std::setw(22) << "Worst quicksort"
         << std::setw(32) << "T(n)=T(n-1)+Theta(n)"
         << "Theta(n^2)"
         << '\n';
}


// ============================================================================
// Section 17: Test suite
// ============================================================================

void runTests()
{
    // Recursive definitions.
    assert(factorial(0) == 1);
    assert(factorial(5) == 120);

    for (int n = 0; n <= 20; ++n)
    {
        std::map<int, long long> memo;

        assert(
            fibonacciRecursive(n) ==
            fibonacciMemoized(n, memo)
        );

        assert(
            fibonacciMemoized(n, memo) ==
            fibonacciIterative(n)
        );

        assert(
            cumulativeWork(n) ==
            cumulativeWorkClosedForm(n)
        );

        assert(
            hanoiMoveCount(n) ==
            hanoiClosedForm(n)
        );
    }

    // Binary search.
    const vector<int> sortedValues{
        0, 2, 4, 6, 8, 10, 12, 14, 16, 18
    };

    for (int value : sortedValues)
    {
        const int index =
            binarySearchRecursive(
                sortedValues,
                value
            );

        assert(index >= 0);
        assert(sortedValues[index] == value);
    }

    assert(
        binarySearchRecursive(
            sortedValues,
            99
        ) == -1
    );

    assert(
        binarySearchRecursive(
            {},
            99
        ) == -1
    );

    // Sorting.
    const vector<int> input{
        7, 2, 9, 1, 5, 2, 8, 0, -3
    };

    const vector<int> expected{
        -3, 0, 1, 2, 2, 5, 7, 8, 9
    };

    assert(mergeSort(input) == expected);
    assert(quickSort(input) == expected);

    // Induction.
    assert(verifyTriangularInduction(100));
    assert(verifyPowerOfTwoInduction(20));
    assert(verifyStrongInduction(100));

    // Structural induction.
    TreeNode* tree = createSampleTree();

    assert(treeSize(tree) == 6);
    assert(treeHeight(tree) == 3);
    assert(leafCount(tree) == 3);
    assert(internalNodeCount(tree) == 3);
    assert(verifyTreeIdentity(tree));
    assert(verifyTreeIdentity(nullptr));

    deleteTree(tree);

    // Recurrence tree.
    assert(recurrenceTreeCost(1) == 1);
    assert(recurrenceTreeCost(2) > 1);
    assert(recurrenceTreeCost(8) > recurrenceTreeCost(4));

    // Master Theorem.
    assert(
        classifyMasterTheorem(1, 2, 0) ==
        MasterCase::Case2
    );

    assert(
        classifyMasterTheorem(2, 2, 1) ==
        MasterCase::Case2
    );

    assert(
        classifyMasterTheorem(4, 2, 1) ==
        MasterCase::Case1
    );

    assert(
        classifyMasterTheorem(2, 4, 1) ==
        MasterCase::Case3
    );

    // Substitution-style finite checks.
    for (int n : {2, 4, 8, 16, 32, 64})
    {
        assert(verifyMergeSortUpperBound(n));
    }

    // Application-level document index.
    DocumentIndex index;

    index.add({104, "legal", 3});
    index.add({101, "finance", 5});
    index.add({109, "security", 2});
    index.add({103, "operations", 4});

    index.build();

    const auto found = index.findById(103);
    assert(found.has_value());
    assert(found->category == "operations");

    const auto missing = index.findById(999);
    assert(!missing.has_value());

    assert(index.cumulativePriorityWork() == 14);
}


// ============================================================================
// Section 18: Demonstrations
// ============================================================================

void printRecursiveDefinitions()
{
    cout << "\nRECURSIVE DEFINITIONS\n";
    cout << "------------------------------------------------------------\n";

    for (int n = 0; n <= 7; ++n)
    {
        cout << "n=" << n
             << " | factorial=" << factorial(n)
             << " | fibonacci=" << fibonacciIterative(n)
             << " | cumulative=" << cumulativeWork(n)
             << '\n';
    }
}


void printFibonacciExperiment()
{
    cout << "\nFIBONACCI RECURSION AND MEMOIZATION\n";
    cout << "------------------------------------------------------------\n";

    for (int n = 5; n <= 10; ++n)
    {
        std::map<int, long long> memo;

        const long long naive =
            fibonacciRecursive(n);

        const long long memoized =
            fibonacciMemoized(n, memo);

        cout << "n=" << n
             << " | value=" << naive
             << " | memoized=" << memoized
             << '\n';
    }
}


void printApplicationCaseStudy()
{
    cout << "\nDOCUMENT INDEX CASE STUDY\n";
    cout << "------------------------------------------------------------\n";

    DocumentIndex index;

    index.add({104, "legal", 3});
    index.add({101, "finance", 5});
    index.add({109, "security", 2});
    index.add({103, "operations", 4});

    cout << "Records before sorting: "
         << index.allRecords().size()
         << '\n';

    index.build();

    cout << "Sorted records:\n";

    for (const auto& record : index.allRecords())
    {
        cout << "  id=" << record.id
             << ", category=" << record.category
             << ", priority=" << record.priority
             << '\n';
    }

    const int targetId = 103;
    const auto result = index.findById(targetId);

    if (result.has_value())
    {
        cout << "Search result for id "
             << targetId
             << ": category="
             << result->category
             << '\n';
    }
    else
    {
        cout << "Document not found\n";
    }

    cout << "Total priority work: "
         << index.cumulativePriorityWork()
         << '\n';
}


void printTreeCaseStudy()
{
    cout << "\nSTRUCTURAL RECURSION ON A TREE\n";
    cout << "------------------------------------------------------------\n";

    TreeNode* tree = createSampleTree();

    cout << "Nodes: "
         << treeSize(tree)
         << '\n';

    cout << "Height: "
         << treeHeight(tree)
         << '\n';

    cout << "Leaves: "
         << leafCount(tree)
         << '\n';

    cout << "Internal nodes: "
         << internalNodeCount(tree)
         << '\n';

    cout << "Nodes = leaves + internal nodes: "
         << std::boolalpha
         << verifyTreeIdentity(tree)
         << '\n';

    deleteTree(tree);
}


void printRecurrenceTreeExamples()
{
    cout << "\nRECURRENCE TREE\n";
    cout << "------------------------------------------------------------\n";

    for (int n : {1, 2, 4, 8, 16})
    {
        cout << "n=" << std::setw(2)
             << n
             << " | T(n)="
             << recurrenceTreeCost(n)
             << '\n';
    }
}


void printMasterTheoremExamples()
{
    cout << "\nMASTER THEOREM\n";
    cout << "------------------------------------------------------------\n";

    struct Example
    {
        int a;
        int b;
        double d;
    };

    const vector<Example> examples{
        {1, 2, 0},
        {2, 2, 1},
        {4, 2, 1},
        {2, 4, 1}
    };

    for (const Example& example : examples)
    {
        cout << "T(n)="
             << example.a
             << "T(n/"
             << example.b
             << ")+Theta(n^"
             << example.d
             << ") -> "
             << masterCaseToString(
                    classifyMasterTheorem(
                        example.a,
                        example.b,
                        example.d
                    )
                )
             << '\n';
    }
}


void printSubstitutionChecks()
{
    cout << "\nSUBSTITUTION-STYLE FINITE CHECKS\n";
    cout << "------------------------------------------------------------\n";

    for (int n : {2, 4, 8, 16, 32, 64})
    {
        cout << "n=" << std::setw(2)
             << n
             << " | T(n) <= 2n log2(n+1): "
             << std::boolalpha
             << verifyMergeSortUpperBound(n)
             << '\n';
    }
}


// ============================================================================
// Section 19: Main program
// ============================================================================

int main()
{
    try
    {
        runTests();

        cout << "RECURRENCE PROOFS: C++ CASE STUDY\n";
        cout << "============================================================\n";

        printRecursiveDefinitions();
        printFibonacciExperiment();
        printApplicationCaseStudy();
        printTreeCaseStudy();
        printRecurrenceTreeExamples();
        printMasterTheoremExamples();
        printSubstitutionChecks();
        printComplexityTable();

        cout << "\nAll C++ correctness checks passed.\n";
    }
    catch (const std::exception& error)
    {
        std::cerr
            << "Program error: "
            << error.what()
            << '\n';

        return 1;
    }

    return 0;
}
