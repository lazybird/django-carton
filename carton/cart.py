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

    def to_dict(self):
        return {
            'product_pk': self.product.pk,
            'quantity': self.quantity,
            'price': self.price,
        }

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
        Removes stale items - they are associated with a product that's no longer
        referenced in the database.
        """
        if not self.products:
            return None
        ids_in_cart = set([product.pk for product in self.products])
        # We retrieve the model class based on the first instance,
        # assuming all products in the cart are of the same model.
        model_class = type(self.products[0])
        ids_in_database = set(model_class.objects.filter(
            pk__in=ids_in_cart).values_list('pk', flat=True))
        removed_product_ids = ids_in_cart - ids_in_database
        for product_pk in removed_product_ids:
            del self._items_dict[product_pk]

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
    def items_serializable(self):
        """
        The list of items formatted for serialization.
        """
        return [item.to_dict() for item in self.items]

    @property
    def count(self):
        """
        The number of items in cart, that's the sum of quantities.
        """
        return sum([item.quantity for item in self.items])

    @property
    def unique_count(self):
        """
        The number of unique items in cart, regardless of the quantity.
        """
        return len(self._items_dict)

    @property
    def is_empty(self):
        return self.unique_count == 0

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
