from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.cache import cache_control
from GuestApp.models import *
from AdminApp.models import *
from VendorApp.models import tbl_product
from django.http import JsonResponse


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = tbl_login.objects.get(username=username, password=password, status="Active")

            if user.role == "Customer":
                try:
                    customer = tbl_customer.objects.get(login=user)

                    if customer.is_rejected:
                        messages.error(
                            request,
                            "❌ Your account has been REJECTED by the administrator."
                        )
                        return render(request, "Guest/login.html")

                    if not customer.is_verified:
                        messages.warning(
                            request,
                            "⏳ Your account is pending admin verification."
                        )
                        return render(request, "Guest/login.html")

                except tbl_customer.DoesNotExist:
                    messages.error(request, "Customer profile not found")
                    return render(request, "Guest/login.html")

            elif user.role == "Vendor":
                try:
                    vendor = tbl_vendor.objects.get(login=user)

                    if vendor.status == "Rejected":
                        messages.error(
                            request,
                            "❌ Your vendor account has been REJECTED by the administrator."
                        )
                        return render(request, "Guest/login.html")

                    if vendor.status == "Pending":
                        messages.warning(
                            request,
                            "⏳ Your vendor account is pending admin verification."
                        )
                        return render(request, "Guest/login.html")

                except tbl_vendor.DoesNotExist:
                    messages.error(request, "Vendor profile not found")
                    return render(request, "Guest/login.html")

            # ✅ Login success
            request.session.flush()
            # request.session['user_id'] = user.login_id
            # request.session['username'] = user.username
            # request.session['role'] = user.role

            if user.role == "Admin":
                request.session['admin'] = user.login_id
                request.session['admin_name'] = user.username
                return redirect('admin_home')
            elif user.role == "Vendor":
                request.session['vendor'] = user.login_id
                request.session['vendor_name'] = user.username
                return redirect('vendor_home')
            else:
                request.session['customer'] = user.login_id
                request.session['customer_name'] = user.username
                return redirect('customer_home')

            messages.success(request, f"Welcome back, {user.username}!")

        except tbl_login.DoesNotExist:
            messages.error(request, "Invalid username or password")

    return render(request, "Guest/login.html")


# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def guest_home(request):
    featured_products = tbl_product.objects.filter(is_featured=True, is_available=True, status='Active')[:8]
    if not featured_products.exists():
        featured_products = tbl_product.objects.filter(is_available=True, status='Active').order_by('-created_at')[:8]
    
    # Get popular products (latest 5 available products)
    popular_products = tbl_product.objects.filter(is_available=True, status='Active').order_by('-created_at')[:5]
    
    # Get all subcategories for category banners
    subcategories = tbl_subcategory.objects.all()
    
    return render(request, 'guest/index.html', {'featured_products': featured_products, 'popular_products': popular_products, 'subcategories': subcategories})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def guest_browse_products(request):
    """Display all products for guests with category and subcategory filters"""
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
    
    # Sort products
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('rent_price_per_day')
    elif sort_by == 'price_high':
        products = products.order_by('-rent_price_per_day')
    elif sort_by == 'popular':
        products = products.order_by('-created_at')
    else:  # newest
        products = products.order_by('-created_at')
    
    context = {
        'categories': categories,
        'subcategories': subcategories,
        'products': products,
        'selected_category': category_id,
        'selected_subcategory': subcategory_id,
        'search_query': search_query,
        'sort_by': sort_by,
        'is_guest': True,
    }
    return render(request, 'guest/browse_products.html', context)

def customer_registration(request):
    districtdata = tbl_district.objects.all().order_by('district_name')

    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        location_id = request.POST.get('location')
        district_id = request.POST.get('district')
        password = request.POST.get('password')
        id_proof = request.FILES.get('id_proof')

        # ID proof validation
        if not id_proof:
            messages.error(request, "ID proof image is required")
            return render(request, 'Guest/customerreg.html', {
                'districtdata': districtdata
            })

        # if id_proof.size > 2 * 1024 * 1024:
        #     messages.error(request, "ID proof must be under 2MB")
        #     return render(request, 'Guest/customerreg.html', {
        #         'districtdata': districtdata
        #     })

        if not id_proof.content_type.startswith('image'):
            messages.error(request, "Only image files are allowed")
            return render(request, 'Guest/customerreg.html', {
                'districtdata': districtdata
            })

        # Duplicate checks
        if tbl_login.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'Guest/customerreg.html', {
                'districtdata': districtdata
            })

        if tbl_customer.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'Guest/customerreg.html', {
                'districtdata': districtdata
            })

        # Create login record
        login_obj = tbl_login.objects.create(
            username=username,
            password=password,
            role="Customer",
            status="Active"
        )

        # Create customer record
        tbl_customer.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
            location_id_id=location_id,
            district_id_id=district_id,
            id_proof=id_proof,
            login=login_obj,
            status="Pending",
            is_verified=False,
            is_rejected=False
        )

        messages.success(
            request,
            "Registration successful! Your account is pending admin verification."
        )
        return redirect('login')

    return render(request, 'Guest/customerreg.html', {
        'districtdata': districtdata
    })


