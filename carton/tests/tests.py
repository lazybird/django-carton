from django.core.urlresolvers import reverse
from django.test import TestCase
from carton.tests.models import Product

try:
    from django.test import override_settings
except ImportError:
    from  django.test.utils import override_settings


class CartTests(TestCase):

    def setUp(self):
        self.deer = Product.objects.create(name='deer', price=10.0, custom_id=1)
        self.moose = Product.objects.create(name='moose', price=20.0, custom_id=2)
        self.url_add = reverse('carton-tests-add')
        self.url_show = reverse('carton-tests-show')
        self.url_remove = reverse('carton-tests-remove')
        self.url_remove_single = reverse('carton-tests-remove-single')
        self.url_quantity = reverse('carton-tests-set-quantity')
        self.url_clear = reverse('carton-tests-clear')
        self.deer_data = {'product_id': self.deer.pk}
        self.moose_data = {'product_id': self.moose.pk}

    def test_product_is_added(self):
        self.client.post(self.url_add, self.deer_data)
        response = self.client.get(self.url_show)
        self.assertContains(response, '1 deer for $10.0')

    def test_multiple_products_are_added(self):
        self.client.post(self.url_add, self.deer_data)
        self.client.post(self.url_add, self.moose_data)
        response = self.client.get(self.url_show)
        self.assertContains(response, '1 deer for $10.0')
        self.assertContains(response, '1 moose for $20.0')

    def test_stale_item_is_removed_from_cart(self):
        # Items that are not anymore reference in the database should not be kept in cart.
        self.client.post(self.url_add, self.deer_data)
        self.client.post(self.url_add, self.moose_data)
        response = self.client.get(self.url_show)
        self.assertContains(response, 'deer')
        self.assertContains(response, 'moose')
        self.deer.delete()
        response = self.client.get(self.url_show)
        self.assertNotContains(response, 'deer')
        self.assertContains(response, 'moose')

    def test_quantity_increases(self):
        self.client.post(self.url_add, self.deer_data)
        self.deer_data['quantity'] = 2
        self.client.post(self.url_add, self.deer_data)
        response = self.client.get(self.url_show)
        self.assertContains(response, '3 deer')

    def test_items_are_counted_properly(self):
        self.deer_data['quantity'] = 2
        self.client.post(self.url_add, self.deer_data)
        self.client.post(self.url_add, self.moose_data)
        response = self.client.get(self.url_show)
        self.assertContains(response, 'items count: 3')
        self.assertContains(response, 'unique count: 2')

    def test_price_is_updated(self):
        # Let's give a discount: $1.5/product. That's handled on the test views.
        self.deer_data['quantity'] = 2
        self.deer_data['discount'] = 1.5
        self.client.post(self.url_add, self.deer_data)
        response = self.client.get(self.url_show)
        # subtotal = 10*2 - 1.5*2
        self.assertContains(response, '2 deer for $17.0')

    def test_products_are_removed_all_together(self):
        self.deer_data['quantity'] = 3
        self.client.post(self.url_add, self.deer_data)
        self.client.post(self.url_add, self.moose_data)
        remove_data = {'product_id': self.deer.pk}
        self.client.post(self.url_remove, remove_data)
        response = self.client.get(self.url_show)
        self.assertNotContains(response, 'deer')
        self.assertContains(response, 'moose')

    def test_single_product_is_removed(self):
        self.deer_data['quantity'] = 3
        self.client.post(self.url_add, self.deer_data)
        remove_data = {'product_id': self.deer.pk}
        self.client.post(self.url_remove_single, remove_data)
        response = self.client.get(self.url_show)
        self.assertContains(response, '2 deer')

    def test_quantity_is_overwritten(self):
        self.deer_data['quantity'] = 3
        self.client.post(self.url_add, self.deer_data)
        self.deer_data['quantity'] = 4
        self.client.post(self.url_quantity, self.deer_data)
        response = self.client.get(self.url_show)
        self.assertContains(response, '4 deer')

    def test_cart_items_are_cleared(self):
        self.client.post(self.url_add, self.deer_data)
        self.client.post(self.url_add, self.moose_data)
        self.client.post(self.url_clear)
        response = self.client.get(self.url_show)
        self.assertNotContains(response, 'deer')
        self.assertNotContains(response, 'moose')

    @override_settings(CART_PRODUCT_LOOKUP={'price__gt': 1})
    def test_custom_product_filter_are_applied(self):
        # We modify the queryset to exclude some products. For these excluded
        # we should not be able to add them in the cart.
        exclude = Product.objects.create(name='EXCLUDE', price=0.99, custom_id=100)
        exclude_data = {'product_id': exclude.pk}
        self.client.post(self.url_add, self.deer_data)
        self.client.post(self.url_add, exclude_data)
        response = self.client.get(self.url_show)
        self.assertNotContains(response, 'EXCLUDE')
        self.assertContains(response, 'deer')
