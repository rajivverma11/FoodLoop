from langchain_core.messages import HumanMessage

from graph import graph
from voice.recorder import record_audio
from voice.transcriber import transcribe_audio
from voice.speaker import speak_text
from logger import setup_logger


logger = setup_logger(__name__)


def test_voice_assistant():
    """
    End-to-end test of the FoodLoop voice assistant.

    Flow:
        Microphone
        -> Recorder
        -> Transcriber
        -> LangGraph
        -> Speaker
    """

    logger.info("Starting FoodLoop voice test")

    try:
        # -------------------------------------------------
        # 1. Record user's voice
        # -------------------------------------------------

        print("\nSpeak now...")

        audio_file = record_audio(
            duration=5
        )

        # -------------------------------------------------
        # 2. Convert voice to text
        # transcribe_audio() deletes the temporary
        # recording when it finishes.
        # -------------------------------------------------

        user_query = transcribe_audio(
            audio_file
        )

        if not user_query:
            logger.warning("No speech was detected")
            print("I couldn't understand what you said.")
            return

        print(f"\nYou: {user_query}")

        # -------------------------------------------------
        # 3. Build LangGraph state
        # -------------------------------------------------

        state = {
            "messages": [
                HumanMessage(content=user_query)
            ],
            "user_query": user_query,
            "route": [],
            "menu_response": "",
            "order_response": "",
            "final_answer": "",
        }

        config = {
            "configurable": {
                "thread_id": "voice-test-1"
            }
        }

        # -------------------------------------------------
        # 4. Run LangGraph
        # -------------------------------------------------

        logger.info("Sending query to FoodLoop graph")

        result = graph.invoke(
            state,
            config=config
        )

        # -------------------------------------------------
        # 5. Get final answer
        # -------------------------------------------------

        final_answer = result.get(
            "final_answer",
            ""
        )

        if not final_answer:
            logger.warning(
                "Graph returned no final answer"
            )
            return

        print(f"\nFoodLoop: {final_answer}")

        # -------------------------------------------------
        # 6. Speak final answer
        # speaker deletes its temporary audio file
        # after playback.
        # -------------------------------------------------

        speak_text(final_answer)

        logger.info(
            "FoodLoop voice test completed"
        )

    except Exception as e:

        logger.exception(
            f"Voice test failed: {e}"
        )


if __name__ == "__main__":
    test_voice_assistant()