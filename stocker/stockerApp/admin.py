from django.contrib import admin
from .models import Stock, StockPrice, Sector, Industry, TechnicalIndicator


admin.site.register(Stock)
admin.site.register(StockPrice)
admin.site.register(Sector)
admin.site.register(Industry)
admin.site.register(TechnicalIndicator)
