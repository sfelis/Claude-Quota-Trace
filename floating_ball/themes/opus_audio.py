"""Opus theme audio — synthesized ambient loop + downloadable CC0 music tracks."""
import math
import os
import struct
from PyQt6.QtCore import QIODevice, QByteArray, QUrl
from PyQt6.QtMultimedia import QAudioSink, QAudioFormat, QAudioOutput, QMediaPlayer


SAMPLE_RATE = 44100
LOOP_SECONDS = 16
TOTAL_SAMPLES = SAMPLE_RATE * LOOP_SECONDS

# Directory containing downloaded music files
_MUSIC_DIR = os.path.join(os.path.dirname(__file__), "music")


def _sin(phase):
    return math.sin(phase)


def _envelope(t, attack, decay, sustain, release, duration):
    """ADSR envelope returning 0.0-1.0."""
    if t < attack:
        return t / attack
    t -= attack
    if t < decay:
        return 1.0 - (1.0 - sustain) * (t / decay)
    t -= decay
    sustain_dur = duration - attack - decay - release
    if t < sustain_dur:
        return sustain
    t -= sustain_dur
    if t < release:
        return sustain * (1.0 - t / release)
    return 0.0


def _generate_loop():
    """Generate the ambient loop as a list of float samples (-1.0 to 1.0)."""
    samples = [0.0] * TOTAL_SAMPLES

    chords = [
        (220.00, 261.63, 329.63),   # Am: A3, C4, E4
        (174.61, 220.00, 261.63),   # F:  F3, A3, C4
        (261.63, 329.63, 392.00),   # C:  C4, E4, G4
        (196.00, 246.94, 293.66),   # G:  G3, B3, D4
    ]
    chord_samples = SAMPLE_RATE * 4

    # Pad layer
    for chord_idx, (f1, f2, f3) in enumerate(chords):
        start = chord_idx * chord_samples
        for i in range(chord_samples):
            t_sec = i / SAMPLE_RATE
            env = _envelope(t_sec, 0.8, 0.5, 0.7, 1.0, 4.0)
            val = 0.0
            for freq in (f1, f2, f3):
                phase = 2.0 * math.pi * freq * t_sec
                val += 0.5 * _sin(phase)
                val += 0.2 * _sin(phase * 2)
                val += 0.08 * _sin(phase * 3)
            val = val / 3.0 * env * 0.35
            samples[start + i] += val

    # Bass drone
    bass_roots = [110.0, 87.31, 130.81, 98.0]
    for chord_idx, bass_freq in enumerate(bass_roots):
        start = chord_idx * chord_samples
        for i in range(chord_samples):
            t_sec = i / SAMPLE_RATE
            env = _envelope(t_sec, 1.2, 0.5, 0.8, 1.5, 4.0)
            tremolo = 0.85 + 0.15 * _sin(2.0 * math.pi * 0.4 * t_sec)
            phase = 2.0 * math.pi * bass_freq * t_sec
            val = _sin(phase) + 0.3 * _sin(phase * 2)
            val = val / 1.3 * env * tremolo * 0.25
            samples[start + i] += val

    # Shimmer arpeggios
    arp_notes_per_chord = [
        [659.26, 784.0, 880.0, 784.0, 659.26, 784.0, 880.0, 1046.5],
        [698.46, 880.0, 1046.5, 880.0, 698.46, 880.0, 1046.5, 1318.5],
        [783.99, 987.77, 1174.7, 987.77, 783.99, 987.77, 1174.7, 1318.5],
        [783.99, 880.0, 987.77, 880.0, 783.99, 987.77, 1046.5, 1174.7],
    ]
    note_dur = 0.5
    note_samples = int(SAMPLE_RATE * note_dur)

    for chord_idx, arp_notes in enumerate(arp_notes_per_chord):
        chord_start = chord_idx * chord_samples
        for note_idx, freq in enumerate(arp_notes):
            note_start = chord_start + note_idx * note_samples
            for i in range(note_samples):
                if note_start + i >= TOTAL_SAMPLES:
                    break
                t_sec = i / SAMPLE_RATE
                env = _envelope(t_sec, 0.05, 0.1, 0.3, 0.25, note_dur)
                phase = 2.0 * math.pi * freq * t_sec
                val = _sin(phase) * env * 0.12
                samples[note_start + i] += val

    # Crossfade loop edges
    fade_samples = int(SAMPLE_RATE * 0.5)
    for i in range(fade_samples):
        fade_in = i / fade_samples
        fade_out = 1.0 - fade_in
        tail_idx = TOTAL_SAMPLES - fade_samples + i
        samples[i] = samples[i] * fade_in + samples[tail_idx] * fade_out
        samples[tail_idx] = samples[tail_idx] * fade_out

    return samples


