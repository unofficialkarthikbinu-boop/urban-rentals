from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_control
from django.template.loader import render_to_string
from django.http import JsonResponse
from AdminApp.models import tbl_categorys, tbl_subcategory
from VendorApp.models import tbl_product
from GuestApp.models import tbl_customer, tbl_login
from .models import tbl_cart, tbl_delivery_address, tbl_order, tbl_order_item, tbl_return_request
from decimal import Decimal
import smtplib
from email.message import EmailMessage


def send_email_notification(subject, body, to_email, html_body=None):
    """
    Helper function to send email notifications.
    """
    try:
        msg = EmailMessage()
        msg.set_content(body)
        if html_body:
            msg.add_alternative(html_body, subtype='html')
            
        msg['Subject'] = subject
        msg['From'] = "urbanrentalsofficial@gmail.com"
        msg['To'] = to_email
        
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login("urbanrentalsofficial@gmail.com", "kilw hwzc jdkz xlmp")
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Helper function to update cart count in session
def update_cart_count(request):
    """Update cart item count in session"""
    if 'customer' in request.session:
        try:
            customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
            cart_items = tbl_cart.objects.filter(customer=customer, is_active=True).count()
            request.session['cart_count'] = cart_items
        except tbl_customer.DoesNotExist:
            request.session['cart_count'] = 0
    else:
        request.session['cart_count'] = 0
from django.views.decorators.cache import cache_control
from django.http import HttpResponse

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customer_home(request):
    # Check if customer is logged in
    if 'customer' not in request.session:
        return HttpResponse("<script>alert('Authentication Required! Please login.');window.location='/guestapp/login/';</script>")
    
    # Get featured products
    featured_products = tbl_product.objects.filter(is_featured=True, is_available=True, status='Active')[:8]
    if not featured_products.exists():
        featured_products = tbl_product.objects.filter(is_available=True, status='Active').order_by('-created_at')[:8]
    
    # Get popular products (latest 5 available products)
    popular_products = tbl_product.objects.filter(is_available=True, status='Active').order_by('-created_at')[:5]
    
    # Get all subcategories for category banners
    subcategories = tbl_subcategory.objects.all()
    
    update_cart_count(request)
    return render(request, 'customer/index.html', {'featured_products': featured_products, 'popular_products': popular_products, 'subcategories': subcategories})

def my_profile(request):
    """Customer Profile View"""
    # Check if customer is logged in
    if 'customer' not in request.session:
        messages.warning(request, "Please login to view profile")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        update_cart_count(request)
        return render(request, 'customer/my_profile.html', {'customer': customer})
    except tbl_customer.DoesNotExist:
        messages.error(request, "Customer account not found")
        return redirect('customer_home')

