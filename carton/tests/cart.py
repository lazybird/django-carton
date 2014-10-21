from carton.cart import CartItem


class TestCartItem(CartItem):
    """
    Customized cart item for unit tests.
    """
    _DISCOUNT = 0.2 # 20%

    @property
    def subtotal(self):
        """
        The price for the first item is as earlier, but the price for each next
        entity of the same item in the cart is lowered for some discount.
        """
        if self.quantity == 1:
            return super(TestCartItem, self).subtotal()
        else:
            return self.price + \
                    self.price * self.quantity * (1 - self._DISCOUNT)
