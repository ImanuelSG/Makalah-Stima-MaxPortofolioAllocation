class Stock:
    def __init__(self, stock_id, stock_name, stock_price, CAGR, industry, market_cap):
        self._stock_id = stock_id
        self._stock_name = stock_name
        self._stock_price = stock_price
        self._CAGR = CAGR
        self._industry = industry
        self._market_cap = market_cap

    # Getter methods
    @property
    def stock_id(self):
        return self._stock_id

    @property
    def stock_name(self):
        return self._stock_name

    @property
    def stock_price(self):
        return self._stock_price

    @property
    def CAGR(self):
        return self._CAGR

    @property
    def industry(self):
        return self._industry

    @property
    def market_cap(self):
        return self._market_cap
