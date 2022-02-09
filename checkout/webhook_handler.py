from django.http import HttpResponse

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
        """
        intent = event.data.object
        print(intent)
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)


    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
