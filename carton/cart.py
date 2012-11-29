from decimal import Decimal

from carton import settings as carton_settings


class CartItem(object):
    """
    A cart item, with the associated product, its quantity and its price.
    """
    def __init__(self, product, quantity, price):
        self.product = product
        self.quantity = int(quantity)
        self.price = Decimal(str(price))

    def __repr__(self):
        return u'CartItem Object (%s)' % self.product

    @property
    def subtotal(self):
        """
        Subtotal for the cart item.
        """
        return self.price * self.quantity


class Cart(object):
    """
    A cart that lives in the session.
    """
    def __init__(self, session, session_key=None):
        self._items_dict = {}
        self.session = session
        session_key = session_key or carton_settings.CART_SESSION_KEY
        # If there is already a cart in session, we extract cart information
        if session_key in self.session:
            self._items_dict = session[session_key]._items_dict
        self.session[session_key] = self
        if carton_settings.CART_REMOVE_STALE_ITEMS:
            self.remove_stale_items()

    def __contains__(self, product):
        """
        Checks if the given product is in the cart.
        """
        return product in self.products

    def remove_stale_items(self):
        """
        Removed stale items. They are associated with a product that's no longer
        referenced in the database.
        """
        for product in self.products:
            if not self.product_exists_in_database(product):
                del self._items_dict[product.pk]

    def product_exists_in_database(self, product):
        """
        Returns True if the given instance exists in the database.
        """
        model_class = type(product)
        return model_class.objects.filter(pk=product.pk).exists()

    def add(self, product, price=None, quantity=1):
        """
        Adds or creates products in cart. For an existing product,
        the quantity is increased and the price is ignored.
        """
        quantity = int(quantity)
        if quantity < 1:
            raise ValueError('Quantity must be at least 1 when adding to cart')
        if product in self.products:
            self._items_dict[product.pk].quantity += quantity
        else:
            if price == None:
                raise ValueError('Missing price when adding to cart')
            self._items_dict[product.pk] = CartItem(product, quantity, price)
        self.session.modified = True

    def remove(self, product):
        """
        Removes the product.
        """
        if product in self.products:
            del self._items_dict[product.pk]
            self.session.modified = True

    def remove_single(self, product):
        """
        Removes a single product by decreasing the quantity.
        """
        if product not in self.products:
            return
        if self._items_dict[product.pk].quantity <= 1:
            # There's only 1 product left so we drop it
            del self._items_dict[product.pk]
        else:
            self._items_dict[product.pk].quantity -= 1
        self.session.modified = True

    def clear(self):
        """
        Removes all items.
        """
        self._items_dict = {}
        self.session.modified = True

    def set_quantity(self, product, quantity):
        """
        Sets the product's quantity.
        """
        if product not in self.products:
            return
        quantity = int(quantity)
        if quantity < 0:
            raise ValueError('Quantity must be positive when updating cart')
        self._items_dict[product.pk].quantity = quantity
        if self._items_dict[product.pk].quantity < 1:
            del self._items_dict[product.pk]
        self.session.modified = True

    @property
    def items(self):
        """
        The list of cart items.
        """
        return self._items_dict.values()

    @property
    def products(self):
        """
        The list of associated products.
        """
        return [item.product for item in self.items]

    @property
    def total(self):
        """
        The total value of all items in the cart.
        """
        return sum([item.subtotal for item in self.items])
