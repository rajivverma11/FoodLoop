from pathlib import Path
import tempfile

import sounddevice as sd
import soundfile as sf
from config import openai_client

from logger import setup_logger


logger = setup_logger(__name__)




def speak_text(text: str) -> None:
    """
    Convert text to speech using OpenAI TTS
    and play the generated audio.

    Args:
        text: Text that should be spoken.
    """

    if not text or not text.strip():
        logger.warning("No text provided to speaker")
        return

    logger.info("Generating speech")

    temp_file_path = None

    try:
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as temp_file:
            temp_file_path = temp_file.name

        # Generate speech
        with openai_client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="wav",
        ) as response:
            response.stream_to_file(
                Path(temp_file_path)
            )

        logger.info("Speech generated")

        # Read WAV file
        audio_data, sample_rate = sf.read(
            temp_file_path,
            dtype="float32",
        )

        # Play audio
        logger.info("Playing speech")

        sd.play(
            audio_data,
            sample_rate,
        )

        sd.wait()

        logger.info("Speech playback completed")

    except Exception as e:
        logger.error(
            f"Speech generation/playback failed: {e}"
        )
        raise

    finally:
        if temp_file_path:
            Path(temp_file_path).unlink(
                missing_ok=True
            )