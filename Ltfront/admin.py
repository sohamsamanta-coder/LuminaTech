
from django.contrib import admin

from .models import (
    Product,
    ProductSpecification,
    Order,
    OrderItem,
)


# ================= PRODUCT ADMIN =================

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


# ================= ORDER ITEM INLINE =================

class OrderItemInline(admin.TabularInline):
    model = OrderItem

    extra = 0
    can_delete = False

    fields = (
        "product",
        "product_name",
        "unit_price",
        "quantity",
        "line_total",
    )

    readonly_fields = (
        "product",
        "product_name",
        "unit_price",
        "quantity",
        "line_total",
    )

    max_num = 0


# ================= ORDER ADMIN =================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    # Order list columns
    list_display = (
        "order_number",
        "full_name",
        "email",
        "total",
        "payment_method",
        "payment_status",
        "status",
        "created_at",
    )

    # Filters on the right side
    list_filter = (
        "status",
        "payment_status",
        "payment_method",
        "created_at",
    )

    # Search functionality
    search_fields = (
        "order_number",
        "full_name",
        "email",
        "phone",
    )

    # Allow changing order status directly from the list.
    list_editable = ("status",)

    # Date navigation
    date_hierarchy = "created_at"

    ordering = ("-created_at",)

    list_per_page = 25

    # Display purchased products inside each order.
    inlines = [OrderItemInline]

    # Customer and payment information should not
    # accidentally be modified by the administrator.
    readonly_fields = (
        "order_number",
        "user",
        "full_name",
        "email",
        "phone",
        "address_line1",
        "address_line2",
        "city",
        "state",
        "pincode",
        "subtotal",
        "delivery_fee",
        "discount",
        "total",
        "payment_method",
        "payment_status",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Order Information",
            {
                "fields": (
                    "order_number",
                    "user",
                    "status",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            "Customer Information",
            {
                "fields": (
                    "full_name",
                    "email",
                    "phone",
                )
            },
        ),
        (
            "Delivery Address",
            {
                "fields": (
                    "address_line1",
                    "address_line2",
                    "city",
                    "state",
                    "pincode",
                )
            },
        ),
        (
            "Payment and Pricing",
            {
                "fields": (
                    "payment_method",
                    "payment_status",
                    "subtotal",
                    "delivery_fee",
                    "discount",
                    "total",
                )
            },
        ),
    )

    # Orders should be created through the checkout process.
    def has_add_permission(self, request):
        return False

    # Preserve order history.
    def has_delete_permission(self, request, obj=None):
        return False


# ================= ADMIN PANEL CUSTOMIZATION =================

admin.site.site_header = "LuminaTech Administration"
admin.site.site_title = "LuminaTech Admin"
admin.site.index_title = "Store Management Dashboard"
