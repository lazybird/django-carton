
Django Carton
=============


      +------+
     /|     /|
    +-+----+ |    django-carton is a simple and lightweight application
    | |    | |    for shopping carts and wish lists.
    | +----+-+
    |/     |/
    +------+



* Simple: You decide how to implement the views, templates and payment
  processing.
* Lightweight: The cart lives in the session.
* Just a container: You define your product model the way you want.


Usage Example
-------------

View:

    from django.http import HttpResponse

    from carton.cart import Cart
    from products.models import Product

    def add(request):
        cart = Cart(request.session)
        product = Product.objects.get(id=request.GET.get('product_id'))
        cart.add(product, price=product.price)
        return HttpResponse("Added")

    def show(request):
        return render(request, 'shopping/show-cart.html')


We are assuming here that your products are defined in an application
called ``products``.

Template:

    {% load carton_tags %}
    {% get_cart as cart %}

    {% for item in cart.items %}
        {{ item.product.name }}
        {{ item.quantity }}
        {{ item.subtotal }}
    {% endfor %}

    You can also use this convinent shortcut:
    {% for product in cart.products %}
        {{ product.name }}
    {% endfor %}

Within the template you can access the product id with {{product.id}}. 

Settings:

    CART_PRODUCT_MODEL = 'products.models.Product'


This project is shipped with an application example called ``shopping``
implementing basic add, remove, display features.
To use it, you will need to install the ``shopping`` application and
include the URLs in your project ``urls.py``

    # settings.py
    INSTALLED_APPS = (
        'carton',
        'shopping',
        'products',
    )

    # urls.py
    urlpatterns = patterns('',
        url(r'^shopping-cart/', include('shopping.urls')),
    )


Assuming you have some products defined, you should be able to
add, show and remove products like this:

    /shopping-cart/add/?id=1
    /shopping-cart/show/
    /shopping-cart/remove/?id=1


Installation
------------

This application requires Django version 1.4; all versions above should be fine.

Just install the package using something like pip and add ``carton`` to
your ``INSTALLED_APPS`` setting.

Add the `CART_PRODUCT_MODEL` setting, a dotted path to your product model.

This is how you run tests:

    ./manage.py test carton.tests --settings=carton.tests.settings


Abstract
--------

The cart is an object that's stored in session. Products are associated
to cart items.

    Cart
    |-- CartItem
    |----- product
    |----- price
    |----- quantity

A cart item stores a price, a quantity and an arbitrary instance of
a product model.


You can access all your product's attributes, for instance it's name:

    {% for item in cart.items %}
        {{ item.price }}
        {{ item.quantity }}
        {{ item.product.name }}
    {% endfor %}



Managing Cart Items
-------------------

These are simple operations to add, remove and access cart items:

    >>> apple = Product.objects.all()[0]
    >>> cart.add(apple, price=1.5)
    >>> apple in cart
    True
    >>> cart.remove(apple)
    >>> apple in cart
    False

    >>> orange = Product.objects.all()[1]
    >>> cart.add(apple, price=1.5)
    >>> cart.total
    Decimal('1.5')
    >>> cart.add(orange, price=2.0)
    >>> cart.total
    Decimal('3.5')

Note how we check weather the product is in the cart - The following
statements are different ways to do the same thing:

    >>> apple in cart
    >>> apple in cart.products
    >>> apple in [item.product for item in cart.items]


The "product" refers to the database object. The "cart item" is where
we store a copy of the product, it's quantity and it's price.

    >>> cart.items
    [CartItem Object (apple), CartItem Object (orange)]

    >>> cart.products
    [<Product: apple>, <Product: orange>]


Clear all items:

    >>> cart.clear()
    >>> cart.total
    0


Increase the quantity by adding more products:

    >>> cart.add(apple, price=1.5)
    >>> cart.add(apple)  # no need to repeat the price.
    >>> cart.total
    Decimal('3.0')


Note that the price is only needed when you add a product for the first time.

    >>> cart.add(orange)
    *** ValueError: Missing price when adding a cart item.


