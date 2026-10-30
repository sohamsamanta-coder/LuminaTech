from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home-page"),
    path("product/<int:product_id>/", views.product_detail, name="product-detail"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path("cart/", views.cart, name="cart"),
]
