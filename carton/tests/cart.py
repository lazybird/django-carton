from decimal import Decimal

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
            return self.price
        else:
            return self.price * Decimal(str(
                    1 + (self.quantity - 1) * (1 - self._DISCOUNT)))
