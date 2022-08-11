from abc import ABCMeta
from typing import List, Optional

from discord.flags import Intents

from app.services import ZerodayCore
from app.services.logger import LogDecorator


class ZerodayTTS(ZerodayCore, metaclass=ABCMeta):
    __slots__ = ("message", "intents")

    def __init__(
        self,
        message: List[str],
        intents: Intents,
        discord_token: Optional[str] = None,
        *args,
        **kwargs
    ):
        self.intents = intents
        super().__init__(message, intents, discord_token, *args, **kwargs)

    async def on_ready(self):
        await self.load_extensions(["cogs.system", "cogs.tts"])

    @LogDecorator
    async def load_extensions(self, cogs: Optional[List[str]]) -> None:
        for cog in cogs:
            if cog is None:
                return None
            await self.load_extension(cog)
        return None
