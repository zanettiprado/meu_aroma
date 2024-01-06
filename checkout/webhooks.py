import stripe
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .webhook_handler import StripeWH_Handler

@require_POST
@csrf_exempt
def webhook(request):
    # Setup Stripe and the webhook secret from your environment
    stripe.api_key = settings.STRIPE_SECRET_KEY
    wh_secret = settings.STRIPE_WH_SECRET

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

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

    # Instantiate the handler
    handler = StripeWH_Handler(request)

    # Map webhook events to methods
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        # Add more event types and their corresponding handler methods here
    }

    event_type = event['type']
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the handler method and return its response
    response = event_handler(event)
    return response

#return here after finish to review

