from typing import List, Optional

from discord.flags import ApplicationFlags, Intents

from app.services import ZerodayCore
from app.services.logger import LogDecorator


class ZerodayTTS(ZerodayCore):
    __slots__ = (
        "message",
        "intents"
    )

    def __init__(
        self, message: List[str], intents: Intents, discord_token: Optional[str] = None, *args, **kwargs
    ):
        self.intents = intents
        super().__init__(message, discord_token, *args, **kwargs)

    @LogDecorator
    def load_extensions(self, cogs: Optional[List[str]]) -> None:
        for cog in cogs:
            if cog is None:
                return None
            self.load_extension(cog)
        return None
