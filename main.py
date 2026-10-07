from langchain_core.messages import HumanMessage

from graph import graph
from voice.recorder import record_audio
from voice.transcriber import transcribe_audio
from voice.speaker import speak_text
from logger import setup_logger


logger = setup_logger(__name__)

THREAD_ID = "foodloop-user-1"


def run_graph(user_query: str) -> str:
    """
    Send a user query through the FoodLoop LangGraph
    and return the final answer.
    """

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
            "thread_id": THREAD_ID
        }
    }

    logger.info("Sending query to FoodLoop graph")

    result = graph.invoke(
        state,
        config=config,
    )

    return result.get(
        "final_answer",
        "I'm sorry, I couldn't process your request.",
    )


def chat_mode():
    """
    Run FoodLoop using keyboard input.
    """

    print("\n--- FoodLoop Chat ---")
    print("Type 'exit' to return to the main menu.\n")

    while True:

        user_query = input("You: ").strip()

        if not user_query:
            continue

        if user_query.lower() == "exit":
            print()
            return

        try:

            final_answer = run_graph(
                user_query
            )

            print(
                f"\nFoodLoop: {final_answer}\n"
            )

        except Exception as e:

            logger.exception(
                f"Chat request failed: {e}"
            )

            print(
                "\nFoodLoop: Sorry, something went wrong.\n"
            )


def voice_mode():
    """
    Run FoodLoop using microphone input and spoken responses.
    """

    print("\n--- FoodLoop Voice Chat ---")
    print("Press Enter when you're ready to speak.")
    print("Say 'exit', 'quit', 'stop', or 'goodbye' to return to the main menu.")
    print("You can also type 'exit' before recording.\n")

    exit_commands = {
        "exit",
        "quit",
        "stop",
        "goodbye",
        "exit voice chat",
        "stop voice chat",
        "go back",
        "main menu",
    }

    while True:

        command = input(
            "\nPress Enter to speak (or type 'exit'): "
        ).strip()

        # -----------------------------------------
        # Allow keyboard exit
        # -----------------------------------------

        if command.lower() == "exit":
            print("\nReturning to main menu...\n")
            return

        try:

            # -----------------------------------------
            # Record user
            # -----------------------------------------

            audio_file = record_audio()

            # -----------------------------------------
            # Speech -> text
            # -----------------------------------------

            user_query = transcribe_audio(
                audio_file
            )

            if not user_query:
                print(
                    "\nFoodLoop: I couldn't understand you."
                )
                continue

            print(
                f"\nYou: {user_query}"
            )

            # -----------------------------------------
            # Allow voice exit
            # -----------------------------------------

            normalized_query = (
                user_query
                .lower()
                .strip()
                .rstrip(".!?")
            )

            if normalized_query in exit_commands:

                print(
                    "\nFoodLoop: Returning to the main menu.\n"
                )

                return

            # -----------------------------------------
            # LangGraph
            # -----------------------------------------

            final_answer = run_graph(
                user_query
            )

            print(
                f"\nFoodLoop: {final_answer}\n"
            )

            # -----------------------------------------
            # Speak response
            # -----------------------------------------

            speak_text(
                final_answer
            )

        except KeyboardInterrupt:

            print(
                "\n\nVoice chat interrupted. "
                "Returning to main menu.\n"
            )

            return

        except Exception as e:

            logger.exception(
                f"Voice request failed: {e}"
            )

            print(
                "\nFoodLoop: Sorry, something went wrong.\n"
            )


def main():

    logger.info("FoodLoop application started")

    while True:

        print("\n==============================")
        print("       Welcome to FoodLoop")
        print("==============================")
        print("1. Chat")
        print("2. Voice Chat")
        print("3. Exit")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":

            chat_mode()

        elif choice == "2":

            voice_mode()

        elif choice == "3":

            print("\nGoodbye!")
            logger.info(
                "FoodLoop application stopped"
            )
            break

        else:

            print(
                "\nInvalid choice. Please enter 1, 2, or 3."
            )


if __name__ == "__main__":
    main()