def _samples_to_pcm(samples):
    """Convert float samples to Int16 PCM QByteArray."""
    buf = QByteArray()
    buf.reserve(len(samples) * 2)
    for s in samples:
        s = max(-1.0, min(1.0, s))
        buf.append(struct.pack('<h', int(s * 32767)))
    return buf


class _AudioLoop(QIODevice):
    """QIODevice that serves PCM data in a loop."""

    def __init__(self, pcm_data: QByteArray):
        super().__init__()
        self._data = pcm_data
        self._pos = 0

    def readData(self, max_len):
        if len(self._data) == 0:
            return b''
        result = bytearray()
        remaining = max_len
        while remaining > 0:
            chunk_size = min(remaining, len(self._data) - self._pos)
            result.extend(self._data[self._pos:self._pos + chunk_size].data())
            self._pos = (self._pos + chunk_size) % len(self._data)
            remaining -= chunk_size
        return bytes(result)

    def writeData(self, data):
        return -1

    def bytesAvailable(self):
        return len(self._data) + super().bytesAvailable()

    def atEnd(self):
        return False

    def isSequential(self):
        return True


def get_available_tracks():
    """Return list of (name, track_type, path_or_none) for all available tracks.

    track_type is 'synth' for the built-in synthesizer or 'file' for MP3 files.
    Only includes file tracks whose MP3 actually exists on disk.
    """
    tracks = [("Opus Synth", "synth", None)]

    file_tracks = [
        ("Dark Cavern 1", "dark_cavern_ambient_1.ogg"),
        ("Dark Cavern 2", "dark_cavern_ambient_2.ogg"),
        ("Ice Shine Bells", "ice_shine_bells.ogg"),
        ("Distant Wonders", "distant_wonders.ogg"),
    ]

    for name, filename in file_tracks:
        path = os.path.join(_MUSIC_DIR, filename)
        if os.path.isfile(path):
            tracks.append((name, "file", path))

    return tracks


class OpusAudio:
    """Manages opus theme audio playback — synth or MP3 file tracks."""

    def __init__(self):
        # Synth playback
        self._sink = None
        self._loop_device = None
        self._pcm = None

        # File playback
        self._player = None
        self._audio_output = None

        self._playing = False
        self._current_track = -1  # index into get_available_tracks()

    def _ensure_synth_generated(self):
        if self._pcm is None:
            samples = _generate_loop()
            self._pcm = _samples_to_pcm(samples)

    def _stop_synth(self):
        if self._sink:
            self._sink.stop()
            self._sink = None
        if self._loop_device:
            self._loop_device.close()
            self._loop_device = None

    def _stop_file(self):
        if self._player:
            self._player.stop()
            self._player = None
        if self._audio_output:
            self._audio_output = None

    def start(self, track_index=0):
        """Start playing the specified track. 0 = synth, 1+ = file tracks."""
        self.stop()

        tracks = get_available_tracks()
        if track_index < 0 or track_index >= len(tracks):
            return

        name, track_type, path = tracks[track_index]

        if track_type == "synth":
            self._start_synth()
        else:
            self._start_file(path)

        self._playing = True
        self._current_track = track_index

    def _start_synth(self):
        self._ensure_synth_generated()

        fmt = QAudioFormat()
        fmt.setSampleRate(SAMPLE_RATE)
        fmt.setChannelCount(1)
        fmt.setSampleFormat(QAudioFormat.SampleFormat.Int16)

        self._loop_device = _AudioLoop(self._pcm)
        self._loop_device.open(QIODevice.OpenModeFlag.ReadOnly)

        self._sink = QAudioSink(fmt)
        self._sink.setVolume(0.15)
        self._sink.start(self._loop_device)

    def _start_file(self, path):
        self._audio_output = QAudioOutput()
        self._audio_output.setVolume(0.3)

        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._audio_output)
        self._player.setSource(QUrl.fromLocalFile(path))
        self._player.setLoops(QMediaPlayer.Loops.Infinite)
        self._player.play()

    def stop(self):
        """Stop all playback."""
        self._stop_synth()
        self._stop_file()
        self._playing = False
        self._current_track = -1

    def is_playing(self):
        return self._playing

    def current_track_index(self):
        return self._current_track
