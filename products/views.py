from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q  # generate search query
from django.db.models.functions import Lower

from .models import Product, Category
from .forms import ProductForm

# Create your views here.


def all_products(request):
    """
    A view to show all products, including sorting and search queries
    the context allows us to send things back to the template
    """
    # return all products from database
    products = Product.objects.all()
    # need to make sure what we want to query such as sort is defined in order
    # to return the template properly when we're not using any of the queries
    # and when not remove any errors
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
            sortkey = request.GET['sort']
            """
            the reason for copying the sort parameter into a new variable
            called sortkey.Is because now we've preserved the original field
            we want it to sort on name.But we have the actual field we're
            going to sort on, lower_name in the sort key variable.If we had
            just renamed sort itself to lower_name we would have lost the
            original field name.
            """
            sort = sortkey
            """
            the annotate is being used for here, is to add an extra field to
            the model (lower_name) which just converts the existing 'name'
            field to lowercase, allowing you to sort it
            """
            # In the event, the user is sorting by name.
            if sortkey == 'name':
                sortkey = 'lower_name'
                """
                .annotate() does is add additional 'fields' to the queryset
                in this view.It allows you to add functionality to the view.
                """
                products = products.annotate(lower_name=Lower('name'))

            # categories to be sorted by name instead of their ids.
            if sortkey == 'category':
                sortkey = 'category__name'
                """
                This would  effectively changing this line to
                products = products.order_by(category__name)
                """

            if 'direction' in request.GET:
                direction = request.GET['direction']
                # check whether the direction is descending in order
                # to decide whether to reverse the order.
                if direction == 'desc':
                    # minus in front of the sort key will reverse the order.
                    sortkey = f'-{sortkey}'
            # sort products
            products = products.order_by(sortkey)

        """
        if category exist in request, split it into a list at the commas.
        And then use that list to filter the current query set of all
        products down to only products whose category name is in the list.
        """
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            """
            using the double underscore syntax is common when making queries
            in django.Using it here means we're looking for the name field of
            the category model.And we're able to do this because category and
            product are related with a foreign key.
            """
            products = products.filter(category__name__in=categories)
            # display for the user categories they currently selected
            # filter all categories down to the ones whose name is in the
            # list from the URL.
            """
            we're converting the list of strings of category names
            passed through the URL into a list of actual category
            objects, so that we can access all their fields in the template.
            """
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                """
                If the query is blank it's not going to return any results.Use
                the Django messages framework to attach an error message to the
                request.And then redirect back to the products url.
                """
                messages.error(request,
                               "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            """
            return results where the query was matched in either
            the product name or the description.
            """
            # The pipe here is what generates the or statement
            # the i in front of contains makes the queries case insensitive.
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            # filter method in order to actually filter the products.
            products = products.filter(queries)
    # is a string made up of two other variables: sort and direction
    # If neither of these variables is determined, they are set to what
    # they were at the top of the view which is none_none.
    # If there is no sorting.
    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
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


def add_product(request):
    """
    Add a product to the store
    instantiate a new instance of the product form from request.post
    and include request .files also.In order to capture in the image 
    of the product if one was submitted.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        # if form valid
        if form.is_valid():
            product = form.save()  # To store the product
            messages.success(request, 'Successfully added product!')
            # update the redirect url to that of the product added
            return redirect(reverse('product_detail', args=[product.id]))  # redirect to the products detail page
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')  # if any errors alert user to check form
    else:
        form = ProductForm()  # this empty form instantiation ensures it doesn't wipe out the form errors.
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


def edit_product(request, product_id):
    """ Edit a product in the store """
    product = get_object_or_404(Product, pk=product_id)  # prefill the form with the product details
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)  # tell it the specific instance we'd like to update is the product obtained above
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))  # redirect to the product detail page using the product id.
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')  # return the form which will have the errors attached.
    else:
        form = ProductForm(instance=product)  # instantiating a product form using the product
        messages.info(request, f'You are editing {product.name}')  # info message 

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


def delete_product(request, product_id):
    """ Delete a product from the store
    whenever someone makes a request to products/delete/ some product id.
    product deleted
    """
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))