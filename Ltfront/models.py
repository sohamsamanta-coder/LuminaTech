import uuid
from django.db import models
from django.conf import settings

class Product(models.Model):
    CATEGORY_CHOICES = [
        ("Laptops", "Laptops"),
        ("Smartphones", "Smartphones"),
        ("Headphones", "Headphones"),
        ("Televisions", "Televisions"),
        ("Gaming", "Gaming"),
        ("Accessories", "Accessories"),
    ]

    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.CharField(max_length=255, blank=True)
    uploaded_image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name

class ProductSpecification(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="specifications"
    )
    label = models.CharField(max_length=100)
    value = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.product.name} - {self.label}"


class CartItem(models.Model):

    # The account that owns this cart item
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    # The product being added to the cart
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    # Number of units selected by the customer
    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_cart_product"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.product.name} ({self.quantity})"

# ================= ORDER NUMBER GENERATOR =================

def generate_order_number():
    return f"LT-{uuid.uuid4().hex[:10].upper()}"


# ================= ORDER MODEL =================

class Order(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ("demo_upi", "Demo UPI"),
        ("demo_card", "Demo Card"),
        ("cod", "Cash on Delivery"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("demo_success", "Demo Payment Successful"),
        ("pending", "Payment Pending"),
    ]

    ORDER_STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    order_number = models.CharField(
        max_length=20,
        unique=True,
        default=generate_order_number,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    # Customer information
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # Delivery address
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    # Order pricing
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    # Payment information
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
    )

    # Order tracking
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default="confirmed",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number


# ================= ORDER ITEM MODEL =================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Store product information at the time of purchase
    product_name = models.CharField(max_length=150)

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    quantity = models.PositiveIntegerField()

    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