def edit_profile(request):
    """Edit Customer Profile View"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login to edit profile")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        update_cart_count(request)
        
        if request.method == 'POST':
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            
            # Basic validation
            if not name or not email or not phone or not address:
                messages.error(request, "All fields are required")
            elif tbl_customer.objects.filter(email=email).exclude(pk=customer.pk).exists():
                messages.error(request, "Email already registered for another customer")
            else:
                try:
                    # Update customer details
                    print(f"DEBUG: Updating customer {customer.pk} email from {customer.email} to {email}")
                    customer.name = name
                    customer.email = email
                    customer.phone = phone
                    customer.address = address
                    
                    customer.save()
                    print("DEBUG: Customer saved successfully")
                    
                    messages.success(request, "Profile updated successfully")
                    return redirect('customer_profile')
                except Exception as e:
                    print(f"DEBUG: Error saving customer: {e}")
                    messages.error(request, f"Error updating profile: {str(e)}")
        
        return render(request, 'customer/edit_profile.html', {'customer': customer})
        
    except tbl_customer.DoesNotExist:
        messages.error(request, "Customer account not found")
        return redirect('customer_home')



def browse_products(request):
    """Display all products with category and subcategory filters"""
    # Check if customer is logged in
    if 'customer' not in request.session:
        messages.warning(request, "Please login to browse products")
        return redirect('login')
    
    categories = tbl_categorys.objects.all()
    subcategories = tbl_subcategory.objects.all()
    products = tbl_product.objects.filter(status='Active')
    
    # Get selected category from request
    category_id = request.GET.get('category')
    subcategory_id = request.GET.get('subcategory')
    search_query = request.GET.get('search', '')
    
    # Filter by category if selected
    if category_id:
        try:
            category = tbl_categorys.objects.get(category_id=category_id)
            products = products.filter(category=category)
            # Filter subcategories by category
            subcategories = subcategories.filter(category_id=category_id)
        except tbl_categorys.DoesNotExist:
            pass
    
    # Filter by subcategory if selected
    if subcategory_id:
        try:
            subcategory = tbl_subcategory.objects.get(subcategory_id=subcategory_id)
            products = products.filter(subcategory=subcategory)
        except tbl_subcategory.DoesNotExist:
            pass
    
    # Filter by search query
    if search_query:
        products = products.filter(
            product_name__icontains=search_query
        ) | products.filter(
            product_description__icontains=search_query
        ) | products.filter(
            brand__icontains=search_query
        )
    
    # Sort products (you can add more sorting options)
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('rent_price_per_day')
    elif sort_by == 'price_high':
        products = products.order_by('-rent_price_per_day')
    elif sort_by == 'popular':
        products = products.order_by('-created_at')
    else:  # newest
        products = products.order_by('-created_at')
    
    update_cart_count(request)
    context = {
        'categories': categories,
        'subcategories': subcategories,
        'products': products,
        'selected_category': category_id,
        'selected_subcategory': subcategory_id,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    
    return render(request, 'customer/browse_products.html', context)


def product_detail(request, product_id):
    """Display product details"""
    # Check if customer is logged in
    if 'customer' not in request.session:
        messages.warning(request, "Please login to view product details")
        return redirect('login')
    
    try:
        from .models import tbl_review
        from django.db.models import Avg
        
        product = tbl_product.objects.get(product_id=product_id, is_available=True, status='Active')
        # Get related images
        images = product.images.all()
        # Get related products from same category
        related_products = tbl_product.objects.filter(
            category=product.category,
            is_available=True,
            status='Active'
        ).exclude(product_id=product_id)[:6]
        
        # Get reviews
        reviews = tbl_review.objects.filter(product=product).order_by('-created_at')
        avg_rating = tbl_review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        
        # Check if customer can review (purchased and delivered/completed)
        can_review = tbl_order_item.objects.filter(
            product=product,
            order__customer=customer,
            order__status__in=['delivered', 'completed']
        ).exists()
        
        update_cart_count(request)
        context = {
            'product': product,
            'images': images,
            'related_products': related_products,
            'reviews': reviews,
            'avg_rating': avg_rating,
            'customer': customer,
            'can_review': can_review,
        }
        return render(request, 'customer/product_detail.html', context)
    except tbl_product.DoesNotExist:
        messages.error(request, "Product not found")
        return redirect('browse_products')


@require_http_methods(["POST"])
def add_to_cart(request, product_id):
    """Add product to cart"""
    # Check if customer is logged in
    if 'customer' not in request.session:
        messages.error(request, "Please login to add items to cart")
        return redirect('login')
    
    try:
        # Get customer using login_id from session and product
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        product = tbl_product.objects.get(product_id=product_id, is_available=True, status='Active')
        
        # Get form data
        rent_type = request.POST.get('rent_type')
        rental_duration = int(request.POST.get('rental_duration', 1))
        quantity = int(request.POST.get('quantity', 1))
        

        # Use current date as start date
        from datetime import datetime, timedelta
        import calendar
        
        rental_start_date = datetime.now().date()
        rental_end_date = None
        
        # Calculate End Date based on type and duration
        if rent_type == 'daily':
            rental_end_date = rental_start_date + timedelta(days=rental_duration)
        elif rent_type == 'monthly':
            # Add months logic
            month = rental_start_date.month - 1 + rental_duration
            year = rental_start_date.year + month // 12
            month = month % 12 + 1
            day = min(rental_start_date.day, calendar.monthrange(year, month)[1])
            rental_end_date = rental_start_date.replace(year=year, month=month, day=day)

        # Validate rent_type
        if rent_type not in ['daily', 'monthly']:
            messages.error(request, "Invalid rent type selected")
            return redirect('product_detail', product_id=product_id)
        
        # Get the appropriate price
        if rent_type == 'daily':
            price_per_unit = product.rent_price_per_day
        else:  # monthly
            price_per_unit = product.rent_price_per_month
        
        if not price_per_unit:
            messages.error(request, f"This product is not available for {rent_type} rent")
            return redirect('product_detail', product_id=product_id)
        
        # Calculate totals
        total_rent = Decimal(str(price_per_unit)) * quantity * rental_duration
        security_deposit = product.security_deposit
        grand_total = total_rent + security_deposit
        
        # Check if item already exists in cart
        cart_item, created = tbl_cart.objects.update_or_create(
            customer=customer,
            product=product,
            rent_type=rent_type,
            defaults={
                'rental_duration': rental_duration,
                'rental_start_date': rental_start_date,
                'rental_end_date': rental_end_date,
                'quantity': quantity,
                'rent_price': price_per_unit,
                'security_deposit': security_deposit,
                'total_rent': total_rent,
                'grand_total': grand_total,
                'is_active': True,
            }
        )
        
        if created:
            messages.success(request, f"{product.product_name} added to cart!")
        else:
            messages.success(request, f"{product.product_name} cart updated!")
        
        update_cart_count(request)
        return redirect('view_cart')
    
    except tbl_customer.DoesNotExist:
        messages.error(request, "Customer not found")
        return redirect('login')
    except tbl_product.DoesNotExist:
        messages.error(request, "Product not found")
        return redirect('browse_products')
    except (ValueError, TypeError) as e:
        messages.error(request, "Invalid input values")
        return redirect('product_detail', product_id=product_id)


def view_cart(request):
    """Display shopping cart"""
    # Check if customer is logged in
    if 'customer' not in request.session:
        messages.warning(request, "Please login to view cart")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        cart_items = tbl_cart.objects.filter(customer=customer, is_active=True)
        
        # Calculate totals
        subtotal = sum(item.total_rent for item in cart_items)
        total_security = sum(item.security_deposit for item in cart_items)
        grand_total = subtotal + total_security
        
        update_cart_count(request)
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'total_security': total_security,
            'grand_total': grand_total,
        }
        return render(request, 'customer/cart.html', context)
    except tbl_customer.DoesNotExist:
        messages.error(request, "Customer not found")
        return redirect('login')


def remove_from_cart(request, cart_id):
    """Remove item from cart"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        cart_item = tbl_cart.objects.get(cart_id=cart_id, customer=customer)
        product_name = cart_item.product.product_name
        cart_item.delete()
        messages.success(request, f"{product_name} removed from cart")
    except (tbl_customer.DoesNotExist, tbl_cart.DoesNotExist):
        messages.error(request, "Item not found in cart")
    
    return redirect('view_cart')


