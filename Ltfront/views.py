from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
import json
import os
from django.http import JsonResponse
from google import genai
from google.genai import types
from .models import Product
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect,get_object_or_404


def home(request):
    """Render the LuminaTech electronics storefront."""
    products = Product.objects.all()
    categories = [label for _, label in Product.CATEGORY_CHOICES]

    return render(
        request,
        "shop/home.html",
        {
            "products": products,
            "categories": categories,
        },
    )
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "shop/product_detail.html", {"product": product})

def about(request):
    return render(request, "shop/about.html")


def contact(request):
    return render(request, "shop/contact.html")

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

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home-page")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
    
        if form.is_valid():
            user = form.save()

            # Log the user in immediately after registration
            login(request, user)

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
        {
            "form": form,
        },
    )


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

                return redirect("home-page")

    else:
        form = UserCreationForm()

    return render(
        request,
        "shop/signup.html",
        {
            "form": form,
        },
    )

def logout_view(request):
    if request.method == "POST":
        logout(request)

    return redirect("home-page")