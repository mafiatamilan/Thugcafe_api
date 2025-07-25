# Pos_App/urls.py

from django.urls import path
from .views import (
    CategoryAPIView, ProductAPIView, CustomerAPIView,
    SaleAPIView, SaleCreateAPIView, SalesDetailAPIView,
    EmployeeAPIView, EmployeeLoginAPIView
)

urlpatterns = [
        path('login/', EmployeeLoginAPIView.as_view(), name='employee-login'),

    path('categories/', CategoryAPIView.as_view(), name='category'),
    path('products/', ProductAPIView.as_view(), name='product'),
    path('customers/', CustomerAPIView.as_view(), name='customer'),
    path('employees/', EmployeeAPIView.as_view(), name='employee'),
    path('sales/', SaleAPIView.as_view(), name='sales'),
    path('sale-details/', SalesDetailAPIView.as_view(), name='sales-details'),
    path('sales/create/', SaleCreateAPIView.as_view(), name='sale-create'),
]