def delivery_details(request):
    """Display and handle delivery details form"""
    # Check if customer is logged in
    if 'customer' not in request.session:
        messages.warning(request, "Please login to proceed")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        
        if request.method == 'POST':
            # Handle form submission
            selected_address_id = request.POST.get('selected_address_id', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            address_line_1 = request.POST.get('address_line_1', '').strip()
            address_line_2 = request.POST.get('address_line_2', '').strip()
            city = request.POST.get('city', '').strip()
            district = request.POST.get('district', '').strip()
            state = request.POST.get('state', '').strip()
            pincode = request.POST.get('pincode', '').strip()
            landmark = request.POST.get('landmark', '').strip()
            is_default = request.POST.get('is_default') == 'on'
            
            # Validation
            if not all([full_name, phone_number, address_line_1, city, state, pincode]):
                messages.error(request, "Please fill in all required fields")
                return redirect('delivery_details')
            
            if len(phone_number) < 10 or not phone_number.isdigit():
                messages.error(request, "Please enter a valid 10-digit phone number")
                return redirect('delivery_details')
            
            if len(pincode) != 6 or not pincode.isdigit():
                messages.error(request, "Please enter a valid 6-digit pincode")
                return redirect('delivery_details')
            
            # Check if a saved address was selected (not creating a new one)
            if selected_address_id:
                try:
                    address = tbl_delivery_address.objects.get(address_id=selected_address_id, customer=customer)
                    # Just use the existing address, don't create a duplicate
                    messages.success(request, "Using saved address for checkout")
                except tbl_delivery_address.DoesNotExist:
                    messages.error(request, "Selected address not found")
                    return redirect('delivery_details')
            else:
                # Create new delivery address
                # If marking as default, unmark others
                if is_default:
                    tbl_delivery_address.objects.filter(customer=customer).update(is_default=False)
                
                address = tbl_delivery_address.objects.create(
                    customer=customer,
                    full_name=full_name,
                    phone_number=phone_number,
                    address_line_1=address_line_1,
                    address_line_2=address_line_2,
                    city=city,
                    district=district,
                    state=state,
                    pincode=pincode,
                    landmark=landmark,
                    is_default=is_default
                )
                messages.success(request, "Delivery address saved successfully!")
            
            request.session['delivery_address_id'] = address.address_id
            
            # Proceed to place order
            return place_order(request)
        
        # GET request - show form with saved addresses
        saved_addresses = tbl_delivery_address.objects.filter(customer=customer).order_by('-is_default', '-created_at')
        
        context = {
            'saved_addresses': saved_addresses,
            'customer': customer,
        }
        return render(request, 'customer/delivery_details.html', context)
    
    except tbl_customer.DoesNotExist:
        messages.error(request, "Customer not found")
        return redirect('login')


@require_http_methods(["POST"])
def set_default_address(request, address_id):
    """Set a delivery address as default"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login to proceed")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        
        # Get the address
        address = tbl_delivery_address.objects.get(address_id=address_id, customer=customer)
        
        # Unmark all other addresses as default
        tbl_delivery_address.objects.filter(customer=customer).update(is_default=False)
        
        # Mark this address as default
        address.is_default = True
        address.save()
        
        messages.success(request, f"Address for {address.full_name} is now set as default!")
        
    except tbl_delivery_address.DoesNotExist:
        messages.error(request, "Address not found")
    except tbl_customer.DoesNotExist:
        messages.error(request, "Customer not found")
        return redirect('login')
    
    return redirect('delivery_details')


@require_http_methods(["POST"])
def delete_address(request, address_id):
    """Delete a delivery address"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login to proceed")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        
        # Get the address
        address = tbl_delivery_address.objects.get(address_id=address_id, customer=customer)
        was_default = address.is_default
        
        # Delete the address
        address.delete()
        
        messages.success(request, "Address deleted successfully!")
        
        # If the deleted address was default, set the most recent one as default
        if was_default:
            remaining_addresses = tbl_delivery_address.objects.filter(customer=customer).order_by('-created_at')
            if remaining_addresses.exists():
                remaining_addresses.first().is_default = True
                remaining_addresses.first().save()
                messages.info(request, "The most recent address is now set as default.")
        
    except tbl_delivery_address.DoesNotExist:
        messages.error(request, "Address not found")
    except tbl_customer.DoesNotExist:
        messages.error(request, "Customer not found")
        return redirect('login')
    
    return redirect('delivery_details')


