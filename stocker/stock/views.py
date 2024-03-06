from django.shortcuts import render, redirect
from django.http import HttpResponse
import yfinance as yf
import pandas as pd
from .models import Stock, Ticker
from .utils.thread_manager import thread_manager
from .utils.helpers import start_loop_parse, get_market_status
from .forms import StockForm
import logging
import sys


DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'


logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(module)10.10s:%(lineno)4.4d | %(levelname)-5.5s  - %(message)s', datefmt='%d/%m/%y %H:%M:%S')


# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s')

# Create console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


def index(request):
    tickers = Ticker.objects.all()
    context = {
        'tickers':  tickers,
        'stat': get_market_status(),
    }
    if thread_manager.get_thread_count()  == 0:
        thread_manager.start_thread(start_loop_parse,)

    return render(request, 'index.html', context)



def stock_data(request, stock='NVDA'):
    symbol = stock
    # Fetch stock data using yfinance
    stock_data = yf.download(symbol, start='2024-01-01', end='2024-03-03')
    stock_data = stock_data.rename(columns={'Adj Close': 'Adjusted'})

    # Преобразование DataFrame в список словарей
    data = stock_data.reset_index().to_dict(orient='records')
    # Get information about the company using Ticker
    ticker = yf.Ticker(symbol)
    myTicker = Ticker.fetch_ticker_data(symbol)
    new_stock = Stock()
    new_stock.symbol = ticker.ticker
    try:
        new_stock.company_name = ticker.get_info()['longName']
        context = {
            'stock_data': data,
            'symbol':  ticker.ticker,
        }
    except Exception:
        myTicker.delete()
        return redirect('index')
    return render(request, 'stock/data.html', context)

def create_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            myTicker = Ticker.fetch_ticker_data(symbol)
            #form.save()
            return redirect('index')
            return redirect('success')  # Redirect to success page or another URL
    else:
        form = StockForm()
    return render(request, 'stock/create.html', {'form': form})
