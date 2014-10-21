from django.conf import settings
from django.utils.importlib import import_module


def _get_module(dotted_path):
    """
    Returns the entity that is imported from dotted path.
    """
    package, module = settings.CART_PRODUCT_MODEL.rsplit('.', 1)
    return getattr(import_module(package), module)


def get_product_model():
    """
    Returns the product model that is used by this cart.
    """
    return _get_module(settings.CART_PRODUCT_MODEL)


def get_cart_item_class():
    """
    Returns the class that is used by this cart for its items.
    """
    return _get_module(settings.CART_ITEM_CLASS)
