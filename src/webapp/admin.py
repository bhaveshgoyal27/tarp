from django.contrib import admin
from .models import Customer,Vendor,Item,Menu,Order,orderItem,User

admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Vendor)
admin.site.register(Item)
admin.site.register(Menu)
admin.site.register(Order)
admin.site.register(orderItem)