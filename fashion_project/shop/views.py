from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import CustomUser, Product, Order
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.urls import reverse




import datetime
import base64
import requests
import json

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .utils.mpesa import get_mpesa_access_token









def index(request):
    cart = request.session.get('cart', [])
    return render(request, 'shop/index.html', {'cart': cart})

def auth(request):
    return render(request, 'shop/auth.html')


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
            # messages.error(request, 'Passwords do not match')
            return HttpResponse('<div style="color: red; margin-bottom: 10px"> Passwords do not match</div>')

        if CustomUser.objects.filter(username=username).exists():
            return HttpResponse('<div style="color: red; margin-bottom: 10px"> Username already taken</div>')
        # user = CustomUser(username=username, email=email)
        # user.set_password(password)
        # user.save()
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        #return HttpResponse('<div style="color: green;">Account created successfully!</div>')
        response = HttpResponse('redirect... ')
        response['HX-Redirect'] = '/login'
        return response
    return render(request, "shop/register.html")
    # else:
    #     return render(request, 'shop/register.html')

def login_user(request): 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
         login(request, user)
        #  response = HttpResponse('')
        #  response['HX-Redirect'] =  reverse('index')
         return redirect('index')
        #  return HttpResponse(
        #     '<div style="color:green;padding-bottom: 10px">Login Successful</div>'
        #     ) 
        else:
        
            return HttpResponse(
                '<div style="color:red; padding-bottom: 20px;">Invalid username or password</div>'
            )
    
    return render(request, 'shop/login.html')









# def women(request):
#     cart = request.session.get('cart', [])
#     return render(request, 'shop/women.html', {'cart': cart})

# 


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



# def men(request):
#     cart = request.session.get('cart', [])
#     sort = request.GET.get('sort')

#     products = Product.objects.filter(category='men')

#     if sort == 'low-to-high':
#         products = products.order_by('price')
#     elif sort == 'high-to-low':
#         products = products.order_by('-price')

#     return render(request, 'shop/men.html', {
#         'cart': cart,
#         'products': products
#     })



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

        # Check if product_id is sent (new approach) or individual fields (old approach)
        product_id = request.POST.get("product_id")
        
        if product_id:
            # New approach: get product from database
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
            # Old approach: get from POST data
            item = {
                "name": request.POST.get("name"),
                "price": int(request.POST.get("price", 0)),
                "image": request.POST.get("image"),
                "quantity": 1,
            }
        
        cart.append(item)
        request.session["cart"] = cart

        # Return updated cart icon HTML for HTMX
        return HttpResponse(f'''
            <a href="{reverse('cart')}" id="cart-icon" style="position: relative; display: inline-block; font-size: 20px;">
                <i class="fa fa-shopping-cart"></i>
                <span style="position: absolute; top: -8px; right: -8px; background: red; color: white; border-radius: 50%; padding: 2px 6px; font-size: 12px; font-weight: bold;">{len(cart)}</span>
            </a>
        ''')
def cart(request):
    cart = request.session.get("cart", [])
    total = sum(item["price"] * item.get("quantity", 1) for item in cart)

    return render(request, "shop/cart.html",
                  {
                      "cart": cart,
                      "total": total
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
        return render(request, "shop/cart_items.html", {
            "cart": cart, 
            "total": total
        })
        

def remove_item(request):
    if request.method == "POST":
        cart = request.session.get("cart", [])
        name = request.POST.get("name")

        cart = [item for item in cart if item["name"] != name]
        request.session["cart"] = cart
        total = sum(i["price"] * i.get("quantity", 1) for i in cart)
        return render(request, "shop/cart_items.html", {
            'cart': cart,
            'total': total
        })
    
def password_reset(request):
    return render(request, "shop/password_reset.html")













def stk_push(request, order_id):
    order = Order.objects.get(id=order_id)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
    ).decode()

    access_token = get_mpesa_access_token()

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": order.amount,
        "PartyA": order.phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": order.phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": f"ORDER-{order.id}",
        "TransactionDesc": "FashionHub Escrow"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers
    )

    return JsonResponse(response.json())




@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)

    callback = data["Body"]["stkCallback"]

    if callback["ResultCode"] == 0:
        metadata = callback["CallbackMetadata"]["Item"]

        receipt = next(
            item["Value"] for item in metadata if item["Name"] == "MpesaReceiptNumber"
        )

        order = Order.objects.filter(status="ESCROW_PENDING").last()
        order.mpesa_receipt = receipt
        order.status = "ESCROWED"
        order.save()

    return HttpResponse("OK")



@csrf_exempt
def checkout_stk(request, order_id):
    if request.method == "POST":
        phone = request.POST.get("phone")
        
        # Get cart from session
        cart = request.session.get("cart", [])
        total = sum(item["price"] * item.get("quantity", 1) for item in cart)
        
        # Create or update order with cart total
        if order_id == 1:  # If using placeholder order_id
            # Create new order or get the most recent pending order
            order, created = Order.objects.get_or_create(
                buyer=request.user if request.user.is_authenticated else User.objects.first(),
                seller=User.objects.first(),  # Replace with actual seller logic
                status="ESCROW_PENDING",
                defaults={
                    'amount': int(total),
                    'phone': phone
                }
            )
            if not created:
                order.amount = int(total)
                order.phone = phone
                order.save()
        else:
            try:
                order = Order.objects.get(id=order_id)
                order.phone = phone
                order.amount = int(total)
                order.save()
            except Order.DoesNotExist:
                return JsonResponse({"error": "Order not found"}, status=404)
        
        # Call stk_push with the request and order_id
        return stk_push(request, order.id)
    


def featured_products(request):
    # Default order
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