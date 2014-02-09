from django.conf import settings

CART_SESSION_KEY = getattr(settings, 'CART_SESSION_KEY', 'CART')

CART_TEMPLATE_TAG_NAME = getattr(settings, 'CART_TEMPLATE_TAG_NAME', 'get_cart')

CART_REMOVE_STALE_ITEMS = getattr(settings, 'CART_REMOVE_STALE_ITEMS', True)
