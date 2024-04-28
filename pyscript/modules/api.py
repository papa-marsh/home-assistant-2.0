from datetime import date, datetime
import requests
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import secrets
    from .dummy import *
else:
    import secrets


class OpenAIClient():
    url = "https://api.openai.com/v1/chat/completions"
    model = "gpt-4-turbo"
    headers = {
        "Content-Type: application/json",
        f"Authorization: Bearer {secrets.OPEN_AI_KEY}",
    }

    @classmethod
    def quick_response(cls, prompt: str, model: str | None = None) -> str:
        """
        Sends a prompt to the OpenAI API and returns the output message from the specified model.
        """
        data = {
            "model": model or cls.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        r = task.executor(requests.get, cls.url, headers=cls.headers, data=data).json()
        output = r["choices"][0]["message"]["content"]

        return output


class StocksAPI():
    def get_quote(self, symbol: str = "SPY") -> dict:
        """
        Returns a dict of "current", "change", and "prev_close" for a given stock symbol.
        Change is returned in percent format (0-100).
        Uses Finnhub API.
        """
        symbol = symbol.upper()
        token = secrets.FINNHUB_TOKEN
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={token}"

        r = task.executor(requests.get, url).json()

        output = {
            "current": r["c"],
            "change": r["dp"],
            "prev_close": r["pc"]
        }

        return output

    def get_weekly_quote(self, symbol: str = "SPY") -> float:
        """
        Returns the price of the given symbol for the most recent week available.
        Uses Alpha Vantage API.
        """
        symbol = symbol.upper()
        key = secrets.ALPHAVANTAGE_KEY
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol}&apikey={key}"

        r = task.executor(requests.get, url).json()

        latest_week = list(r["Weekly Time Series"].keys())[0]

        latest_week_number = datetime.strptime(latest_week, "%Y-%m-%d").isocalendar().week
        current_week_number = date.today().isocalendar().week

        week_key = "1. open" if latest_week_number == current_week_number else "4. close"

        price = r["Weekly Time Series"][latest_week][week_key]

        return price

    def get_weekly_change(self, symbol: str = "SPY") -> float:
        """
        Uses Finnhub API for current price and Alpha Vantage API for week open price.
        Returns the weekly change for a given stock symbol.
        Change is returned in decimal format (0-1).
        """
        current_price = self.get_quote(symbol)["current"]
        week_open_price = float(self.get_weekly_quote(symbol))

        return (current_price / week_open_price) - 1


class CryptoAPI():
    def get_quotes(self, symbols: list[str], limit: int = 500) -> dict:
        """
        Returns a dict of market data keyed by symbol.
        Each symbol is a dict with keys "rank", "price", "change_hour", "change_day", and "change_week".
        Change is returned in percent format (0-100).
        Uses CoinMarketCap API.
        """
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?start=1&limit={limit}&convert=USD"
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": f"{secrets.CMC_KEY}",
        }

        if not symbols:
            symbols = ["BTC"]

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
