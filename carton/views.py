from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from .models import Cart, CartItem
from . import serializers as cart_serializers


class CartViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """
    A viewset for managing shopping cart items.
    """

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update', 'add']:
            return cart_serializers.CartWriteSerializer
        return cart_serializers.CartSerializer

    def get_cart(self):
        session_key = self.request.session.session_key
        session_key = 'q1p4f04pg4i36d47mubkr85hotm8dgi2'
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

    def get_object(self):
        queryset = self.get_queryset()
        pk = self.kwargs.get('pk')
        return get_object_or_404(queryset, product_id=pk)

    def get_or_create_item(self, product_id):
        """
        Get the cart item for the given product id.
        If does not exist, create one.
        """
        queryset = self.get_queryset()
        try:
            cart_item = queryset.get(product_id=product_id)
        except CartItem.DoesNotExist:
            price = self.get_price(product_id=product_id)
            try:
                cart_item = self.cart.items.create(
                    product_id=product_id,
                    quantity=0,
                    price=price
                )
            except IntegrityError as e:
                raise ValidationError({'detail': e})
        return cart_item

    def list(self, request, *args, **kwargs):
        """
        Get the list of cart items.
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve single items given the product ID.
        """
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Removes the cart item given the product ID.
        """
        return super().destroy(request, *args, **kwargs)

    @action(methods=['post'], detail=True)
    def add(self, request, *args, **kwargs):
        """
        Add a cart item if it does not exist.
        Addup the quantity if the item is already there.
        """
        pk = self.kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity_to_add = serializer.validated_data['quantity']
        cart_item = self.get_or_create_item(product_id=pk)
        cart_item.quantity = cart_item.quantity + quantity_to_add
        cart_item.save()
        return self.retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Set the quantity if the product exist.
        Add the product is it does not exist.
        """
        pk = self.kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart_item = self.get_or_create_item(product_id=pk)
        cart_item.quantity = serializer.validated_data['quantity']
        cart_item.save()
        return self.retrieve(request, *args, **kwargs)
