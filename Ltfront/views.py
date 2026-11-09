import json
import os
import re
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.views.decorators.http import require_GET, require_POST
from google import genai
from .models import CartItem, Order, OrderItem, Product

# HOME PAGE
def home(request):

    products = Product.objects.all()
    paginator = Paginator(products, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    categories = [label for _, label in Product.CATEGORY_CHOICES]

    return render(

        request,

        "shop/home.html",

        {

            "products": page_obj,

            "page_obj": page_obj,

            "page_range": paginator.get_elided_page_range(

                number=page_obj.number,

                on_each_side=1,

                on_ends=1,

            ),

            "categories": categories,

        },

    )





# PRODUCT DETAIL PAGE



def product_detail(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    return render(request, "shop/product_detail.html", {"product": product})



@require_POST
def buy_now(request, product_id):
    """Start checkout for one selected product without changing the cart."""
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    request.session["buy_now_checkout"] = {
        "product_id": product.id,
        "quantity": quantity,
    }
    # A previous cart checkout or coupon must not affect this new purchase.
    request.session.pop("checkout_data", None)
    request.session.pop("applied_coupon", None)

    if not request.user.is_authenticated:
        request.session["continue_buy_now_after_login"] = True
        messages.info(request, "Please sign in to continue with your purchase.")
        return redirect("login")

    return redirect("checkout")





# ABOUT AND CONTACT PAGES



def about(request):

    return render(request, "shop/about.html")





def contact(request):

    return render(request, "shop/contact.html")





# CART PAGE



def cart(request):

    # Opening the cart switches the customer back to normal cart checkout.
    request.session.pop("buy_now_checkout", None)
    request.session.pop("continue_buy_now_after_login", None)

    products = Product.objects.all()

    return render(request, "shop/cart.html", {"products": products})





# CART HELPER FUNCTIONS



def get_request_data(request):

    """Support both JSON requests and normal form submissions."""

    if request.content_type == "application/json":

        try:

            data = json.loads(request.body or "{}")

            return data if isinstance(data, dict) else {}

        except (json.JSONDecodeError, UnicodeDecodeError):

            return {}

    return request.POST





def get_product_image(product):

    """Prefer an uploaded image; otherwise use the existing static image."""

    if product.uploaded_image:

        try:

            return product.uploaded_image.url

        except ValueError:

            pass



    if product.image:

        return static(product.image)



    return ""





def build_cart_payload(request):

    """

    Get the current user's database cart or the guest's session cart.

    cart_count represents distinct products, not total quantities.

    """

    cart_items = []

    subtotal = Decimal("0.00")



    if request.user.is_authenticated:

        items = CartItem.objects.filter(

            user=request.user

        ).select_related("product")



        for cart_item in items:

            product = cart_item.product

            quantity = cart_item.quantity

            item_subtotal = product.price * quantity

            subtotal += item_subtotal



            cart_items.append({

                "id": product.id,

                "name": product.name,

                "category": product.category,

                "price": str(product.price),

                "quantity": quantity,

                "subtotal": str(item_subtotal),

                "image": get_product_image(product),

            })

    else:

        guest_cart = request.session.get("guest_cart", {})



        for product_id, quantity in guest_cart.items():

            try:

                product_id = int(product_id)

                quantity = int(quantity)

            except (ValueError, TypeError):

                continue



            if quantity < 1:

                continue



            product = Product.objects.filter(id=product_id).first()

            if not product:

                continue



            item_subtotal = product.price * quantity

            subtotal += item_subtotal



            cart_items.append({

                "id": product.id,

                "name": product.name,

                "category": product.category,

                "price": str(product.price),

                "quantity": quantity,

                "subtotal": str(item_subtotal),

                "image": get_product_image(product),

            })



    return {

        "items": cart_items,

        "cart_count": len(cart_items),

        "subtotal": str(subtotal),

    }





def build_checkout_cart_payload(request):
    """Use the Buy Now product when present; otherwise use the regular cart."""
    buy_now_data = request.session.get("buy_now_checkout")

    if buy_now_data:
        try:
            product_id = int(buy_now_data.get("product_id"))
            quantity = int(buy_now_data.get("quantity", 1))
        except (AttributeError, TypeError, ValueError):
            product_id = None
            quantity = 0

        if product_id and quantity >= 1:
            product = Product.objects.filter(id=product_id).first()

            if product:
                item_subtotal = product.price * quantity
                return {
                    "items": [{
                        "id": product.id,
                        "name": product.name,
                        "category": product.category,
                        "price": str(product.price),
                        "quantity": quantity,
                        "subtotal": str(item_subtotal),
                        "image": get_product_image(product),
                    }],
                    "cart_count": 1,
                    "subtotal": str(item_subtotal),
                }

        # Discard invalid/stale Buy Now data and safely fall back to the cart.
        request.session.pop("buy_now_checkout", None)

    return build_cart_payload(request)


# CART STATE API



@require_GET

def cart_state(request):

    """Return the current cart contents for the navbar and cart page."""

    return JsonResponse(build_cart_payload(request))





# ADD PRODUCT TO CART



@require_POST

def cart_add(request):

    data = get_request_data(request)



    try:

        product_id = int(data.get("product_id"))

        quantity = int(data.get("quantity", 1))

    except (ValueError, TypeError):

        return JsonResponse({"error": "Invalid product or quantity."}, status=400)



    if quantity < 1:

        return JsonResponse({"error": "Quantity must be at least 1."}, status=400)



    product = Product.objects.filter(id=product_id).first()

    if not product:

        return JsonResponse({"error": "Product not found."}, status=404)



    if request.user.is_authenticated:

        cart_item, created = CartItem.objects.get_or_create(

            user=request.user,

            product=product,

            defaults={"quantity": quantity},

        )



        if not created:

            CartItem.objects.filter(

                id=cart_item.id,

                user=request.user,

            ).update(quantity=F("quantity") + quantity)

    else:

        guest_cart = request.session.get("guest_cart", {})

        try:

            current_quantity = int(guest_cart.get(str(product_id), 0))

        except (ValueError, TypeError):

            current_quantity = 0



        guest_cart[str(product_id)] = current_quantity + quantity

        request.session["guest_cart"] = guest_cart

        request.session.modified = True



    return JsonResponse({"success": True, **build_cart_payload(request)})





# UPDATE CART QUANTITY



@require_POST

def cart_update(request):

    data = get_request_data(request)



    try:

        product_id = int(data.get("product_id"))

        quantity = int(data.get("quantity"))

    except (ValueError, TypeError):

        return JsonResponse({"error": "Invalid product or quantity."}, status=400)



    if quantity < 1:

        return JsonResponse({"error": "Quantity must be at least 1."}, status=400)



    if request.user.is_authenticated:

        updated = CartItem.objects.filter(

            user=request.user,

            product_id=product_id,

        ).update(quantity=quantity)



        if not updated:

            return JsonResponse({"error": "Cart item not found."}, status=404)

    else:

        guest_cart = request.session.get("guest_cart", {})

        if str(product_id) not in guest_cart:

            return JsonResponse({"error": "Cart item not found."}, status=404)



        guest_cart[str(product_id)] = quantity

        request.session["guest_cart"] = guest_cart

        request.session.modified = True



    return JsonResponse({"success": True, **build_cart_payload(request)})





# REMOVE PRODUCT FROM CART



@require_POST

def cart_remove(request):

    data = get_request_data(request)



    try:

        product_id = int(data.get("product_id"))

    except (ValueError, TypeError):

        return JsonResponse({"error": "Invalid product."}, status=400)



    if request.user.is_authenticated:

        CartItem.objects.filter(

            user=request.user,

            product_id=product_id,

        ).delete()

    else:

        guest_cart = request.session.get("guest_cart", {})

        guest_cart.pop(str(product_id), None)

        request.session["guest_cart"] = guest_cart

        request.session.modified = True



    return JsonResponse({"success": True, **build_cart_payload(request)})





# MERGE GUEST CART INTO USER ACCOUNT



def merge_guest_cart(request, user):

    """

    Transfer guest cart products into the user's database cart.

    If a product already exists, increase its quantity.

    """

    guest_cart = request.session.get("guest_cart", {})

    if not guest_cart:

        return



    with transaction.atomic():

        for product_id, quantity in guest_cart.items():

            try:

                product_id = int(product_id)

                quantity = int(quantity)

            except (ValueError, TypeError):

                continue



            if quantity < 1:

                continue



            product = Product.objects.filter(id=product_id).first()

            if not product:

                continue



            cart_item, created = CartItem.objects.get_or_create(

                user=user,

                product=product,

                defaults={"quantity": quantity},

            )



            if not created:

                CartItem.objects.filter(

                    id=cart_item.id,

                    user=user,

                ).update(quantity=F("quantity") + quantity)



    request.session.pop("guest_cart", None)





# GEMINI AI CHATBOT



@require_POST

def chatbot(request):

    user_message = request.POST.get("message", "").strip()



    if not user_message:

        return JsonResponse({"reply": "Please enter a question."}, status=400)



    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:

        return JsonResponse(

            {"reply": "Gemini API key is not configured."},

            status=500,

        )



    try:

        client = genai.Client(api_key=api_key)

        products = Product.objects.all()



        product_context = "\n".join(

            f"- {product.name} | Category: {product.category} | "

            f"Price: ₹{product.price} | Description: {product.description}"

            for product in products

        )



        prompt = f"""

You are Lumina, the AI shopping assistant for LuminaTech.



Available products:

{product_context}



Rules:

1. Answer general electronics questions clearly.

2. When discussing LuminaTech products, use the product list above.

3. Do not invent products, prices, or specifications.

4. If a requested product is not listed, say so.

5. Keep answers concise and useful.



User:

{user_message}

"""



        response = client.models.generate_content(

            model="gemini-3.5-flash-lite",

            contents=prompt,

        )



        return JsonResponse({

            "reply": response.text or "I couldn't generate a response."

        })



    except Exception as e:

        print("Gemini API error:", repr(e))

        return JsonResponse(

            {"reply": "Lumina could not connect to the AI service right now."},

            status=500,

        )





# SIGNUP



def signup_view(request):

    if request.user.is_authenticated:

        return redirect("home-page")



    if request.method == "POST":

        form = UserCreationForm(request.POST)

        email = request.POST.get("email", "").strip()



        if form.is_valid():

            if not email:

                form.add_error(None, "Email address is required.")

            else:

                try:

                    validate_email(email)

                except ValidationError:

                    form.add_error(None, "Please enter a valid email address.")

                else:

                    user = form.save()

                    user.email = email

                    user.save()



                    login(request, user)

                    merge_guest_cart(request, user)



                    messages.success(

                        request,

                        "Account created successfully. Welcome to LuminaTech!",

                    )

                    if request.session.pop("continue_buy_now_after_login", False):
                        return redirect("checkout")

                    return redirect("home-page")

    else:

        form = UserCreationForm()



    return render(request, "shop/signup.html", {"form": form})





# LOGIN



def login_view(request):

    if request.user.is_authenticated:

        return redirect("home-page")



    if request.method == "POST":

        username = request.POST.get("username", "").strip()

        password = request.POST.get("password", "")



        user = authenticate(

            request,

            username=username,

            password=password,

        )



        if user is not None:

            login(request, user)

            merge_guest_cart(request, user)



            if user.email:

                try:

                    send_mail(

                        subject="Successful login to LuminaTech",

                        message=f"""

Hi {user.username},



We noticed a new login to your LuminaTech account.



If this was you, no further action is needed — you're all set to go!



Didn't log in?



If you didn't initiate this request, please reset your password

immediately to secure your account and contact our support team.



Best regards,



The LuminaTech Team

                        """,

                        from_email=None,

                        recipient_list=[user.email],

                        fail_silently=False,

                    )

                    print(f"Login notification sent to {user.email}")

                except Exception as e:

                    print("Login notification email failed:", repr(e))



            messages.success(request, "You are now logged in.")

            if request.session.pop("continue_buy_now_after_login", False):
                return redirect("checkout")

            return redirect("home-page")



        messages.error(request, "Invalid username or password.")



    return render(request, "shop/login.html")





# LOGOUT



def logout_view(request):

    if request.method == "POST":

        logout(request)

    return redirect("home-page")





# CHECKOUT PAGE — LOGIN REQUIRED



@login_required(login_url="login")

def checkout(request):

    # A saved account email is required to place an order.

    account_email = (request.user.email or "").strip()

    if not account_email:

        messages.error(

            request,

            "Please add an email address to your account before checkout.",

        )

        return redirect("home-page")



    cart_data = build_checkout_cart_payload(request)



    if not cart_data["items"]:

        messages.warning(

            request,

            "Your cart is empty. Please add products before checkout.",

        )

        return redirect("cart")



    subtotal = Decimal(cart_data["subtotal"])



    # Apply coupon

    if request.method == "POST" and request.POST.get("apply_coupon"):

        coupon_code = request.POST.get("coupon_code", "").strip().upper()



        if coupon_code == "LUMINA10":

            if subtotal >= Decimal("1000"):

                request.session["applied_coupon"] = coupon_code

                messages.success(request, "Coupon LUMINA10 applied successfully!")

            else:

                request.session.pop("applied_coupon", None)

                messages.error(

                    request,

                    "This coupon requires a minimum order of ₹1,000."

                )

        else:

            request.session.pop("applied_coupon", None)

            messages.error(request, "Invalid coupon code.")



        return redirect("checkout")



    coupon_code = request.session.get("applied_coupon", "")



    delivery_fee, discount, total = calculate_order_totals(
        subtotal,
        coupon_code,
    )

    if coupon_code and discount == Decimal("0.00"):
        request.session.pop("applied_coupon", None)
        coupon_code = ""



    errors = []



    if request.method == "GET":

        user = request.user

        form_data = {

            "full_name": user.get_full_name() or user.username,

            "email": account_email,

            "phone": "",

            "address_line1": "",

            "address_line2": "",

            "city": "",

            "state": "",

            "pincode": "",

        }

    else:

        # Email is always taken from the logged-in account, not the form.

        form_data = {

            "full_name": request.POST.get("full_name", "").strip(),

            "email": account_email,

            "phone": request.POST.get("phone", "").strip(),

            "address_line1": request.POST.get("address_line1", "").strip(),

            "address_line2": request.POST.get("address_line2", "").strip(),

            "city": request.POST.get("city", "").strip(),

            "state": request.POST.get("state", "").strip(),

            "pincode": request.POST.get("pincode", "").strip(),

        }



        required_fields = [

            "full_name",

            "email",

            "phone",

            "address_line1",

            "city",

            "state",

            "pincode",

        ]



        for field in required_fields:

            if not form_data[field]:

                errors.append(f"{field.replace('_', ' ').title()} is required.")



        try:

            validate_email(form_data["email"])

        except ValidationError:

            errors.append("Please enter a valid email address.")



        # Indian mobile number: optional +91 prefix, then 10 digits starting 6-9.

        if form_data["phone"] and not re.fullmatch(

            r"(?:\+91[\s-]?)?[6-9]\d{9}",

            form_data["phone"],

        ):

            errors.append("Please enter a valid Indian mobile number.")



        if form_data["pincode"] and not re.fullmatch(

            r"[1-9]\d{5}",

            form_data["pincode"],

        ):

            errors.append("Please enter a valid 6-digit PIN code.")



        if not errors:

            request.session["checkout_data"] = form_data

            return redirect("payment")



    return render(

        request,

        "shop/checkout.html",

        {
            "items": cart_data["items"],
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "total": total,
            "form_data": form_data,
            "errors": errors,
            "email_locked": True,
            "discount": discount,
            "coupon_code": coupon_code,
            "is_buy_now": bool(request.session.get("buy_now_checkout")),
        },

    )

def calculate_order_totals(subtotal, coupon_code=""):
    """Calculate delivery, the uncapped 10% coupon, and the final total."""
    subtotal = Decimal(str(subtotal))
    coupon_code = (coupon_code or "").strip().upper()

    delivery_fee = (
        Decimal("0.00")
        if subtotal >= Decimal("10000")
        else Decimal("99.00")
    )

    discount = Decimal("0.00")
    if coupon_code == "LUMINA10" and subtotal >= Decimal("1000"):
        discount = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))

    total = subtotal + delivery_fee - discount
    return delivery_fee, discount, total