@require_http_methods(["POST"])
def place_order(request):
    """Create an order from cart items"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login to place an order")
        return redirect('login')
    
    try:
        # Get customer
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        
        # Get active cart items
        cart_items = tbl_cart.objects.filter(customer=customer, is_active=True)
        
        if not cart_items.exists():
            messages.warning(request, "Your cart is empty. Please add items before placing an order.")
            return redirect('view_cart')

        # Check for missing rental dates in cart items and fix them
        from datetime import datetime, timedelta
        import calendar
        
        for item in cart_items:
            if not item.rental_start_date or not item.rental_end_date:
                # Default to today
                item.rental_start_date = datetime.now().date()
                
                if item.rent_type == 'daily':
                    item.rental_end_date = item.rental_start_date + timedelta(days=item.rental_duration)
                elif item.rent_type == 'monthly':
                    # Add months logic
                    month = item.rental_start_date.month - 1 + item.rental_duration
                    year = item.rental_start_date.year + month // 12
                    month = month % 12 + 1
                    day = min(item.rental_start_date.day, calendar.monthrange(year, month)[1])
                    item.rental_end_date = item.rental_start_date.replace(year=year, month=month, day=day)
                
                item.save()
        
        # Get delivery address (priority: session > default)
        delivery_address = None
        
        # Check session
        if 'delivery_address_id' in request.session:
            try:
                delivery_address = tbl_delivery_address.objects.get(
                    address_id=request.session['delivery_address_id'],
                    customer=customer
                )
            except tbl_delivery_address.DoesNotExist:
                pass
        
        # Fallback to default if not found in session
        if not delivery_address:
            delivery_address = tbl_delivery_address.objects.filter(customer=customer, is_default=True).first()
        
        if not delivery_address:
            messages.warning(request, "Please set a default delivery address before placing an order.")
            return redirect('delivery_details')
        
        # Calculate totals
        total_rent = Decimal('0.00')
        total_security_deposit = Decimal('0.00')
        
        for item in cart_items:
            total_rent += item.total_rent
            total_security_deposit += item.security_deposit
        
        grand_total = total_rent + total_security_deposit
        
        # Generate unique order number
        from datetime import datetime
        order_number = f"ORD-{customer.customer_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create order
        order = tbl_order.objects.create(
            customer=customer,
            delivery_address=delivery_address,
            order_number=order_number,
            status='pending',
            total_rent=total_rent,
            total_security_deposit=total_security_deposit,
            grand_total=grand_total
        )
        
        # Create order items from cart
        for cart_item in cart_items:
            print(f"DEBUG: creating order item. start_date: {cart_item.rental_start_date}, end_date: {cart_item.rental_end_date}")
            tbl_order_item.objects.create(
                order=order,
                product=cart_item.product,
                rent_type=cart_item.rent_type,
                rental_duration=cart_item.rental_duration,
                rental_start_date=cart_item.rental_start_date,
                rental_end_date=cart_item.rental_end_date,
                quantity=cart_item.quantity,
                rent_price=cart_item.rent_price,
                security_deposit=cart_item.security_deposit,
                total_rent=cart_item.total_rent,
                grand_total=cart_item.grand_total,
            )
        
        # Mark cart items as inactive
        cart_items.update(is_active=False)
        
        # Update session cart count
        update_cart_count(request)
        
        messages.success(request, f"Order {order_number} placed successfully! Your order is pending vendor confirmation.")
        return redirect('order_confirmation', order_id=order.order_id)
        
    except tbl_customer.DoesNotExist:
        messages.error(request, "Customer not found")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Error placing order: {str(e)}")
        return redirect('view_cart')


def order_confirmation(request, order_id):
    """Display order confirmation page"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login to view your order")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        order = tbl_order.objects.get(order_id=order_id, customer=customer)
        
        context = {
            'order': order,
            'order_items': order.items.all(),
        }
        
        return render(request, 'customer/order_confirmation.html', context)
        
    except tbl_customer.DoesNotExist:
        messages.error(request, "Customer not found")
        return redirect('login')
    except tbl_order.DoesNotExist:
        messages.error(request, "Order not found")
        return redirect('view_cart')


