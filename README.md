# FoodLoop

FoodLoop is a multi-agent, voice-enabled food delivery assistant built
with LangGraph. It supports both typed chat and voice interaction and
routes each customer request to the appropriate specialist agent.

The application currently supports:

-   Menu discovery and dish recommendations using RAG
-   Order lookup using order ID, tracking ID, or customer email
-   Multi-agent routing for requests that involve both menu and order
    questions
-   Persistent Chroma vector storage for menu data
-   Conversation state using LangGraph checkpointing
-   Voice recording, speech-to-text, and text-to-speech
-   Application logging
-   Automatic cleanup of temporary audio files

## Architecture

``` text
                         User
                           |
                +----------+----------+
                |                     |
             Chat Mode             Voice Mode
                |                     |
                |                 recorder.py
                |                     |
                |                 WAV (temporary)
                |                     |
                |                transcriber.py
                |                     |
                +----------+----------+
                           |
                       User Query
                           |
                           v
                     Orchestrator
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
           Menu          Order          Both
           Agent         Agent         Agents
             |             |
             v             v
       Menu RAG Tool   Order Lookup Tool
             |             |
             v             v
          Chroma         ORDER_DB
             \             /
              \           /
               v         v
                 Synthesizer
                      |
                      v
                 Final Answer
                      |
              +-------+-------+
              |               |
           Terminal        speaker.py
                              |
                              v
                           Speaker
```

## Project Structure

``` text
FoodLoop/
├── agents/
│   ├── menuAgent.py
│   ├── orchestrator.py
│   ├── orderAgent.py
│   ├── prompts.py
│   └── synthesizer.py
│
├── data/
│   ├── __init__.py
│   ├── menu.py
│   └── order.py
│
├── tools/
│   ├── indexMenu.py
│   ├── menuTools.py
│   ├── orderTools.py
│   └── rag.py
│
├── voice/
│   ├── recorder.py
│   ├── speaker.py
│   └── transcriber.py
│
├── chroma_db/
├── config.py
├── graph.py
├── logger.py
├── main.py
├── state.py
├── test.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## Multi-Agent Design

### Orchestrator

The orchestrator analyzes the customer's request and returns a
structured routing decision.

Possible routes are:

``` text
["menu"]
["order"]
["menu", "order"]
```

Examples:

``` text
"I want vegetarian Italian food."
        -> menu

"Where is order ORD-207?"
        -> order

"Where is ORD-209 and recommend an Italian dish."
        -> menu + order
```

### Menu Agent

The Menu Agent handles:

-   Menu searches
-   Dish recommendations
-   Cuisine questions
-   Dietary requirements
-   Price-related requests
-   General food questions

For food-related requests, the agent uses the menu search tool rather
than relying on the LLM's internal knowledge.

### Order Agent

The Order Agent handles order-related questions.

Orders can be searched using:

-   Order ID
-   Tracking ID
-   Customer email

Example:

``` text
Where is my order ORD-207?
```

The agent calls the order lookup tool, which searches the local order
database.

### Both Agents

If a request contains both menu and order questions, both specialist
agents are used.

Example:

``` text
Where is my order ORD-209 and recommend an Italian dish under $15.
```

The menu portion is handled by the Menu Agent and the order portion by
the Order Agent.

### Synthesizer

The Synthesizer creates the final customer-facing response.

For a single-agent request, the specialist response can be returned
directly.

For a multi-agent request, the Synthesizer combines the Menu Agent and
Order Agent responses into one concise answer.

## Menu RAG

FoodLoop uses retrieval-augmented generation for menu discovery.

The menu data is converted into LangChain `Document` objects and
embedded into a persistent Chroma vector database.

``` text
menu.py
   |
   v
indexMenu.py
   |
   v
Embedding Model
   |
   v
Chroma
   |
   v
chroma_db/
```

At query time:

``` text
Customer Question
       |
       v
Query Embedding
       |
       v
Chroma Similarity Search
       |
       v
Relevant Menu Documents
       |
       v
Menu Agent
```

Because Chroma is persistent, the menu does not need to be rebuilt every
time the application starts.

## Voice Architecture

FoodLoop supports an end-to-end voice interaction flow.

``` text
Microphone
    |
    v
recorder.py
    |
    v
Temporary WAV
    |
    v
transcriber.py
    |
    v
Speech-to-Text
    |
    v
LangGraph
    |
    v
Final Answer
    |
    v
speaker.py
    |
    v
Text-to-Speech
    |
    v
Mac Speaker
```

### Recorder

`voice/recorder.py`:

1.  Displays a 5-second countdown.
2.  Records the user's microphone for 10 seconds.
3.  Creates a temporary WAV file.
4.  Returns the temporary file path.

Example:

``` text
Get ready to speak...

5...
4...
3...
2...
1...

🎤 Speak now!
```

### Transcriber

`voice/transcriber.py` sends the temporary recording to OpenAI
speech-to-text and returns the transcription.

After transcription finishes, the temporary microphone recording is
deleted.

### Speaker

`voice/speaker.py` converts the final FoodLoop response into speech.

The generated speech audio is temporary and is deleted after playback.

Therefore, audio files are not intentionally retained after processing.

## Voice Exit Commands

While in voice mode, the user can say commands such as:

``` text
exit
quit
stop
goodbye
exit voice chat
stop voice chat
go back
main menu
```

These commands return the application to the main menu without sending
the command through the agent graph.

The user can also type:

``` text
exit
```

or use `Ctrl+C` to interrupt voice mode.

## State

The LangGraph state is represented by `StackState`.

It contains fields such as:

``` python
messages
user_query
route
menu_response
order_response
final_answer
```

`messages` uses a reducer so new messages can be appended to the
existing conversation state.

## Logging

FoodLoop uses Python's standard `logging` package.

The logger is configured in `logger.py`.

Example:

``` python
from logger import setup_logger

