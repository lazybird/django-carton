from django.conf import settings

CART_SESSION_KEY = getattr(settings, 'CART_SESSION_KEY', 'CART')

CART_TEMPLATE_TAG_NAME = getattr(settings, 'CART_TEMPLATE_TAG_NAME', 'get_cart')

CART_ITEM_CLASS = getattr(settings, 'CART_ITEM_CLASS', 'carton.cart.CartItem')