def my_orders(request):
    """Display customer's orders"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login to view your orders")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        orders = tbl_order.objects.filter(customer=customer).order_by('-created_at')
        
        # Add return request info to each order
        for order in orders:
            return_requests = tbl_return_request.objects.filter(order=order)
            if return_requests.exists():
                # Get the latest return request
                order.latest_return = return_requests.latest('request_date')
                # Check if any return is completed
                order.has_completed_return = return_requests.filter(status='completed').exists()
            else:
                order.latest_return = None
                order.has_completed_return = False
        
        context = {
            'orders': orders,
            'customer': customer,
        }
        
        return render(request, 'customer/my_orders.html', context)
    
    except tbl_customer.DoesNotExist:
        messages.error(request, "Customer not found")
        return redirect('login')


def payment_page(request, order_id):
    """Display payment page for confirmed orders"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login to proceed")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        order = tbl_order.objects.get(order_id=order_id, customer=customer)
        
        # Only allow payment for confirmed orders
        if order.status != 'confirmed':
            messages.warning(request, "This order is not ready for payment")
            return redirect('my_orders')
        
        context = {
            'order': order,
            'customer': customer,
        }
        
        return render(request, 'customer/payment_page.html', context)
    
    except (tbl_customer.DoesNotExist, tbl_order.DoesNotExist):
        messages.error(request, "Order not found")
        return redirect('my_orders')


