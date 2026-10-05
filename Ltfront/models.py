from django.db import models

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