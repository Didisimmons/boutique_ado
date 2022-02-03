"""
This file allows us to call the updated total,
each time a line item is attached to the order.
Post, in this case, means after.This implies
these signals are sent by django to the entire application
after a model instance is saved and after it's deleted respectively.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver # To recieve the signals

from .models import OrderLineItem

"""
This will handle signals from the post_save event.These
parameters refer to the sender of the signal. In our case OrderLineItem.
The actual instance of the model that sent it.A boolean sent by django
referring to whether this is a new instance or one being updated.
And any keyword arguments.
"""
@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    instance.order which refers to the order this specific line item is related to.
    """
    instance.order.update_total()

@receiver(post_delete, sender=OrderLineItem)
def update_on_save(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    instance.order.update_total()