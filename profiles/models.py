from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """
    User profile model for storing additional user information.
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    default_phone_number = models.CharField(max_length=20,
                                            null=True,
                                            blank=True)
    default_street_address1 = models.CharField(max_length=80,
                                               null=True,
                                               blank=True)
    default_street_address2 = models.CharField(max_length=80,
                                               null=True,
                                               blank=True)
    default_town_or_city = models.CharField(max_length=40,
                                            null=True,
                                            blank=True)
    default_county = models.CharField(max_length=80,
                                      null=True,
                                      blank=True)
    default_postcode = models.CharField(max_length=20,
                                        null=True,
                                        blank=True)

    def __str__(self):
        return self.user.username
    

class PartnerApplication(models.Model):
    """
    Partner application model for storing partnership applications.
    """
    
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    company_name = models.CharField(max_length=100,
                                    blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    additional_info = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=[('Pending',
                                                       'Pending'),
                                                      ('Approved',
                                                       'Approved'),
                                                      ('Rejected',
                                                       'Rejected')],
                              default='Pending')
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update user profile when a User object is saved.
    """
    

    if created:
        UserProfile.objects.create(user=instance)
    # Existing users: just save the profile
    instance.userprofile.save()