from django.contrib import admin
from .models import Item, Discount, Tax, Order

admin.site.register(Item)
admin.site.register(Discount)
admin.site.register(Tax)
admin.site.register(Order)