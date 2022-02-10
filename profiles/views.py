from django.shortcuts import render, get_object_or_404

from .models import UserProfile


def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)  # Get the profile for the current user. And then return it to the template.

    template = 'profiles/profile.html'
    context = {
        'profile':profile,
    }

    return render(request, template, context)
