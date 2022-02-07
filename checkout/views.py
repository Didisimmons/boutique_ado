from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from bag.contexts import bag_contents

import stripe 


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # retrieve bag from session
    bag = request.session.get('bag', {})
    if not bag:
        # if there's nothing present in the bag 
        messages.error(request, "There's nothing in your bag at the moment")
        # This will prevent people from manually accessing the URL by typing /checkout
        return redirect(reverse('products')) 
   
    # to get the python dictionary from bag app
    # to calculate the current bag total 
    current_bag = bag_contents(request)
    # retrieve grand total from current bag
    total = current_bag['grand_total']
    stripe_total = round(total * 100)
    # creating payment intent
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    print(intent)

    # an instace for our order form
    order_form = OrderForm()

    # if you forget your public_key
    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')
    # create template
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }
    return render(request, template, context)
