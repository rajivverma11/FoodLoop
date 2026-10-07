from config import openai_client
from pathlib import Path

from logger import setup_logger

logger = setup_logger(__name__)




def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribe a WAV audio file into text using OpenAI speech-to-text.

    Args:
        audio_file_path: Path to the recorded WAV file.

    Returns:
        Transcribed text.
    """

    logger.info(f"Transcribing audio: {audio_file_path}")

    try:
        with open(audio_file_path, "rb") as audio_file:

            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )

        text = transcription.text.strip()

        logger.info("Audio transcription completed")
        logger.info(f"Transcribed text: {text}")

        return text

    except FileNotFoundError:
        logger.error(
            f"Audio file not found: {audio_file_path}"
        )
        raise

    except Exception as e:
        logger.error(
            f"Audio transcription failed: {e}"
        )
        raise

    finally:
        audio_path = Path(audio_file_path)

        if audio_path.exists():
            audio_path.unlink()
            logger.info("Temporary recording deleted")