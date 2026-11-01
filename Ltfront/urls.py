
from django.urls import path

from . import views


urlpatterns = [
    # Main pages
    path("", views.home, name="home-page"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    # Product pages
    path(
        "product/<int:product_id>/",
        views.product_detail,
        name="product-detail"
    ),

    # Authentication
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),

    # AI chatbot
    path("chatbot/", views.chatbot, name="chatbot"),

    # Cart page
    path("cart/", views.cart, name="cart"),

    # Cart API
    path("cart/state/", views.cart_state, name="cart-state"),
    path("cart/add/", views.cart_add, name="cart-add"),
    path("cart/update/", views.cart_update, name="cart-update"),
    path("cart/remove/", views.cart_remove, name="cart-remove"),
]
