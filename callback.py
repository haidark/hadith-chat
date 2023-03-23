"""Callback handlers used in the app."""
from langchain.callbacks.base import AsyncCallbackHandler

class DiscordCallbackHandler(AsyncCallbackHandler):
    """Callback handler for question generation."""

    def __init__(self):
        pass