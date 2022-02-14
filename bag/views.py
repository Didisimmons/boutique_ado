from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages

from products.models import Product


def view_bag(request):
    """ A view that renders the bag contents page """
    return render(request, 'bag/bag.html')

# This view we'll get the bag variable if it exists in the session or create it if it doesn't.
# Then add the item to the bag or update the quantity if it already exists.
def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """

    product = get_object_or_404(Product, pk=item_id) # To add a message to the request object using get object just incase the product is not found
    quantity = int(request.POST.get('quantity')) # we need to convert it to an integer since it'll come from the template as a string
    redirect_url = request.POST.get('redirect_url')
    # Size starts out as None
    size = None
    # If the size is in the post request, set it to S, M, L, XL, etc
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    """
    This is handy in a situation like an e-commerce store
    Because it allows us to store the contents of the shopping bag
    in the HTTP session while the user browses the site and adds items to be purchased.
    By storing the shopping bag in the session.
    It will persist until the user closes their browser so that they can add something to the bag.
    Then browse to a different part of the site add something else
    and so on without losing the contents of their bag
    """
    # we first check to see if there's a bag variable in the session and if not we'll create one.
    bag = request.session.get('bag', {})
    
    # If size is not None
    if size:
        # Then check if the item is already in the bag
        if item_id in list(bag.keys()):
            """
            If item is already in the bag.Then we need to check if another
            item of the same id and same size already exists.If so increment
            the quantity for that size and otherwise just set it equal to the quantity.
            if in bag the items_by_size dict is guaranteed to exist check if the size is in it
            """
            if size in bag[item_id]['items_by_size'].keys():
                # If so, increment that size by 1
                bag[item_id]['items_by_size'][size] += quantity
                # create updated messaged for products with size 
                messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
            else:
                bag[item_id]['items_by_size'][size] = quantity
                messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
        else:
            """
            If the items are not already in the bag we need to add it.
            But we're actually going to do it as a dictionary with a key of
            items_by_size.Since we may have multiple items with this item id
            with different sizes.This allows us to structure the bags such that
            we can have a single item id for each item.But still track multiple
            sizes
            """
            bag[item_id] = {'items_by_size': {size: quantity}}
            # adding an item with a size 
            messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
    # if there's no size this would run
    else:
        """
        If the item (key)is already in the bag
        dictionary matching this product id.
        Then its quantity would be incremented.
        """
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
            # message for adding items to the bag
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
        else:
            # key of the items id equal to quanity
            bag[item_id] = quantity
            # using some string formatting to let the user know they've added this product to their bag.
            messages.success(request, f'Added { product.name } to your bag')

    # putting this the bag variable into the session.
    # To overwrite the variable in the session with the updated version.
    request.session['bag'] = bag
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """ Adjust the quantity of the specified product to the specified amount"""
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    bag = request.session.get('bag', {})

    if size:
        """
        Remember that this is coming from a form on the shopping bag page
        which will contain the new quantity the user wants in the bag. So
        the idea would be If there's a size. Of course we'll need to drill into the
        items by size dictionary, find that specific size and either set its
        quantity to the updated one or remove it if the quantity submitted is zero.
        """
        if quantity > 0 :
            bag[item_id]['items_by_size'][size] = quantity
            messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
        else:
            del bag[item_id]['items_by_size'][size]
            # if quantity is set to zero
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
            messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')
    else:
        """
        If there's no size that logic is quite simple and we can remove the item
        These two operations are basically the same.They just need to be handled
        differently due to the more complex structure of the bag for items that have sizes
        """
        if quantity > 0 :
            bag[item_id] = quantity
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
        else:
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your bag')

    request.session['bag'] = bag
    return redirect(reverse('view_bag'))

def remove_from_bag(request, item_id):
    """ Remove items from the shopping bag intended quantity is zero """
    """
    Because this view will be posted to from a JavaScript function.
    We want to return an actual 200 HTTP response.
    Implying that the item was successfully removed.
    """
    try:
        product = get_object_or_404(Product, pk=item_id)
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']
        bag = request.session.get('bag', {})

        if size:
            """
        if size is in request.post delete that size key in the items by size dictionary.
        Also if that's the only size they had in the bag.
        """
            del bag[item_id]['items_by_size'][size]
            """
            If the items by size dictionary is now empty which will evaluate to false.
            We might as well remove the entire item id so we don't end up with an empty items
            by size dictionary hanging around
            """
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
            messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')
    
        else:
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your bag')

        request.session['bag'] = bag
        return HttpResponse(status=200)

    except Exception as e:
        # if any error occurs in the removal process,the user will get a notification about it
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)
