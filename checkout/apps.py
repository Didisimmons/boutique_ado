from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'checkout'

    """
    To let django know that there's a new signals module with some listeners in it
    we need to override the ready method and import our signals module
    """
    def ready(self):
        # every time a line item is saved or deleted.
        # Our custom update_total model method will be called.
        # Updating the order totals automatically.
        import checkout.signals
