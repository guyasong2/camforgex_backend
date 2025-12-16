from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        ARTIST = 'ARTIST', 'Artist'
        PROMOTER = 'PROMOTER', 'Promoter'

    class PromoterType(models.TextChoices):
        DJ = 'DJ', 'DJ'
        TAXI = 'TAXI', 'Taxi Driver'
        INFLUENCER = 'INFLUENCER', 'Influencer'
        OTHER = 'OTHER', 'Other'

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.ARTIST)
    display_name = models.CharField(max_length=120, blank=True)
    promoter_type = models.CharField(max_length=20, choices=PromoterType.choices, blank=True)
    is_promoter_approved = models.BooleanField(default=False)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)

    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"