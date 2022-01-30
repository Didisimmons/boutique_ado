from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

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
    # In order to add all the bags current items to the context of all templates.
    # Accessing the shopping bag in the session, retrieve bag if it exixts else initialize it to an empty dictionary
    bag = request.session.get('bag', {})
    """
    We need to iterate through all the items in the shopping bag.
    tally up the total cost and product count.
    And add the products and their data to the bag items list.
    display them on the shopping bag page and throughout the site.
    """
    # bag from session
    for item_id, quantity in bag.items():
        # retrieve product
        product = get_object_or_404(Product, pk=item_id)
        total += quantity * product.price
        product_count += quantity
        """
        add a dictionary to the list of bag items containing not only
        the id and the quantity,But also the product object itself.
        This will give us access to all the other fields such as the product image and so on.
        When iterating through the bag items in our templates.
        """

        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'product': product,
        })

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