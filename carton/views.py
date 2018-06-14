from rest_framework import viewsets
from rest_framework.decorators import action


from .models import Cart, CartItem
from .serializers import CartItemSerializer


class CartItemViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing shopping cart items.
    """
    serializer_class = CartItemSerializer
    lookup_field = 'product__pk'

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

    def get_price(self, product):
        # TODO: how to get the price
        return product.price or 100.00

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        price = self.get_price(product)
        serializer.save(cart=self.cart, price=price)

    @action(methods=['post'], detail=True)
    def add(self, request, pk=None, *args, **kwargs):
        """
        Add a cart item if it does not exist.
        Sum-up the the item is already there.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        try:
            cart_item = self.cart.items.get(product=product)
        except CartItem.DoesNotExist:
            cart_item = None
        if cart_item:
            quantity_to_add = serializer.validated_data['quantity']
            serializer.data['quantity'] = cart_item.quantity + quantity_to_add
            cart_item.quantity = cart_item.quantity + quantity_to_add
            cart_item.save()
            return self.retrieve(request, pk=pk, *args, **kwargs)
        else:
            return self.create(request, *args, **kwargs)
