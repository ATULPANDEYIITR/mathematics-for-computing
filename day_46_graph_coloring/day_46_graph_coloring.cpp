#include <algorithm>
#include <functional>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

/*
 * Case study: assigning radio frequencies to geographically interfering
 * transmitters. Each transmitter is a vertex; an edge represents interference.
 * Adjacent transmitters must receive different frequency channels.
 */

class InterferenceGraph {
private:
    vector<string> names_;
    vector<set<int>> adjacency_;
    map<string, int> index_;

public:
    int addTransmitter(const string& name) {
        if (name.empty()) {
            throw invalid_argument("Transmitter name cannot be empty.");
        }
        if (index_.count(name)) {
            return index_.at(name);
        }

        int id = static_cast<int>(names_.size());
        names_.push_back(name);
        adjacency_.emplace_back();
        index_[name] = id;
        return id;
    }

    void addInterference(const string& left, const string& right) {
        if (left == right) {
            throw invalid_argument("A transmitter cannot interfere with itself.");
        }

        int u = addTransmitter(left);
        int v = addTransmitter(right);
        adjacency_[u].insert(v);
        adjacency_[v].insert(u);
    }

    int size() const {
        return static_cast<int>(names_.size());
    }

    const string& name(int vertex) const {
        return names_.at(vertex);
    }

    const set<int>& neighbors(int vertex) const {
        return adjacency_.at(vertex);
    }

    vector<int> degrees() const {
        vector<int> result(size());
        for (int v = 0; v < size(); ++v) {
            result[v] = static_cast<int>(adjacency_[v].size());
        }
        return result;
    }

    bool validColoring(const vector<int>& colors) const {
        if (static_cast<int>(colors.size()) != size()) {
            return false;
        }

        for (int color : colors) {
            if (color < 0) return false;
        }

        for (int u = 0; u < size(); ++u) {
            for (int v : adjacency_[u]) {
                if (colors[u] == colors[v]) return false;
            }
        }
        return true;
    }

    vector<int> greedyDsatur() const {
        vector<int> colors(size(), -1);

        for (int colored = 0; colored < size(); ++colored) {
            int selected = -1;
            int bestSaturation = -1;
            int bestDegree = -1;

            for (int v = 0; v < size(); ++v) {
                if (colors[v] != -1) continue;

                set<int> neighborColors;
                for (int neighbor : adjacency_[v]) {
                    if (colors[neighbor] != -1) {
                        neighborColors.insert(colors[neighbor]);
                    }
                }

                int saturation = static_cast<int>(neighborColors.size());
                int degree = static_cast<int>(adjacency_[v].size());

                if (saturation > bestSaturation ||
                    (saturation == bestSaturation && degree > bestDegree)) {
                    selected = v;
                    bestSaturation = saturation;
                    bestDegree = degree;
                }
            }

            set<int> unavailable;
            for (int neighbor : adjacency_[selected]) {
                if (colors[neighbor] != -1) {
                    unavailable.insert(colors[neighbor]);
                }
            }

            int color = 0;
            while (unavailable.count(color)) ++color;
            colors[selected] = color;
        }

        if (!validColoring(colors)) {
            throw logic_error("DSATUR generated an invalid coloring.");
        }
        return colors;
    }

    pair<bool, vector<int>> bipartiteTest() const {
        vector<int> side(size(), -1);

        for (int start = 0; start < size(); ++start) {
            if (side[start] != -1) continue;

            vector<int> queue{start};
            size_t head = 0;
            side[start] = 0;

            while (head < queue.size()) {
                int u = queue[head++];

                for (int v : adjacency_[u]) {
                    if (side[v] == -1) {
                        side[v] = 1 - side[u];
                        queue.push_back(v);
                    } else if (side[v] == side[u]) {
                        return {false, {}};
                    }
                }
            }
        }
        return {true, side};
    }

