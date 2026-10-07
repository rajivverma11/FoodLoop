import tempfile
import time
import wave

import sounddevice as sd

from logger import setup_logger


logger = setup_logger(__name__)

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "int16"

DEFAULT_COUNTDOWN = 5
DEFAULT_DURATION = 10


def record_audio(
    duration: int = DEFAULT_DURATION,
    countdown: int = DEFAULT_COUNTDOWN,
) -> str:
    """
    Count down, record audio from the microphone,
    and save it as a temporary WAV file.

    Args:
        duration: Number of seconds to record.
        countdown: Number of seconds before recording starts.

    Returns:
        Path to the temporary WAV file.
    """

    print("\nGet ready to speak...\n")

    # -------------------------------------------------
    # Countdown before recording
    # -------------------------------------------------

    for seconds_remaining in range(countdown, 0, -1):
        print(f"{seconds_remaining}...")
        time.sleep(1)

    print("\n🎤 Speak now!\n")

    logger.info(
        f"Recording audio for {duration} seconds"
    )

    # -------------------------------------------------
    # Record microphone audio
    # -------------------------------------------------

    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
    )

    sd.wait()

    logger.info("Recording completed")

    print("\nRecording completed.")

    # -------------------------------------------------
    # Create temporary WAV file
    # -------------------------------------------------

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False,
    )

    temp_file.close()

    # -------------------------------------------------
    # Write recorded audio
    # -------------------------------------------------

    with wave.open(temp_file.name, "wb") as wav_file:

        wav_file.setnchannels(CHANNELS)

        # int16 = 2 bytes
        wav_file.setsampwidth(2)

        wav_file.setframerate(SAMPLE_RATE)

        wav_file.writeframes(
            audio.tobytes()
        )

    logger.info(
        f"Temporary audio created: {temp_file.name}"
    )

    return temp_file.name