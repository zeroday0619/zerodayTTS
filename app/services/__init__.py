import os
from itertools import cycle
from typing import List

import discord
from discord.ext import tasks
from discord.ext.commands import Bot
from discord.flags import Intents

from .logger import generate_log


class ZerodayCore(Bot):
    __slots__ = (
        "message", "intents"
    )

    def __init__(self, message: List[str], intents: Intents, discord_token=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = generate_log()
        self.message = cycle(message)
        self.intents = intents
        self.discord_token = discord_token or os.environ.get("DISCORD_TOKEN")

    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user}")
        await self.change_status.start()

    @tasks.loop(seconds=10)
    async def change_status(self):
        msg = self.message
        await self.change_presence(
            status=discord.Status.online, activity=discord.Game(name=next(msg))
        )

    def launch(self):
        try:
            self.run(self.discord_token)
        except KeyboardInterrupt:
            pass
