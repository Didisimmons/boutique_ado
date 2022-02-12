from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),  # to specify that the product ID should be an integer.
    path('add/', views.add_product, name='add_product'),
]
