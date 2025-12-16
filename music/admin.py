from django.contrib import admin
from .models import Track, ProcessingJob

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'status', 'bpm', 'created_at')
    list_filter = ('status',)

@admin.register(ProcessingJob)
class ProcessingJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'track', 'state', 'progress', 'created_at', 'finished_at')
    list_filter = ('state',)