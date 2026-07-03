from django.urls import path
from . import views


urlpatterns = [
    path('adminhome/', views.admin_home, name='admin_home'), 
    path('district/', views.district, name='district'),
    path('viewdistrict/', views.viewdistrict, name='viewdistrict'),
    path('deletedistrict/<int:did>/', views.deletedistrict, name='deletedistrict'),
    path('editdistrict/<int:did>/', views.editdistrict, name='editdistrict'),
    path('location/', views.location, name='location'),
    path('viewlocation/', views.viewlocation, name='viewlocation'),
    path('editlocation/<int:lid>/', views.editlocation, name='editlocation'),
    path('deletelocation/<int:lid>/', views.deletelocation, name='deletelocation'),
    path('category/', views.category, name='categoryreg'),
    path('viewcategory/', views.viewcategory, name='viewcategory'),
    path('editcategory/<int:id>/', views.editcategory, name='editcategory'),
    path('deletecategory/<int:id>/', views.deletecategory, name='deletecategory'),
    path('customer-verification/', views.customer_verification, name='customer_verification'),
    path('verify-customer/<int:customer_id>/', views.verify_customer, name='verify_customer'),
    path('reject-customer/<int:customer_id>/', views.reject_customer, name='reject_customer'),
    path('subcategory/', views.subcategory_registration, name='subcategory_registration'),
    path('viewsubcategory/', views.viewsubcategory, name='viewsubcategory'),
    path('editsubcategory/<int:id>/', views.editsubcategory, name='edit_subcategory'),
    path('deletesubcategory/<int:id>/', views.deletesubcategory, name='delete_subcategory'),
    path('vendor-verification/', views.vendor_verification, name='vendor_verification'),
    path('approve-vendor/<int:vendor_id>/', views.approve_vendor, name='approve_vendor'),
    path('reject-vendor/<int:vendor_id>/', views.reject_vendor, name='reject_vendor'),
    
    # Reports
    path('sales-report/', views.admin_sales_report, name='admin_sales_report'),
    path('sales-report/export/', views.admin_sales_report_export, name='admin_sales_report_export'),
]