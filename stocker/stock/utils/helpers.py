import time
from .thread_manager import thread_manager
from ..models import Ticker 
from datetime import datetime, timedelta, time as ddtime
from keras.models import model_from_json
from keras.models import Sequential
from keras.layers import Dense


def get_market_status():
    current_time = datetime.utcnow().time()
    market_open_time = ddtime(9, 30)  # Market open time (e.g., 9:30 AM)
    market_close_time = ddtime(16, 0)  # Market close time (e.g., 4:00 PM)
    pre_market_open_time = ddtime(4, 0)  # Pre-market open time (e.g., 4:00 AM)
    pre_market_close_time = ddtime(9, 30)  # Pre-market close time (e.g., 9:30 AM)
    post_market_open_time = ddtime(16, 0)  # Post-market open time (e.g., 4:00 PM)
    post_market_close_time = ddtime(20, 0)  # Post-market close time (e.g., 8:00 PM)

    # Adjust current time to UTC
    current_time_utc = (datetime.utcnow() - timedelta(hours=5)).time()  # Adjust for UTC+5 timezone

    # Check current time against trading hours
    if market_open_time <= current_time_utc < market_close_time:
        return "Market"
    elif pre_market_open_time <= current_time_utc < pre_market_close_time:
        return "PreMarket"
    elif post_market_open_time <= current_time_utc < post_market_close_time:
        return "PostMarket"
    else:
        return "Closed"

def get_pre_single(ticker: Ticker):
    pre_price = ticker.get_pre_market_price()
    if pre_price is not None and float(pre_price) > 0:
        ticker.preMarket = pre_price
        thread_manager.lock.acquire()
        ticker.save()
        try:
            thread_manager.lock.release()
        except:
            pass

def get_post_single(ticker: Ticker):
    post_price = ticker.get_post_market_price()
    if post_price is not None and float(post_price) > 0:
        ticker.postMarket = post_price
        thread_manager.lock.acquire()
        ticker.save()
        try:
            thread_manager.lock.release()
        except:
            pass

def periodc_get_pre_market_for_all_tickers():
    tickers = Ticker.objects.all()
    mar = get_market_status()
    for ticker in tickers:
        if mar == 'PreMarket':
            thread_manager.start_thread(get_pre_single, ticker)
            time.sleep(0.031)
        if mar == 'PostMarket':
            thread_manager.start_thread(get_post_single, ticker)
            time.sleep(0.021)
        thread_manager.start_thread(Ticker.fetch_ticker_data, ticker.symbol)
        #Ticker.fetch_ticker_data(ticker.symbol)
        time.sleep(0.09)
    print(f'FINISH PARSE {tickers.count()} Thread {thread_manager.get_thread_count()}')


def start_loop_parse():
    while True:
        periodc_get_pre_market_for_all_tickers()
        time.sleep(0.3)
        if thread_manager.get_thread_count() > 20:
            time.sleep(0.6)
        thread_manager.close_finished_threads()
        if thread_manager.get_thread_count() > 20:
            time.sleep(0.6)
        thread_manager.close_finished_threads()
        if thread_manager.get_thread_count() > 40:
            thread_manager.stop_all_threads()
            time.sleep(2)


def get_precent(total: float, part: float) -> float:
    """
    Calculates the percentage of 'part' in 'total', rounded to 3 digits.
    Returns 0 if 'part' is 0.

    Args:
        total: The total value.
        part: The value to be compared.

    Returns:
        The percentage of 'part' in 'total', rounded to 3 digits, or 0 if 'part' is 0.
    """
    if part == 0:
        return 0
    return round(part / total * 100, 3)


def get_part(percent: float, total: float) -> float:
    """
    Calculates the part value, given a percentage and a total value.

    Args:
        percent: The percentage.
        total: The total value.

    Returns:
        The part value.
    """
    return percent / 100 * total


def save_model(model: Sequential, model_path: str, weights_path: str):
    model_json = model.to_json()
    with open(model_path, "w") as json_file:
        json_file.write(model_json)

    model.save_weights(weights_path)


def load_model(model_path: str, weights_path: str) -> Sequential:
    json_file = open(model_path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights(weights_path)
    # Compile loaded model
    loaded_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    return loaded_model


def create_moodel(input_dim=100, num_classes=5) -> Sequential:
        # Создание модели
    model = Sequential()
    model.add(Dense(128, input_dim=input_dim, activation='relu')) # Входной слой
    model.add(Dense(64, activation='relu')) # Скрытый слой
    model.add(Dense(num_classes, activation='softmax')) # Выходной слой с 5 нейронами для классификации JSON, CSV, XML, HTML и другого формата

    # Компиляция модели
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    return model
