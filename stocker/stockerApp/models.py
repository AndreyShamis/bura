from django.db import models
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response


class Exchange(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField()

    def __str__(self):
        return self.name
    

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


class Sector(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.sector})"


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
