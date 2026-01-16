from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.conf import settings
from .models import Product, Order
from .utils.mpesa import get_mpesa_access_token
import datetime
import base64
import requests
import json



def index(request):
    cart = request.session.get('cart', [])
    return render(request, 'shop/index.html', {'cart': cart})




def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        print("Username:", username)
        print("Email:", email)
        print("Password:", password)
        print("Confirm Password:", confirm_password)
        print(username)

        if password != confirm_password:
            return HttpResponse('<div style="color: red; margin-bottom: 10px"> Passwords do not match</div>')

        if User.objects.filter(username=username).exists():
            return HttpResponse('<div style="color: red; margin-bottom: 10px"> Username already taken</div>')
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        response = HttpResponse('redirect... ')
        response['HX-Redirect'] = '/login'
        return response
    return render(request, "shop/register.html")

def login_user(request): 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
         login(request, user)
         next_url = request.GET.get('next', 'index')
         response = HttpResponse('')

         if '/' not in next_url:
             response['HX-Redirect'] = reverse(next_url)
         else:
             response['HX-Redirect'] = next_url
         return response
        else:
        
            return HttpResponse(
                '<div style="color:red; padding-bottom: 20px;">Invalid username or password</div>'
            )
    
    return render(request, 'shop/login.html')


@login_required(login_url="login")
def women(request):
    cart = request.session.get('cart', [])
    sort = request.GET.get('sort')
    subcategory = request.GET.get("sub")

    products = Product.objects.filter(category='women')
    if subcategory:
        products = products.filter(subcategory=subcategory)

    if sort == 'low-to-high':
        products = products.order_by('price')
    elif sort == 'high-to-low':
        products = products.order_by('-price')

    template = "shop/women_products.html" if request.headers.get("HX-Request") else "shop/women.html"

    return render(request, template, {
        'cart': cart,
        'products': products,
        "subcategories": ["clothing", "shoes", "handbags"]
    })


@login_required(login_url="login")
def men(request):
    cart = request.session.get('cart', [])
    sort = request.GET.get('sort')
    subcategory = request.GET.get("sub")

    products = Product.objects.filter(category='men')
    if subcategory:
        products = products.filter(subcategory=subcategory)

    if sort == 'low-to-high':
        products = products.order_by('price')
    elif sort == 'high-to-low':
        products = products.order_by('-price')

    template = "shop/product_grid.html" if request.headers.get("HX-Request") else "shop/men.html"

    return render(request, template, {
        'cart': cart,
        'products': products,
        "subcategories": ["clothing", "shoes", "watches"]
    })




def add_to_cart(request):
    if request.method == "POST":
        cart = request.session.get("cart", [])

        product_id = request.POST.get("product_id")
        
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                item = {
                    "name": product.name,
                    "price": int(product.price),
                    "image": product.image.url if product.image else "",
                    "quantity": 1,
                }
            except Product.DoesNotExist:
                return HttpResponse("Product not found", status=404)
        else:
            item = {
                "name": request.POST.get("name"),
                "price": int(request.POST.get("price", 0)),
                "image": request.POST.get("image"),
                "quantity": 1,
            }
        
        cart.append(item)
        request.session["cart"] = cart

        return HttpResponse(f'''
            <a href="{reverse('cart')}" id="cart-icon" style="position: relative; display: inline-block; font-size: 20px;">
                <i class="fa fa-shopping-cart"></i>
                <span style="position: absolute; top: -8px; right: -8px; background: red; color: white; border-radius: 50%; padding: 2px 6px; font-size: 12px; font-weight: bold;">{len(cart)}</span>
            </a>
        ''')
    

@login_required
def cart(request):
    cart_items = request.session.get("cart", [])
    
    for item in cart_items:
        item["total_price"] = item["price"] * item.get("quantity", 1)
    
    total = sum(item["total_price"] for item in cart_items)

    order = None
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(
            buyer=request.user,
            status="PENDING",
            defaults={"amount": total}
        )
        
        if not created and order.amount != total:
            order.amount = total
            order.save()

    return render(request, "shop/cart.html", {
        "cart": cart_items,
        "total": total,
        "order": order
    })

def update_cart (request):
    if request.method == "POST":
        cart = request.session.get("cart", [])
        action = request.POST.get("action")
        name = request.POST.get("name")

        for item in cart: 
            if item["name"] == name:
                if "quantity" not in item:
                    item["quantity"] = 1
                if action == "increase":
                    item["quantity"] += 1
                elif action == "decrease" and item["quantity"] > 1:
                    item["quantity"] -= 1
                break
        request.session["cart"] =  cart
        total = sum(i["price"] * i.get("quantity", 1) for i in cart)
        
        order = None
        if request.user.is_authenticated:
            order = Order.objects.filter(buyer=request.user, status="PENDING").first()
        
        return render(request, "shop/cart_items.html", {
            "cart": cart, 
            "total": total,
            "order": order
        })
        

