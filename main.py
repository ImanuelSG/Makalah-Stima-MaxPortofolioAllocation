import math
import threading
import time
from typing import List, Dict, Tuple
from stock import Stock

def algorithm(stock_list: List[Stock], max_allocation_percent: float, cash: float) -> Tuple[Dict[str, Tuple[Stock, int]], float]:
    # Sort stocks by CAGR in descending order
    stock_list = sorted(stock_list, key=lambda x: x.CAGR, reverse=True)
    best_portfolio = {}
    best_return = 0

    max_allocation = cash * (max_allocation_percent / 100)

    def backtrack(portfolio, current_cash, current_return, index, industries):
        nonlocal best_portfolio, best_return

        # Check if the current portfolio satisfies the constraints
        if len(portfolio) > 0 and current_return > best_return:
            best_portfolio = portfolio.copy()
            best_return = current_return

        # Try adding more stocks to the portfolio
        for i in range(index, len(stock_list)):
            stock = stock_list[i]
            if stock.stock_price <= current_cash and stock.stock_id not in portfolio:
                if stock.industry not in industries:
                    # Calculate the maximum number of lots that can be purchased without exceeding 1% of the market cap
                    max_lots = min(
                        math.floor((stock.market_cap * 0.01 / stock.stock_price) / 100),
                        math.floor(max_allocation / (stock.stock_price * 100))
                    )
                   
                    lots_to_buy = min(max_lots, math.floor(current_cash / (stock.stock_price * 100)))

                    if lots_to_buy > 0:
                        # Add the stock to the portfolio
                        portfolio[stock.stock_id] = (stock, lots_to_buy)
                        # Deduct the spent cash
                        new_cash = current_cash - lots_to_buy * stock.stock_price * 100
                        # Calculate the new expected return
                        new_return = current_return + lots_to_buy * stock.stock_price * 100 * (1 + stock.CAGR / 100)
                        # Add the industry to the industries set
                        industries.add(stock.industry)
                        # Recursive call to continue building the portfolio
                        backtrack(portfolio, new_cash, new_return, i + 1, industries)
                        # Backtrack: remove the industry and stock from the current portfolio
                        industries.remove(stock.industry)
                        del portfolio[stock.stock_id]

    backtrack({}, cash, 0, 0, set())

    return best_portfolio, best_return

def read_csv(file_path: str) -> List[Stock]:
    stock_list = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:
            stock_id, stock_name, stock_price, CAGR, industry, market_cap = line.strip().split(',')
            stock = Stock(stock_id, stock_name, float(stock_price), float(CAGR), industry, float(market_cap))
            stock_list.append(stock)
    return stock_list

def main():
    stock_list = read_csv('indonesian_stocks_CAGR.csv')

    max_allocation_percent = 30  # Maximum allocation per stock in percentage
    cash = 500000000  # Total cash available for investment

    # Measure execution time
    start_time = time.time()

    # Create a thread for the algorithm
    best_portfolio, best_return = None, 0

    def run_algorithm():
        nonlocal best_portfolio, best_return
        best_portfolio, best_return = algorithm(stock_list, max_allocation_percent, cash)

    thread = threading.Thread(target=run_algorithm)
    thread.start()
    thread.join()

    end_time = time.time()
    execution_time = end_time - start_time

    print("Portofolio Terbaik:")
    for stock_id, (stock, lots) in best_portfolio.items():
        print(f"{lots} lot saham {stock.stock_name} ({stock.stock_id}) pada harga Rp{stock.stock_price:,.2f}".replace(',', '.'))


    print(f"\nTotal Investasi: Rp. {cash:,.2f}".replace(',', '.') )
    print(f"Dana setelah setahun: Rp. {best_return:,.2f}".replace(',', '.'))
    print(f"\nEkspektasi Keuntungan Setahun: Rp. {best_return - cash:,.2f}".replace(',', '.'))
    print (f"Persentase Keuntungan: {(best_return - cash) / cash * 100:.2f}%")
    print(f"Waktu Eksekusi: {execution_time:.2f} detik")

if __name__ == "__main__":
    main()
