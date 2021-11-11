from django.http import HttpResponse

from carton.cart import Cart


def show(request):
    cart = Cart(request.session)

    template = """
        {} {} for ${}
        items count: {}
        unique count: {}
    """

    response = ''.join(
        template.format(
            item.quantity,
            item.product.name,
            item.subtotal,
            cart.count,
            cart.unique_count,
        ) for item in cart.items
    )

    return HttpResponse(response)
