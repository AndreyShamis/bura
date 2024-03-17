from datetime import datetime
import threading
from django.db import models
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from django.urls import path
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pprint
import time
import re
import logging
from .utils.thread_manager import thread_manager

class Exchange(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField()

    def __str__(self):
        return self.name


class Sector(models.Model):
    sectorKey = models.CharField(max_length=100, null=True, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    sectorDisp = models.CharField(max_length=100, null=True, blank=True)
    
    @staticmethod
    def fetch_sector(name, sectorKey, sectorDisp):
        try:
            thread_manager.lock.acquire()
            obj, created = Sector.objects.get_or_create(name=name, sectorKey=sectorKey, sectorDisp=sectorDisp)
            obj.save()
            return obj
        except Exception as ex:
            logging.error(f'[Sector:fetch_sector]{ex}')
            return None
        finally:
            try:
                thread_manager.lock.release()
            except:
                pass

    def __str__(self):
        return f'{self.sectorDisp}'
 

class Industry(models.Model):
    industryKey = models.CharField(max_length=100, null=True, unique=True)
    name = models.CharField(max_length=100, null=True, unique=True)
    sector = models.ForeignKey(Sector, null=True, on_delete=models.CASCADE)
    industryDisp = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.industryDisp}'


    @staticmethod
    def fetch_industry(name, industryKey, industryDisp, sector):
        try:
            thread_manager.lock.acquire()
            obj, created = Industry.objects.get_or_create(name=name, industryKey=industryKey, industryDisp=industryDisp, sector=sector)
            obj.save()
            return obj
        except Exception as ex:
            logging.error(f'[Industry:fetch_industry]{ex}')
            return None
        finally:
            try:
                thread_manager.lock.release()
            except:
                pass

class Ticker(models.Model):

    lock = threading.Lock()
    
    symbol = models.CharField(max_length=10, unique=True)

    preMarket = models.FloatField(null=True, blank=True)
    postMarket = models.FloatField(null=True, blank=True)
    fiftyTwoWeekChange = models.FloatField(null=True, blank=True)
    SandP52WeekChange = models.FloatField(null=True, blank=True)
    address1 = models.CharField(max_length=255, null=True, blank=True)
    ask = models.FloatField(null=True, blank=True)
    askSize = models.IntegerField(null=True, blank=True)
    auditRisk = models.IntegerField(null=True, blank=True)
    averageDailyVolume10Day = models.IntegerField(null=True, blank=True)
    averageVolume = models.IntegerField(null=True, blank=True)
    averageVolume10days = models.IntegerField(null=True, blank=True)
    beta = models.FloatField(null=True, blank=True)
    bid = models.FloatField(null=True, blank=True)
    bidSize = models.IntegerField(null=True, blank=True)
    boardRisk = models.IntegerField(null=True, blank=True)
    bookValue = models.FloatField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    compensationAsOfEpochDate = models.DateTimeField(null=True, blank=True)
    compensationRisk = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    currentPrice = models.FloatField(null=True, blank=True)
    currentRatio = models.FloatField(null=True, blank=True)
    dateShortInterest = models.DateTimeField(null=True, blank=True)
    dayHigh = models.FloatField(null=True, blank=True)
    dayLow = models.FloatField(null=True, blank=True)
    debtToEquity = models.FloatField(null=True, blank=True)
    dividendRate = models.FloatField(null=True, blank=True)
    dividendYield = models.FloatField(null=True, blank=True)
    earningsGrowth = models.FloatField(null=True, blank=True)
    earningsQuarterlyGrowth = models.FloatField(null=True, blank=True)
    ebitda = models.BigIntegerField(null=True, blank=True)
    ebitdaMargins = models.FloatField(null=True, blank=True)
    enterpriseToEbitda = models.FloatField(null=True, blank=True)
    enterpriseToRevenue = models.FloatField(null=True, blank=True)
    enterpriseValue = models.BigIntegerField(null=True, blank=True)
    exDividendDate = models.DateTimeField(null=True, blank=True)
    exchange = models.CharField(max_length=10, null=True, blank=True)
    fiftyDayAverage = models.FloatField(null=True, blank=True)
    fiftyTwoWeekHigh = models.FloatField(null=True, blank=True)
    fiftyTwoWeekLow = models.FloatField(null=True, blank=True)
    financialCurrency = models.CharField(max_length=10, null=True, blank=True)
    firstTradeDateEpochUtc = models.BigIntegerField(null=True, blank=True)
    fiveYearAvgDividendYield = models.FloatField(null=True, blank=True)
    floatShares = models.BigIntegerField(null=True, blank=True)
    forwardEps = models.FloatField(null=True, blank=True)
    forwardPE = models.FloatField(null=True, blank=True)
    freeCashflow = models.BigIntegerField(null=True, blank=True)
    fullTimeEmployees = models.IntegerField(null=True, blank=True)
    gmtOffSetMilliseconds = models.IntegerField(null=True, blank=True)
    governanceEpochDate = models.DateTimeField(null=True, blank=True)
    grossMargins = models.FloatField(null=True, blank=True)
    heldPercentInsiders = models.FloatField(null=True, blank=True)
    heldPercentInstitutions = models.FloatField(null=True, blank=True)
    impliedSharesOutstanding = models.BigIntegerField(null=True, blank=True)
    industry = models.CharField(max_length=255, null=True, blank=True)
    industryDisp = models.CharField(max_length=255, null=True, blank=True)
    industryKey = models.CharField(max_length=255, null=True, blank=True)
    lastDividendDate = models.DateTimeField(null=True, blank=True)
    lastDividendValue = models.FloatField(null=True, blank=True)
    lastFiscalYearEnd = models.DateTimeField(null=True, blank=True)
    lastSplitDate = models.DateTimeField(null=True, blank=True)
    lastSplitFactor = models.CharField(max_length=255, null=True, blank=True)
    longName = models.CharField(max_length=255, null=True, blank=True)
    marketCap = models.BigIntegerField(null=True, blank=True)
    maxAge = models.IntegerField(null=True, blank=True)
    messageBoardId = models.CharField(max_length=255, null=True, blank=True)
    mostRecentQuarter = models.DateTimeField(null=True, blank=True)
    netIncomeToCommon = models.BigIntegerField(null=True, blank=True)
    nextFiscalYearEnd = models.DateTimeField(null=True, blank=True)
    numberOfAnalystOpinions = models.IntegerField(null=True, blank=True)
    openPrice = models.FloatField(null=True, blank=True)
    operatingCashflow = models.BigIntegerField(null=True, blank=True)
    operatingMargins = models.FloatField(null=True, blank=True)
    overallRisk = models.IntegerField(null=True, blank=True)
    payoutRatio = models.FloatField(null=True, blank=True)
    pegRatio = models.FloatField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    previousClose = models.FloatField(null=True, blank=True)
    priceHint = models.IntegerField(null=True, blank=True)
    priceToBook = models.FloatField(null=True, blank=True)
    priceToSalesTrailing12Months = models.FloatField(null=True, blank=True)
    profitMargins = models.FloatField(null=True, blank=True)
    quickRatio = models.FloatField(null=True, blank=True)
    quoteType = models.CharField(max_length=255, null=True, blank=True)
    recommendationKey = models.CharField(max_length=255, null=True, blank=True)
    recommendationMean = models.FloatField(null=True, blank=True)
    regularMarketDayHigh = models.FloatField(null=True, blank=True)
    regularMarketDayLow = models.FloatField(null=True, blank=True)
    regularMarketOpen = models.FloatField(null=True, blank=True)
    regularMarketPreviousClose = models.FloatField(null=True, blank=True)
    regularMarketVolume = models.BigIntegerField(null=True, blank=True)
    returnOnAssets = models.FloatField(null=True, blank=True)
    returnOnEquity = models.FloatField(null=True, blank=True)
    revenueGrowth = models.FloatField(null=True, blank=True)
    revenuePerShare = models.FloatField(null=True, blank=True)
    sector = models.CharField(max_length=255, null=True, blank=True)
    sectorDisp = models.CharField(max_length=255, null=True, blank=True)
    sectorKey = models.CharField(max_length=255, null=True, blank=True)

    appSector = models.ForeignKey(Sector, null=True, on_delete=models.CASCADE)

    shareHolderRightsRisk = models.IntegerField(null=True, blank=True)
    sharesOutstanding = models.BigIntegerField(null=True, blank=True)
    sharesPercentSharesOut = models.FloatField(null=True, blank=True)
    sharesShort = models.BigIntegerField(null=True, blank=True)
    sharesShortPreviousMonthDate = models.DateTimeField(null=True, blank=True)
    sharesShortPriorMonth = models.BigIntegerField(null=True, blank=True)
    shortName = models.CharField(max_length=255, null=True, blank=True)
    shortPercentOfFloat = models.FloatField(null=True, blank=True)
    shortRatio = models.FloatField(null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    symbol = models.CharField(max_length=10, null=True, blank=True)
    targetHighPrice = models.FloatField(null=True, blank=True)
    targetLowPrice = models.FloatField(null=True, blank=True)
    targetMeanPrice = models.FloatField(null=True, blank=True)
    targetMedianPrice = models.FloatField(null=True, blank=True)
    timeZoneFullName = models.CharField(max_length=255, null=True, blank=True)
    timeZoneShortName = models.CharField(max_length=10, null=True, blank=True)
    totalCash = models.BigIntegerField(null=True, blank=True)
    totalCashPerShare = models.FloatField(null=True, blank=True)
    totalDebt = models.BigIntegerField(null=True, blank=True)
    totalRevenue = models.BigIntegerField(null=True, blank=True)
    trailingAnnualDividendRate = models.FloatField(null=True, blank=True)
    trailingAnnualDividendYield = models.FloatField(null=True, blank=True)
    trailingEps = models.FloatField(null=True, blank=True)
    trailingPE = models.FloatField(null=True, blank=True)
    trailingPegRatio = models.FloatField(null=True, blank=True)
    twoHundredDayAverage = models.FloatField(null=True, blank=True)
    underlyingSymbol = models.CharField(max_length=10, null=True, blank=True)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)
    zipCode = models.CharField(max_length=10, null=True, blank=True)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
    }
    urlka = 'https://finance.yahoo.com/quote/'
    def __str__(self):
        return f'{self.symbol} - {self.currentPrice} [{self.askSize}/{self.bidSize}]'


    def get_post_market_price(self):
        try:
            response = requests.get(f"{self.urlka}{self.symbol}", headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            value = soup.find('fin-streamer', {'data-field': 'postMarketPrice'}).text
            value = re.findall(r'\d+\.\d+', value)[0]
            if value is not None:
                return value
        except Exception as ex:
            logging.error(f'[get_post_market_price]{self.symbol}:{ex}')
            return -1
        return 0

    def get_pre_market_price(self):
        dbg = ''
        try:
            response = requests.get(f"{self.urlka}{self.symbol}", headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            dbg = soup.find('fin-streamer', {'data-field': 'preMarketPrice'})
            if dbg is not None:
                value = dbg.text
                value = re.findall(r'\d+\.\d+', value)
                if value:
                    return value[0]
        except Exception as ex:
            logging.error(f'[get_pre_market_price]{self.symbol}:{ex} - {dbg}')
            return -1
        return 0

    @staticmethod
    def fetch_ticker_data(symbol: str):
        # Fetch data using yfinance
        ticker = yf.Ticker(symbol)
        try:
            ticker_info = ticker.info
        except Exception as ex:
            logging.error(f'[fetch_ticker_data]{symbol}:{ex}')
            time.sleep(0.3)
            return None
        Ticker.lock.acquire()        # Create or update Ticker object
        obj, created = Ticker.objects.get_or_create(symbol=symbol)
        Ticker.lock.release()
        for field in Ticker._meta.fields:
            field_name = field.name
            if field_name != 'id':  # Exclude id and symbol fields
                field_name_search = field_name
                if field_name == 'openPrice':
                    field_name_search = 'open'
                if field_name == 'zipCode':
                    field_name_search = 'zip'
                value = ticker_info.get(field_name_search)
                if field_name == 'bidSize':
                    if symbol == 'NVDA':
                        pass
                if value is not None:
                    if isinstance(field, models.DateTimeField) and not isinstance(value, str):
                        # Convert non-string datetime to string
                        value = datetime.fromtimestamp(int(value))
                    setattr(obj, field_name, value)


        try:
            #sector = Sector.fetch_sector(obj.sector, obj.sectorKey, obj.sectorDisp)
            #Industry.fetch_industry(obj.industry, obj.industryDisp, obj.industryKey, sector)
            thread_manager.lock.acquire()
            obj.save()
        except:
            pass
        finally:
            try:
                thread_manager.lock.release()
            except:
                pass
        return obj
    

class Stock(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_change = models.DecimalField(max_digits=10, decimal_places=2)
    percent_change = models.DecimalField(max_digits=5, decimal_places=2)
    volume = models.IntegerField()
    market_cap = models.DecimalField(max_digits=20, decimal_places=2)
    sector = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.symbol} ({self.company_name}- {self.price})"

    @property
    def is_bullish(self):
        return self.price_change > 0

    @property
    def is_bearish(self):
        return self.price_change < 0

    @property
    def is_trending_up(self):
        return self.percent_change > 0.5

    @property
    def is_trending_down(self):
        return self.percent_change < -0.5


class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.IntegerField()
    market_type = models.CharField(
        max_length=20, choices=[("pre", "Pre-market"), ("post", "Post-market"), ("regular", "Regular market")]
    )

    def __str__(self):
        return f"{self.stock.symbol} - {self.timestamp} - {self.price} - {self.market_type}"


class TechnicalIndicator(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.stock.symbol} - {self.name} - {self.value} - {self.timestamp}"


class StockNews(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    news = models.TextField()
    date = models.DateField(auto_now_add=True)


class IndicatorCalculator:
    @staticmethod
    def calculate_sma(data, window):
        if len(data) < window:
            return None
        return sum(data[-window:]) / window

    @staticmethod
    def calculate_ema(data, window):
        if len(data) < window:
            return None
        k = 2 / (window + 1)
        ema = sum(data[:window]) / window
        for price in data[window:]:
            ema = (price - ema) * k + ema
        return ema


class StockPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPrice
        fields = '__all__'


class StockSerializer(serializers.ModelSerializer):
    prices = StockPriceSerializer(many=True, read_only=True)

    class Meta:
        model = Stock
        fields = '__all__'


class StockPriceList(APIView):
    def get(self, request):
        stocks = Stock.objects.all()
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)


class StockPriceDetail(APIView):
    def get_object(self, symbol):
        try:
            return Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            raise Http404

    def get(self, request, symbol):
        stock = self.get_object(symbol)
        prices = StockPrice.objects.filter(stock=stock)
        serializer = StockPriceSerializer(prices, many=True)
        return Response(serializer.data)


urlpatterns = [
    path('api/stocks/', StockPriceList.as_view()),
    path('api/stocks/<str:symbol>/', StockPriceDetail.as_view()),
]
