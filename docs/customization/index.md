# Customizing GhostBrain

GhostBrain is built on top of [Pipecat](https://github.com/pipecat-ai/pipecat), a highly modular framework for real-time voice and multimodal AI. This makes it incredibly easy to swap out models, add new capabilities, or change the flow of the conversation without having to rewrite the core networking and streaming logic.

## The Pipecat Pipeline

The heart of GhostBrain is defined in `src/ghost_brain/core/pipeline.py`. It constructs a sequential stream of data frames:

```python
pipeline = Pipeline([
    transport.input(),    # Receives audio from user
    stt,                  # Converts audio -> text
    user_agg,             # Aggregates text into LLM Context
    llm,                  # Generates text response
    tts,                  # Converts text -> audio
    transport.output(),   # Sends audio to user
    assistant_agg,        # Appends assistant's response to history
])
```

Because of this modular design, replacing Groq with OpenAI, or Deepgram with AssemblyAI, is simply a matter of swapping out the variable initialization.

## Customization Guides

Choose a guide below to start modifying GhostBrain for your specific use case:

* **[Adding Tools](tools.md)**: Empower the LLM to call external APIs, fetch data, or query databases during the call.
* **[Switching the STT](stt.md)**: Change the Speech-to-Text provider (e.g., to Whisper, Gladia, or AssemblyAI).
* **[Switching the LLM (Brain)](llm.md)**: Change the language model provider (e.g., to OpenAI, Anthropic, or Together AI).
* **[Switching the TTS](tts.md)**: Change the Text-to-Speech voice provider (e.g., to ElevenLabs or Cartesia).
* **[Custom Context & Prompts](context.md)**: Inject dynamic data (RAG) before the call starts or customize the system personality.
