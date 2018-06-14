from django.contrib.gis import admin

from .models import Cart, CartItem


class BaseCartItemAdmin(object):
    fields = ('product', 'quantity', 'price')
    # readonly_fields = ('product', 'quantity', 'price')


class CartItemInline(BaseCartItemAdmin, admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(CartItem)
class BaseCartItemAdmin(BaseCartItemAdmin, admin.ModelAdmin):
    pass


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'session_key', 'user', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    # readonly_fields = ('session', 'user')
    inlines = (CartItemInline,)
