from django.contrib import admin
from .models import Order, OrderLineItem

# Register your models here.
class OrderLineItemAdminInline(admin.TabularInline):
    """to allow us to add and edit line items in the admin
    right from inside the order model"""
    model = OrderLineItem
    # make the line item total in the form read-only.
    readonly_fields = ('lineitem_total',)

class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)

    # These fields are all things that will be calculated by our model methods.
    readonly_fields = ('order_number', 'date',
                       'delivery_cost', 'order_total',
                       'grand_total',)

    """
    will allow us to specify the order of the fields
    in the admin interface, which would otherwise be 
    adjusted by django due to the use of some read-only fields.
    This way the order stays the same as it appears in the model.
    """
    fields = ('order_number', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'delivery_cost',
              'order_total', 'grand_total',)

    # To restrict the columns that show up in the order list to only a few key items.
    list_display = ('order_number', 'date', 'full_name',
                    'order_total', 'delivery_cost',
                    'grand_total',)

    # set them to be ordered by date in reverse chronological order
    # putting the most recent orders at the top.
    ordering = ('-date',)

# going to skip registering the OrderLineItem model. Since it's accessible via the inline on the order model.
admin.site.register(Order, OrderAdmin)