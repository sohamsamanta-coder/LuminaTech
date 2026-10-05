from django.contrib import admin

from .models import Product, ProductSpecification


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 5
    ordering = ("order",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price")
    list_filter = ("category",)
    search_fields = ("name", "category")
    inlines = [ProductSpecificationInline]