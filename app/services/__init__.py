import asyncio
import os
import signal
from itertools import cycle
from typing import List

import discord
from databases import Database, DatabaseURL
from discord.ext import tasks
from discord.ext.commands import Bot
from discord.flags import Intents

from .logger import generate_log


class ZerodayCore(Bot):
    __slots__ = ("message", "intents")

    _database = Database(url=DatabaseURL(os.environ.get("DATABASE_URL")))

    def __init__(
        self, message: List[str], intents: Intents, discord_token=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.logger = generate_log()
        self.message = cycle(message)
        self.intents = intents
        self.discord_token = discord_token or os.environ.get("DISCORD_TOKEN")

    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user}")
        try:
            await self._database.connect()
            await self.change_status.start()
        except asyncio.CancelledError:
            await self._database.disconnect()
            self.change_status.stop()
            pass

    @tasks.loop(seconds=10)
    async def change_status(self):
        msg = self.message
        await self.change_presence(
            status=discord.Status.online, activity=discord.Game(name=next(msg))
        )

    def launch(self):
        """
        reference code: https://github.com/TeamSayumi/pycord/blob/feature/slash/discord/client.py#L613
        """
        try:
            self.run(self.discord_token)
        except asyncio.CancelledError:
            pass
        except RuntimeError:
            pass
