from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from checkout.webhook_handler import StripeWH_Handler

import stripe

@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe"""
    # Setup
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=e, status=400)

    """
    by using a class we can make our work reusable such that we
    could import it into other projects,Subclass it to override the methods.
    Or even open-source it and share it publicly.
    """
    # Set up a webhook handler
    handler = StripeWH_Handler(request)

    """
    create a dictionary and the dictionaries keys will be
    the names of the webhooks coming from stripe.
    While its values will be the actual methods inside the handler.
    """
    # Map webhook events to relevant handler functions
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }

    """
    get the type of the event from stripe. So this will
    return something like payment intent.succeeded or
    payment intent.payment failed.
    """
    # Get the webhook type from Stripe
    event_type = event['type']

    # If there's a handler for it, get it from the event map
    # Use the generic one by default,look up the key in the dictionary.
    # At this point, event handler is nothing more than an alias for whatever function we pulled out of the dictionary.
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the event handler with the event to get the response from the webhook handler
    response = event_handler(event)
    return response