    int chromaticNumber() const {
        if (size() == 0) return 0;

        auto [bipartite, side] = bipartiteTest();
        if (bipartite) {
            bool hasEdge = false;
            for (const auto& neighbors : adjacency_) {
                if (!neighbors.empty()) {
                    hasEdge = true;
                    break;
                }
            }
            return hasEdge ? 2 : 1;
        }

        vector<int> best = greedyDsatur();
        int upperBound = *max_element(best.begin(), best.end()) + 1;

        // Exact search tries each smaller color bound. It assigns only
        // existing colors or the next new color, avoiding color-label symmetry.
        for (int limit = 1; limit < upperBound; ++limit) {
            vector<int> colors(size(), -1);

            function<bool(int, int)> search = [&](int colored, int usedColors) {
                if (colored == size()) return true;

                int selected = -1;
                int bestSaturation = -1;
                int bestDegree = -1;

                for (int v = 0; v < size(); ++v) {
                    if (colors[v] != -1) continue;

                    set<int> neighborColors;
                    for (int neighbor : adjacency_[v]) {
                        if (colors[neighbor] != -1) {
                            neighborColors.insert(colors[neighbor]);
                        }
                    }

                    int saturation = static_cast<int>(neighborColors.size());
                    int degree = static_cast<int>(adjacency_[v].size());

                    if (saturation > bestSaturation ||
                        (saturation == bestSaturation && degree > bestDegree)) {
                        selected = v;
                        bestSaturation = saturation;
                        bestDegree = degree;
                    }
                }

                set<int> unavailable;
                for (int neighbor : adjacency_[selected]) {
                    if (colors[neighbor] != -1) {
                        unavailable.insert(colors[neighbor]);
                    }
                }

                int maximumCandidate = min(limit - 1, usedColors);
                for (int color = 0; color <= maximumCandidate; ++color) {
                    if (unavailable.count(color)) continue;
                    if (color == usedColors && usedColors >= limit) continue;

                    colors[selected] = color;
                    int nextUsed = max(usedColors, color + 1);

                    if (search(colored + 1, nextUsed)) return true;
                    colors[selected] = -1;
                }
                return false;
            };

            if (search(0, 0)) return limit;
        }

        return upperBound;
    }

    void printNetwork(const vector<int>& colors) const {
        if (!validColoring(colors)) {
            throw invalid_argument("Cannot print an invalid frequency assignment.");
        }

        for (int v = 0; v < size(); ++v) {
            cout << "  " << names_[v] << " -> channel " << colors[v] << '\n';
        }
        cout << "  Channels used: "
             << (colors.empty() ? 0 :
                 *max_element(colors.begin(), colors.end()) + 1)
             << '\n';
    }
};

int main() {
    try {
        cout << "RADIO FREQUENCY ASSIGNMENT\n";

        InterferenceGraph network;
        network.addInterference("North-Hill", "City-Center");
        network.addInterference("North-Hill", "River-Side");
        network.addInterference("City-Center", "Airport");
        network.addInterference("River-Side", "Airport");
        network.addInterference("Airport", "Industrial-Zone");
        network.addInterference("Industrial-Zone", "City-Center");
        network.addInterference("River-Side", "Industrial-Zone");

        cout << "\nInterference graph degrees:\n";
        vector<int> degrees = network.degrees();
        for (int v = 0; v < network.size(); ++v) {
            cout << "  " << network.name(v) << ": " << degrees[v] << '\n';
        }

        cout << "\nDSATUR frequency assignment:\n";
        vector<int> coloring = network.greedyDsatur();
        network.printNetwork(coloring);

        cout << "\nBipartite: "
             << (network.bipartiteTest().first ? "yes" : "no") << '\n';
        cout << "Chromatic number: " << network.chromaticNumber() << '\n';

        cout << "\nBIPARTITE NETWORK EXAMPLE\n";
        InterferenceGraph alternating;
        alternating.addInterference("Tower-A", "Tower-B");
        alternating.addInterference("Tower-A", "Tower-C");
        alternating.addInterference("Tower-D", "Tower-B");
        alternating.addInterference("Tower-D", "Tower-C");

        auto [isBipartite, partition] = alternating.bipartiteTest();
        cout << "Bipartite: " << (isBipartite ? "yes" : "no") << '\n';
        vector<int> twoColors(alternating.size(), 0);
        if (isBipartite) {
            twoColors = partition;
            alternating.printNetwork(twoColors);
        }

        cout << "\nVALIDATION\n";
        cout << "Original coloring valid: "
             << (network.validColoring(coloring) ? "yes" : "no") << '\n';

        vector<int> invalid(network.size(), 0);
        cout << "All transmitters on one channel valid: "
             << (network.validColoring(invalid) ? "yes" : "no") << '\n';

        try {
            network.addInterference("North-Hill", "North-Hill");
        } catch (const invalid_argument& error) {
            cout << "Self-interference rejected: " << error.what() << '\n';
        }

        cout << "\nCOMPUTATIONAL TRADE-OFFS\n";
        cout << "Bipartite testing takes O(V + E) time.\n";
        cout << "DSATUR is a heuristic and may use more channels than necessary.\n";
        cout << "Exact chromatic-number search has exponential worst-case cost.\n";
        cout << "Real deployments must also account for signal strength, geography,\n";
        cout << "legal spectrum allocations, and interference outside the model.\n";

    } catch (const exception& error) {
        cerr << "Failure: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
