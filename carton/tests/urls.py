from django.conf.urls import url, patterns


urlpatterns = patterns(
    'carton.tests.views',
    url(r'^show/$', 'show', name='carton-tests-show'),
)
