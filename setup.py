from setuptools import setup, find_packages

import carton


setup(
    name='django-carton',
    version=carton.__version__,
    description=carton.__doc__,
    packages=find_packages(),
    url='http://github.com/lazybird/django-carton/',
    author='lazybird',
    long_description=open('README.md').read(),
    include_package_data=True,
)
