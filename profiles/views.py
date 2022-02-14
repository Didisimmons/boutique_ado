from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from .forms import UserProfileForm

from checkout.models import Order

# only logged in users should have access to this view
@login_required
def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)  # Get the profile for the current user. And then return it to the template.

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)  # Create a new instance of the user profile form and the instance being updated is the profile above
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Update failed. Please ensure the form is valid.')
    else:
        form = UserProfileForm(instance=profile)  # Populate it with the user's current profile information.
    """
    use the profile and the related name on the order model.
    To get the users orders and return those to the template
    """
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True  # This simple change will make it so the shopping bag only shows up in the success message when we're not on the profile page.
    }

    return render(request, template, context)


def order_history(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)  # retrieve order

    # message letting the user know they're looking at a past order confirmation.
    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    template = 'checkout/checkout_success.html'
    # template for rendering order confirmation.
    context = {
        'order': order,
        'from_profile': True,  # used to check in that template if the user got there via the order history view.
    }

    return render(request, template, context)