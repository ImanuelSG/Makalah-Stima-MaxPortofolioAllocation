import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def calculate_CAGR(start_price, end_price, periods):
    return ((end_price / start_price) ** (1 / periods) - 1) * 100

def get_stock_data(ticker):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=20*365)  # 20 years ago
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

def main():
    try:
        indonesian_stocks_df = pd.read_csv('indonesian_stocks_list.csv')
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return

    stock_list = []

    for index, row in indonesian_stocks_df.iterrows():
        ticker = row['symbol'] + '.JK'  # Add .JK to match Yahoo Finance ticker format
        try:
            if ticker == "XCID.JK":
                continue
            data = get_stock_data(ticker)
            
            if not data.empty and len(data) >= 3600:  # Ensure sufficient data points for 20 years
                start_price = data['Adj Close'].iloc[0]
                end_price = data['Adj Close'].iloc[-1]
                periods = 20  # 20 years

                CAGR = calculate_CAGR(start_price, end_price, periods)

                stock_info = yf.Ticker(ticker).info
                sector = stock_info.get('industry', 'Unknown')

                if CAGR > 0:
                    if sector == 'Unknown':
                        continue

                    sector = sector.replace(',', '-')  # Replace commas with hyphens
                    
                    stock_list.append({
                        'Stock ID': row['symbol'],
                        'Stock Name': stock_info.get('shortName', 'Unknown'),
                        'Stock Price': end_price,
                        'CAGR (%)': CAGR,
                        'Industry': sector,
                        'Market Cap': stock_info.get('marketCap', 'Unknown'),
                    })

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    stock_list = sorted(stock_list, key=lambda x: x['CAGR (%)'], reverse=True)        
    stock_list = stock_list[:100]  # Limit to top 100 stocks

    df = pd.DataFrame(stock_list)
    df.to_csv('indonesian_stocks_CAGR.csv', index=False)
    print('Data has been exported to indonesian_stocks_CAGR.csv')

if __name__ == '__main__':
    main()
