from rest_framework import serializers

from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ('product', 'quantity', 'price')


class CartItemUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ('quantity',)


class CartItemAddSerializer(CartItemUpdateSerializer):

    class Meta:
        model = CartItem
        fields = ('product', 'quantity', 'price')
        read_only_fields = ('product', 'price')


class CartItemCreateSerializer(CartItemUpdateSerializer):

    class Meta:
        model = CartItem
        fields = ('product', 'quantity', 'price')
        read_only_fields = ('price',)
