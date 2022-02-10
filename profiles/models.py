from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_countries.fields import CountryField

"""
creating a user profile model which has a one-to-one
field attached to the user.And each profile can only
be attached to one user.will automatically create a
profile for everyone who signs up
"""
class UserProfile(models.Model):
    """
    A user profile model for maintaining default
    delivery information and order history
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # just like a foreign key except specifies that each user can only have one profile.
    """
    rest of the fields in this model are the delivery information fields we want the
    user to be able to provide defaults for. in the profile we want all these fields to be optional
    so provide null equals true and blank equals true for each of them.
    """
    default_phone_number = models.CharField(max_length=20, null=True, blank=True)
    default_street_address1 = models.CharField(max_length=80, null=True, blank=True)
    default_street_address2 = models.CharField(max_length=80, null=True, blank=True)
    default_town_or_city = models.CharField(max_length=40, null=True, blank=True)
    default_county = models.CharField(max_length=80, null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_country = CountryField(blank_label='Country', null=True, blank=True)

    # return username
    def __str__(self):
        return self.user.username


"""
each time a user object is saved.create a
profile for them if the user has just been created.
Or just save the profile to update it if the user already existed.
"""
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile
    if you had many users who needed profiles created
    do it through the shell by getting all the users.
    And then creating a profile for them in a loop 
    """
    if created:
        UserProfile.objects.create(user=instance)
    # Existing users: just save the profile
    instance.userprofile.save()
