

from django.db import models
from GuestApp.models import tbl_customer
from VendorApp.models import tbl_product


class tbl_cart(models.Model):
    RENT_TYPE_CHOICES = (
        ('daily', 'Daily Rent'),
        ('monthly', 'Monthly Rent'),
    )

    cart_id = models.AutoField(primary_key=True)

    # Relations
    customer = models.ForeignKey(
        tbl_customer,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    product = models.ForeignKey(
        tbl_product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    # Rent selection
    rent_type = models.CharField(
        max_length=10,
        choices=RENT_TYPE_CHOICES
    )

    rental_duration = models.PositiveIntegerField(
        help_text="Number of days or months"
    )

    rental_start_date = models.DateField(null=True, blank=True)
    rental_end_date = models.DateField(null=True, blank=True)

    quantity = models.PositiveIntegerField(default=1)

    # Pricing
    rent_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per day or per month"
    )

    security_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    total_rent = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total rent + security deposit"
    )

    is_active = models.BooleanField(default=True)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_cart'
        verbose_name = 'Cart'
        verbose_name_plural = 'Cart'
        unique_together = ('customer', 'product', 'rent_type')

    def __str__(self):
        return f"{self.customer} - {self.product} ({self.rent_type})"
    
class tbl_delivery_address(models.Model):
    address_id = models.AutoField(primary_key=True)

    customer = models.ForeignKey(
        tbl_customer,
        on_delete=models.CASCADE,
        related_name='delivery_addresses'
    )

    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    landmark = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_delivery_address'
        verbose_name = 'Delivery Address'
        verbose_name_plural = 'Delivery Addresses'

    def __str__(self):
        return f"{self.full_name} - {self.city} ({self.pincode})"


class tbl_order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Vendor Confirmed'),
        ('paid', 'Payment Completed'),
        ('delivered', 'Delivered'),
        ('completed', 'Order Completed'),
        ('cancelled', 'Cancelled'),
    )

    order_id = models.AutoField(primary_key=True)
    
    # Relations
    customer = models.ForeignKey(
        tbl_customer,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    
    delivery_address = models.ForeignKey(
        tbl_delivery_address,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    
    # Order details
    order_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False
    )
    
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending'
    )
    
    # Pricing
    total_rent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    
    total_security_deposit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    
    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tbl_order'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer} ({self.status})"


