from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q  # generate search query
from .models import Product

# Create your views here.


def all_products(request):
    """ A view to show all products, including sorting and search queries
    the context allows us to send things back to the template"""
    # return all products from database
    products = Product.objects.all()
    # start with it as none at the top of this view to ensure we don't get an error
    # when loading the products page without a search term
    query = None

    if request.GET:
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

    context = {
        'products': products,
        'search_item': query,
    }
    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)