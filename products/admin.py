from django.contrib import admin
from .models import Product, Category

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    # tuple informs admin user which fields to display
    # if you want to change the order of the columns in the admin dashboard,
    # you can just adjust the order here in the list display attribute.
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
    )

    """
    sorting products by the SKU, however when 
    sorting multiple columns ensure its a tuple
    even if its one field.
    To reverse the simply put a minus in front 
    of SKU
    """
    ordering = ('sku',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
