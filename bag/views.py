from django.shortcuts import render, redirect

# Create your views here.
def view_bag(request):
    """ A view that renders the bag contents page """
    return render(request, 'bag/bag.html')

"""
This view we'll get the bag variable if it exists in the session or create it if it doesn't.
Then add the item to the bag or update the quantity if it already exists.
And
"""
def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """
    quantity = int(request.POST.get('quantity')) # we need to convert it to an integer since it'll come from the template as a string
    redirect_url = request.POST.get('redirect_url')
    size = None
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
    # stuffinng the producst into the bag 
    bag = request.session.get('bag', {})
    
    if size:
        if item_id in list(bag.keys()):
            """
            If the item is already in the bag.Then we need to check if another 
            item of the same id and same size already exists.If so increment
            the quantity for that size and otherwise just set it equal to the quantity.
            Since the item already exists in the bag. But this is a new size for that item.
            """
            if size in bag[item_id]['items_by_size'].keys():
                bag[item_id]['items_by_size'][size] += quantity
            else:
                bag[item_id]['items_by_size'][size] = quantity
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
    # if there's no size this would run
    else:
        """
        If the item (key)is already in the bag
        dictionary matching this product id.
        Then its quantity would be incremented.
        """
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        else:
            # key of the items id equal to quanity
            bag[item_id] = quantity

    # putting this the bag variable into the session.
    # To overwrite the variable in the session with the updated version.
    request.session['bag'] = bag
    return redirect(redirect_url)
