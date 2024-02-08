import yfinance as yf
import pandas as pd
import numpy as np
import tensorflow as tf
from pprint import pprint
import seaborn as sns
import logging
import matplotlib.pyplot as plt
# import Prophet
# import TextBlob
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'


logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(module)10.10s:%(lineno)4.4d | %(levelname)-5.5s  - %(message)s', datefmt='%d/%m/%y %H:%M:%S')
#logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


msft = yf.Ticker("MSFT")
# get historical market data
hist = msft.history(period="1m")
data = yf.download("MSFT", start="2024-02-05", end="2024-02-08", period="1m")
print(msft.actions)
print(msft.info)


class StockInfo:
    _volume = 0

    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.download(ticker, period="1d", interval="1m", progress=False)
        self._open = self.stock["Open"].iloc[-1]
        self._close = self.stock["Close"].iloc[-1]
        self._high = self.stock["High"].iloc[-1]
        self._low = self.stock["Low"].iloc[-1]

        
        try:
            self._volume = self.stock["Volume"].iloc[-1]
        except Exception as e:
            logging.exception(e)

    def get_current_price(self):
        return self._close
    
    def get_day_open(self):
        return self._open
    
    def get_day_high(self):
        return self._high

    def get_day_low(self):
        return self._low

    def get_volume(self):
        return self._volume

    def print_summary(self):
        logging.info(f"CUR : {self.get_current_price()} OPEN: {self.get_day_open()}  \t MAX: {self.get_day_high()} \t MIN: {self.get_day_low()}\t VOL: {self.get_volume()}")


# Генерация данных для примера
np.random.seed(0)
x = np.linspace(0, 100, 1000)
y = np.sin(x) + np.random.normal(0, 0.1, size=x.shape)

# Нормализация данных
x = (x - np.mean(x)) / np.std(x)
y = (y - np.mean(y)) / np.std(y)

# Разделение данных на обучающий и тестовый наборы
split = int(0.8 * len(x))
x_train, x_test = x[:split], x[split:]
y_train, y_test = y[:split], y[split:]

# Создание нейронной сети
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, input_shape=(1,), activation='relu'),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(1)
])

model.compile(optimizer='adam', loss='mse')

# Обучение модели
model.fit(x_train, y_train, epochs=50, batch_size=16, verbose=1)

# Предсказание следующего значения
next_value = model.predict(np.array([x_test[-1]]))
print("Предсказанное следующее значение:", next_value[0][0])

# Оценка вероятности роста или падения
predictions = model.predict(x_test)
change_probabilities = predictions - y_test.reshape(-1, 1)
increase_probability = np.mean(change_probabilities > 0)
decrease_probability = np.mean(change_probabilities < 0)
print("Вероятность подъема в следующий раз:", increase_probability)
print("Вероятность падения в следующий раз:", decrease_probability)




ticker = "AAPL"
stock_info = StockInfo(ticker)

# Печать информации о акции
stock_info.print_summary()

# Доступ к другим полям
print(f"Открытие: {stock_info.stock['Open'].iloc[-1]}")
print(f"Закрытие: {stock_info.stock['Close'].iloc[-1]}")

def anali(ticker: str= 'AAPL', show_visual: bool = False):
    logging.info(f'  --------------------   {ticker} start  --------------------   ')
    # Получаем данные о ценах акций компании
    data = yf.download(ticker, start='2022-11-01', end='2024-02-07')

    # Создаем новый столбец с ценами акций на следующий день
    data['Next Day Price'] = data['Close'].shift(-1)
    data['Negative'] = np.zeros(data['Next Day Price'].size)
    data['Memuca'] = np.zeros(data['Next Day Price'].size)

    # Удаляем строки с пропущенными значениями (последняя строка будет содержать NaN, так как нет следующей цены)
    data.dropna(inplace=True)
    # Определяем независимую и зависимую переменные
    X = np.array(data['Close']).reshape(-1, 1)  # Закрытые цены
    y = np.array(data['Next Day Price'])  # Следующий день цены

    ar3 = np.stack(( np.array(data['Open']), np.array(data['High']),  np.array(data['Low']), np.array(data['Close']), np.array(data['Negative']), np.array(data['Negative']), np.array(data['Negative']), np.array(data['Negative']), np.array(data['Memuca'])), axis=1)
    prev_x = None
    for x in ar3:
        if prev_x is not None:
            if prev_x[0] > x[0]:
                x[4] = 1
            else:
                x[4] = -1
            if prev_x[1] > x[1]:
                x[5] = 1
            else:
                x[5] = -1
            if prev_x[2] > x[2]:
                x[6] = 1
            else:
                x[6] = -1
            if prev_x[3] > x[3]:
                x[7] = 1
            else:
                x[7] = -1

            x[8] = (x[0] + x[1] + x[2] + x[3])/4
            #logging.warning(f'{x[0]:<10}')
        prev_x = x
    # Разделяем данные на тренировочный и тестовый набор
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Создаем и обучаем модель линейной регрессии
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Предсказываем цены на акции на тестовом наборе данных
    predictions = model.predict(X_test)

    # Считаем среднеквадратичную ошибку модели
    mse = np.mean((predictions - y_test)**2)

    if show_visual:
        # Визуализация реальных и предсказанных цен на акции
        plt.scatter(X_test, y_test, color='black')
        plt.plot(X_test, predictions, color='blue', linewidth=3)
        plt.xlabel(f'{ ticker} : Closing Price')
        plt.ylabel(f'{ ticker} : Next Day Price')
        plt.title(f'{ ticker} : Stock Price Prediction')
        plt.show()

    # Пример использования модели для прогнозирования цены на акцию завтра
    last_price = data['Close'].iloc[-1].reshape(1, -1)  # Закрытая цена последнего дня
    next_day_prediction = model.predict(last_price)

        # Обучение модели на исторических данных
    # model2 = LinearRegression()
    # model2.fit(data[['Open', 'High', 'Low', 'Volume']], data['Close'])

    # Прогнозирование цены акции на следующий день
    prediction = 0# model2.predict([[data['Open'].iloc[-1].values, data['High'].iloc[-1].values, data['Low'].iloc[-1].values, data['Volume'].iloc[-1]]])

    logging.info(f'{ ticker } - Predicted price for tomorrow: {next_day_prediction[0]} (Mean Squared Error: {mse}) - \t {prediction}')


anali('AAPL')
anali('AMZN')
anali('MSFT')
anali('NFLX')

anali('AMD')
anali('SPY')
anali('QQQ')


# data = yf.download("GOOG", start="2023-01-01", end="2024-01-01")
# # Вычисление скользящих средних
# data['SMA_50'] = data['Close'].rolling(50).mean()
# data['SMA_200'] = data['Close'].rolling(200).mean()

# # Построение графиков
# plt.plot(data['Close'])
# plt.plot(data['SMA_50'])
# plt.plot(data['SMA_200'])
# plt.show(block=False)


# # Обучение модели на исторических данных
# model = LinearRegression()
# model.fit(data[['Open', 'High', 'Low', 'Volume']], data['Close'])

# # Прогнозирование цены акции на следующий день
# prediction = model.predict([[data['Open'].iloc[-1], data['High'].iloc[-1], data['Low'].iloc[-1], data['Volume'].iloc[-1]]])

# logging.info('f{prediction}')


# # Распределение цены акции
# sns.distplot(data['Close'])
# plt.show()

# # Тепловая карта корреляций
# sns.heatmap(data.corr(), annot=True)
# plt.show()




