"""Automated speech recognition in Rhasspy using Pocketsphinx."""
import io
import logging
import os
import time
import typing
import wave
from pathlib import Path

from google.auth import environment_vars
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from rhasspyasr import Transcriber, Transcription, TranscriptionToken

_LOGGER = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


class GoogleCloudTranscriber(Transcriber):
    """Speech to text with Google Cloud Speech-to-text API."""

    def __init__(
            self,
            credentials_file: Path,
            language_code: str,
            debug: bool = False,
    ):
        self.credentials_file = credentials_file
        self.language_code = language_code
        self.debug = debug
        os.environ[environment_vars.CREDENTIALS] = str(credentials_file)
        self.client = speech.SpeechClient()

    def transcribe_wav(self, wav_bytes: bytes) -> typing.Optional[Transcription]:
        """Speech to text from WAV data."""

        # Compute WAV duration
        audio_data: bytes = bytes()
        with io.BytesIO(wav_bytes) as wav_buffer:
            with wave.open(wav_buffer) as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                wav_duration = frames / float(rate)

                # Extract raw audio data
                # TODO do we need this?
                audio_data = wav_file.readframes(wav_file.getnframes())

        # Process data as an entire utterance
        start_time = time.perf_counter()
        text, confidence = self._transcribe_wav(wav_bytes)

        transcribe_seconds = time.perf_counter() - start_time
        _LOGGER.debug("Decoded audio in %s second(s)", transcribe_seconds)

        if text is not None:
            return Transcription(
                text=text,
                likelihood=confidence,
                transcribe_seconds=transcribe_seconds,
                wav_seconds=wav_duration
            )

        return None

    def _transcribe_wav(self, wav_data: bytes) -> [str, float]:
        """POST to remote server and return response."""
        headers = {"Content-Type": "audio/wav"}
        _LOGGER.debug(
            "POSTing %d byte(s) of WAV data to Google Cloud STT", len(wav_data)
        )

        audio = types.RecognitionAudio(content=wav_data)
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            model='command_and_search',
            language_code=self.language_code)

        response = self.client.recognize(config, audio)
        if len(response.results) == 0:
            _LOGGER.debug("No results returned.")
            return None, 0

        result = response.results[0].alternatives[0]

        _LOGGER.debug("Transcription confidence: %s", result.confidence)
        return result.transcript, result.confidence

    def transcribe_stream(
            self,
            audio_stream: typing.Iterable[bytes],
            sample_rate: int,
            sample_width: int,
            channels: int,
    ) -> typing.Optional[Transcription]:
        """Speech to text from an audio stream."""
        raise NotImplementedError('Stream recognition not implemented yet.')

    def stop(self):
        """Stop the transcriber."""
        pass

    def __repr__(self) -> str:
        return (
            "GoogleCloudTranscriber("
            f"language_code={self.language_code})"
            ")"
        )
