import os
from dataclasses import dataclass
import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr
from pydub import AudioSegment

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
DEFAULT_DRUM_LOOP = os.path.join(ASSETS_DIR, 'drum_loop_120bpm.wav')  

@dataclass
class ProcessParams:
    noise_reduction_strength: float = 0.6
    add_drums: bool = True
    drum_mix: float = 0.4  # 0..1
    target_bpm: float | None = None
    export_format: str = 'mp3'  # 'mp3' or 'wav'

class AudioProcessor:
    @staticmethod
    def load_audio(path):
        y, sr = librosa.load(path, sr=None, mono=True)
        return y, sr

    @staticmethod
    def estimate_bpm(y, sr):
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        return float(tempo)

    @staticmethod
    def reduce_noise(y, sr, strength):
        # basic spectral gating
        # Estimate noise profile using the first 0.5 seconds
        n_samples = int(0.5 * sr)
        noise_clip = y[:max(1, n_samples)]
        reduced = nr.reduce_noise(y=y, y_noise=noise_clip, sr=sr, prop_decrease=strength, stationary=False)
        return reduced

    @staticmethod
    def time_stretch_to_bpm(y, sr, current_bpm, target_bpm):
        if not target_bpm or current_bpm <= 0:
            return y
        rate = target_bpm / current_bpm
        return librosa.effects.time_stretch(y, rate)

    @staticmethod
    def add_drum_loop(y, sr, target_bpm, mix=0.4, loop_path=DEFAULT_DRUM_LOOP):
        if not os.path.exists(loop_path):
            return y  # fail silently if missing asset

        drum_y, drum_sr = librosa.load(loop_path, sr=sr, mono=True)
        drum_bpm = AudioProcessor.estimate_bpm(drum_y, sr)
        if target_bpm:
            rate = target_bpm / drum_bpm if drum_bpm > 0 else 1.0
            drum_y = librosa.effects.time_stretch(drum_y, rate)

        # Tile drum to cover track duration
        times = int(np.ceil(len(y) / len(drum_y)))
        drum_tiled = np.tile(drum_y, times)[:len(y)]

        # Mix with given ratio
        y_max = np.max(np.abs(y)) or 1.0
        drum_max = np.max(np.abs(drum_tiled)) or 1.0
        y_norm = y / y_max
        drum_norm = drum_tiled / drum_max
        mixed = (1 - mix) * y_norm + mix * drum_norm

        # Normalize to prevent clipping
        mixed = mixed / (np.max(np.abs(mixed)) or 1.0) * 0.9
        return mixed

    @staticmethod
    def export_audio(y, sr, output_path, export_format='mp3'):
        if export_format.lower() == 'wav':
            sf.write(output_path, y, sr)
            return output_path

        # Export mp3 via pydub (requires ffmpeg installed)
        tmp_wav = output_path.replace('.mp3', '.wav')
        sf.write(tmp_wav, y, sr)
        seg = AudioSegment.from_wav(tmp_wav)
        seg.export(output_path, format='mp3', bitrate='192k')
        os.remove(tmp_wav)
        return output_path

    @staticmethod
    def process(input_path, output_path, params: ProcessParams):
        y, sr = AudioProcessor.load_audio(input_path)
        base_bpm = AudioProcessor.estimate_bpm(y, sr)

        # 1) Noise reduction
        y = AudioProcessor.reduce_noise(y, sr, params.noise_reduction_strength)

        # 2) BPM/Time stretch
        y = AudioProcessor.time_stretch_to_bpm(y, sr, base_bpm, params.target_bpm)
        final_bpm = params.target_bpm or base_bpm

        # 3) Optional drum overlay
        if params.add_drums:
            y = AudioProcessor.add_drum_loop(y, sr, final_bpm, params.drum_mix)

        # 4) Export
        AudioProcessor.export_audio(y, sr, output_path, params.export_format)

        return {
            'duration_seconds': len(y) / float(sr),
            'bpm': float(final_bpm),
            'sr': sr
        }