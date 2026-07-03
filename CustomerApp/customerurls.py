from django.urls import path
from . import views

urlpatterns = [
    path('customerhome/', views.customer_home, name='customer_home'),
    path('customer-profile/', views.my_profile, name='customer_profile'),
    path('my-profile/edit/', views.edit_profile, name='edit_customer_profile'),
    path('browse-products/', views.browse_products, name='browse_products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('delivery-details/', views.delivery_details, name='delivery_details'),
    path('set-default-address/<int:address_id>/', views.set_default_address, name='set_default_address'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('payment/<int:order_id>/', views.payment_page, name='payment_page'),
    path('process-payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('track-order/<int:order_id>/', views.track_order, name='track_order'),
    path('return-product/<int:order_id>/', views.return_product, name='return_product'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),
    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('track-order/<int:order_id>/', views.track_order, name='track_order'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),
    path('submit-order-review/<int:order_item_id>/', views.submit_order_review, name='submit_order_review'),
    
    # Return & Pickup
    path('return-request/', views.return_request, name='return_request'),
    path('initiate-return/<int:order_item_id>/', views.initiate_return_request, name='initiate_return_request'),
    path('return-status/', views.return_request_status, name='return_request_status'),
]