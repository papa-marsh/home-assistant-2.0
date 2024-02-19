from datetime import date, datetime
import requests
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..modules import secrets
else:
    import secrets


class StocksAPI():

    def get_stock_quote(self, symbol: str = "SPY") -> dict:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol.upper()}&token={secrets.FINNHUB_TOKEN}"
        r = task.executor(requests.get, url).json()

        output = {
            "current": r["c"],
            "change": r["dp"],
            "prev_close": r["pc"]
        }

        return output

    def get_stock_week(self, symbol: str = "SPY") -> float:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol.upper()}&apikey={secrets.ALPHAVANTAGE_KEY}"
        r = task.executor(requests.get, url).json()

        latest_week = list(r["Weekly Time Series"].keys())[0]

        latest_week_number = datetime.strptime(latest_week, "%Y-%m-%d").isocalendar().week
        current_week_number = date.today().isocalendar().week

        week_key = "1. open" if latest_week_number == current_week_number else "4. close"
        price = r["Weekly Time Series"][latest_week][week_key]

        return price

    def get_stock_week_change(self, symbol: str = "SPY") -> float:
        current_price = self.get_stock_quote(symbol)["current"]
        week_open_price = float(self.get_stock_week(symbol))

        return (current_price / week_open_price) - 1


class CryptoAPI():
    def get_crypto_quotes(self, symbols=["BTC"], limit=500) -> dict:
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?start=1&limit={limit}&convert=USD"
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": f"{secrets.CMC_KEY}",
        }

        r = task.executor(requests.get, url, headers=headers).json()
        parsed = {}

        for data_by_symbol in r["data"]:
            symbol = data_by_symbol["symbol"]
            if symbol in symbols:
                parsed[symbol] = {
                    "rank": data_by_symbol["cmc_rank"],
                    "price": data_by_symbol["quote"]["USD"]["price"],
                    "change_hour": data_by_symbol["quote"]["USD"]["percent_change_1h"],
                    "change_day": data_by_symbol["quote"]["USD"]["percent_change_24h"],
                    "change_week": data_by_symbol["quote"]["USD"]["percent_change_7d"],
                }

        return parsed