def remove_item(request):
    if request.method == "POST":
        cart = request.session.get("cart", [])
        name = request.POST.get("name")

        cart = [item for item in cart if item["name"] != name]
        request.session["cart"] = cart

        if not cart and request.user.is_authenticated:
            Order.objects.filter(
                buyer=request.user,
                status="PENDING"
            ).delete()

        total = sum(i["price"] * i.get("quantity", 1) for i in cart)
        
        order = None
        if request.user.is_authenticated:
            order = Order.objects.filter(buyer=request.user, status="PENDING").first()

        return render(request, "shop/cart_items.html", {
            "cart": cart,
            "total": total,
            "order": order
        })



def stk_push(request, order_id):
    order = Order.objects.get(id=order_id)

    email = request.POST.get('email')
    city = request.POST.get('city')
    location = request.POST.get('location')
    #amount = request.POST.get('amount', order.amount)
    phone_input = request.POST.get('phone')

    if phone_input:
        order.phone = phone_input
    if email:
        order.email = email
    if city:
        order.city = city
    if location:
        order.location = location
    order.save()

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
    ).decode()

    access_token = get_mpesa_access_token()

    if not order.phone:
        return JsonResponse({"error": "Phone number is required"}, status=400)
    
    phone = order.phone.strip()

    phone = phone.replace('+', '').replace(' ', '').replace('-', '')
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    elif phone.startswith('7') or phone.startswith('1'):
        phone = '254' + phone

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": order.amount,
        "PartyA": phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": f"ORDER-{order.id}",
        "TransactionDesc": "FashionHub Escrow"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    print("Payload:", payload)  
    print("Headers:", headers)  
    
    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers
    )

    response_data = response.json()
    print("M-Pesa Response:", response_data)  
    
    if response_data.get("ResponseCode") == "0":
        return HttpResponse("""
            <div style="text-align: center; padding: 20px; background: #d4edda; color: #155724; border-radius: 6px; margin: 20px 0;">
                <h3 style="margin: 0 0 10px 0;">✓ Success</h3>
                <p style="margin: 0;">Payment request sent! Check your phone for the M-Pesa prompt.</p>
            </div>
        """)
    else:
        error_message = response_data.get("CustomerMessage", "Payment request failed")
        return HttpResponse(f"""
            <div style="text-align: center; padding: 20px; background: #f8d7da; color: #721c24; border-radius: 6px; margin: 20px 0;">
                <h3 style="margin: 0 0 10px 0;">✗ Error</h3>
                <p style="margin: 0;">{error_message}</p>
            </div>
        """)


@csrf_exempt
def mpesa_callback(request):
    try:
        data = json.loads(request.body)
        print("M-Pesa callback received:", data)
        
        callback = data.get("Body", {}).get("stkCallback", {})
        
        # Check if payment was successful
        if callback.get("ResultCode") == 0:
            # Extract M-Pesa receipt number
            metadata = callback.get("CallbackMetadata", {}).get("Item", [])
            receipt = None
            
            for item in metadata:
                if item.get("Name") == "MpesaReceiptNumber":
                    receipt = item.get("Value")
                    break
            
            # Get the order reference from callback
            #checkout_request_id = callback.get("CheckoutRequestID")
            
            # Find the most recent pending order and update it
            order = Order.objects.filter(status="PENDING").order_by('-id').first()
            
            if order and receipt:
                order.mpesa_receipt = receipt
                order.status = "PAID"
                order.save()
                print(f"Order {order.tracking_number} updated - Receipt: {receipt}, Status: PAID")
                
                # Get email, city, location from order
                email = order.email or order.buyer.email
                city = order.city
                location = order.location
                
                # Send confirmation email with receipt
                if email:
                    try:
                        subject = f"Payment Confirmed - FashionHub Order {order.tracking_number}"
                        message = f"""
                        Dear {order.buyer.username},

                        Your payment has been successfully received!

                        Payment Details:
                        - M-Pesa Receipt: {receipt}
                        - Order Number: {order.tracking_number}
                        - Amount Paid: KES {order.amount}
                        - Phone: {order.phone}
                        - Payment Status: PAID

                        Delivery Information:
                        - City: {city if city else 'Not provided'}
                        - Location: {location if location else 'Not provided'}

                        Your order is now being processed and will be delivered within 1-2 days.

                        Thank you for shopping with FashionHub!

                        Best regards,
                        The FashionHub Team
                        """
                        
                        send_mail(
                            subject,
                            message,
                            settings.EMAIL_HOST_USER,
                            [email],
                            fail_silently=False,
                        )
                        print(f"Confirmation email sent to {email}")
                    except Exception as e:
                        print(f"Email sending failed: {e}")
            else:
                print("No pending order found or no receipt number")
        else:
            result_desc = callback.get("ResultDesc", "Payment failed")
            print(f"Payment failed: {result_desc}")
            
    except Exception as e:
        print(f"Callback error: {e}")
    
    return HttpResponse("OK")


