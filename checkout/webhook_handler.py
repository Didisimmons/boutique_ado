from django.http import HttpResponse
from django.core.mail import send_mail  # assist to send email
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile

import json
import time
"""
Handle Stripe webhooks
The idea here is that for each type of webhook.
We want a different method to handle it which makes them easy to manage.
And makes it easy to add more as stripe adds new ones.
"""


class StripeWH_Handler:
    """
    The init method of the class is a setup method that's called
    every time an instance of the class is created.
    we're going to use it to assign the request as an attribute
    of the class just in case we need to access any attributes
    of the request coming from stripe.
    """
    def __init__(self, request):
        self.request = request

    # It just starts with an underscore since it'll only be used inside this class.
    # use the render_to_string method to render both confirmation email texts into two strings.
    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        cust_email = order.email  # retrieve customers email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})  # context just like we pass to a template
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})
        
        # send the email
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,  # the email we want to send from
            [cust_email]  # a list of emails were sending to, which in this case will be only the customer's email.
        ) 

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        The class method will take the event stripe is sending us
        and simply return an HTTP response indicating it was received.
        print out the payment intent coming from stripe once the user
        makes a payment. With any luck it should have our metadata attached
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        This will be sent each time a user completes the payment process.
        The only reason we're doing this is in case the form isn't
        submitted for some reason.like if the user closes the page
        on the loading screen.
        """
        intent = event.data.object
        pid = intent.id  # retrieve payment intent and shopping bag
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info  # users save info preference from the metadata stripe_element.js

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        # Clean data in the shipping details
        """
        to ensure the data is in the same form as what we want in our database.
        I'll replace any empty strings in the shipping details with none.
        Since stripe will store them as blank strings which is not the same
        as the null value we want in the database.
        """
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        """
        Update profile information if save_info was checked
        remember that we added that handy key in the payment intent called metadata
        which contains the username of the user that placed the order.
        It also contains whether or not they wanted to save their info
        """
        profile = None
        # we can still allow anonymous user to checkout
        username = intent.metadata.username
        # if they're not anonymous let's try to get their profile using their username.
        # If they've got the save info box checked which again comes from the metadata we added.
        # Then we'll want to update their profile by adding the shipping details as their default delivery information
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1
                profile.default_street_address2 = shipping_details.address.line2
                profile.default_county = shipping_details.address.state
                profile.save()
        """
        The first thing then is to check if the order exists already.
        If it does we'll just return a response, and say everything is all set.
        And if it doesn't we'll create it here in the webhook.
        start by assuming the order doesn't exist.
        """
        order_exists = False
        """
        Instead of just immediately going to create the order if it's
        not found in the database by creating a bit of delay
        """
        attempt = 1
        """
        All of this ensures that when we receive a webhook from stripe that a payment has been processed successfully.
        We'll try to find an order with the same customer information and the same grand total,
        Which was created with the exact same shopping bag.And it's associated with the same payment intent.
        get the order using all the information from the payment intent.
        the iexact lookup will provide an exact match but case-insensitive
        """
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True  # if order is found set true
                break  # if order is found
            # This will in effect cause the webhook handler to try to find the order five times over five seconds
            # before giving up and creating the order itself.
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        # If we found the order in the database because it was already created by the form. Let's send it just before returning that response to stripe
        if order_exists:
            self._send_confirmation_email(order) # If the order was created by the webhook handler send the before returning that response to stripe.
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)  # if order is true return a 200 HTTP response to stripe, with the message that we verified the order already exists
        else:
            # if the order does not exist, create it just like we would if the form were submitted (checkout method in views.py)
            order = None
            """
            In this way, the webhook handler can create orders for both authenticated users by attaching their profile.
            And for anonymous users by setting that field to none.
            """
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                """
                still want to iterate through the bag items, the only difference here is
                that we're going to load the bag from the JSON version in the payment intent
                instead of from the session
                """
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            #  if anything goes wrong I'll just delete the order if it was created and return a 500 server error response to stripe
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        self._send_confirmation_email(order)  # If the order was created by the webhook handler send the email
        return HttpResponse(
            # order must have been created by the webhook handler. So we should return a response to stripe indicating that.
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)


    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