class tbl_order_item(models.Model):
    RENT_TYPE_CHOICES = (
        ('daily', 'Daily Rent'),
        ('monthly', 'Monthly Rent'),
    )
    
    order_item_id = models.AutoField(primary_key=True)
    
    # Relations
    order = models.ForeignKey(
        tbl_order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    product = models.ForeignKey(
        tbl_product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items'
    )
    
    # Rental details
    rent_type = models.CharField(max_length=10, choices=RENT_TYPE_CHOICES)
    rental_duration = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    
    # Pricing
    rent_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    
    security_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    total_rent = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    
    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    
    # Rental Dates
    rental_start_date = models.DateField(null=True, blank=True)
    rental_end_date = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'tbl_order_item'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"{self.order.order_number} - {self.product}"


class tbl_payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )

    payment_id = models.AutoField(primary_key=True)
    
    order = models.ForeignKey(
        tbl_order,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    customer = models.ForeignKey(
        tbl_customer,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    admin_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    vendor_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    payment_method = models.CharField(max_length=50, null=True, blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tbl_payment'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"




class tbl_review(models.Model):
    RATING_CHOICES = (
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    )
    
    review_id = models.AutoField(primary_key=True)
    
    product = models.ForeignKey(
        'VendorApp.tbl_product',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    customer = models.ForeignKey(
        tbl_customer,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    order = models.ForeignKey(
        tbl_order,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True
    )
    
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, default=5)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    is_verified_purchase = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tbl_review'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ('product', 'customer', 'order')
    
    def __str__(self):
        return f"Review: {self.title} - {self.product.product_name} by {self.customer.name}"

class tbl_return_request(models.Model):
    """
    Model to track return/pickup requests with defect assessment and extra day penalties.
    """
    RETURN_STATUS_CHOICES = (
        ('requested', 'Return Requested'),
        ('scheduled', 'Pickup Scheduled'),
        ('picked_up', 'Item Picked Up'),
        ('completed', 'Return Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    DEFECT_CHOICES = (
        ('no_defect', 'No Defect'),
        ('minor', 'Minor Defect (5% deduction)'),
        ('moderate', 'Moderate Defect (15% deduction)'),
        ('major', 'Major Defect (30% deduction)'),
    )
    
    return_id = models.AutoField(primary_key=True)
    
    # Relations
    order_item = models.ForeignKey(
        tbl_order_item,
        on_delete=models.CASCADE,
        related_name='return_requests'
    )
    
    customer = models.ForeignKey(
        tbl_customer,
        on_delete=models.CASCADE,
        related_name='return_requests'
    )
    
    order = models.ForeignKey(
        tbl_order,
        on_delete=models.CASCADE,
        related_name='return_requests'
    )
    
    # Status & Dates
    status = models.CharField(
        max_length=20,
        choices=RETURN_STATUS_CHOICES,
        default='requested'
    )
    
    request_date = models.DateTimeField(auto_now_add=True)
    pickup_scheduled_date = models.DateTimeField(null=True, blank=True)
    pickup_completed_date = models.DateTimeField(null=True, blank=True)
    actual_return_date = models.DateField(null=True, blank=True, help_text="Date when customer returns the product")
    
    # Defect Assessment
    defect_status = models.CharField(
        max_length=20,
        choices=DEFECT_CHOICES,
        default='no_defect'
    )
    
    defect_description = models.TextField(null=True, blank=True)
    defect_image = models.ImageField(upload_to='return_defect_images/', null=True, blank=True)
    
    # Extra Days (if rental period exceeded)
    extra_days = models.IntegerField(default=0, help_text="Days beyond the scheduled rental period")
    
    # Deductions & Refund
    defect_deduction_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage deducted for defects (e.g., 5, 15, 30)"
    )
    
    defect_deduction_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    extra_days_deduction_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Total deduction for extra days"
    )
    
    total_deduction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tbl_return_request'
        verbose_name = 'Return Request'
        verbose_name_plural = 'Return Requests'
        ordering = ['-request_date']
    
    def __str__(self):
        return f"Return {self.return_id} - {self.customer.name} ({self.status})"
    
    def calculate_extra_days(self):
        """Calculate extra days beyond rental period"""
        if self.actual_return_date and self.order_item.rental_end_date:
            from datetime import timedelta
            extra = (self.actual_return_date - self.order_item.rental_end_date).days
            self.extra_days = max(0, extra)
            return self.extra_days
        return 0
    
    def calculate_deductions(self, extra_day_percentage=5):
        """
        Calculate all deductions:
        - Defect deduction based on defect_status
        - Extra days deduction (% per day)
        
        extra_day_percentage: percentage per extra day (default 5%)
        """
        # Set defect percentage based on status
        defect_percentages = {
            'no_defect': 0,
            'minor': 5,
            'moderate': 15,
            'major': 30
        }
        
        self.defect_deduction_percentage = defect_percentages.get(self.defect_status, 0)
        
        # Calculate defect deduction amount
        from decimal import Decimal
        self.defect_deduction_amount = (
            self.order_item.security_deposit * 
            Decimal(self.defect_deduction_percentage) / 100
        )
        
        # Calculate extra days deduction
        self.calculate_extra_days()
        self.extra_days_deduction_amount = (
            self.order_item.security_deposit * 
            Decimal(self.extra_days) * 
            Decimal(extra_day_percentage) / 100
        )
        
        # Total deduction
        self.total_deduction = self.defect_deduction_amount + self.extra_days_deduction_amount
        
        # Refund amount (cannot be negative)
        self.refund_amount = max(
            Decimal('0.00'),
            self.order_item.security_deposit - self.total_deduction
        )
        
        self.save()