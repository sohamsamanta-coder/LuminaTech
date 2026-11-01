
import json
import os
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.views.decorators.http import require_GET, require_POST

from google import genai

from .models import Product, CartItem


# HOME PAGE

def home(request):
    products = Product.objects.all()

    paginator = Paginator(products, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    categories = [
        label for _, label in Product.CATEGORY_CHOICES
    ]

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

    return render(
        request,
        "shop/product_detail.html",
        {"product": product},
    )


# ABOUT AND CONTACT PAGES

def about(request):
    return render(request, "shop/about.html")


def contact(request):
    return render(request, "shop/contact.html")


# CART PAGE

def cart(request):
    # Kept temporarily for compatibility with your current
    # cart template. We will connect the template to the
    # cart API in the next stage.
    products = Product.objects.all()

    return render(
        request,
        "shop/cart.html",
        {"products": products},
    )


# CART HELPER FUNCTIONS

def get_request_data(request):
    """
    Supports both JSON requests and normal form submissions.
    """

    if request.content_type == "application/json":
        try:
            data = json.loads(request.body or "{}")
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    return request.POST


def get_product_image(product):
    """
    Uses an uploaded product image first.
    Otherwise, uses the existing static image.
    """

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
    Gets the current user's database cart or the guest's
    session cart and prepares the data for JavaScript.
    """

    cart_items = []
    subtotal = Decimal("0.00")
    cart_count = 0

    if request.user.is_authenticated:

        items = CartItem.objects.filter(
            user=request.user
        ).select_related("product")

        for cart_item in items:
            product = cart_item.product
            quantity = cart_item.quantity

            item_subtotal = product.price * quantity
            subtotal += item_subtotal
            cart_count += quantity

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

            product = Product.objects.filter(
                id=product_id
            ).first()

            if not product:
                continue

            item_subtotal = product.price * quantity
            subtotal += item_subtotal
            cart_count += quantity

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


# CART STATE API

@require_GET
def cart_state(request):
    """
    Returns the current cart contents.
    Used by the navbar and cart page.
    """

    return JsonResponse(build_cart_payload(request))


# ADD PRODUCT TO CART

@require_POST
def cart_add(request):
    data = get_request_data(request)

    try:
        product_id = int(data.get("product_id"))
        quantity = int(data.get("quantity", 1))
    except (ValueError, TypeError):
        return JsonResponse(
            {"error": "Invalid product or quantity."},
            status=400,
        )

    if quantity < 1:
        return JsonResponse(
            {"error": "Quantity must be at least 1."},
            status=400,
        )

    product = Product.objects.filter(id=product_id).first()

    if not product:
        return JsonResponse(
            {"error": "Product not found."},
            status=404,
        )

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
            ).update(
                quantity=F("quantity") + quantity
            )

    else:
        guest_cart = request.session.get("guest_cart", {})

        current_quantity = int(
            guest_cart.get(str(product_id), 0)
        )

        guest_cart[str(product_id)] = (
            current_quantity + quantity
        )

        request.session["guest_cart"] = guest_cart
        request.session.modified = True

    return JsonResponse({
        "success": True,
        **build_cart_payload(request),
    })


# UPDATE CART QUANTITY

@require_POST
def cart_update(request):
    data = get_request_data(request)

    try:
        product_id = int(data.get("product_id"))
        quantity = int(data.get("quantity"))
    except (ValueError, TypeError):
        return JsonResponse(
            {"error": "Invalid product or quantity."},
            status=400,
        )

    if quantity < 1:
        return JsonResponse(
            {"error": "Quantity must be at least 1."},
            status=400,
        )

    if request.user.is_authenticated:

        updated = CartItem.objects.filter(
            user=request.user,
            product_id=product_id,
        ).update(quantity=quantity)

        if not updated:
            return JsonResponse(
                {"error": "Cart item not found."},
                status=404,
            )

    else:
        guest_cart = request.session.get("guest_cart", {})

        if str(product_id) not in guest_cart:
            return JsonResponse(
                {"error": "Cart item not found."},
                status=404,
            )

        guest_cart[str(product_id)] = quantity

        request.session["guest_cart"] = guest_cart
        request.session.modified = True

    return JsonResponse({
        "success": True,
        **build_cart_payload(request),
    })


# REMOVE PRODUCT FROM CART

@require_POST
def cart_remove(request):
    data = get_request_data(request)

    try:
        product_id = int(data.get("product_id"))
    except (ValueError, TypeError):
        return JsonResponse(
            {"error": "Invalid product."},
            status=400,
        )

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

    return JsonResponse({
        "success": True,
        **build_cart_payload(request),
    })


# MERGE GUEST CART INTO USER ACCOUNT

def merge_guest_cart(request, user):
    """
    Transfers guest cart products into the logged-in
    user's database cart.

    If a product already exists in the account cart,
    its quantity is increased.
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

            product = Product.objects.filter(
                id=product_id
            ).first()

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
                ).update(
                    quantity=F("quantity") + quantity
                )

    # Remove the guest cart after merging.
    request.session.pop("guest_cart", None)


# GEMINI AI CHATBOT

@require_POST
def chatbot(request):
    user_message = request.POST.get("message", "").strip()

    if not user_message:
        return JsonResponse(
            {"reply": "Please enter a question."},
            status=400,
        )

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
                form.add_error(
                    None,
                    "Email address is required."
                )

            else:
                user = form.save()

                user.email = email
                user.save()

                login(request, user)

                # Merge the guest cart into the new account.
                merge_guest_cart(request, user)

                messages.success(
                    request,
                    "Account created successfully. Welcome to LuminaTech!"
                )

                return redirect("home-page")

    else:
        form = UserCreationForm()

    return render(
        request,
        "shop/signup.html",
        {"form": form},
    )



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

            # Merge the guest cart into the existing account.
            merge_guest_cart(request, user)

            messages.success(
                request,
                "You are now logged in."
            )

            return redirect("home-page")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "shop/login.html",
    )


# LOGOUT

def logout_view(request):
    if request.method == "POST":
        logout(request)

    return redirect("home-page")
