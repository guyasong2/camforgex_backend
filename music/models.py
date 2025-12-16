import uuid
from django.db import models
from django.conf import settings

def track_upload_path(instance, filename):
    return f"tracks/{instance.owner_id}/{uuid.uuid4()}_{filename}"

def processed_upload_path(instance, filename):
    return f"tracks/{instance.track.owner_id}/processed/{uuid.uuid4()}_{filename}"

class Track(models.Model):
    class Status(models.TextChoices):
        UPLOADED = 'UPLOADED'
        PROCESSING = 'PROCESSING'
        PROCESSED = 'PROCESSED'
        FAILED = 'FAILED'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tracks')
    title = models.CharField(max_length=200)
    original_file = models.FileField(upload_to=track_upload_path)
    processed_file = models.FileField(upload_to=track_upload_path, blank=True, null=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    bpm = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADED)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} ({self.owner})'

class ProcessingJob(models.Model):
    class State(models.TextChoices):
        QUEUED = 'QUEUED'
        RUNNING = 'RUNNING'
        DONE = 'DONE'
        FAILED = 'FAILED'

    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='jobs')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    params = models.JSONField(default=dict)
    state = models.CharField(max_length=20, choices=State.choices, default=State.QUEUED)
    progress = models.PositiveSmallIntegerField(default=0)  
    log = models.TextField(blank=True)
    output_file = models.FileField(upload_to=processed_upload_path, null=True, blank=True)
    celery_task_id = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def append_log(self, text):
        self.log = (self.log or '') + f'\n{text}'
        self.save(update_fields=['log'])