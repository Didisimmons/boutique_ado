from django.db import models

# Create your models here.


class Category(models.Model):
    """
    adjust the verbose name or the plural form of it from
    the Django defaults dashboard.
    """
    class Meta:
        verbose_name_plural = 'Categories'
    name = models.CharField(max_length=254)
    # makes the name appear more friendly on the front end and is optional.
    # the name field gives us a programmatic way to find it in things
    # like views and other code.
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
    # This would be false by default and allowed to be blank both in the database and in forms.
    """ 
    rather than actually implement different sizes for every product.
    in the database.this project we'll mimic the functionality by simply
    describing whether or not the object has different sizes available.
    And if so we'll provide the user a choice of some generic sizes.
    Which will be added to the item details in their shopping bag.
    """     
    has_sizes = models.BooleanField(default=False, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    # return product name
    def __str__(self):
        return self.name
