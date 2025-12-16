from django.contrib import admin
from .models import Campaign, Assignment, PlayEvent

admin.site.register(Campaign)
admin.site.register(Assignment)
admin.site.register(PlayEvent)