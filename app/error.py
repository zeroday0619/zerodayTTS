from discord.ext import commands


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""
    pass


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""
    pass
