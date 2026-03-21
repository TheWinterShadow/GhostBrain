"""Ghost Brain: voice-interviewer bot with Pipecat, Twilio, and GCP."""

from ghost_brain.__about__ import __version__
from ghost_brain.app import app

__all__ = ["__version__", "app"]
