"""Ghostwriter: voice-interviewer bot with Pipecat, Twilio, and GCP."""

from ghostwriter.__about__ import __version__
from ghostwriter.app import app

__all__ = ["__version__", "app"]
