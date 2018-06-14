from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CartonConfig(AppConfig):
    name = 'carton'
    verbose_name = _('Shopping Cart')
