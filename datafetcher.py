import investpy

def fetch_and_save_indonesian_stocks():
    try:
        indonesian_stocks_df = investpy.stocks.get_stocks(country='indonesia')
        indonesian_stocks_df.to_csv('indonesian_stocks_list.csv', index=False)
        print('Saham indonesia berhasil diunduh dan disimpan di indonesian_stocks_list.csv')
    except Exception as e:
        print(f"Error fetching Indonesian stocks: {e}")

if __name__ == '__main__':
    fetch_and_save_indonesian_stocks()
