"""Command-line interface to rhasspy-asr-google"""
import argparse
import dataclasses
import json
import logging
import os
import sys
import wave
from pathlib import Path

from . import GoogleCloudTranscriber

_LOGGER = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


def main():
    """Main method."""
    args = get_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    _LOGGER.debug(args)

    # Dispatch to appropriate sub-command
    args.func(args)


# -----------------------------------------------------------------------------


def get_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(prog="rhasspy-asr-google")
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to the console"
    )

    # Create subparsers for each sub-command
    sub_parsers = parser.add_subparsers()
    sub_parsers.required = True
    sub_parsers.dest = "command"

    # -------------------------------------------------------------------------

    # Transcribe settings
    transcribe_parser = sub_parsers.add_parser(
        "transcribe", help="Do speech to text on one or more WAV files"
    )
    transcribe_parser.set_defaults(func=transcribe)

    transcribe_parser.add_argument(
        "wav_file", nargs="*", help="WAV file(s) to transcribe"
    )
    transcribe_parser.add_argument(
        "--credentials",
        required=True,
        help="Path to Google Cloud credentials file (json)",
    )
    transcribe_parser.add_argument(
        "--language-code", required=True, help="Language code for Google Cloud STT API"
    )
    transcribe_parser.add_argument(
        "--frames-in-chunk",
        type=int,
        default=1024,
        help="Number of frames to process at a time",
    )

    return parser.parse_args()


# -----------------------------------------------------------------------------


def transcribe(args: argparse.Namespace):
    """Transcribes WAV file(s)"""
    # Load transcriber
    args.credentials_file = Path(args.credentials)
    args.language_code = args.language_code

    transcriber = GoogleCloudTranscriber(
        args.credentials_file,
        args.language_code,
        debug=args.debug,
    )

    try:
        if args.wav_file:
            # Transcribe WAV files
            for wav_path in args.wav_file:
                _LOGGER.debug("Processing %s", wav_path)
                wav_bytes = open(wav_path, "rb").read()
                result = transcriber.transcribe_wav(wav_bytes)
                print_json(result)
        else:
            # Read WAV data from stdin
            if os.isatty(sys.stdin.fileno()):
                print("Reading WAV data from stdin...", file=sys.stderr)

            # Stream in chunks
            with wave.open(sys.stdin.buffer, "rb") as wav_file:

                def audio_stream(wav_file, frames_in_chunk):
                    num_frames = wav_file.getnframes()
                    try:
                        while num_frames > frames_in_chunk:
                            yield wav_file.readframes(frames_in_chunk)
                            num_frames -= frames_in_chunk

                        if num_frames > 0:
                            # Last chunk
                            yield wav_file.readframes(num_frames)
                    except KeyboardInterrupt:
                        pass

                result = transcriber.transcribe_stream(
                    audio_stream(wav_file, args.frames_in_chunk),
                    wav_file.getframerate(),
                    wav_file.getsampwidth(),
                    wav_file.getnchannels(),
                )

                print_json(result)
    except KeyboardInterrupt:
        pass
    finally:
        transcriber.stop()


def print_json(result):
    """Print data class as JSON"""
    json.dump(dataclasses.asdict(result), sys.stdout)
    print("")


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
