import requests
import secrets
from datetime import date, datetime


def get_stock_week_change(symbol="SPY"):
    return (get_stock_quote(symbol)["current"] / float(get_stock_week(symbol))) - 1


def get_stock_quote(symbol="SPY"):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol.upper()}&token={secrets.FINNHUB_TOKEN}"
    r = task.executor(requests.get, url).json()

    return {"current": r["c"], "change": r["dp"], "prev_close": r["pc"]}


def get_stock_week(symbol="SPY"):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol.upper()}&apikey={secrets.ALPHAVANTAGE_KEY}"
    r = task.executor(requests.get, url).json()

    latest_week = list(r["Weekly Time Series"].keys())[0]

    latest_week_number = datetime.strptime(latest_week, "%Y-%m-%d").isocalendar().week
    current_week_number = date.today().isocalendar().week

    week_key = "1. open" if latest_week_number == current_week_number else "4. close"

    return r["Weekly Time Series"][latest_week][week_key]


def get_crypto_quotes(symbols=["BTC"], limit=500):
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?start=1&limit={limit}&convert=USD"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": f"{secrets.CMC_KEY}",
    }

    r = task.executor(requests.get, url, headers=headers).json()
    parsed = {}

    for symbol_data in r["data"]:
        if symbol_data["symbol"] in symbols:
            parsed[symbol_data["symbol"]] = {
                "rank": symbol_data["cmc_rank"],
                "price": symbol_data["quote"]["USD"]["price"],
                "change_hour": symbol_data["quote"]["USD"]["percent_change_1h"],
                "change_day": symbol_data["quote"]["USD"]["percent_change_24h"],
                "change_week": symbol_data["quote"]["USD"]["percent_change_7d"],
            }

    return parsed
