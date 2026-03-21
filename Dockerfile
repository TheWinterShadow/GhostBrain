# Ghost Brain voice bot — production image for Cloud Run.
# Python 3.12, system deps for audio (portaudio), install package via pip.

FROM python:3.12-slim

# System dependencies for audio (Pipecat / Silero VAD, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    portaudio19-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python package from repo (no dev deps)
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

# Non-root user (optional; Cloud Run can run as root)
# USER nobody

EXPOSE 8080
CMD ["uvicorn", "ghost_brain.app:app", "--host", "0.0.0.0", "--port", "8080"]