def vendor_registration(request):
    """Handle vendor registration"""
    districtdata = tbl_district.objects.all().order_by('district_name')

    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        location_id = request.POST.get('location')
        district_id = request.POST.get('district')
        password = request.POST.get('password')
        gstin = request.POST.get('gstin')
        aadhar_proof = request.FILES.get('aadhar_proof')
        shop_license = request.FILES.get('shop_license')

        # Validation: Required files
        if not aadhar_proof:
            messages.error(request, "Aadhar proof is required")
            return render(request, 'Guest/vendorreg.html', {'districtdata': districtdata})

        if not shop_license:
            messages.error(request, "Shop license is required")
            return render(request, 'Guest/vendorreg.html', {'districtdata': districtdata})

        # Validation: File types
        allowed_aadhar = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp']
        allowed_license = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp']

        if aadhar_proof.content_type not in allowed_aadhar:
            messages.error(request, "Aadhar proof must be PDF or image (JPEG, PNG, WebP)")
            return render(request, 'Guest/vendorreg.html', {'districtdata': districtdata})

        if shop_license.content_type not in allowed_license:
            messages.error(request, "Shop license must be PDF or image (JPEG, PNG, WebP)")
            return render(request, 'Guest/vendorreg.html', {'districtdata': districtdata})

        # Validation: Duplicate username
        if tbl_login.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another.")
            return render(request, 'Guest/vendorreg.html', {'districtdata': districtdata})

        # Validation: Duplicate email
        if tbl_vendor.objects.filter(email=email).exists():
            messages.error(request, "Email already registered as vendor")
            return render(request, 'Guest/vendorreg.html', {'districtdata': districtdata})

        # Validation: Duplicate GSTIN
        if tbl_vendor.objects.filter(gstin=gstin).exists():
            messages.error(request, "GSTIN already registered")
            return render(request, 'Guest/vendorreg.html', {'districtdata': districtdata})

        try:
            # Create login record
            login_obj = tbl_login.objects.create(
                username=username,
                password=password,
                role="Vendor",
                status="Active"
            )

            # Create vendor record
            vendor_obj = tbl_vendor.objects.create(
                name=name,
                email=email,
                phone=phone,
                address=address,
                location_id=location_id,
                district_id=district_id,
                aadhar_proof=aadhar_proof,
                shop_license=shop_license,
                gstin=gstin,
                login=login_obj,
                status="Pending"
            )

            messages.success(
                request,
                "✅ Registration successful! Your account is pending admin verification. You will be notified once verified."
            )
            return redirect('login')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, 'Guest/vendorreg.html', {'districtdata': districtdata})

    return render(request, 'Guest/vendorreg.html', {'districtdata': districtdata})


def get_locations_by_district(request):
    district_id = request.GET.get('district_id')
    try:
        locations = tbl_location.objects.filter(district_id=district_id).values('location_id', 'location_name')
        data = {
            'locations': list(locations),
            'success': True
        }
    except Exception as e:
        data = {
            'locations': [],
            'success': False,
            'error': str(e)
        }
    
    return JsonResponse(data)

def logout(request):
    # Clear all persistent messages before logging out
    from django.contrib.messages.storage.fallback import FallbackStorage
    storage = messages.get_messages(request)
    # Iterate through all messages to mark them as used
    for _ in storage:
        pass
    
    request.session.flush()
    return redirect('login')

def guest_product_detail(request, product_id):
    try:
        from VendorApp.models import tbl_product
        from CustomerApp.models import tbl_review
        from django.db.models import Avg

        product = tbl_product.objects.get(product_id=product_id, is_available=True, status='Active')
        images = product.images.all()
        related_products = tbl_product.objects.filter(
            category=product.category,
            is_available=True,
            status='Active'
        ).exclude(product_id=product_id)[:4]

        reviews = tbl_review.objects.filter(product=product).order_by('-created_at')
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        context = {
            'product': product,
            'images': images,
            'related_products': related_products,
            'reviews': reviews,
            'avg_rating': round(avg_rating, 1)
        }
        return render(request, 'Guest/product_detail.html', context)
    except Exception as e:
        messages.error(request, "Product not found")
        return redirect('guest_home')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def guest_view_cart(request):
    """Display guest session cart"""
    guest_cart = request.session.get('guest_cart', [])
    
    # Calculate totals
    total_rent = 0
    total_security_deposit = 0
    total_grand = 0
    
    from decimal import Decimal
    
    for item in guest_cart:
        total_rent += Decimal(item.get('total_rent', 0))
        total_security_deposit += Decimal(item.get('security_deposit', 0))
        total_grand += Decimal(item.get('grand_total', 0))
    
    context = {
        'guest_cart': guest_cart,
        'total_rent': total_rent,
        'total_security_deposit': total_security_deposit,
        'total_grand': total_grand,
    }
    
    return render(request, 'Guest/cart.html', context)
