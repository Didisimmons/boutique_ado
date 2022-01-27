from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q  # generate search query
from .models import Product, Category

# Create your views here.


def all_products(request):
    """ 
    A view to show all products, including sorting and search queries
    the context allows us to send things back to the template
    """
    # return all products from database
    #need to make sure what we want to query such as sort is defined in order to return the template properly when we're not using any of the queries.
    products = Product.objects.all()
    # start with it as none at the top of this view to ensure we don't get an error
    # when loading the products page without a search term
    query = None
    # to capture this category parameter.
    categories = None
    sort = None
    direction = None
    

    if request.GET:
        """
        If the requests get parameters do contain sort. 
        """
        if 'sort' in request.GET:
            sortKey = request.GET['sort']
            """the reason for copying the sort parameter into a new variable called sortkey.
            Is because now we've preserved the original field we want it to sort on name.
            But we have the actual field we're going to sort on, lower_name in the sort key variable.
            If we had just renamed sort itself to lower_name we would have lost the original field name.
            """
            sort = sortKey
            """
            in order to allow case-insensitive sorting on the name field,
            we need to first annotate all the products with a new field.
            Annotation allows us to add a temporary field on a model.
            """
            # In the event, the user is sorting by name.
            if sortKey == 'name':
                sortKey = 'lower_name'
                # we annotate the current list of products with a new field.
                products = products.annotate(lower_name=Lower('name'))
                
            if 'direction' in request.GET:
                # 
                direction = request.GET['direction']
                # check whether the direction is descending in order to decide whether to reverse the order.
                if direction == 'desc':
                    # minus in front of the sort key will reverse the order.
                    sortKey = f'-{sortKey}'
            # soort products
            products = products.order_by(sortKey)

        """
        if category exist in request, split it into a list at the commas.
        And then use that list to filter the current query set of all 
        products down to only products whose category name is in the list.
        """
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            """
            using the double underscore syntax is common when making queries in django.
            Using it here means we're looking for the name field of the category model.
            And we're able to do this because category and product are related with a foreign key.
            """
            products = products.filter(category__name__in=categories)
            # display for the user which categories they currently have selected.
            # filter all categories down to the ones whose name is in the list from the URL.
            """
            we're converting the list of strings of category names passed through 
            the URL into a list of actual category objects, so that we can access
            all their fields in the template.
            """
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                """
                If the query is blank it's not going to return any results.Use
                the Django messages framework to attach an error message to the request.
                And then redirect back to the products url.
                """
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            """
            return results where the query was matched in either
            the product name or the description.
            """
            # The pipe here is what generates the or statement
            # the i in front of contains makes the queries case insensitive.
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            # I can pass them to the filter method in order to actually filter the products.
            products = products.filter(queries)
    # return the current sorting methodology to the template using string formatting.
    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_item': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }
    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)