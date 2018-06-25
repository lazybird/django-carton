from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext as _

from . import settings as cart_settings


class Cart(models.Model):
    session_key = models.CharField(verbose_name=_('session key'), max_length=40, unique=True)
    user = models.ForeignKey(
        to=get_user_model(), verbose_name=_('user'), null=True, blank=True,
        on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("updated"), auto_now=True)

    class Meta:
        verbose_name = _('shopping cart')
        verbose_name_plural = _('shopping carts')

    def __str__(self):
        return _(f"Cart session: {self.session_key} / user: {self.user}")


class CartItem(models.Model):
    cart = models.ForeignKey(
        to='Cart', verbose_name=_('cart'), related_name='items',
        on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name=_('quantity'))
    price = models.DecimalField(verbose_name=_("price"), max_digits=6, decimal_places=2)
    product = models.ForeignKey(
        to=cart_settings.CART_PRODUCT_MODEL, verbose_name='produit',
        related_name='+', on_delete=models.CASCADE)
    extra = JSONField(null=True, blank=True)

    class Meta:
        verbose_name = _('cart item')
        verbose_name_plural = _('cart items')
        unique_together = ('cart', 'product')

    def __str__(self):
        return _(f"{self.product} {self.price} {self.quantity}")

    @property
    def total(self):
        return self.quantity * self.price
