from django.core.exceptions import ImproperlyConfigured

from carton import settings as carton_settings


def get_product_model():
    """
    Returns the Product model that is used by this cart.
    """
    from django.db.models import get_model

    try:
        app_label, model_name = carton_settings.CART_PRODUCT_MODEL.split('.')
    except ValueError:
        raise ImproperlyConfigured("CART_PRODUCT_MODEL must be of the form 'app_label.model_name'")
    product_model = get_model(app_label, model_name)
    if product_model is None:
        raise ImproperlyConfigured("CART_PRODUCT_MODEL refers to model '%s' that has not been installed" % carton_settings.CART_PRODUCT_MODEL)
    return product_model
