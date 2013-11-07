from django.http import HttpResponse

from carton.cart import Cart
from carton.tests.models import Product


def show(request):
    cart = Cart(request.session)
    response = ''
    for item in cart.items:
        response += '%(quantity)s %(item)s for $%(price)s\n' % {
            'quantity': item.quantity,
            'item': item.product.name,
            'price': item.subtotal,
        }
        response += 'items count: %s\n' % cart.count
        response += 'unique count: %s\n' % cart.unique_count
    return HttpResponse(response)


def add(request):
    cart = Cart(request.session)
    product = Product.objects.get(pk=request.POST.get('product_id'))
    quantity = request.POST.get('quantity', 1)
    discount = request.POST.get('discount', 0)
    price = product.price - float(discount)
    cart.add(product, price, quantity)
    return HttpResponse()


def remove(request):
    cart = Cart(request.session)
    product = Product.objects.get(pk=request.POST.get('product_id'))
    cart.remove(product)
    return HttpResponse()


def remove_single(request):
    cart = Cart(request.session)
    product = Product.objects.get(pk=request.POST.get('product_id'))
    cart.remove_single(product)
    return HttpResponse()


def clear(request):
    cart = Cart(request.session)
    cart.clear()
    return HttpResponse()


def set_quantity(request):
    cart = Cart(request.session)
    product = Product.objects.get(pk=request.POST.get('product_id'))
    quantity = request.POST.get('quantity')
    cart.set_quantity(product, quantity)
    return HttpResponse()
