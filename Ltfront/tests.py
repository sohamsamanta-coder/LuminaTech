from django.test import TestCase

from .models import Product


class HomePageTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_product_is_visible_on_home_page(self):
        Product.objects.create(
            name="Test Laptop",
            category="Laptops",
            price="59999.00",
            image="shop/images/laptop.svg",
            description="Test product",
        )

        response = self.client.get("/")

        self.assertContains(response, "Test Laptop")
        self.assertContains(response, "59999")
