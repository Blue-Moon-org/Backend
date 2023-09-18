from django.contrib import admin

from .models import (
    Product,
    OrderProduct,
    Order,
    Payment,
    Coupon,
    Refund,
    Address,
    Variation,
    ProductVariation,
)


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = "Update orders to refund granted"


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "ordered",
        "being_delivered",
        "received",
        "refund_requested",
        "refund_granted",
        "shipping_address",
        "billing_address",
        "payment",
        "coupon",
    ]
    list_display_links = [
        "user",
        "shipping_address",
        "billing_address",
        "payment",
        "coupon",
    ]
    list_filter = [
        "ordered",
        "being_delivered",
        "received",
        "refund_requested",
        "refund_granted",
    ]
    search_fields = ["user__username", "ref_code"]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "street_address",
        "apartment_address",
        "country",
        "zip_code",
        "address_type",
        "default",
    ]
    list_filter = ["default", "address_type", "country"]
    search_fields = ["user", "street_address", "apartment_address", "zip_code"]


class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ["variation", "value", "attachment"]
    list_filter = ["variation", "variation__product"]
    search_fields = ["value"]


class ProductVariationInLineAdmin(admin.TabularInline):
    model = ProductVariation
    extra = 1


class VariationAdmin(admin.ModelAdmin):
    list_display = ["product", "name"]
    list_filter = ["product"]
    search_fields = ["name"]
    inlines = [ProductVariationInLineAdmin]


admin.site.register(ProductVariation, ProductVariationAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(Product)
admin.site.register(OrderProduct)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
# admin.site.register(UserProfile)
