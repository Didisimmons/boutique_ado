import uuid # generate order number

from django.db import models
from django.db.models import Sum
from django.conf import settings

from products.models import Product

# Create your models here.
""" Handle all orders in the store """
class Order(models.Model):
    # We're gonna automatically generate this order number and we'll want it to be unique and permanent so users can find their previous orders.
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = models.CharField(max_length=40, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)  # The auto now add attribute on the date field which will automatically set the order date and time whenever a new order is created.
    # the last three fields will be calculated using a model method when an order is saved
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    # To assist customers to purchase the same things twice on separate occasions
    original_bag = models.TextField(null=False, blank=False, default='')  # contains the original shopping bag that created it
    stripe_pid = models.CharField(max_length=254, null=False, blank=False, default='')  # contains the stripe payment intent id which is unique

    # quick model methods it's prepended with an underscore by convention to indicate it's a private method
    def _generate_order_number(self):
        """
        Generate a random, unique order number of 32 characters using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        The way this works is by using the sum function across all
        the line-item total fields for all line items on this order.
        The default behaviour is to add a new field to the query set
        called line-item total sum which we can then get and set the 
        order total to that.
        """
        """
        The zero will prevent an error if we manually delete all the
        line items from an order by making sure that this sets the
        order total to zero instead of none. Without this, the next
        line would cause an error because it would try to determine if
        none is less than or equal to the delivery threshold
        """
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            # Setting it to zero if the order total is higher than the threshold.
            self.delivery_cost = 0
        # calculate grand total
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        So that if the order we're saving right now doesn't have an order number.
        We'll call the generate order number method.
        And then execute the original save method.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        # returning just the order number for the order model.
        return self.order_number

"""
The basic idea here. Is when a user checks out. We'll first use the information 
they put into the payment form to create an order instance.
And then we'll iterate through the items in the shopping bag.
Creating an order line item for each one. Attaching it to the order.
And updating the delivery cost, order total, and grand total along the way.
"""
class OrderLineItem(models.Model):
    """"
    A line-item will be like an individual shopping bag item. Relating to a specific order
    And referencing the product itself.
    There's a foreign key to the order. With a related name of line items.
    So when accessing orders we'll be able to make calls such as order.lineitems.all
    And order.lineitems.filter
    """
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE) # can access all the fields of the associated product as well.
    product_size = models.CharField(max_length=2, null=True, blank=True) # XS, S, M, L, XL or null/blak since there are products with no sizes 
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    """
    Like setting the order number on the order model we also need
    to set the line-item total field by overriding its save method.
    """
    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        # returning the SKU of the product along with the order number it's part of for each order line item.
        return f'SKU {self.product.sku} on order {self.order.order_number}'
