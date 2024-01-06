class StripeWH_Handler:
    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(content=f'Unhandled webhook received: {event["type"]}', status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        # Handle the payment confirmation here
        # You'll likely need to update the order status, send confirmation emails, etc.
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)

    # Add more handlers as needed for different Stripe events
    
    
    
    # return to fix this later one 