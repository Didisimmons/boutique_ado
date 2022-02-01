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
    for item_id, item_data in bag.items():
        """
        only want to execute this code if the item has no sizes.
        Which will be evident by checking whether or not the item
        data is an integer.If it's an integer then we know the item
        data is just the quantity.Otherwise we know it's a dictionary
        and we need to iterate through the inner dictionary of items_by_size
        incrementing the product count and total accordingly.also for each of
        these items, we'll add the size to the bag items returned to the template as well.
        """
        if isinstance(item_data, int):
            product = get_object_or_404(Product, pk=item_id)
            total += item_data * product.price
            product_count += item_data
            """
            add a dictionary to the list of bag items containing not only
            the id and the quantity,But also the product object itself.
            This will give us access to all the other fields such as the product image and so on.
            When iterating through the bag items in our templates.
            """
            bag_items.append({
                'item_id': item_id,
                'quantity': item_data,
                'product': product,
            })
        else:
            """
            need to iterate through the inner dictionary of items_by_size
            incrementing the product count and total accordingly.Also
            for each of these items, we'll add the size to the bag items
            returned to the template as well.This is how we'll be able to
            render the sizes in the template.
            """
            product = get_object_or_404(Product, pk=item_id)
            for size, quantity in item_data['items_by_size'].items():
                total += quantity * product.price
                product_count += quantity
                bag_items.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'product': product,
                    'size': size,
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