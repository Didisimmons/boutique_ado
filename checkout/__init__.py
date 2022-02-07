# inform django the name of the default config class for the app
default_app_config = 'checkout.apps.CheckoutConfig'

"""
without this file django would be unaware
of our custom ready method so signals would
not work
"""