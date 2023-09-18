from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from core.models import User
from product.models import (
    LineItem,
    Product,
    Order,
    OrderProduct,
    Coupon,
    ProductImage,
    Review,
    Variation,
    ProductVariation,
    Payment,
    Address,
    CreditCard,
    Bank,
    Refunds,
)

class StringSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ("id", "code", "amount")

class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.fullname")
    # category = serializers.SerializerMethodField()
    # label = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "price",
            "owner",
            "discount_price",
            "category",
            "label",
            "slug",
            "description",
            "timestamp",
        )

    # def get_category(self, obj):
    #     return obj.get_category_display()

    # def get_label(self, obj):
    #     return obj.get_label_display()

class VariationDetailSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = Variation
        fields = ("id", "name", "product")

    def get_product(self, obj):
        return ProductSerializer(obj.product).data

class ProductVariationDetailSerializer(serializers.ModelSerializer):
    variation = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariation
        fields = ("id", "value", "attachment", "variation")

    def get_variation(self, obj):
        return VariationDetailSerializer(obj.variation).data

class OrderProductSerializer(serializers.ModelSerializer):
    product_variations = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderProduct
        fields = ("id", 
                  "product", 
                  "product_variations", 
                  "quantity", 
                  "dimension",
                  "final_price")

    def get_product(self, obj):
        return ProductSerializer(obj.product).data

    def get_product_variations(self, obj):
        return ProductVariationDetailSerializer(
            obj.product_variations.all(), many=True
        ).data

    def get_final_price(self, obj):
        return obj.get_final_price()

class CreditCardSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.nickname")

    class Meta:
        model = CreditCard
        fields = [
            "user",
            "card_number",
            "brand",
            "exp_month",
            "exp_year",
            "cvv",
            "fullname",
        ]

class BankSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.nickname")

    class Meta:
        model = Bank
        fields = ["user", "account_number", "bank", "fullname"]

class OrderSerializer(serializers.ModelSerializer):
    order_products = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    coupon = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("id", "order_products", "total", "coupon")

    def get_order_products(self, obj):
        return OrderProductSerializer(obj.products.all(), many=True).data

    def get_total(self, obj):
        return obj.get_total()

    def get_coupon(self, obj):
        if obj.coupon is not None:
            return CouponSerializer(obj.coupon).data
        return None

class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = ("id", "value", "attachment")

class VariationSerializer(serializers.ModelSerializer):
    product_variations = serializers.SerializerMethodField()

    class Meta:
        model = Variation
        fields = ("id", "name", "product_variations")

    def get_product_variations(self, obj):
        return ProductVariationSerializer(
            obj.productvariation_set.all(), many=True
        ).data

class ProductImagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = ["image"]

class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    variations = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField(method_name="get_images")

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "price",
            "discount_price",
            "category",
            "images",
            "label",
            "slug",
            "description",
            "variations",
        )

    def get_images(self, obj):
        data = ProductImagesSerializer(ProductImage.objects.filter(product=obj.id), many=True).data
        return data
    
    def get_category(self, obj):
        return obj.get_category_display()

    def get_label(self, obj):
        return obj.get_label_display()

    def get_variations(self, obj):
        return VariationSerializer(obj.variation_set.all(), many=True).data

class AddressSerializer(serializers.ModelSerializer):
    country = CountryField()
    user = serializers.ReadOnlyField(source="user.fullname")

    class Meta:
        model = Address
        fields = (
            "id",
            "user",
            "street_address",
            "apartment_address",
            "country",
            "zip_code",
            "address_type",
            "default",
        )

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "amount", "timestamp")

class NewRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refunds
        fields = [
            "customer",
            "refund_id",
            "amount",
            "currency",
            "related_charge",
            "refund_reason",
            "status",
        ]

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refunds
        fields = [
            "id",
            "customer",
            "refund_id",
            "amount",
            "related_charge",
            "refund_reason",
            "status",
            "created_at",
            "updated_at",
        ]

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "user",
            "review",
            "created_at",
            "updated_at",
        ]

class LineItemProductSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField(method_name="get_reviews")

    class Meta:
        model = Product
        fields = ('id', 
                'title', 
                'description',
                'price', 
                'category', 
                'slug', 
                'images', 
                'reviews')
        
    def get_reviews(self, obj):
        data = ReviewSerializer(Review.objects.filter(product=obj.id), many=True).data
        return data

class OrderUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id',
                  'email', 
                  'phone_number', 
                  'fullname', 
                  'user_type',
                  ]

class LineItemIndexSerializer(serializers.ModelSerializer):
    user = OrderUserSerializer(many=False)

    order = OrderSerializer(many=False)
    product = ProductSerializer(many=False)
    class Meta:
        model = LineItem
        fields = ['id', 
                  'user',
                  'order', 
                  'product', 
                  'price',
                  'tracking_number', 
                  'quantity', 
                  'tracking_number', 
                  'order_status',
                  ]