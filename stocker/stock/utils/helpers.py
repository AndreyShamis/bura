import time
from ..models import Ticker 

def periodc_get_pre_market_for_all_tickers():
    tickers = Ticker.objects.all()
    for ticker in tickers:
        pre_price = ticker.get_pre_market_price()
        if pre_price is not None and float(pre_price) > 0:
            ticker.preMarket = pre_price
            ticker.save()
        
        # post_price = ticker.get_post_market_price()
        # if post_price is not None and float(post_price) > 0:
        #     ticker.postMarket = post_price
        #     ticker.save()
        
        Ticker.fetch_ticker_data(ticker.symbol)
    print(f'FINISH PARSE {tickers.count()}')


def start_loop_parse():
    while True:
        periodc_get_pre_market_for_all_tickers()
        time.sleep(0.1)
