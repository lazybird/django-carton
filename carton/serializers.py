from rest_framework import serializers

from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ('product', 'quantity', 'price')
        read_only_fields = ('price',)
