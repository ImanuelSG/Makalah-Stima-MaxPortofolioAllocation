#include <iostream>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <cmath>
#include <string>
#include <thread>
#include <chrono>
#include <iomanip>

using namespace std;

// Define a custom facet to use dots as thousands separator
struct DotSeparator : public std::numpunct<char>
{
    char do_thousands_sep() const { return '.'; }     // Define dot as the thousands separator
    std::string do_grouping() const { return "\03"; } // Group digits in threes
};

// Function to format a number with dots as separator
template <typename T>
string format_with_dots(T number)
{
    stringstream ss;
    ss.imbue(locale(locale(), new DotSeparator)); // Set the custom facet for thousands separator
    if (number == floor(number))
    {                                             // Check if the number has no fractional part
        ss << fixed << setprecision(0) << number; // Set precision to 0 decimal places
    }
    else
    {
        ss << fixed << setprecision(2) << number; // Set precision to two decimal places
    }
    return ss.str();
}

struct Stock
{
    string stock_id;
    string stock_name;
    double stock_price;
    double CAGR;
    string industry;
    double market_cap;
};

vector<Stock> read_csv(const string &file_path)
{
    vector<Stock> stock_list;
    ifstream file(file_path);
    string line;

    if (!file.is_open())
    {
        cerr << "Error opening file: " << file_path << endl;
        return stock_list;
    }

    getline(file, line); // Skip headers

    while (getline(file, line))
    {
        stringstream ss(line);
        string stock_id, stock_name, stock_price, CAGR, industry, market_cap;

        getline(ss, stock_id, ',');
        getline(ss, stock_name, ',');
        getline(ss, stock_price, ',');
        getline(ss, CAGR, ',');
        getline(ss, industry, ',');
        getline(ss, market_cap, ',');

        Stock stock = {stock_id, stock_name, stod(stock_price), stod(CAGR), industry, stod(market_cap)};
        stock_list.push_back(stock);
    }

    file.close();
    return stock_list;
}

void backtrack(unordered_map<string, pair<Stock, int>> &best_portfolio,
               double &best_return,
               unordered_map<string, pair<Stock, int>> &portfolio,
               double current_cash,
               double current_return,
               int index,
               unordered_set<string> &industries,
               const vector<Stock> &stock_list,
               double max_allocation)
{

    if (!portfolio.empty() && current_return > best_return)
    {
        best_portfolio = portfolio;
        best_return = current_return;
    }

    for (int i = index; i < stock_list.size(); ++i)
    {
        const Stock &stock = stock_list[i];
        if (stock.stock_price <= current_cash && portfolio.find(stock.stock_id) == portfolio.end())
        {
            if (industries.find(stock.industry) == industries.end())
            {
                int max_lots = min(
                    static_cast<int>(floor((stock.market_cap * 0.01 / stock.stock_price) / 100)),
                    static_cast<int>(floor(max_allocation / (stock.stock_price * 100))));

                int lots_to_buy = min(max_lots, static_cast<int>(floor(current_cash / (stock.stock_price * 100))));

                if (lots_to_buy > 0)
                {
                    portfolio[stock.stock_id] = {stock, lots_to_buy};
                    double new_cash = current_cash - lots_to_buy * stock.stock_price * 100;
                    double new_return = current_return + lots_to_buy * stock.stock_price * 100 * (1 + stock.CAGR / 100);
                    industries.insert(stock.industry);

                    backtrack(best_portfolio, best_return, portfolio, new_cash, new_return, i + 1, industries, stock_list, max_allocation);

                    industries.erase(stock.industry);
                    portfolio.erase(stock.stock_id);
                }
            }
        }
    }
}

pair<unordered_map<string, pair<Stock, int>>, double> algorithm(vector<Stock> &stock_list, double max_allocation_percent, double cash)
{
    sort(stock_list.begin(), stock_list.end(), [](const Stock &a, const Stock &b)
         { return a.CAGR > b.CAGR; });

    unordered_map<string, pair<Stock, int>> best_portfolio;
    double best_return = 0;
    double max_allocation = cash * (max_allocation_percent / 100);

    unordered_map<string, pair<Stock, int>> portfolio;
    unordered_set<string> industries;

    backtrack(best_portfolio, best_return, portfolio, cash, 0, 0, industries, stock_list, max_allocation);

    return {best_portfolio, best_return};
}

void print_portfolio(const unordered_map<string, pair<Stock, int>> &portfolio, double best_return, double cash)
{
    cout << "\n";
    cout << "Portofolio Terbaik:\n\n";
    for (const auto &entry : portfolio)
    {
        const Stock &stock = entry.second.first;
        int lots = entry.second.second;
        cout << format_with_dots(lots) << " lot saham " << stock.stock_name << " (" << stock.stock_id << ") pada harga Rp" << format_with_dots(stock.stock_price) << "\n";
    }

    int total = 0;
    for (const auto &entry : portfolio)
    {
        const Stock &stock = entry.second.first;
        int lots = entry.second.second;
        total += lots * stock.stock_price * 100;

    }

    cout << "\nTotal Investasi: Rp. " << format_with_dots(total) << "\n";
    cout << "Sisa Dana: Rp. " << format_with_dots(cash - total) << "\n\n";
    cout << "Dana setelah setahun: Rp. " << format_with_dots(best_return) << "\n";
    cout << "\nEkspektasi Keuntungan Setahun: Rp. " << format_with_dots(best_return - cash) << "\n";
    cout << "Persentase Keuntungan: " << format_with_dots(((best_return - cash) / cash * 100)) << "%\n";
}

int main()
{
    double max_allocation_percent, cash;

    cout << "Masukkan persentase maksimum alokasi untuk tiap saham: ";
    cin >> max_allocation_percent;

    cout << "Masukkan dana yang ingin diinvestasikan: ";
    cin >> cash;

    vector<Stock> stock_list = read_csv("indonesian_stocks_CAGR.csv");

    // Measure execution time
    auto start_time = chrono::high_resolution_clock::now();

    unordered_map<string, pair<Stock, int>> best_portfolio;
    double best_return = 0;

    thread algorithm_thread([&]()
                            { tie(best_portfolio, best_return) = algorithm(stock_list, max_allocation_percent, cash); });

    algorithm_thread.join();

    auto end_time = chrono::high_resolution_clock::now();
    chrono::duration<double> execution_time = end_time - start_time;

    print_portfolio(best_portfolio, best_return, cash);
    cout << "Waktu Eksekusi: " << execution_time.count() << " detik\n";

    return 0;
}
