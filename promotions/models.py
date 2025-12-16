import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from music.models import Track

def generate_join_code():
    return uuid.uuid4().hex[:12]

class Campaign(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT'
        ACTIVE = 'ACTIVE'
        PAUSED = 'PAUSED'
        ENDED = 'ENDED'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaigns')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='campaigns')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price_per_play = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.05'))
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_budget = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def can_spend(self, amount: Decimal) -> bool:
        return self.remaining_budget >= amount and self.status == self.Status.ACTIVE

    def spend(self, amount: Decimal):
        if not self.can_spend(amount):
            raise ValueError('Insufficient campaign budget or not active.')
        self.remaining_budget -= amount
        self.save(update_fields=['remaining_budget'])

class Assignment(models.Model):
    class Status(models.TextChoices):
        INVITED = 'INVITED'
        ACCEPTED = 'ACCEPTED'
        REJECTED = 'REJECTED'

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='assignments')
    promoter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignments')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INVITED)
    join_code = models.CharField(max_length=12, unique=True, default=generate_join_code, editable=False, db_index=True)
    payout_per_play = models.DecimalField(max_digits=10, decimal_places=2)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PlayEvent(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='plays')
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    device_id = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ['-timestamp']