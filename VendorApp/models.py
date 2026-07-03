from django.db import models
from GuestApp.models import tbl_vendor
from AdminApp.models import tbl_categorys, tbl_subcategory


class tbl_product(models.Model):
    product_id = models.AutoField(primary_key=True)

    category = models.ForeignKey(tbl_categorys, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(tbl_subcategory, on_delete=models.CASCADE, related_name='products')
    vendor = models.ForeignKey(tbl_vendor, on_delete=models.CASCADE, related_name='products')

    product_name = models.CharField(max_length=150)
    product_description = models.TextField()
    brand = models.CharField(max_length=100, blank=True, null=True)

    rent_price_per_day = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rent_price_per_month = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    stock_quantity = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    product_image = models.ImageField(upload_to='product_images/main/')

    status = models.CharField(max_length=50, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

class tbl_furniture_details(models.Model):
    product = models.OneToOneField(
        tbl_product,
        on_delete=models.CASCADE,
        related_name='furniture_details'
    )

    furniture_type = models.CharField(max_length=100)   # Sofa, Bed, Table
    size = models.CharField(max_length=100)             # 6x6, King, Large
    thickness = models.CharField(max_length=50)         # 12mm, 18mm
    material = models.CharField(max_length=100)         # Wood, MDF, Steel
    extra_features = models.TextField(blank=True, null=True)

class tbl_appliance_details(models.Model):
    product = models.OneToOneField(
        tbl_product,
        on_delete=models.CASCADE,
        related_name='appliance_details'
    )

    operation_type = models.CharField(max_length=100)   # Manual / Semi-Auto / Fully Automatic
    power_rating = models.CharField(max_length=50)
    voltage = models.CharField(max_length=50)
    warranty_period = models.CharField(max_length=50)

class tbl_product_image(models.Model):
    product = models.ForeignKey(
        tbl_product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='product_images/gallery/')
