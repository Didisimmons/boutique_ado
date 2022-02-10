from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.contexts import bag_contents

import stripe
import json


@require_POST
def cache_checkout_data(request):
    try:
        """
        a way to determie in the webhoook whether a user had saved the
        save ifo box checked.
        """ 
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            """
            tell it what we want to modify in our case we'll add some metadata.
            Let's add the user who's placing the order.
            Will add whether or not they wanted to save their information.
            And add a JSON dump of their shopping bag
            """
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        bag = request.session.get('bag', {})
        # put form data into a dictionary(fields from checkout form)
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # create instance of form using form data
        order_form = OrderForm(form_data)
        # if form is valid save order
        if order_form.is_valid():  # retrieve client secret if form is valid and split it to get the payment intent id
            """
            By adding commit equals false this helps
            prevent multiple save events from being executed on the database.
            """
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)  # dump shopping to a JSON string set it on the order and save
            order.save()
            # iterate through the bag items to create each line item
            # code similar to context.py
            """
            First we get the Product ID out of the bag.
            Then if its value is an integer we know 
            we're working with an item that doesn't have sizes.
            So the quantity will just be the item data
            """
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        """
                        Otherwise, if the item has sizes. we'll iterate through each size and create a line item accordingly.
                        """
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                # just in case a product isn't found we'll add an error message.
                # Delete the empty order and return the user to the shopping bag page.
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))
            """
            We'll attach whether or not the user wanted to save their profile information to the session.
            And then redirect them to a new page. We'll name the new URL check out success.
            And pass it the order number as an argument.
            """
            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            # if form is not valid the errors would show
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')
    else:
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
        stripe.api_key = stripe_secret_key
        # creating payment intent
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    This is simply going to take the order number
    and render a nice success page letting the user
    know that their payment is complete
    """
    # first check whether the user wanted to save their information by getting that from the session
    save_info = request.session.get('save_info')
    # use the order number to get the order created in the previous view
    # which we'll send back to the template.
    order = get_object_or_404(Order, order_number=order_number)
    # attach a success message letting the user know what their order number is.
    # And that will be sending an email to the email they put in the form.
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    # Finally, I'll delete the user shopping bag from the session since it'll no longer be needed for this session.
    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)