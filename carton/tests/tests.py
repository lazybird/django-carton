from importlib import import_module

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase

from carton.cart import Cart
from carton.tests.models import Product
from carton.tests.views import show

try:
    from django.test import override_settings
except ImportError:
    from django.test.utils import override_settings


class CartTests(TestCase):

    def setUp(self):
        engine = import_module(settings.SESSION_ENGINE)
        self.session = engine.SessionStore()
        self.session.save()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = self.session.session_key

        self.factory = RequestFactory()

        self.cart = Cart(self.session)

        self.deer = Product.objects.create(name='deer', price=10.0, custom_id=1)
        self.moose = Product.objects.create(name='moose', price=20.0, custom_id=2)

    def show_response(self):
        """
        Utility method to return a response from the `show` view.
        """
        request = self.factory.get(reverse('carton-tests-show'))
        request.session = self.session

        return show(request)

    def test_product_is_added(self):
        """
        Can a product be added to the cart?
        """
        self.cart.add(self.deer, 10.00, 1)
        self.session.save()

        self.assertContains(self.show_response(), '1 deer for $10.0')

    def test_multiple_products_are_added(self):
        """
        Can multiple products be added to the cart?
        """
        self.cart.add(self.deer, 10.00, 1)
        self.cart.add(self.moose, 20.00, 1)
        self.session.save()

        response = self.show_response()

        self.assertContains(response, '1 deer for $10.0')
        self.assertContains(response, '1 moose for $20.0')

    def test_stale_item_is_removed_from_cart(self):
        """
        Are items which are not in the database kept out of the cart?
        """
        self.cart.add(self.deer, 10.00, 1)
        self.cart.add(self.moose, 20.00, 1)
        self.session.save()

        response = self.show_response()

        self.assertContains(response, 'deer')
        self.assertContains(response, 'moose')

        self.deer.delete()

        response = self.show_response()

        self.assertNotContains(response, 'deer')
        self.assertContains(response, 'moose')

    def test_quantity_increases(self):
        """
        Do multiple calls to `add` increase the quantity in the cart?
        """
        self.cart.add(self.deer, 10.00, 1)
        self.cart.add(self.deer, 10.00, 2)
        self.session.save()

        self.assertContains(self.show_response(), '3 deer')

    def test_items_are_counted_properly(self):
        """
        Are items in the cart counted correctly?
        """
        self.cart.add(self.deer, 10.00, 2)
        self.cart.add(self.moose, 20.00, 1)
        self.session.save()

        response = self.show_response()

        self.assertContains(response, 'items count: 3')
        self.assertContains(response, 'unique count: 2')

    def test_products_are_removed_all_together(self):
        """
        Can all products of a single type be removed?
        """
        self.cart.add(self.deer, 10.00, 3)
        self.cart.add(self.moose, 20.00, 1)
        self.session.save()

        self.cart.remove(self.deer)

        response = self.show_response()

        self.assertNotContains(response, 'deer')
        self.assertContains(response, 'moose')

    def test_single_product_is_removed(self):
        """
        Can a single instance of a product be removed?
        """
        self.cart.add(self.deer, 10.00, 3)
        self.session.save()

        self.cart.remove_single(self.deer)

        self.assertContains(self.show_response(), '2 deer')

    def test_quantity_is_overwritten(self):
        """
        Can an items quantity be changed?
        """
        self.cart.add(self.deer, 10.00, 3)
        self.session.save()

        self.cart.set_quantity(self.deer, 4)

        self.assertContains(self.show_response(), '4 deer')

    def test_cart_items_are_cleared(self):
        """
        Can a cart be entirely cleared?
        """
        self.cart.add(self.deer, 10.00, 1)
        self.cart.add(self.moose, 20.00, 1)
        self.cart.clear()
        self.session.save()

        response = self.show_response()

        self.assertNotContains(response, 'deer')
        self.assertNotContains(response, 'moose')

    @override_settings(CART_PRODUCT_LOOKUP={'price__gt': 1})
    def test_custom_product_filter_are_applied(self):
        """
        We modify the cart queryset to exclude some products. We
        should not be able to add excluded products to the cart.
        """
        exclude = Product.objects.create(
            name='EXCLUDED',
            price=0.99,
            custom_id=100,
        )

        self.cart.add(self.deer, 10.00, 1)
        self.cart.add(exclude, exclude.price, 1)
        self.session.save()

        response = self.show_response()

        self.assertNotContains(response, 'EXCLUDE')
        self.assertContains(response, 'deer')
