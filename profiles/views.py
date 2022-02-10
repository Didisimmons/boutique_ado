from django.shortcuts import render, get_object_or_404

from .models import UserProfile
from .forms import UserProfileForm



def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)  # Get the profile for the current user. And then return it to the template.

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')

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
        'on_profile_page': True
    }

    return render(request, template, context)

    