You can tell how many items are in your cart:

    >>> cart.clear()
    >>> cart.add(apple, price=1.5)
    >>> cart.add(orange, price=2.0, quantity=3)
    >>> cart.count
    4
    >>> cart.unique_count  # Regarless of product's quantity
    2


You can add several products at the same time:

    >>> cart.clear()
    >>> cart.add(orange, price=2.0, quantity=3)
    >>> cart.total
    Decimal('6')
    >>> cart.add(orange, quantity=2)
    >>> cart.total
    Decimal('10')


The price is relevant only the first time you add a product:

    >>> cart.clear()
    >>> cart.add(orange, price=2.0)
    >>> cart.total
    Decimal('2')
    >>> cart.add(orange, price=100)  # this price is ignored
    >>> cart.total
    Decimal('4')


Note how the price is ignored on the second call.


You can change the quantity of product that are already in the cart:

    >>> cart.add(orange, price=2.0)
    >>> cart.total
    Decimal('2')
    >>> cart.set_quantity(orange, quantity=3)
    >>> cart.total
    Decimal('6')
    >>> cart.set_quantity(orange, quantity=1)
    >>> cart.total
    Decimal('2')
    >>> cart.set_quantity(orange, quantity=0)
    >>> cart.total
    0
    >>> cart.set_quantity(orange, quantity=-1)
    *** ValueError: Quantity must be positive when updating cart



Removing all occurrence of a product:

    >>> cart.add(apple, price=1.5, quantity=4)
    >>> cart.total
    Decimal('6.0')
    >>> cart.remove(apple)
    >>> cart.total
    0
    >>> apple in cart
    False


Remove a single occurrence of a product:

    >>> cart.add(apple, price=1.5, quantity=4)
    >>> cart.remove_single(apple)
    >>> apple in cart
    True
    >>> cart.total
    Decimal('4.5')
    >>> cart.remove_single(apple)
    >>> cart.total
    Decimal('3.0')
    >>> cart.remove_single(apple)
    >>> cart.total
    Decimal('1.5')
    >>> cart.remove_single(apple)
    >>> cart.total
    0


Multiple carts
--------------

Django Carton has support for using multiple carts in the same project.
The carts would need to be stored in Django session using different session
keys.

    from carton.cart import Cart

    cart_1 = Cart(session=request.session, session_key='CART-1')
    cart_2 = Cart(session=request.session, session_key='CART-2')


Working With Product Model
--------------------------

Django Carton needs to know how to list your product objects.

The default behaviour is to get the product model using the
`CART_PRODUCT_MODEL` setting and list all products.

The default queryset manager is used and all products are
retrieved. You can filter products by defining some lookup
parameters in `CART_PRODUCT_LOOKUP` setting.

    # settings.py

    CART_PRODUCT_LOOKUP = {
        'published': True,
        'status': 'A',
    }


If you need further customization of the way product model and queryset
are retrieved, you can always sub-class the default `Cart` and overwrite
the `get_queryset` method. In that case, you should take into account that:

* You probably won't need `CART_PRODUCT_MODEL` and `CART_PRODUCT_LOOKUP`
  if you get a direct access to your product model and define the
  filtering directly on the cart sub-class.
* You probably have to write your own template tag to retrieve the cart
  since the default `get_cart` template tag point on the `Cart` class
  defined by django-carton.


Settings
--------

### Template Tag Name

You can retrieve the cart in templates using
`{% get_cart as my_cart %}`.

You can change the name of this template tag using the
`CART_TEMPLATE_TAG_NAME` setting.


    # In you project settings
    CART_TEMPLATE_TAG_NAME = 'get_basket'

    # In templates
    {% load carton_tags %}
    {% get_basket as my_basket %}


### Stale Items

Cart items are associated to products in the database. Sometime a product can be found
in the cart when its database instance has been removed. These items are called stale
items. By default they are removed from the cart.

### Session Key

The `CART_SESSION_KEY` settings controls the name of the session key.