@require_http_methods(["POST"])
def process_payment(request, order_id):
    """Process payment for order"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login to proceed")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        order = tbl_order.objects.get(order_id=order_id, customer=customer)
        
        # Only allow payment for confirmed orders
        if order.status != 'confirmed':
            messages.warning(request, "This order is not ready for payment")
            return redirect('my_orders')
        
        # Get payment details
        payment_method = request.POST.get('payment_method')
        
        if not payment_method:
            messages.error(request, "Please select a payment method")
            return redirect('payment_page', order_id=order_id)
        
        # Calculate commission and vendor amount
        total_amount = order.grand_total
        admin_commission = total_amount * Decimal('0.05')
        vendor_amount = total_amount - admin_commission
        
        # Create payment record
        from .models import tbl_payment
        import uuid
        
        payment = tbl_payment.objects.create(
            order=order,
            customer=customer,
            transaction_id=str(uuid.uuid4()),
            amount=total_amount,
            payment_method=payment_method,
            status='success',
            admin_commission=admin_commission,
            vendor_amount=vendor_amount
        )
        
        # Update order status to paid
        order.status = 'paid'
        order.save()
        
        # ========== DECREMENT PRODUCT STOCK AFTER SUCCESSFUL PAYMENT ==========
        from UrbanRentalsProject.utils import decrement_product_stock
        
        order_items = order.items.all()
        stock_errors = []
        
        for order_item in order_items:
            success, message, product = decrement_product_stock(order_item)
            if not success:
                stock_errors.append(f"Stock Error for {order_item.product.product_name if order_item.product else 'Unknown'}: {message}")
                print(f"[WARNING] {message}")
            else:
                print(f"[SUCCESS] {message}")
        
        # Log any stock-related warnings
        if stock_errors:
            warning_msg = "Payment successful, but encountered stock management issues:\n" + "\n".join(stock_errors)
            print(f"[STOCK WARNING] {warning_msg}")
        # ========================================================================
        
        # --- SEND INVOICE EMAIL ---
        try:
            invoice_subject = f"Invoice for Order #{order.order_number} - UrbanRentals"
            
            # --- Generate HTML Invoice ---
            invoice_context = {
                'customer': customer,
                'order': order,
                'payment': payment,
                'my_orders_url': request.build_absolute_uri(reverse('my_orders')),
            }
            try:
                invoice_html = render_to_string('Customer/email_invoice.html', invoice_context)
            except Exception as e:
                print(f"Template rendering error: {e}")
                invoice_html = None
            
            # Plain text fallback
            invoice_body = f"Hello {customer.name},\n\n"
            invoice_body += "Thank you for your payment! Here are your order details:\n\n"
            invoice_body += f"Order ID: {order.order_number}\n"
            invoice_body += f"Date: {payment.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            invoice_body += f"Total: {order.grand_total}\n"
            invoice_body += f"\nView your order here: {request.build_absolute_uri(reverse('my_orders'))}"
            
            if send_email_notification(invoice_subject, invoice_body, customer.email, html_body=invoice_html):
                 messages.success(request, "Payment successful! Invoice sent to your email.")
            else:
                 messages.success(request, "Payment successful! (Invoice email failed)")
        
        except Exception as e:
            print(f"Error generating invoice: {e}")
            messages.success(request, "Payment successful! (Error sending invoice)")

        return redirect('payment_success', order_id=order_id)
    
    except (tbl_customer.DoesNotExist, tbl_order.DoesNotExist):
        messages.error(request, "Order not found")
        return redirect('my_orders')
    except Exception as e:
        messages.error(request, f"Error processing payment: {str(e)}")
        return redirect('payment_page', order_id=order_id)


def payment_success(request, order_id):
    """Display payment success page"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login to view this page")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        order = tbl_order.objects.get(order_id=order_id, customer=customer)
        
        context = {
            'order': order,
            'customer': customer,
        }
        
        return render(request, 'customer/payment_success.html', context)
    
    except (tbl_customer.DoesNotExist, tbl_order.DoesNotExist):
        messages.error(request, "Order not found")
        return redirect('my_orders')


