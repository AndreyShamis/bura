from django.shortcuts import render, redirect
from django.http import HttpResponse
import yfinance as yf
import pandas as pd
from .models import Stock, StockPrice, Ticker
from .utils.thread_manager import thread_manager
from .utils.helpers import start_loop_parse, get_market_status, load_model, save_model, create_moodel
from .forms import StockForm
import logging
import sys
from .templatetags.custom_filters import *

from sklearn.model_selection import train_test_split
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from datetime import datetime, timedelta


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
    tickers = Ticker.objects.all().order_by('symbol')
    context = {
        'tickers':  tickers,
        'stat': get_market_status(),
    }
    if thread_manager.get_thread_count()  == 0:
        thread_manager.start_thread(start_loop_parse,)

    return render(request, 'stock/list.html', context)



def stock_data(request, stock='NVDA'):
    symbol = stock
    # Получить сегодняшнюю дату
    today = datetime.now().date()

    # Вычислить дату 30 дней назад
    start_date = today - timedelta(days=30)

    # Преобразовать даты в строковый формат, требуемый yfinance
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = today.strftime('%Y-%m-%d')
    stock_data = yf.download(symbol, start=start_str, end=end_str)
    stock_data = stock_data.rename(columns={'Adj Close': 'Adjusted'})

    # Преобразование DataFrame в список словарей
    data = stock_data.reset_index().to_dict(orient='records')
    # Get information about the company using Ticker
    ticker = yf.Ticker(symbol)
    myTicker = Ticker.fetch_ticker_data(symbol)
    new_stock = Stock()
    new_stock.symbol = ticker.ticker
    # Пример использования
    tickers = "AAPL,ABBNY,AI,AMZN,ARCC,ARKF,ARKG,ARKK,ARKQ,ARKX,BLCN,CFG,CHMI,COIN,DT,FSLY,GBTC,GOOG,HIVE,IBM,IBOT,INMD,IONQ,LDOS,LRN,META,MNMD,MRNA,MSFT,MTTCF,NEE,NNXPF,NVDA,NXST,PATH,PBW,PLTR,PLUG,PRNT,QS,QTUM,QUBT,SGMO,SHOP,SPCE,STNE,STWD,TDOC,TECL,TM,TQQQ,TSLA,TWLO,VALE,VEEV,VGT,VTVT,XITK,ZTEK,".split(", ")
    stock_data = StockPrice.fetch_stock_price(tickers)

    try:
        new_stock.company_name = ticker.get_info()['longName']
        context = {
            'ticker':  myTicker,
            'stock_data': data,
            'symbol':  ticker.ticker,
            'stock_data2': stock_data,
            'tickers':  ",".join(tickers),
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


import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np

def ai(request):
    text = """
[{"symbol":"SPY","marketPercent":0,"volume":1006823,"lastSalePrice":511.72,"lastSaleSize":200,"lastSaleTime":1709931599550,"lastUpdated":1709935200000,"bids":[],"asks":[],"systemEvent":{"systemEvent":"C","timestamp":1709935800008},"securityEvent":{"securityEvent":"MarketClose","timestamp":1709931600000},"trades":[{"price":511.72,"size":200,"tradeId":4043426685,"isISO":false,"isOddLot":false,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931599550},{"price":511.75,"size":100,"tradeId":4043408781,"isISO":false,"isOddLot":false,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931599504},{"price":511.75,"size":100,"tradeId":4043224995,"isISO":false,"isOddLot":false,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931599047},{"price":511.85,"size":100,"tradeId":4042727928,"isISO":true,"isOddLot":false,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597943},{"price":511.87,"size":200,"tradeId":4042718213,"isISO":false,"isOddLot":false,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597921},{"price":511.87,"size":200,"tradeId":4042695757,"isISO":false,"isOddLot":false,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597844},{"price":511.88,"size":100,"tradeId":4042689767,"isISO":false,"isOddLot":false,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597817},{"price":511.87,"size":1,"tradeId":4042686667,"isISO":true,"isOddLot":true,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597806},{"price":511.87,"size":1,"tradeId":4042682621,"isISO":true,"isOddLot":true,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597803},{"price":511.87,"size":2,"tradeId":4042682561,"isISO":true,"isOddLot":true,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597803},{"price":511.87,"size":3,"tradeId":4042682509,"isISO":true,"isOddLot":true,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597803},{"price":511.87,"size":4,"tradeId":4042682465,"isISO":true,"isOddLot":true,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597803},{"price":511.87,"size":5,"tradeId":4042682417,"isISO":true,"isOddLot":true,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597803},{"price":511.87,"size":7,"tradeId":4042682348,"isISO":true,"isOddLot":true,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597803},{"price":511.89,"size":3,"tradeId":4042418304,"isISO":true,"isOddLot":true,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597202},{"price":511.89,"size":2,"tradeId":4042418252,"isISO":true,"isOddLot":true,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597202},{"price":511.89,"size":5,"tradeId":4042418206,"isISO":true,"isOddLot":true,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597202},{"price":511.89,"size":10,"tradeId":4042418164,"isISO":true,"isOddLot":true,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597202},{"price":511.89,"size":19,"tradeId":4042418119,"isISO":true,"isOddLot":true,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931597202},{"price":511.88,"size":200,"tradeId":4041799543,"isISO":false,"isOddLot":false,"isOutsideRegularHours":false,"isSinglePriceCross":false,"isTradeThroughExempt":false,"timestamp":1709931596004}],"tradeBreaks":[]}]
"""
    testInput = request.POST.get('textToAnalyze', '')

        # Определение классов форматов
    classes = ['json', 'csv', 'xml', 'html', 'unknown']

    # Примеры для обучения
    train_data = [
        '{"name": "John", "age": 30}',  # JSON
        'name,age\nJohn,30',  # CSV
        '<person><name>John</name><age>30</age></person>',  # XML
        '<html><body><p>Hello, World!</p></body></html>',  # HTML
        'This is some unknown format text.'  # Unknown
    ]

    # Соответствующие метки
    train_labels = [0, 1, 2, 3, 4]

    # Токенизация текста
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(train_data)
    sequences = tokenizer.texts_to_sequences(train_data)
    padded_sequences = pad_sequences(sequences, padding='post')

    # One-hot encoding меток
    one_hot_labels = tf.one_hot(train_labels, depth=len(classes))

    model = tf.keras.models.load_model('text_format_model.h5')

    # # Определение модели
    # model = tf.keras.Sequential([
    #     tf.keras.layers.Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=64),
    #     tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),
    #     tf.keras.layers.Dense(len(classes), activation='softmax')
    # ])

    # # Компиляция модели
    # model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    # # Обучение модели
    # model.fit(padded_sequences, one_hot_labels, epochs=100, verbose=1)


    

    logger.info(f"{testInput}")
    # # Пример данных
    # texts = ["{...}", "1,2,3", "<xml>...</xml>", "<html>...</html>", "..."]
    # labels = [0, 1, 2, 3, 4] # 0 - JSON, 1 - CSV, 2 - XML, 3 - HTML, 4 - другой формат

    # # Разделение данных на обучающую и тестовую выборки
    # X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

    # # Предварительная обработка текста
    # X_train = preprocess_text(X_train)
    # X_test = preprocess_text(X_test)
    # # Преобразование текста в числовой вектор
    # vectorized_text = preprocess_text(text, 100)
    format_name = []
    # Примеры использования
    print(predict_format('{"name": "Alice", "age": 25}', tokenizer, model,  sequences, classes))  # JSON
    # print(predict_format('name,age\nAlice,25', tokenizer, model,  sequences, classes))  # CSV
    # print(predict_format('<person><name>Alice</name><age>25</age></person>', tokenizer, model,  sequences, classes))  # XML
    # print(predict_format('<html><body><h1>Welcome!</h1></body></html>', tokenizer, model,  sequences, classes))  # HTML
    # print(predict_format('This is a new format text.', tokenizer, model,  sequences, classes))  # Unknown
    # Предсказание формата текста
    try:
        pass
        # model  = create_moodel()
        # Обучение модели
        # model.fit(np.array(X_train), np.array(y_train), epochs=10, batch_size=32 ,verbose=1) # model.fit(X_train, y_train, epochs=10, batch_size=32) 
        # Тестирование модели
        # _, accuracy = model.evaluate(X_test, y_test)
        # print('Accuracy: %.2f' % (accuracy*100))
        # prediction = model.predict(np.array([vectorized_text]))
        # Определение формата по индексу максимального значения в предсказании
        # format_index = np.argmax(prediction)
        # format_name = ['JSON', 'CSV', 'XML', 'HTML', 'Other'][format_index]
    except Exception as ex:
        logger.error(f'{ex}')
    context = {
        'testInput': testInput,
        'format_name': format_name,
        'result': predict_format(testInput, tokenizer, model, sequences, classes),
    }
    #model.save('text_format_model.h5')
    return render(request, 'ai.html', context)

# Функция для предсказания формата текста
def predict_format(text, tokenizer, model, sequences, classes):
    sequence = tokenizer.texts_to_sequences([text])
    padded_sequence = pad_sequences(sequence, maxlen=max(len(seq) for seq in sequences), padding='post')
    prediction = model.predict(padded_sequence)
    predicted_class = np.argmax(prediction[0])
    return classes[predicted_class]



def preprocess_text(texts, max_len=100):
    tokenizer = Tokenizer(num_words=10000, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    padded_sequences = pad_sequences(sequences, maxlen=max_len, padding='post', truncating='post')
    return padded_sequences