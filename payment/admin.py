from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
# Register your models here.
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)

#Cretae an OrderItemInline
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0

#Extend our Order model
class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ['date_ordered']
    # fields = ['user', 'full_name', 'email', 'shipping_address1', 'amount_paid', 'date_ordered', 'is_shipped', 'date_shipped']
    inlines = [OrderItemInline]

#Ungreister Order items
admin.site.unregister(Order)

#Reregister Order and OrderAdmin
admin.site.register(Order, OrderAdmin)