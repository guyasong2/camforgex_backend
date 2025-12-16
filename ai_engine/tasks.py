from celery import shared_task
from django.utils import timezone
from django.core.files.base import File
from django.core.files import File as DjangoFile
from django.conf import settings
import os
import uuid
from .services import AudioProcessor, ProcessParams
from music.models import ProcessingJob, Track

@shared_task(bind=True)
def process_track_task(self, job_id: int):
    job = ProcessingJob.objects.select_related('track').get(id=job_id)
    track = job.track

    try:
        job.state = ProcessingJob.State.RUNNING
        job.progress = 5
        job.save(update_fields=['state', 'progress'])

        params = ProcessParams(**job.params)
        export_ext = 'mp3' if params.export_format.lower() == 'mp3' else 'wav'

        output_dir = os.path.join(settings.MEDIA_ROOT, 'processed', str(track.owner_id))
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, f'{uuid.uuid4()}.{export_ext}')

        meta = AudioProcessor.process(track.original_file.path, out_path, params)

        with open(out_path, 'rb') as f:
            job.output_file.save(os.path.basename(out_path), DjangoFile(f), save=True)

        # Update track
        track.processed_file = job.output_file
        track.duration_seconds = meta.get('duration_seconds')
        track.bpm = meta.get('bpm')
        track.status = Track.Status.PROCESSED
        track.save(update_fields=['processed_file', 'duration_seconds', 'bpm', 'status'])

        job.progress = 100
        job.state = ProcessingJob.State.DONE
        job.finished_at = timezone.now()
        job.append_log('Processing completed successfully.')
        job.save(update_fields=['progress', 'state', 'finished_at', 'log'])
        return {'ok': True, 'track_id': track.id}
    except Exception as e:
        job.state = ProcessingJob.State.FAILED
        job.append_log(f'ERROR: {e}')
        job.finished_at = timezone.now()
        job.save(update_fields=['state', 'finished_at', 'log'])
        Track.objects.filter(id=track.id).update(status=Track.Status.FAILED)
        raise