logger = setup_logger(__name__)
```

Application components can then log events with:

``` python
logger.info("Menu Agent started")
logger.warning("No matching menu item found")
logger.error("Order lookup failed")
```

Logs are currently written to standard output and appear in the
terminal.

Example:

``` text
14:25:11 | agents.orchestrator          | INFO    | Routing to: ['order']
14:25:11 | agents.orderAgent            | INFO    | Order Agent started
14:25:12 | agents.orderAgent            | INFO    | Calling tool: lookup_order
14:25:13 | agents.synthesizer           | INFO    | Synthesizer started
```

## Requirements

-   Python 3.11+
-   OpenAI API key
-   Microphone access for voice mode
-   Speaker/audio output for voice responses

Major Python packages include:

-   LangGraph
-   LangChain
-   LangChain OpenAI
-   LangChain Chroma
-   ChromaDB
-   OpenAI
-   Pydantic
-   python-dotenv
-   sounddevice
-   soundfile

## Setup

### 1. Clone or open the project

``` bash
cd FoodLoop
```

### 2. Install dependencies

This project uses `uv`.

``` bash
uv sync
```

If the voice dependencies have not yet been added:

``` bash
uv add sounddevice soundfile
```

### 3. Configure the OpenAI API key

Create a `.env` file in the project root:

``` text
OPENAI_API_KEY=your_openai_api_key
```

Do not commit the `.env` file to source control.

A typical `.gitignore` should include:

``` text
.env
.venv/
__pycache__/
*.pyc
```

## Build the Menu Vector Database

Before running menu searches for the first time, index the menu into
Chroma:

``` bash
uv run python tools/indexMenu.py
```

The resulting persistent vector database is stored under:

``` text
chroma_db/
```

The indexer is designed to avoid re-adding menu IDs that already exist.

## Running FoodLoop

Start the application with:

``` bash
uv run python main.py
```

The application presents two interaction modes plus an exit option:

``` text
==============================
       Welcome to FoodLoop
==============================
1. Chat
2. Voice Chat
3. Exit

Enter your choice:
```

## Chat Mode

Select:

``` text
1
```

Then type requests directly.

Example:

``` text
You: Show me vegetarian Italian food under $15

FoodLoop: I recommend the Margherita Pizza...
```

To return to the main menu:

``` text
exit
```

## Voice Mode

Select:

``` text
2
```

Press Enter when ready to speak.

FoodLoop performs a countdown:

``` text
5...
4...
3...
2...
1...

🎤 Speak now!
```

The application records the request, transcribes it, sends it through
the same LangGraph used by chat mode, and speaks the final response.

## Testing

Run:

``` bash
uv run python test.py
```

Useful test scenarios include:

### Menu-only request

``` text
I want a vegetarian Italian dish under $15.
```

Expected route:

``` text
["menu"]
```

### Order-only request

``` text
Where is my order ORD-207?
```

Expected route:

``` text
["order"]
```

### Multi-agent request

``` text
Where is my order ORD-209 and recommend an Italian dish under $15.
```

Expected route:

``` text
["menu", "order"]
```

### Voice request

A voice test should exercise:

``` text
Recorder
   ->
Transcriber
   ->
LangGraph
   ->
Speaker
```

## Example End-to-End Request

``` text
User:
Where is my order ORD-207 and recommend an Italian dish under $15?

                    |
                    v

Orchestrator:
["menu", "order"]

          +---------+---------+
          |                   |
          v                   v
      Menu Agent          Order Agent
          |                   |
          v                   v
      Chroma RAG           ORDER_DB
          |                   |
          +---------+---------+
                    |
                    v
               Synthesizer
                    |
                    v

FoodLoop:
Your order ORD-207 is out for delivery.
For an Italian option under $15, you could try the
Margherita Pizza for $13.99.
```

## Development Notes

The project intentionally separates responsibilities:

``` text
agents/     -> LLM agent behavior and routing
tools/      -> deterministic operations available to agents
data/       -> menu and order data
voice/      -> recording, transcription, and speech playback
graph.py    -> LangGraph workflow
state.py    -> shared graph state
main.py     -> application entry point
logger.py   -> logging configuration
```

This separation makes individual components easier to test and replace.

## Future Improvements

Potential next steps include:

-   Stop microphone recording automatically when the user stops speaking
-   Add LangGraph human-in-the-loop interruption when an order
    identifier is missing
-   Run Menu and Order agents in parallel for multi-agent requests
-   Improve multi-turn conversation handling
-   Add stronger retrieval filtering for cuisine, dietary tags,
    availability, and price
-   Add structured tracing and LLM observability
-   Add automated unit and integration tests
-   Add a web or mobile user interface

## Summary

FoodLoop demonstrates an end-to-end multi-agent AI application
combining:

``` text
LangGraph orchestration
        +
LLM tool calling
        +
RAG with Chroma
        +
Structured routing
        +
Conversation state
        +
Speech-to-text
        +
Text-to-speech
```

Both chat and voice modes share the same underlying agent graph, keeping
the core application logic independent of the user interface.
