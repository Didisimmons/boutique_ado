from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    # defines the model and the fields we want to include.
    class Meta:
        model = Product
        fields = '__all__'  #  will include all the fields.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()  # retrieve all categories
        # categories to show up in the form using their friendly name
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories] #  create a list of tuples of the friendly names associated with their category ids

        # update the category field on the form.To use friendly_names for choices instead of using the id.The effect of this will be seen in the select box that gets generated in the form
        self.fields['category'].choices = friendly_names
        # iterate through the rest of these fields and set classes on them to make them match the theme of our store.
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