def track_order(request, order_id):
    """View to track order status"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login to track your order")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        order = tbl_order.objects.get(order_id=order_id, customer=customer)
        
        # Get return requests for this order
        return_requests = tbl_return_request.objects.filter(order=order)
        completed_returns = return_requests.filter(status='completed')
        
        context = {
            'order': order,
            'customer': customer,
            'return_requests': return_requests,
            'has_completed_return': completed_returns.exists(),
            'completed_returns': completed_returns,
        }
        return render(request, 'customer/track_order.html', context)
    except (tbl_customer.DoesNotExist, tbl_order.DoesNotExist):
        messages.error(request, "Order not found")
        return redirect('my_orders')


@require_http_methods(["GET", "POST"])
def add_review(request, product_id):
    """Add or update product review"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login to write a review")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        product = tbl_product.objects.get(product_id=product_id)
        
        # Check if customer has purchased this product and it is delivered
        has_purchased = tbl_order_item.objects.filter(
            product=product,
            order__customer=customer,
            order__status__in=['delivered', 'completed']
        ).exists()
        
        if not has_purchased:
            messages.error(request, "You can only review products that have been delivered.")
            return redirect('product_detail', product_id=product_id)
        
        if request.method == 'POST':
            rating = request.POST.get('rating')
            title = request.POST.get('title', '').strip()
            comment = request.POST.get('comment', '').strip()
            
            # Validation
            if not all([rating, title, comment]):
                messages.error(request, "Please fill in all fields")
                return redirect('add_review', product_id=product_id)
            
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    messages.error(request, "Rating must be between 1 and 5")
                    return redirect('add_review', product_id=product_id)
            except:
                messages.error(request, "Invalid rating")
                return redirect('add_review', product_id=product_id)
            
            if len(title) < 5:
                messages.error(request, "Title must be at least 5 characters")
                return redirect('add_review', product_id=product_id)
            
            if len(comment) < 10:
                messages.error(request, "Review comment must be at least 10 characters")
                return redirect('add_review', product_id=product_id)
            
            # Check if customer has purchased this product
            order_items = tbl_order_item.objects.filter(
                product=product,
                order__customer=customer,
                order__status__in=['delivered', 'completed']
            )
            
            is_verified_purchase = order_items.exists()
            order = order_items.first().order if order_items.exists() else None
            
            # Create or update review
            from .models import tbl_review
            
            review, created = tbl_review.objects.update_or_create(
                product=product,
                customer=customer,
                order=order,
                defaults={
                    'rating': rating,
                    'title': title,
                    'comment': comment,
                    'is_verified_purchase': is_verified_purchase,
                }
            )
            
            if created:
                messages.success(request, "Review added successfully!")
            else:
                messages.success(request, "Review updated successfully!")
            
            return redirect('product_detail', product_id=product_id)
        
        else:  # GET request
            from .models import tbl_review
            
            existing_review = tbl_review.objects.filter(
                product=product,
                customer=customer
            ).first()
            
            context = {
                'product': product,
                'existing_review': existing_review,
            }
            
            return render(request, 'customer/add_review.html', context)
    
    except tbl_product.DoesNotExist:
        messages.error(request, "Product not found")
        return redirect('browse_products')
    except tbl_customer.DoesNotExist:
        messages.warning(request, "Customer not found")
        return redirect('login')


