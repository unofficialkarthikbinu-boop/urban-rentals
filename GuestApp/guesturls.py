from django.urls import path
from . import views

urlpatterns = [
    path('guesthome/', views.guest_home, name='guest_home'), 
    path('login/', views.login, name='login'),
    path('browse-products/', views.guest_browse_products, name='guest_browse_products'),
    path('product/<int:product_id>/', views.guest_product_detail, name='guest_product_detail'),
    path('cart/', views.guest_view_cart, name='guest_view_cart'),
    path('customerreg/', views.customer_registration, name='customer_registration'),
    path('vendorreg/', views.vendor_registration, name='vendor_registration'),
    path('get-locations/', views.get_locations_by_district, name='get_locations'),
    path('logout/', views.logout, name='logout'),
]