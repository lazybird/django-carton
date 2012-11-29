from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('shopping.views',
    url(r'^add/$', 'add', name='shopping-cart-add'),
    url(r'^remove/$', 'remove', name='shopping-cart-remove'),
    url(r'^show/$', 'show', name='shopping-cart-show'),
)

