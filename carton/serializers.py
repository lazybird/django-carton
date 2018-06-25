from rest_framework import serializers

from .models import CartItem


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ('product', 'quantity', 'price')


class CartWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ('product', 'quantity', 'price')
        read_only_fields = ('price', 'product')
