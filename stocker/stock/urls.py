from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<stock>", views.stock_data, name="stock"),
    path('create/', views.create_stock, name='create_stock'),
    path('ai/', views.ai, name='ai'),

]