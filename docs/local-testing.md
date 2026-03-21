# Local Testing Guide

This guide explains how to test GhostBrain locally using your computer's microphone, without setting up Twilio phone numbers or webhooks.

## Overview

GhostBrain provides two methods for local testing:

1. **PyAudio Method** (Recommended) - Direct microphone access
2. **Daily Method** - WebRTC-based with shareable rooms

Both methods use the same AI pipeline as production but bypass Twilio's telephony layer.

## Prerequisites

### Required API Keys

You'll need API keys from these services (all offer free tiers):

1. **Deepgram** - For speech-to-text
   - Sign up at: https://console.deepgram.com/signup
   - Get API key from: Dashboard → API Keys
   - Free tier: $200 credit

2. **Groq** - For LLM inference
   - Sign up at: https://console.groq.com/
   - Get API key from: API Keys section
   - Free tier: Generous rate limits

3. **OpenAI** - For text-to-speech
   - Sign up at: https://platform.openai.com/
   - Get API key from: API Keys section
   - Free tier: $5 credit for new accounts

### Environment Setup

Create a `.env` file in the project root:

```bash
# Required API Keys
GHOST_BRAIN_DEEPGRAM_API_KEY=your_deepgram_key_here
GHOST_BRAIN_GROQ_API_KEY=your_groq_key_here
GHOST_BRAIN_OPENAI_API_KEY=your_openai_key_here

# Optional: For Daily method
DAILY_API_TOKEN=your_daily_token_here

# Optional: Twilio (not needed for local testing)
GHOST_BRAIN_TWILIO_ACCOUNT_SID=optional
GHOST_BRAIN_TWILIO_AUTH_TOKEN=optional
```

## Method 1: PyAudio (Recommended)

### Installation

1. **Install system dependencies:**

   **macOS:**
   ```bash
   brew install portaudio
   ```

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install portaudio19-dev python3-pyaudio
   ```

   **Windows:**
   ```bash
   # PyAudio wheels usually include PortAudio
   # If not, download from: http://www.portaudio.com/
   ```

2. **Install Python dependencies:**
   ```bash
   pip install pyaudio
   ```

### Running the Test

1. **Ensure your microphone is connected and working**

2. **Run the test script:**
   ```bash
   hatch run python -m ghost_brain.local_mic_test
   ```

3. **You should see:**
   ```
   ============================================================
   🎤 Ghost Brain Local Microphone Test
   ============================================================

   Instructions:
     • Speak clearly into your microphone
     • Wait for the bot to finish speaking before responding
     • Press Ctrl+C to stop and save the transcript

   Starting... Say hello to begin!
   ```

4. **Start talking!** The bot will:
   - Transcribe your speech in real-time
   - Generate intelligent responses
   - Speak back to you through your speakers

5. **End the session:** Press `Ctrl+C` to stop. The transcript will be:
   - Saved to `local_mic_transcript.txt`
   - Printed to your console

### Troubleshooting PyAudio

**"Microphone not found" errors:**
```bash
# List available audio devices
python -c "import pyaudio; p = pyaudio.PyAudio(); print([p.get_device_info_by_index(i) for i in range(p.get_device_count())])"
```

**Permission errors on macOS:**
- Go to System Settings → Privacy & Security → Microphone
- Ensure Terminal/IDE has microphone access

**Audio feedback/echo:**
- Use headphones instead of speakers
- Reduce speaker volume
- Increase VAD threshold in the code

## Method 2: Daily WebRTC

### Overview

Daily provides WebRTC-based audio transport that works in browsers. This method is useful for:
- Testing with remote team members
- Browser-based testing
- When PyAudio has compatibility issues

### Installation

No additional installation needed - Daily is included in the Pipecat dependencies.

### Running the Test

1. **Optional: Set Daily API token** (for room creation):
   ```bash
   export DAILY_API_TOKEN=your_daily_token
   ```

   Without a token, you can still join existing rooms.

2. **Run the test script:**
   ```bash
   hatch run python -m ghost_brain.local_test
   ```

3. **The script will output a room URL:**
   ```
   Created new room: https://your-domain.daily.co/your-room-name
   Open this URL in a browser to join the conversation
   ```

4. **Open the URL in a web browser** and allow microphone access

5. **Start talking** through your browser

### Joining an Existing Room

To join a specific Daily room:
```bash
DAILY_ROOM_URL=https://your-domain.daily.co/existing-room hatch run python -m ghost_brain.local_test
```

## How It Works

### Audio Flow

```
Your Microphone
      ↓
PyAudio/Daily Capture (16kHz PCM)
      ↓
Pipecat Pipeline
      ├─→ Deepgram STT (speech → text)
      ├─→ Groq LLM (text → response)
      └─→ OpenAI TTS (response → speech)
      ↓
