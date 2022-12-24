from django.contrib import admin
from django.urls import path
from . import views

app_name='myapp'

urlpatterns = [
   path('',views.index),
   path('products/',views.products,name='products'),
   path('products/<int:pk>/',views.productDetailView.as_view(),name='product_detail'),
   path('products/add/',views.ProductCreateView.as_view(),name='add_product'),
   path('products/update/<int:pk>/',views.ProductUpdateView.as_view(),name='update_product'),
   path('products/delete/<int:pk>/',views.ProductDeleteView.as_view(),name='delete_product'),
   path('products/my_listings',views.my_listings,name='my_listings'),
   path('success/',views.PaymentSuccessView.as_view(),name='success'),
   path('success/',views.PaymentFailedView.as_view(),name='success'),
   path('api/checkout-session/<id>',views.checkout_session,name='api_checkout_session'),
] 