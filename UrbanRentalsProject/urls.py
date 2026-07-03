"""
URL configuration for UrbanRentalsProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from GuestApp import views as guest_views

urlpatterns = [
    path('', guest_views.guest_home, name='home'),
    path('admin/', admin.site.urls),
    path('adminapp/', include('AdminApp.adminurls')),
    path('guestapp/', include('GuestApp.guesturls')),
    path('customerapp/', include('CustomerApp.customerurls')),
    path('vendorapp/', include('VendorApp.vendorurls')),
    path('chat/', include('ChatApp.urls')),
    
    
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
