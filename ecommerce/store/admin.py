from django.contrib import admin
from .models import *

admin.site.Register(Customer)
admin.site.Register(Product)
admin.site.Register(Order)
admin.site.Register(OrderItem)
admin.site.Register(ShippingAddress)

# Register your models here.
