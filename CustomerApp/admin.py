from django.contrib import admin
from .models import tbl_cart, tbl_delivery_address, tbl_order, tbl_order_item, tbl_payment

@admin.register(tbl_cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'customer', 'product', 'rent_type', 'quantity', 'grand_total', 'is_active']
    list_filter = ['is_active', 'rent_type', 'added_on']
    search_fields = ['customer__customer_name', 'product__product_name']
    readonly_fields = ['added_on']

@admin.register(tbl_delivery_address)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ['address_id', 'customer', 'full_name', 'city', 'pincode', 'is_default']
    list_filter = ['is_default', 'created_at']
    search_fields = ['customer__customer_name', 'full_name', 'city']
    readonly_fields = ['created_at']

@admin.register(tbl_order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'order_number', 'customer', 'status', 'grand_total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'customer__customer_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    
@admin.register(tbl_order_item)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order_item_id', 'order', 'product', 'quantity', 'grand_total']
    list_filter = ['order__created_at']
    search_fields = ['order__order_number', 'product__product_name']

@admin.register(tbl_payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'transaction_id', 'order', 'customer', 'status', 'amount', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'order__order_number', 'customer__name']
    readonly_fields = ['created_at']