def featured_products(request):
    sort_order = request.GET.get('sort', 'default')

    if sort_order == 'low-to-high':
        products = Product.objects.all().order_by('price')
    elif sort_order == 'high-to-low':
        products = Product.objects.all().order_by('-price')
    else:
        products = Product.objects.all()

    return render(request, 'shop/featured.html', {
        'products': products,
        'sort_order': sort_order
    })


@csrf_exempt
def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email")
        
        if not email:
            return JsonResponse({
                "success": False,
                "message": "Please enter a valid email address"
            })
        
        try:
            subject = "Welcome to FashionHub Newsletter!"
            message = f"""
            Dear Subscriber,

            Thank you for subscribing to FashionHub's newsletter!

            You'll now be the first to know about:
            - New arrivals and exclusive collections
            - Special deals and discounts
            - Fashion tips and styling advice
            - Upcoming sales and events

            Stay stylish!

            Best regards,
            The FashionHub Team
            """
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            
            return JsonResponse({
                "success": True,
                "message": "Successfully subscribed! Check your email for confirmation."
            })
            
        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": f"Subscription failed. Please try again later."
            })
    
    return JsonResponse({
        "success": False,
        "message": "Invalid request method"
    })


def faq(request):
    return render(request, "shop/faq.html")

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        
        # Send contact email to admin
        try:
            subject = f"Contact Form: Message from {name}"
            admin_message = f"""
            You have received a new contact form submission:
            
            Name: {name}
            Email: {email}
            
            Message:
            {message}
            
            ---
            Reply directly to: {email}
            """
            
            send_mail(
                subject,
                admin_message,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],  # Send to yourself
                fail_silently=False,
            )
            
            index_url = reverse('index')
            return HttpResponse(f"""
                <div style="padding: 20px;">
                    <div style="margin-bottom: 20px;">
                        <a href="{index_url}" style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; font-weight: 500;">
                            ← Back to Home
                        </a>
                    </div>
                    <hr style="border: none; border-top: 2px solid #ddd; margin: 20px 0;">
                    <div style="text-align: center; padding: 40px; background: #d4edda; color: #155724; border-radius: 8px;">
                        <h2 style="margin: 0 0 15px 0;">✓ Thank You for Contacting Us!</h2>
                        <p style="margin: 0; font-size: 16px;">We've received your message and will get back to you soon.</p>
                    </div>
                </div>
            """)
        except Exception as e:
            index_url = reverse('index')
            return HttpResponse(f"""
                <div style="padding: 20px;">
                    <div style="margin-bottom: 20px;">
                        <a href="{index_url}" style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; font-weight: 500;">
                            ← Back to Home
                        </a>
                    </div>
                    <hr style="border: none; border-top: 2px solid #ddd; margin: 20px 0;">
                    <div style="text-align: center; padding: 40px; background: #f8d7da; color: #721c24; border-radius: 8px;">
                        <h2 style="margin: 0 0 15px 0;">✗ Error</h2>
                        <p style="margin: 0; font-size: 16px;">Failed to send message. Please try again.</p>
                    </div>
                </div>
            """)
    
    return render(request, "shop/contact.html")

def shipping_info(request):
    return render(request, "shop/shipping_info.html")

def returns(request):
    return render(request, "shop/returns.html")

def logout_view(request):
    logout(request)
    return redirect("index")

@user_passes_test(lambda u: u.is_staff)
def inventory(request):
    """Dashboard for tracking orders and product inventory - Admin only"""
    # Get all orders
    orders = Order.objects.all().order_by('-id')[:20]  
    
    # Get statistics
    total_orders = Order.objects.count()
    paid_orders = Order.objects.filter(status='PAID').count()
    pending_orders = Order.objects.filter(status='PENDING').count()
    total_revenue = Order.objects.filter(status='PAID').aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Get products by category
    women_products = Product.objects.filter(category='women').order_by('name')
    men_products = Product.objects.filter(category='men').order_by('name')
    
    return render(request, 'shop/inventory.html', {
        'orders': orders,
        'total_orders': total_orders,
        'paid_orders': paid_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'women_products': women_products,
        'men_products': men_products,
    })

def check_order_status(request):
    """Check if order status has changed to PAID"""
    if not request.user.is_authenticated:
        return HttpResponse("")
    
    order = Order.objects.filter(buyer=request.user).order_by('-id').first()
    
    if order:
        # Stop polling if status is PAID
        polling_attr = 'hx-get="/check-order-status/" hx-trigger="every 3s" hx-swap="outerHTML"' if order.status == 'PENDING' else ''
        bg_color = '#04AA6D' if order.status == 'PAID' else '#ffa500'
        
        return HttpResponse(f"""
        <div id="order-status" {polling_attr}>
        <span style="padding: 6px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; background-color: {bg_color}; color: white;">
            {order.status}
        </span>
        </div>
        """)
    return HttpResponse("")
