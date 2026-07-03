from django.db import models

class tbl_login(models.Model):
    login_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True, db_index=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    status = models.CharField(max_length=50)

class tbl_customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True, db_index=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    id_proof = models.ImageField(
        upload_to='customer_id_proofs/',
        null=True,
        blank=True
    )

    login = models.OneToOneField(
        tbl_login,
        on_delete=models.CASCADE,
        related_name='customer_account'
    )

    district_id = models.ForeignKey(
        'AdminApp.tbl_district',
        on_delete=models.CASCADE
    )

    location_id = models.ForeignKey(
        'AdminApp.tbl_location',
        on_delete=models.CASCADE
    )

    status = models.CharField(max_length=20, default="Pending")
    is_verified = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class tbl_vendor(models.Model):
    vendor_id = models.AutoField(primary_key=True)
    login = models.OneToOneField(
        'tbl_login',
        on_delete=models.CASCADE,
        related_name='vendor'
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    district = models.ForeignKey('AdminApp.tbl_district', on_delete=models.CASCADE)
    location = models.ForeignKey('AdminApp.tbl_location', on_delete=models.CASCADE)

    # 🔹 Proof fields (ONLY TWO)
    aadhar_proof = models.FileField(upload_to='vendor/aadhar/')
    shop_license = models.FileField(upload_to='vendor/shop_license/')
    
    # GSTIN field
    gstin = models.CharField(max_length=15, unique=True, null=True, blank=True)

    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name