Your Speakers
```

### Key Differences from Production

| Component | Production (Twilio) | Local Testing |
|-----------|-------------------|---------------|
| Audio Input | Phone call (8kHz) | Microphone (16kHz) |
| Transport | WebSocket | PyAudio/Daily |
| Latency | ~500-850ms | ~300-500ms |
| Audio Quality | Telephony grade | Full quality |
| Accessibility | Phone number | Local only |

### Voice Pipeline Components

1. **Voice Activity Detection (VAD)**
   - Silero VAD model
   - Detects speech vs. silence
   - Prevents interruptions
   - Configurable sensitivity

2. **Speech-to-Text (STT)**
   - Deepgram Nova-2 model
   - Real-time streaming
   - High accuracy
   - Automatic punctuation

3. **Language Model (LLM)**
   - Llama 3.1 70B via Groq
   - Conversational context
   - Interview-style responses
   - Customizable personality

4. **Text-to-Speech (TTS)**
   - OpenAI TTS-1 model
   - "Alloy" voice
   - Natural intonation
   - Low latency

## Customization

### Changing the System Prompt

Edit `local_mic_test.py` or `local_test.py`:

```python
llm = GroqLLMService(
    api_key=self.settings.groq_api_key,
    model="llama-3.3-70b-versatile",
    system_instruction=(
        "You are a helpful assistant specializing in technical interviews. "
        "Ask probing questions about the candidate's experience. "
        "Keep responses concise and professional."
    ),
)
```

### Adjusting Audio Settings

**VAD Sensitivity:**
```python
vad_analyzer = SileroVADAnalyzer(
    sample_rate=16000,
    params=VADParams(
        stop_secs=0.5,      # How long to wait after speech stops
        min_volume=0.1,     # Minimum volume threshold
    ),
)
```

**Audio Quality:**
```python
# In LocalAudioTransport.__init__
self.sample_rate = 16000  # Can increase to 24000 or 48000
self.chunk_size = 1024     # Larger = more latency, smaller = more CPU
```

### Using Different Models

**Different LLM:**
```python
# Example: Use Mixtral instead
llm = GroqLLMService(
    api_key=self.settings.groq_api_key,
    model="mixtral-8x7b-32768",  # Faster, smaller model
    # ... rest of config
)
```

**Different Voice:**
```python
# OpenAI voices: alloy, echo, fable, onyx, nova, shimmer
tts = OpenAITTSService(
    api_key=self.settings.openai_api_key,
    voice="nova",  # Different voice
    model="tts-1-hd",  # Higher quality version
)
```

## Performance Tips

### Reducing Latency

1. **Use wired internet** instead of WiFi
2. **Close unnecessary applications** to free CPU
3. **Use a good quality microphone** to reduce STT errors
4. **Adjust VAD settings** to be less conservative:
   ```python
   params=VADParams(stop_secs=0.2)  # Faster cutoff
   ```

### Improving Accuracy

1. **Speak clearly** and at normal pace
2. **Minimize background noise**
3. **Use headphones** to prevent echo
4. **Position microphone correctly** (6-12 inches from mouth)

## Common Issues

### "No module named 'pyaudio'"
```bash
pip install pyaudio
# or
hatch run pip install pyaudio
```

### "API key not found"
Ensure your `.env` file has all required keys:
```bash
cat .env | grep GHOST_BRAIN_
```

### "Connection refused" or timeout errors
Check your firewall isn't blocking:
- Deepgram API: `api.deepgram.com:443`
- Groq API: `api.groq.com:443`
- OpenAI API: `api.openai.com:443`

### High CPU usage
- Reduce sample rate to 8000 Hz
- Increase chunk size to 2048
- Check for other CPU-intensive processes

### Audio drops or stuttering
- Check your internet connection stability
- Try reducing concurrent applications
- Ensure audio drivers are up to date

## Testing Scenarios

### Basic Conversation Test
1. Start the bot
2. Say: "Hello, can you hear me?"
3. Wait for response
4. Have a brief conversation
5. Check transcript for accuracy

### Interruption Handling
1. Start speaking
2. While bot is responding, try to interrupt
3. VAD should handle this gracefully

### Long Form Response
1. Ask a complex question requiring detailed answer
2. Verify bot can speak for extended periods
3. Check audio doesn't cut off mid-sentence

### Silence Handling
1. Start the bot
2. Stay silent for 10+ seconds
3. Bot should wait patiently
4. Resume speaking - bot should respond normally

## Next Steps

After successful local testing:

1. **Deploy to Cloud Run** - See [deployment guide](deployment.md)
2. **Set up Twilio** - Configure phone numbers and webhooks
3. **Add monitoring** - Set up logging and alerts
4. **Customize personality** - Adjust system prompts for your use case
5. **Implement analytics** - Track conversation metrics
