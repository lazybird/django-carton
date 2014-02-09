SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'carton-tests.db',
    }
}

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.sites',
    'carton',
    'carton.tests',
)

ROOT_URLCONF = 'carton.tests.urls'

SECRET_KEY = 'any-key'

CART_PRODUCT_MODEL = 'carton.tests.models.Product'
