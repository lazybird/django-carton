from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

from .models import Cart, CartItem
from . import serializers as cart_serializers


class CartItemViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing shopping cart items.
    """
    lookup_field = 'product_id'

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return cart_serializers.CartItemUpdateSerializer
        if self.action in ['add']:
            return cart_serializers.CartItemAddSerializer
        if self.action in ['create']:
            return cart_serializers.CartItemCreateSerializer
        return cart_serializers.CartItemSerializer

    def get_cart(self):
        session_key = self.request.session.session_key
        if self.request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.request.user)
            cart.session_key = session_key
            cart.save()
        else:
            cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart

    @property
    def cart(self):
        return self.get_cart()

    def get_queryset(self):
        return self.cart.items.all()

    def get_price(self, product_id):
        # TODO: how to get the price
        return 100.00

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data.get('product')
        try:
            cart_item = self.cart.items.get(product_id=product.id)
        except CartItem.DoesNotExist:
            cart_item = None
        quantity_to_add = serializer.validated_data['quantity']
        if cart_item:
            cart_item.quantity = quantity_to_add
            cart_item.save()
            return Response(serializer.data)
        else:
            price = self.get_price(product_id=product.id)
            self.cart.items.create(product_id=product.id, quantity=quantity_to_add, price=price)
        return self.retrieve(request, product_id=product.id, *args, **kwargs)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['post'], detail=True)
    def add(self, request, product_id=None, *args, **kwargs):
        """
        Add a cart item if it does not exist.
        Sum-up the the item is already there.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            cart_item = self.cart.items.get(product_id=product_id)
        except CartItem.DoesNotExist:
            cart_item = None
        quantity_to_add = serializer.validated_data['quantity']
        if cart_item:
            serializer.data['quantity'] = cart_item.quantity + quantity_to_add
            cart_item.quantity = cart_item.quantity + quantity_to_add
            cart_item.save()
        else:
            price = self.get_price(product_id=product_id)
            self.cart.items.create(product_id=product_id, quantity=quantity_to_add, price=price)
        return self.retrieve(request, product_id=product_id, *args, **kwargs)
