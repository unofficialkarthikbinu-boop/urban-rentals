from django.db import models

# Create your models here.
class tbl_district(models.Model):
    district_id = models.AutoField(primary_key=True)
    district_name = models.CharField(max_length=100)

class tbl_location(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=100)
    district_id = models.ForeignKey(tbl_district, on_delete=models.CASCADE)

class tbl_categorys(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField()
    category_image = models.ImageField(upload_to='category_images/')

class tbl_subcategory(models.Model):
    subcategory_id = models.AutoField(primary_key=True)

    category = models.ForeignKey(
        'AdminApp.tbl_categorys',
        on_delete=models.CASCADE,
        related_name='subcategories'
    )

    subcategory_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    subcategory_image = models.ImageField(
        upload_to='subcategory_images/',
        null=True,
        blank=True
    )


    def __str__(self):
        return f"{self.subcategory_name} ({self.category.category_name})"

