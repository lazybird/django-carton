import django
from django.conf import settings

if django.VERSION[:2] == (1, 9):
    from importlib import import_module
else:
    from django.utils.importlib import import_module


def get_product_model():
    """
    Returns the product model that is used by this cart.
    """
    package, module = settings.CART_PRODUCT_MODEL.rsplit('.', 1)
    return getattr(import_module(package), module)
