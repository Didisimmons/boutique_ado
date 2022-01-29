from decimal import Decimal
from django.conf import settings

def bag_contents(request):
    """
    This is what's known as a context processor.
    its purpose is to make this dictionary available to all 
    templates across the entire application.You can use 
    request.user in any template due to the presence of the
    built-in request context processor.
    This context concept is the same as the context we've been using in our views
    the only difference is we're returning it directly and making it available to
    all templates by putting it in settings.py.
    """
    bag_items = [] # empty list for bag items to live
    total = 0
    product_count = 0

    """
    To entice customers to purchase more.We're going
    to give them free delivery if they spend more than the amount
    specified in the free delivery threshold in settings.py.
    """
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE /100)
        # For convenience we let the user know how much more they need to spend to get free delivery
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0

    grand_total = delivery + total
    # all these items in the context would be available in all templates across the site.
    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context