from django.conf import settings
from django.utils.module_loading import import_by_path


def get_product_model():
    """
    Returns the product model that is used by this cart.
    """
    return import_by_path(settings.CART_PRODUCT_MODEL)