@require_http_methods(["POST"])
def submit_order_review(request, order_item_id):
    """Submit review for a product from track order page (AJAX)"""
    if 'customer' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please login to write a review'}, status=401)
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        order_item = tbl_order_item.objects.get(order_item_id=order_item_id, order__customer=customer)
        product = order_item.product
        order = order_item.order
        
        # Check if order is delivered
        if order.status not in ['delivered', 'completed']:
             return JsonResponse({'success': False, 'message': 'You can only review products after delivery.'}, status=403)
        
        # Get form data
        rating = request.POST.get('rating', '').strip()
        title = request.POST.get('title', '').strip()
        comment = request.POST.get('comment', '').strip()
        
        # Validation
        if not all([rating, title, comment]):
            return JsonResponse({'success': False, 'message': 'Please fill in all fields'})
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return JsonResponse({'success': False, 'message': 'Rating must be between 1 and 5'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid rating'})
        
        if len(title) < 5:
            return JsonResponse({'success': False, 'message': 'Title must be at least 5 characters'})
        
        if len(comment) < 10:
            return JsonResponse({'success': False, 'message': 'Review comment must be at least 10 characters'})
        
        # Create or update review
        from .models import tbl_review
        
        review, created = tbl_review.objects.update_or_create(
            product=product,
            customer=customer,
            order=order,
            defaults={
                'rating': rating,
                'title': title,
                'comment': comment,
                'is_verified_purchase': True,
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Review submitted successfully!' if created else 'Review updated successfully!'
        })
    
    except tbl_order_item.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Order item not found'}, status=404)
    except tbl_customer.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Customer not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'}, status=500)


from datetime import datetime
from django.shortcuts import get_object_or_404

def return_product(request, order_id):
    """Handle return request for an order"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login to request a return")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        order = get_object_or_404(tbl_order, order_id=order_id, customer=customer)
        
        # Only allows return if currently paid (active rental)
        if order.status in ['paid', 'delivered', 'completed']:
            # Create return requests for all items in the order
            from .models import tbl_return_request
            
            items_returned_count = 0
            for item in order.items.all():
                # Check if return request already exists
                if not tbl_return_request.objects.filter(order_item=item).exists():
                    tbl_return_request.objects.create(
                        order_item=item,
                        customer=customer,
                        order=order,
                        status='requested'
                    )
                    items_returned_count += 1
            
            if items_returned_count > 0:
                order.status = 'return_requested'
                order.save()
                messages.success(request, f"Return requested for Order #{order.order_number}. Our team will contact you for pickup.")
            else:
                messages.error(request, "Return request already exists for all items in this order.")
                
        elif order.status == 'return_requested':
             messages.info(request, "Return is already requested for this order.")
        else:
            messages.error(request, "This order cannot be returned at this stage.")
            
    except tbl_customer.DoesNotExist:
        messages.error(request, "Customer account not found")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        
    return redirect('my_orders')

# ============= RETURN & PICKUP MANAGEMENT =============

def return_request(request):
    """Customer views completed orders and can request return"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        orders = tbl_order.objects.filter(
            customer=customer,
            status__in=['paid', 'completed']
        ).prefetch_related('items__product').order_by('-created_at')
        
        context = {
            'orders': orders,
            'page_title': 'Request Return & Pickup'
        }
        return render(request, 'Customer/return_request.html', context)
    except tbl_customer.DoesNotExist:
        messages.error(request, "Customer not found")
        return redirect('login')


def initiate_return_request(request, order_item_id):
    """Customer initiates return request for an item"""
    if 'customer' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please login'}, status=401)
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        order_item = tbl_order_item.objects.get(order_item_id=order_item_id)
        
        if order_item.order.customer != customer:
            return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
        
        existing_return = tbl_return_request.objects.filter(
            order_item=order_item,
            status__in=['requested', 'scheduled', 'picked_up']
        ).first()
        
        if existing_return:
            return JsonResponse({
                'success': False,
                'message': f'This item already has an active return request'
            })
        
        new_return = tbl_return_request.objects.create(
            order_item=order_item,
            customer=customer,
            order=order_item.order,
            status='requested'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Return request created',
            'return_id': new_return.return_id
        })
    except tbl_order_item.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Order item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def return_request_status(request):
    """Customer views their return requests status"""
    if 'customer' not in request.session:
        messages.warning(request, "Please login")
        return redirect('login')
    
    try:
        customer = tbl_customer.objects.get(login__login_id=request.session['customer'])
        return_requests = tbl_return_request.objects.filter(
            customer=customer
        ).select_related('order_item__product', 'order').order_by('-request_date')
        
        context = {
            'all_returns': return_requests,
            'pending': return_requests.filter(status='requested'),
            'scheduled': return_requests.filter(status='scheduled'),
            'picked_up': return_requests.filter(status='picked_up'),
            'completed': return_requests.filter(status='completed'),
            'page_title': 'My Return Requests'
        }
        return render(request, 'Customer/return_request_status.html', context)
    except tbl_customer.DoesNotExist:
        messages.error(request, "Customer not found")
        return redirect('login')