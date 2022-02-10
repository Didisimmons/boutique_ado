from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county',)
    # This is going to override the init method of the form which will allow us to customize it 
    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        # we call the default init method to set the form up as it would be by default.
        super().__init__(*args, **kwargs)
        placeholders = {
            # created a dictionary of placeholders which will show up
            # in the form fields rather than having clunky looking labels
            # and empty text boxes in the template
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County, State or Locality', 
        }

        """
        setting the autofocus attribute on the full name field to true
        so the cursor will start in the full name field when the user loads the page.
        """
        self.fields['full_name'].widget.attrs['autofocus'] = True
        """
        iterate through the forms fields adding a star to the placeholder
        if it's a required field on the model.
        """
        for field in self.fields:
            if field != 'country':  # if the field is not equal to country , make the other fields mandatory 
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                # Setting all the placeholder attributes to their values in the dictionary above.
                self.fields[field].widget.attrs['placeholder'] = placeholder
            """
            Adding a CSS class(stripe-style-input) that would be applied on the stripe
            classes in checkout.css  we'll use later. Then removing the form fields labels.
            Since we won't need them given the placeholders are now set."""
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False