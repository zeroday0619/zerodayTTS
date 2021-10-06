from typing import List, Optional

from app.services import ZerodayCore
from app.services.logger import LogDecorator


class ZerodayTTS(ZerodayCore):
    __slots__ = "message"

    def __init__(
        self, message: List[str], discord_token: Optional[str] = None, *args, **kwargs
    ):
        super().__init__(message, discord_token, *args, **kwargs)

    @LogDecorator
    def load_extensions(self, cogs: Optional[List[str]]) -> None:
        for cog in cogs:
            if cog is None:
                return None
            self.load_extension(cog)
        return None
