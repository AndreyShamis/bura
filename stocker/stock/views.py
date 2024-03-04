from django.shortcuts import render
from django.http import HttpResponse
import yfinance as yf
import pandas as pd
from .models import Stock, Ticker as MyTicker


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def stock_data(request):
    symbol = 'IREN'  # Example stock symbol
    symbols = ['IREN', 'MSFT', 'SPY', 'QQQ', 'NVDA', 'META', 'GOOG', 'GOOGL', 'INTC', 'MBLY']
    for s in symbols:
        # Fetch stock data using yfinance
        stock_data = yf.download(s, start='2024-01-01', end='2024-03-03')
        stock_data = stock_data.rename(columns={'Adj Close': 'Adjusted'})

        # Преобразование DataFrame в список словарей
        data = stock_data.reset_index().to_dict(orient='records')
        # Get information about the company using Ticker
        ticker = yf.Ticker(s)
        myTicker = MyTicker.fetch_ticker_data(s)
        new_stock = Stock()
        new_stock.symbol = ticker.ticker
        new_stock.company_name = ticker.get_info()['longName']
    context = {
        'stock_data': data,
        'symbol':  ticker.ticker,
    }
    return render(request, 'stock/data.html', context)

