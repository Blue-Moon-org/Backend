from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from core.api.serializers import UserLessInfoSerializer
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
    owner = serializers.ReadOnlyField(source="owner.brand_name")
    images = serializers.SerializerMethodField(method_name="get_images")
    # category = serializers.SerializerMethodField()
    # label = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "price",
            "owner",
            "images",
            "discount_price",
            "category",
            "label",
            "slug",
            "description",
            "timestamp",
        )

    def get_images(self, obj):
        data = ProductImagesSerializer(
            ProductImage.objects.filter(product=obj.id), many=True
        ).data
        return data


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
    # product_variations = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderProduct
        fields = (
            "id",
            "product",
            "product_variations",
            "quantity",
            "dimension",
            "final_price",
        )

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
    # payload_3 = {
    #     "cardno": "4187451811620618",
    #     "cvv": "306",
    #     "expirymonth": "05",
    #     "expiryyear": "25",
    #     "amount": "100",
    #     "email": "korneliosyaovi@gmail.com",
    #     "phonenumber": "08109328188",
    #     "firstname": "Cornelius",
    #     "lastname": "Ashley",
    #     "IP": "355426087298442",
    #     "pin": "7991",
    #     "currency": "NGN"
    #     }

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


class RantingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["rating"]


class ProductDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(method_name="get_user")
    owner = serializers.SerializerMethodField(method_name="get_owner")
    # owner = serializers.ReadOnlyField(source="owner.fullname")
    category = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    variations = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField(method_name="get_images")
    rating = serializers.SerializerMethodField(method_name="get_ratings")
    user_has_carted = serializers.SerializerMethodField(
        method_name="get_user_has_carted"
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "user",
            "owner",
            "title",
            "price",
            "discount_price",
            "category",
            "rating",
            "images",
            "label",
            "slug",
            "description",
            "variations",
            "user_has_carted",
        )

    def get_user(self, obj):
        request = self.context.get("request")
        data = UserLessInfoSerializer(request.user, context={"request": request}).data
        return data

    def get_owner(self, obj):
        request = self.context.get("request")
        data = UserLessInfoSerializer(
            User.objects.filter(id=obj.owner.id).first(), context={"request": request}
        ).data
        return data

    def get_images(self, obj):
        data = ProductImagesSerializer(
            ProductImage.objects.filter(product=obj.id), many=True
        ).data
        return data

    def get_ratings(self, obj):
        reviews = Review.objects.filter(product=obj)
        num_reviews = len(reviews)

        if num_reviews == 0:
            return 0  # Return 0 if there are no reviews
        total_rating = sum([review.rating for review in reviews])
        avg_rating = total_rating / num_reviews
        return avg_rating

    def get_category(self, obj):
        return obj.get_category_display()

    def get_label(self, obj):
        return obj.get_label_display()

    def get_variations(self, obj):
        return VariationSerializer(obj.variation_set.all(), many=True).data

    def get_user_has_carted(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Order.objects.filter(
                user=request.user, ordered=False, products__product_id=obj.id
            ).exists()
        return False


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
    owner = serializers.SerializerMethodField(method_name="get_owner")

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "owner",
            "rating",
            "review",
            "created_at",
            "updated_at",
        ]

    def get_owner(self, obj):
        request = self.context.get("request")
        data = UserLessInfoSerializer(
            User.objects.filter(id=obj.user.id).first(), context={"request": request}
        ).data
        return data


class LineItemProductSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField(method_name="get_reviews")

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "description",
            "price",
            "category",
            "slug",
            "images",
            "reviews",
        )

    def get_reviews(self, obj):
        data = ReviewSerializer(Review.objects.filter(product=obj.id), many=True).data
        return data


class OrderUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "phone", "fullname", "account_type", "address"]


class OrderSellerrSerializer(serializers.ModelSerializer):
    brand_image = serializers.SerializerMethodField(method_name="get_brand_image")
    image = serializers.SerializerMethodField(method_name="get_image")
    class Meta:
        model = User
        fields = [
            "id",
            "fullname",
            "brand_image",
            "image",
            "brand_name",
        ]

    def get_image(self, obj):
        
        return obj.image_url

    def get_brand_image(self, obj):
        
        return obj.brand_image_url

class LineItemIndexSerializer(serializers.ModelSerializer):
    user = OrderUserSerializer(many=False)
    seller = OrderSellerrSerializer(many=False)
    products = OrderProductSerializer(many=True)
    # price = serializers.SerializerMethodField(method_name="get_price")
    # quantity = serializers.SerializerMethodField(method_name="get_quantity")

    class Meta:
        model = LineItem
        fields = [
            "id",
            "order_status",
            "user",
            "seller",
            "order",
            "products",
            "price",
            "tracking_number",
            "quantity",
        ]
    # def get_price(self, obj):
        
    #     return obj.products.all()[0].get_final_price()
    
    # def get_quantity(self, obj):
        
    #     return obj.products.all()[0].quantity


class LineItemStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItem
        fields = [
            "id",
            "order_status",
            "tracking_number",
        ]


class MyLineItemIndexSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True)
    user = OrderSellerrSerializer(many=False)
    seller = OrderSellerrSerializer(many=False)
    # order = OrderSerializer(many=False)

    class Meta:
        model = LineItem
        fields = [
            "id",
            "user",
            "seller",
            "products",
            "tracking_number",
            "quantity",
            "order_status",
        ]

    # def get_order_products(self, obj):
    #     request = self.context.get("request")
    #     if request and request.user.is_authenticated:
    #         return OrderProductSerializer(
    #             obj.order.products.filter(product__owner_id=request.user.id), many=True
    #         ).data
    #     else:
    #         return []