# PAYMENT PROCESSING AND ORDER CREATION — LOGIN REQUIRED



@login_required(login_url="login")

def payment(request):

    account_email = (request.user.email or "").strip()

    if not account_email:

        messages.error(

            request,

            "Please add an email address to your account before placing an order.",

        )

        return redirect("home-page")



    checkout_data = request.session.get("checkout_data")

    if not checkout_data:

        messages.warning(

            request,

            "Please complete your delivery information before proceeding.",

        )

        return redirect("checkout")



    # Never trust an email value stored in an old or modified session.

    checkout_data["email"] = account_email

    request.session["checkout_data"] = checkout_data



    cart_data = build_checkout_cart_payload(request)

    items = cart_data["items"]



    if not items:

        messages.warning(

            request,

            "Your shopping cart is currently empty. Please add products to continue.",

        )

        return redirect("cart")



    subtotal = Decimal(cart_data["subtotal"])
    coupon_code = request.session.get("applied_coupon", "")

    # Recalculate the coupon on the server using the current cart subtotal.
    delivery_fee, discount, total = calculate_order_totals(
        subtotal,
        coupon_code,
    )

    if coupon_code and discount == Decimal("0.00"):
        request.session.pop("applied_coupon", None)
        coupon_code = ""

    payment_error = None




    if request.method == "POST":

        payment_method = request.POST.get("payment_method", "")

        allowed_methods = ["demo_upi", "demo_card", "cod"]



        if payment_method not in allowed_methods:

            payment_error = "Please select a valid payment method to continue."

        else:

            try:

                with transaction.atomic():

                    order = Order.objects.create(

                        user=request.user,

                        full_name=checkout_data["full_name"],

                        email=account_email,

                        phone=checkout_data["phone"],

                        address_line1=checkout_data["address_line1"],

                        address_line2=checkout_data["address_line2"],

                        city=checkout_data["city"],

                        state=checkout_data["state"],

                        pincode=checkout_data["pincode"],

                        subtotal=subtotal,

                        delivery_fee=delivery_fee,

                        discount=discount,

                        total=total,

                        payment_method=payment_method,

                        payment_status=(

                            "pending" if payment_method == "cod"

                            else "demo_success"

                        ),

                        status="confirmed",

                    )



                    for item in items:

                        product = Product.objects.get(id=item["id"])

                        quantity = int(item["quantity"])

                        unit_price = product.price

                        line_total = unit_price * quantity



                        OrderItem.objects.create(

                            order=order,

                            product=product,

                            product_name=product.name,

                            unit_price=unit_price,

                            quantity=quantity,

                            line_total=line_total,

                        )



                    # A Buy Now order is separate from the saved shopping cart.
                    buy_now_mode = bool(request.session.get("buy_now_checkout"))
                    if not buy_now_mode:
                        CartItem.objects.filter(user=request.user).delete()



                request.session["last_order_number"] = order.order_number

                request.session.pop("checkout_data", None)
                request.session.pop("applied_coupon", None)
                request.session.pop("buy_now_checkout", None)



            except Exception as e:

                print("Order processing error:", repr(e))

                payment_error = (

                    "We were unable to process your order at this time. "

                    "Please try again."

                )

            else:

                payment_labels = {

                    "demo_upi": "UPI (Test Checkout)",

                    "demo_card": "Card (Test Checkout)",

                    "cod": "Cash on Delivery",

                }

                payment_label = payment_labels[payment_method]
                payment_status_label = (
                    "Pending - payable on delivery"
                    if payment_method == "cod"
                    else "Not processed"
                )

                order_items = order.items.all()



                item_details = "\n".join(

                    (

                        f"- {item.product_name} | "

                        f"Quantity: {item.quantity} | "

                        f"Unit Price: ₹{item.unit_price:,.2f} | "

                        f"Total: ₹{item.line_total:,.2f}"

                    )

                    for item in order_items

                )



                delivery_address = (

                    f"{order.address_line1}\n"

                    f"{order.address_line2}\n"

                    f"{order.city}, {order.state} - {order.pincode}"

                )



                # CUSTOMER ORDER CONFIRMATION EMAIL

                customer_message = f"""
LUMINATECH
Smart Technology. Better Living.

ORDER CONFIRMATION
==================================================

Dear {order.full_name},

Thank you for choosing LuminaTech. Your order has been
successfully placed. Please find your order details below.

ORDER DETAILS
--------------------------------------------------
Order Number : {order.order_number}
Order Date   : {order.created_at.strftime("%d %B %Y, %I:%M %p")}
Order Status : {order.get_status_display()}

PURCHASED ITEMS
--------------------------------------------------
"""
                for item in order_items:
                    customer_message += (
                        f"{item.product_name}\n"
                        f"  Quantity   : {item.quantity}\n"
                        f"  Unit Price : ₹{item.unit_price:,.2f}\n"
                        f"  Item Total : ₹{item.line_total:,.2f}\n\n"
                    )

                customer_message += f"""ORDER SUMMARY
--------------------------------------------------
Subtotal     : ₹{order.subtotal:,.2f}
Delivery Fee : ₹{order.delivery_fee:,.2f}
"""
                if order.discount > 0:
                    customer_message += f"Discount     : -₹{order.discount:,.2f}\n"

                customer_message += f"""TOTAL AMOUNT : ₹{order.total:,.2f}

PAYMENT INFORMATION
--------------------------------------------------
Payment Method : {payment_label}
Payment Status : {payment_status_label}

"""
                if payment_method == "cod":
                    customer_message += (
                        "Your order is confirmed with Cash on Delivery. "
                        "Payment is due when your order is delivered.\n\n"
                    )
                else:
                    customer_message += (
                        "Your order has been recorded successfully. "
                        "Online payment processing is currently unavailable, "
                        "and no money has been charged.\n\n"
                    )

                customer_message += f"""DELIVERY ADDRESS
--------------------------------------------------
{order.full_name}
{delivery_address}
Phone : {order.phone}
Email : {order.email}

==================================================
Thank you for shopping with LuminaTech.

For assistance, please contact our support team.

Best regards,
LuminaTech Team
Smart Technology. Better Living.

© 2026 LuminaTech. All rights reserved.
"""

                try:

                    send_mail(

                        subject=f"Order Confirmed: {order.order_number} | LuminaTech",

                        message=customer_message,

                        from_email=None,

                        recipient_list=[order.email],

                        fail_silently=False,

                    )

                    print(f"Order confirmation email sent to {order.email}")

                except Exception as e:

                    print("Customer confirmation email failed:", repr(e))



                # STORE ADMINISTRATION EMAIL

                admin_email = (

                    os.getenv("STORE_ORDER_NOTIFICATION_EMAIL")

                    or settings.EMAIL_HOST_USER

                )



                if admin_email:

                    admin_message = f"""
LUMINATECH - NEW ORDER NOTIFICATION
==================================================

A new order has been placed on your store.

ORDER DETAILS
--------------------------------------------------
Order Number : {order.order_number}
Order Date   : {order.created_at.strftime("%d %B %Y, %I:%M %p")}
Order Status : {order.get_status_display()}

CUSTOMER INFORMATION
--------------------------------------------------
Name  : {order.full_name}
Email : {order.email}
Phone : {order.phone}

DELIVERY ADDRESS
--------------------------------------------------
{order.full_name}
{delivery_address}

ORDERED PRODUCTS
--------------------------------------------------
"""
                    for item in order_items:
                        admin_message += (
                            f"{item.product_name}\n"
                            f"  Quantity   : {item.quantity}\n"
                            f"  Unit Price : ₹{item.unit_price:,.2f}\n"
                            f"  Item Total : ₹{item.line_total:,.2f}\n\n"
                        )

                    admin_message += f"""PAYMENT AND PRICING
--------------------------------------------------
Subtotal     : ₹{order.subtotal:,.2f}
Delivery Fee : ₹{order.delivery_fee:,.2f}
"""
                    if order.discount > 0:
                        admin_message += f"Discount     : -₹{order.discount:,.2f}\n"

                    admin_message += f"""ORDER TOTAL  : ₹{order.total:,.2f}

Payment Method : {payment_label}
Payment Status : {payment_status_label}
Order Status   : {order.get_status_display()}

==================================================

Please review this order and update its progress
through the LuminaTech Administration Panel.

This is an automated order notification.

Regards,
LuminaTech System
"""
                    try:

                        send_mail(

                            subject=f"New Order Received: {order.order_number}",

                            message=admin_message,

                            from_email=None,

                            recipient_list=[admin_email],

                            fail_silently=False,

                        )

                        print(f"New order notification sent to {admin_email}")

                    except Exception as e:

                        print("Store notification email failed:", repr(e))



                messages.success(

                    request,

                    "Thank you! Your order has been successfully placed.",

                )

                return redirect(

                    "order-success",

                    order_number=order.order_number,

                )



    return render(

        request,

        "shop/payment.html",

        {

            "checkout_data": checkout_data,

            "items": items,

            "subtotal": subtotal,

            "delivery_fee": delivery_fee,
            "discount": discount,
            "coupon_code": coupon_code,
            "total": total,
            "payment_error": payment_error,

        },

    )





# ORDER SUCCESS PAGE — LOGIN REQUIRED, OWN ORDERS ONLY



@login_required(login_url="login")

def order_success(request, order_number):

    order = get_object_or_404(

        Order,

        order_number=order_number,

        user=request.user,

    )



    return render(
        request,
        "shop/order_success.html",
        {
            "order": order,
            "items": order.items.all(),
        },
    )
