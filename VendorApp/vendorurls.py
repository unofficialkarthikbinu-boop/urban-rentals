from django.urls import path
from . import views

urlpatterns = [
    path('vendorhome/', views.vendor_home, name='vendor_home'),
    path('myprofile/', views.my_profile, name='vendor_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Product Management
    path('products/', views.vendor_products, name='vendor_products'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('get-subcategories/', views.get_subcategories, name='get_subcategories'),
    
    # Order Management
    path('orders/', views.vendor_orders, name='vendor_orders'),
    path('order/<int:order_id>/', views.order_details, name='order_details'),
    path('order/<int:order_id>/accept/', views.accept_order, name='accept_order'),
    path('order/<int:order_id>/reject/', views.reject_order, name='reject_order'),
    path('order/<int:order_id>/delivered/', views.mark_delivered, name='mark_delivered'),
    
    # Return & Pickup Management
    path('returns/', views.vendor_return_requests, name='vendor_return_requests'),
    path('return/<int:return_id>/schedule/', views.schedule_pickup, name='schedule_pickup'),
    path('return/<int:return_id>/complete/', views.complete_pickup, name='complete_pickup'),
    
    # Reports
    path('sales-report/', views.vendor_report, name='vendor_report'),
    path('sales-report/export/', views.vendor_report_export, name='vendor_report_export'),
]