from GuestApp.models import tbl_customer, tbl_vendor

def verification_counts(request):
    """
    Context processor to make pending verification counts available 
    globally to admin templates.
    """
    # Only run queries if an admin is logged in
    if 'admin' in request.session:
        # Customers pending verification (neither verified nor rejected)
        pending_customers = tbl_customer.objects.exclude(is_verified=True).exclude(is_rejected=True).count()
        
        # Vendors pending verification
        pending_vendors = tbl_vendor.objects.filter(status='Pending').count()
        
        return {
            'pending_customer_count': pending_customers,
            'pending_vendor_count': pending_vendors
        }
    
    return {}
