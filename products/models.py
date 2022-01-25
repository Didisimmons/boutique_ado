from django.db import models

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=254)
    # makes the name appear more friendly on the front end and is optional.
    # the name field gives us a programmatic way to find it in things like views and other code.
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    """
    The first field is a foreign key to the category model.
    We'll allow this to be null in the database and blank in forms
    and if a category is deleted we'll set any products that use it
    to have null for this field rather than deleting the product.
    each product requires a name, a description, and a price.
    But everything else is optional.
    """
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    # return product name 
    def __str__(self):
        return self.name
