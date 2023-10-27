from django.http import Http404
import stripe
import uuid
from django_countries import countries
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
import logging
from helper.utils import get_timezone_datetime, designer_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from core.models import User
from rest_framework.generics import RetrieveAPIView, ListAPIView
from helper.utils import CustomPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_200_OK

from notification.models import Notification
from .serializers import (
    LineItemIndexSerializer,
    MyLineItemIndexSerializer,
    ProductSerializer,
    OrderSerializer,
    ProductDetailSerializer,
    AddressSerializer,
    CreditCardSerializer,
    BankSerializer,
    PaymentSerializer,
    RefundSerializer,
    ReviewSerializer,
)
from product.models import (
    ORDER_TRACKING_CHOICES,
    LineItem,
    Product,
    OrderProduct,
    Order,
    Address,
    Payment,
    Coupon,
    ProductImage,
    Bank,
    CreditCard,
    Refunds,
    Review,
)
from rave_python import Rave
from decouple import config


log = logging.getLogger(__name__)
RAVE_PUBLIC_KEY = config("RAVE_PUBLIC_KEY")
RAVE_SECRET_KEY = config("RAVE_SECRET_KEY")
rave = Rave(RAVE_PUBLIC_KEY, RAVE_SECRET_KEY, usingEnv=False)


class MarketFeedView(ListAPIView):
    serializer_class = ProductDetailSerializer
    pagination_class = CustomPagination  # Use the custom pagination class
    permission_classes = [IsAuthenticated]

    def list(self, request, category="All", *args, **kwargs):
        if category == "All" or category == "":
            queryset = Product.objects.all()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
            else:
                serializer = self.get_serializer(queryset, many=True)

        else:
            queryset = Product.objects.filter(category=category)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
            else:
                serializer = self.get_serializer(queryset, many=True)

        category_data = {
            "category": category,
            "product": serializer.data,
        }

        response_data = {
            "status": True,
            "message": "Products fetched successfully",
            "categoryData": category_data,
        }
        return self.get_paginated_response(response_data)


class RefundTransactions(object):
    def __init__(self, charge_id, refund_id=""):
        self.charge_id = charge_id
        self.refund_id = refund_id

    def create_refund(self):
        response = stripe.Refund.create(
            charge=self.charge_id,
        )
        return response

    def retrieve_refund(self):
        response = stripe.Refund.retrieve(
            self.refund_id,
        )
        return response

    def update_refund(self, metadata):
        response = stripe.Refund.modify(
            self.refund_id,
            metadata=metadata,
        )
        return response

    def cancel_refund(self):
        response = stripe.Refund.cancel(
            self.refund_id,
        )
        return response

    def list_refunds(self, q, data_obj, singlecharge, limit, source="local_db"):
        if singlecharge:
            if source == "stripe":
                response = stripe.Refund.list(charge=self.charge_id, limit=limit)
                return response
            elif source == "local_db":
                if type(int(q)) == int:
                    if data_obj == "":
                        refunds = Refunds.objects.filter(customer=q)
                        serializer = RefundSerializer(refunds, many=True)
                    else:
                        refunds = Refunds.objects.filter(
                            customer=q,
                            amount=data_obj.amount,
                            currency=data_obj.currency,
                            status=data_obj.status,
                            created_at__range=[data_obj.start_date, data_obj.end_date],
                        )
                        serializer = RefundSerializer(refunds, many=True)
                return serializer.data
        else:
            if source == "stripe":
                if q == "":
                    response = stripe.Refund.list(limit=limit)
                    return response

            if source == "local_db":
                if q == "":
                    refunds = Refunds.objects.all()[:limit]
                    serializer = RefundSerializer(refunds, many=True)
                    return serializer.data


class UserIDView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"userID": request.user.id}, status=HTTP_200_OK)


class ProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Deserialize the request data
        user = request.user
        data = request.POST
        serializer = ProductSerializer(data=data)
        images = request.FILES.getlist("images")

        # Validate the data
        if serializer.is_valid():
            product = serializer.save(owner=user)
            # Save each image associated with the product
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            # Save the product to the database

            return Response(
                {"status": True, "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": False, "error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, pk, format=None):
        # Retrieve the product instance from the database
        product = get_object_or_404(Product, pk=pk)

        # Deserialize the request data and specify the instance to update
        serializer = ProductSerializer(product, data=request.data, partial=True)

        # Validate and save the updated product
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        # Retrieve the product instance from the database
        product = get_object_or_404(Product, pk=pk)

        # Delete the product
        product.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    pagination_class = CustomPagination  # Use the custom pagination class

    def list(self, request, pk, *args, **kwargs):
        queryset = Review.objects.filter(id=pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)
        response_data = {
            "status": True,
            "message": "Reviws fetched successfully",
            "reviews": serializer.data,
        }
        return self.get_paginated_response(response_data)


class ReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        data = request.data
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user)

            return Response(
                {"status": True, "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": False, "error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    

class RatingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        reviews = Review.objects.filter(product__owner_id=id)
        num_reviews = len(reviews)

        if num_reviews == 0:
            avg_rating = 0  # Return 0 if there are no reviews
        else:
            total_rating = sum([review.rating for review in reviews])
            avg_rating = total_rating / num_reviews

        return Response(
            {"status": True, "rating":avg_rating},
            status=status.HTTP_201_CREATED,
        )


# @method_decorator(designer_required, name='dispatch')
class UserProdctsView(ListAPIView):
    serializer_class = ProductDetailSerializer
    pagination_class = CustomPagination  # Use the custom pagination class
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = Product.objects.filter(owner=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "status": True,
            "message": "Products fetched successfully",
            "data": serializer.data,
        }

        return self.get_paginated_response(response_data)


class ProductListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        q = request.GET.get("category")
        prod = Product.objects.filter(category=q)
        serializer = ProductSerializer(prod, many=True)
        return Response({"status": True, "data": serializer.data})


class ProductDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()


class BankView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.user).first()
        data = request.data
        serializer = BankSerializer(data=data)

        if serializer.is_valid():
            serializer.save(user=user)

            return Response(
                {"status": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_200_OK,
            )

    def get(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.user).first()
        bank = get_object_or_404(Bank, user=user)
        serializer = BankSerializer(bank)
        return Response(
            {"status": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.user).first()
        data = request.data
        bank = get_object_or_404(Bank, user=user)
        serializer = BankSerializer(data=data, partial=True)
        if serializer.is_valid():
            serializer.instance = bank
            serializer.save()

            return Response(
                {"status": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )

    def delete(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.user).first()
        bank = get_object_or_404(Bank, user=user)
        bank.delete()
        return Response(
            {"status": True, "message": "Data has been deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


class CreditcardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.user).first()
        data = request.data
        serializer = CreditCardSerializer(data=data)

        if serializer.is_valid():
            serializer.save(user=user)

            return Response(
                {"status": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_200_OK,
            )

    def get(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.user).first()
        crd = get_object_or_404(CreditCard, user=user)
        serializer = CreditCardSerializer(crd)
        return Response(
            {"status": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.user).first()
        data = request.data
        crd = get_object_or_404(CreditCard, user=user)
        serializer = CreditCardSerializer(data=data, partial=True)
        if serializer.is_valid():
            serializer.instance = crd
            serializer.save()

            return Response(
                {"status": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )

    def delete(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.user).first()
        crd = get_object_or_404(CreditCard, user=user)
        crd.delete()
        return Response(
            {"status": True, "message": "Data has been deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


class OrderQuantityUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.user).first()
        slug = request.data.get("slug", None)
        if slug is None:
            return Response({"message": "Invalid data"}, status=HTTP_200_OK)

        product = get_object_or_404(Product, slug=slug)
        order_qs = Order.objects.filter(user=user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order product is in the order
            if order.products.filter(product__slug=product.slug).exists():
                order_product = OrderProduct.objects.filter(
                    product=product, user=user, ordered=False
                )[0]
                if order_product.quantity > 1:
                    order_product.quantity -= 1
                    order_product.save()
                else:
                    order.products.remove(order_product)
                return Response(status=HTTP_200_OK)
            else:
                return Response(
                    {"message": "This item was not in your cart"},
                    status=HTTP_200_OK,
                )
        else:
            return Response(
                {"message": "You do not have an active order"},
                status=HTTP_200_OK,
            )


class OrderItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        prod = OrderProduct.objects.get(pk=pk)
        prod.delete()
        return Response(
            {"status": True, "message": "Product has been removed"},
            status=status.HTTP_204_NO_CONTENT,
        )


# class AddToCartView(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, request, slug, *args, **kwargs):

#         user = User.objects.filter(email=request.user).first()
#         #slug = request.data.get("slug", None)
#         variations = request.data.get("variations", [])
#         qty = request.data.get("quantity", 1)
#         if slug is None:
#             return Response({"status":False,
#                              "message": "Invalid request"},
#                              status=HTTP_200_OK)

#         product = get_object_or_404(Product, slug=slug)

#         minimum_variation_count = Variation.objects.filter(product=product).count()
#         if len(variations) < minimum_variation_count:
#             return Response(
#                 {"status":False,
#                  "message": "Please specify the required variation types"},
#                 status=HTTP_200_OK,
#             )

#         order_product_qs = OrderProduct.objects.filter(
#             product=product, user=user, ordered=False
#         )
#         for v in variations:
#             order_product_qs = order_product_qs.filter(
#                 Q(product_variations__exact=v)
#             )

#         if order_product_qs.exists():
#             order_product = order_product_qs.first()
#             order_product.quantity = qty
#             order_product.save()
#         else:
#             order_product = OrderProduct.objects.create(
#                 product=product, user=user, ordered=False
#             )
#             order_product.product_variations.add(*variations)
#             order_product.quantity = qty
#             order_product.save()

#         order_qs = Order.objects.filter(user=user, ordered=False)
#         if order_qs.exists():
#             order = order_qs[0]
#             if order.products.filter(product__id=order_product.product.id).exists():
#                 order.products.remove(order_product)
#                 order.save()
#                 return Response(
#                     {"status": True, "message": "Product removed from cart"},
#                     status=HTTP_200_OK,
#                 )
#             else:
#                 order.products.add(order_product)
#                 order.save()
#                 return Response(
#                     {"status": True, "message": "Product added from cart"},
#                     status=HTTP_200_OK,
#                 )

#         else:
#             ordered_date = timezone.now()
#             order = Order.objects.create(user=user, ordered_date=ordered_date)
#             order.products.add(order_product)
#             order.save()
#             return Response(
#                 {"status": True, "message": "Product added to cart"},
#                 status=HTTP_200_OK,
#             )


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug, *args, **kwargs):
        user = User.objects.filter(email=request.user).first()

        # Get variations and quantity from the request data
        variations = request.data.get("variations", [])
        qty = request.data.get("quantity", 1)

        if slug is None:
            return Response(
                {"status": False, "message": "Invalid request"},
                status=HTTP_200_OK,
            )

        product = get_object_or_404(Product, slug=slug)

        if not variations:
            # If no variations are specified, treat it as if there are no variations
            order_product_qs = OrderProduct.objects.filter(
                product=product,
                user=user,
                ordered=False,
            )
        else:
            order_product_qs = OrderProduct.objects.filter(
                product=product, user=user, ordered=False
            )

            # Filter by specified variations if any
            for v in variations:
                order_product_qs = order_product_qs.filter(
                    Q(product_variations__exact=v)
                )

        if order_product_qs.exists():
            order_product = order_product_qs.first()
            order_product.quantity = qty
            order_product.save()
        else:
            order_product = OrderProduct.objects.create(
                product=product, user=user, ordered=False
            )
            if variations:
                order_product.product_variations.add(*variations)
            order_product.quantity = qty
            order_product.save()

        order_qs = Order.objects.filter(user=user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.products.filter(product__id=order_product.product.id).exists():
                order.products.remove(order_product)
                order.save()
                return Response(
                    {"status": True, "message": "Product removed from cart"},
                    status=HTTP_200_OK,
                )
            else:
                order.products.add(order_product)
                order.save()
                return Response(
                    {"status": True, "message": "Product added to cart"},
                    status=HTTP_200_OK,
                )
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(user=user, ordered_date=ordered_date)
            order.products.add(order_product)
            order.save()
            return Response(
                {"status": True, "message": "Product added to cart"},
                status=HTTP_200_OK,
            )


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return order
        except ObjectDoesNotExist:
            raise Http404("You do not have an active order")


class OrdersView(ListAPIView):
    serializer_class = LineItemIndexSerializer
    pagination_class = CustomPagination  # Use the custom pagination class
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        status = self.request.GET.get("status")
        user = self.request.user

        if status is not None:
            queryset = LineItem.objects.select_related("order").filter(
                order__user=user, order_status=status.capitalize()
            )
        else:
            queryset = LineItem.objects.select_related("order").filter(
                order__user=user
            )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({"order_items": serializer.data})

        serializer = self.get_serializer(queryset, many=True)
        return Response({"order_items": serializer.data})


class UpdateOrderStatusView(APIView):
    def put(self, request, id):
        try:
            line_item = LineItem.objects.get(id=id)
        except LineItem.DoesNotExist:
            return Response(
                {"error": {"status": False, "message": "Order not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )

        new_order_status = request.data.get("order_status")

        if new_order_status in [choice[0] for choice in ORDER_TRACKING_CHOICES]:
            line_item.order_status = new_order_status
            line_item.save()
            serializer = LineItemIndexSerializer(line_item)
            return Response(
                {"status": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": {"status": False, "message": "Invalid order status"}},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MyOrdersView(ListAPIView):
    serializer_class = MyLineItemIndexSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        status = self.request.GET.get("status")
        user = self.request.user

        if status is not None:
            queryset = LineItem.objects.filter(
                seller=user, order_status=status.capitalize()
            )
        else:
            queryset = LineItem.objects.select_related("order").filter(
                seller=user
            )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response({"order_items": serializer.data})

        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response({"order_items": serializer.data})


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.user).first()
        order = Order.objects.filter(user=user, ordered=False)
        if order.exists():
            serializer = OrderSerializer(order.first())
            return Response(
                {"status": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {"status": False, "message": "You do not have an active order"},
                status=status.HTTP_200_OK,
            )


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.user).first()
        order = Order.objects.get(user=user, ordered=False)
        token = request.data.get("stripeToken")
        billing_address_id = request.data.get("selectedBillingAddress")
        shipping_address_id = request.data.get("selectedShippingAddress")

        billing_address = Address.objects.get(id=billing_address_id)
        shipping_address = Address.objects.get(id=shipping_address_id)
        time_sent = get_timezone_datetime()

        if user.stripe_customer_id != "" and user.stripe_customer_id is not None:
            customer = stripe.Customer.retrieve(user.stripe_customer_id)
            customer.sources.create(source=token)

        else:
            customer = stripe.Customer.create(
                email=user.email,
            )
            customer.sources.create(source=token)
            user.stripe_customer_id = customer["id"]
            user.one_click_purchasing = True
            user.save()

        amount = int(order.get_total() * 100)

        try:
            # charge the customer because we cannot charge the token more than once
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                customer=user.stripe_customer_id,
            )
            time_arrived = get_timezone_datetime()
            time_range = [time_sent, time_arrived]
            # charge once off on the token
            # charge = stripe.Charge.create(
            #     amount=amount,  # cents
            #     currency="usd",
            #     source=token
            # )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge["id"]
            payment.user = user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order
            order_products = order.items.all()
            order_products.update(ordered=True)
            for item in order_products:
                item.save()

            order.ordered = True
            order.payment = payment
            order.billing_address = billing_address
            order.shipping_address = shipping_address
            order.ref_code = str(uuid.uuid4().hex)[:10].upper()
            order_number = order.save()
            order.set_line_items_from_cart(order, order_number, user)
            order.set_transaction(user, charge, time_range)

            return Response(
                {"status": True, "message": "Payment Succesful"}, status=HTTP_200_OK
            )

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get("error", {})
            return Response(
                {"status": False, "message": f"{err.get('message')}"},
                status=HTTP_200_OK,
            )

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            # messages.warning(self.request, "Rate limit error")
            return Response(
                {"status": False, "message": "Rate limit error"}, status=HTTP_200_OK
            )

        except stripe.error.InvalidRequestError as e:
            # print(e)
            # Invalid parameters were supplied to Stripe's API
            return Response(
                {"status": False, "message": "Invalid parameters"}, status=HTTP_200_OK
            )

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return Response(
                {"status": False, "message": "Not authenticated"}, status=HTTP_200_OK
            )

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            return Response(
                {"status": False, "message": "Network error"}, status=HTTP_200_OK
            )

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong. You were not charged. Please try again.",
                },
                status=HTTP_200_OK,
            )

        except Exception as e:
            # send an email to ourselves
            return Response(
                {
                    "status": False,
                    "message": "A serious error occurred. We have been notifed.",
                },
                status=HTTP_200_OK,
            )


class OrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tracking_number):
        # cart = OrderProduct.objects.filter(
        #     user=request.user,
        #     ordered=True,
        # )
        order_item = (
            LineItem.objects
            .filter(tracking_number=tracking_number)
            .first()
        )
        if order_item != None:
            context = {
                "page_title": "Order Item #" + str(order_item.id) + " Status",
                "order_status": order_item.order_status,
            }
            return Response({"data": context, "status": True})
        else:
            return Response({"message": "Invalid tracking_number", "status": False})


class Checkout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.user).first()
        orders = Order.objects.filter(user=user, ordered=False)
        if not orders:
            return Response(
                {"status": False, "message": "Your cart is empty"},
                status=HTTP_200_OK,
            )
        order = orders.first()
        payment_method = request.data.get(
            "payment_method"
        )  # New parameter for payment method
        # billing_address_id = request.data.get("BillingAddress")
        # shipping_address_id = request.data.get("ShippingAddress")
        # billing_address = Address.objects.get(id=billing_address_id)
        # shipping_address = Address.objects.get(id=shipping_address_id)
        time_sent = get_timezone_datetime()

        # Check the selected payment method
        if payment_method == "flutterwave":
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[-1].strip()
            else:
                ip = request.META.get("REMOTE_ADDR")

            amount = str(order.get_total())
            data = request.data

            payload = {
                "cardno": data.get("card_number"),
                "cvv": data.get("cvv"),
                "expirymonth": data.get("exp_month"),
                "expiryyear": data.get("exp_year"),
                "amount": amount,
                "email": user.email,
                "phonenumber": user.phone,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "IP": ip,
                "pin": data.get("pin"),
                "currency": data.get("currency"),
            }

            try:
                charge = rave.Card.charge(payload)
                time_arrived = get_timezone_datetime()
                time_range = [time_sent, time_arrived]

                payment = Payment()
                payment.txfre = charge["txRef"]
                payment.user = user
                payment.amount = order.get_total()
                payment.save()

                order_products = order.items.all()
                order_products.update(ordered=True)
                for item in order_products:
                    item.save()

                order.ordered = True
                order.payment = payment
                # order.billing_address = billing_address
                # order.shipping_address = shipping_address
                order.ref_code = str(uuid.uuid4().hex)[:10].upper()
                order_number = order.save()
                order.set_line_items_from_cart(order, order_number, user)
                order.set_transaction(payment_method, user, charge, time_range)

                #     notify = Notification.objects.create(
                #     notification_type="NO",
                #     comments=f"@{user.firstname} liked your post",
                #     to_user=post.owner,
                #     from_user=user,
                # )
                #     notify.save()

                return Response(
                    {"status": True, "message": "Payment Successful"},
                    status=HTTP_200_OK,
                )

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get("error", {})
                return Response(
                    {"status": False, "message": f"{err.get('message')}"},
                    status=HTTP_200_OK,
                )

        elif payment_method == "pay_on_delivery":  # Handle Pay on Delivery
            
            order_products = order.products.all()
            time_arrived = get_timezone_datetime()
            time_range = [time_sent, time_arrived]

            # # order.payment = payment
            # order.billing_address = billing_address
            # order.shipping_address = shipping_address
            order.ref_code = str(uuid.uuid4().hex)[:10].upper()
            order_number = order.generate_number()
            order.set_line_items_from_cart(order, order_number, user)
            order.set_transaction(payment_method, user, time_range)
            order.ordered = True
            for item in order_products:
                to_user = User.objects.filter(email=item.product.owner.email).first()
                order.notify_owner(from_user=user, to_user=to_user)
            order.save()

            return Response(
                {"status": True, "message": "Order placed with Pay on Delivery"},
                status=HTTP_200_OK,
            )

        else:
            return Response(
                {"status": False, "message": "Invalid payment method selected"},
                status=HTTP_200_OK,
            )


class AddCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.user).first()
        code = request.data.get("code", None)
        if code is None:
            return Response(
                {"status": False, "message": "Invalid data received"},
                status=HTTP_200_OK,
            )
        order = Order.objects.get(user=user, ordered=False)
        coupon = get_object_or_404(Coupon, code=code)
        order.coupon = coupon
        order.save()
        return Response({"status": True, "message": "Coupon added"}, status=HTTP_200_OK)


class CountryListView(APIView):
    def get(self, request):
        return Response(countries, status=HTTP_200_OK)


class AddressListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        address_type = request.query_params.get("address_type", None)
        user = User.objects.filter(email=request.user).first()
        address = Address.objects.filter(user=user, address_type=address_type)
        serializer = AddressSerializer(address, many=True)

        return Response(
            {
                "status": True,
                "message": "Address Feteched Successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class AddressCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = User.objects.filter(email=request.user).first()
        data = request.data
        serializer = AddressSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user)

            return Response(
                {
                    "status": True,
                    "message": "Address Feteched Successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_200_OK,
            )


class AddressUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        data = request.data
        address = get_object_or_404(Address, pk=pk)
        serializer = AddressSerializer(data=data, partial=True)

        if serializer.is_valid():
            serializer.instance = address
            serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "Address Updated Successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": serializer.errors},
                status=status.HTTP_200_OK,
            )


class AddressDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        prod = Address.objects.get(pk=pk)
        prod.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentListView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = User.objects.filter(email=request.user).first()
        p = Payment.objects.filter(user=user)
        serializer = PaymentSerializer(p, many=True)
        return Response(
            {
                "status": True,
                "message": "Payments Feteched Successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class MyProducts(ListAPIView):
    serializer_class = ProductDetailSerializer
    pagination_class = CustomPagination  # Use the custom pagination class
    permission_classes = [IsAuthenticated]

    def list(self, request, id, *args, **kwargs):
        queryset = Product.objects.filter(owner__id=id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "status": True,
            "message": "Products fetched successfully",
            "products": serializer.data,
        }
        return self.get_paginated_response(response_data)


class CatalogueView(ListAPIView):
    serializer_class = ProductDetailSerializer
    pagination_class = CustomPagination  # Use the custom pagination class
    permission_classes = [IsAuthenticated]

    def list(self, request, category="All", *args, **kwargs):
        if category == "All" or category == "":
            queryset = Product.objects.all()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
            else:
                serializer = self.get_serializer(queryset, many=True)

        else:
            queryset = Product.objects.filter(category=category)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
            else:
                serializer = self.get_serializer(queryset, many=True)

        category_data = {
            "category": category,
            "product": serializer.data,
        }

        response_data = {
            "status": True,
            "message": "Products fetched successfully",
            "categoryData": category_data,
        }
        return self.get_paginated_response(response_data)
