from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _  # used for translation

#  CustomClearableFileInput inherits the built-in one
class CustomClearableFileInput(ClearableFileInput):
    clear_checkbox_label = _('Remove')  # override the clear checkbox label
    initial_text = _('Current Image')  #  initial text the input text 
    input_text = _('')  # template name With our own values
    template_name = 'products/custom_widget_templates/custom_clearable_file_input.html'  # inside the product apps templates folder I'll create that new template.Making sure its name and location matches what's in our class
