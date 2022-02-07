from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


def checkout(request):
    # retrieve bag from session
    bag = request.session.get('bag', {})
    if not bag:
        # if there's nothing present in the bag 
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products')) # This will prevent people from manually accessing the URL by typing /checkout

    # an instace for our order form
    order_form = OrderForm()
    # create template
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key':'pk_test_k00xao0P5r64RAYcBGuR9enF002XDNTq52',
        'client_secret': 'test client secret', 
    }

    return render(request, template, context)

