from django.shortcuts import render
from django.http import HttpResponse
import yfinance as yf
import pandas as pd
from .models import Stock, Ticker as MyTicker


def index(request):
    tickers = MyTicker.objects.all()
    for s in tickers:
        MyTicker.fetch_ticker_data(s.symbol)
    context = {
        'tickers':  tickers,
    }

    tickers = MyTicker.objects.all()
    return render(request, 'index.html', context)


def stock_data(request, symbol='NVDA'):
    # Fetch stock data using yfinance
    stock_data = yf.download(symbol, start='2024-01-01', end='2024-03-03')
    stock_data = stock_data.rename(columns={'Adj Close': 'Adjusted'})

    # Преобразование DataFrame в список словарей
    data = stock_data.reset_index().to_dict(orient='records')
    # Get information about the company using Ticker
    ticker = yf.Ticker(symbol)
    myTicker = MyTicker.fetch_ticker_data(symbol)
    new_stock = Stock()
    new_stock.symbol = ticker.ticker
    new_stock.company_name = ticker.get_info()['longName']
    context = {
        'stock_data': data,
        'symbol':  ticker.ticker,
    }
    return render(request, 'stock/data.html', context)

