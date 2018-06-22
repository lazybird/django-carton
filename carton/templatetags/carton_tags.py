from django import template

from carton.models import Cart
from carton.settings import CART_TEMPLATE_TAG_NAME

register = template.Library()


@register.simple_tag(takes_context=True, name=CART_TEMPLATE_TAG_NAME)
def get_cart(context):
    """
    Make the cart object available in template.

    Sample usage::

        {% load carton_tags %}
        {% get_cart as cart %}
        {% for product in cart.products %}
            {{ product }}
        {% endfor %}
    """
    request = context['request']
    return Cart.objects.get(session_key=request.session.session_key)
