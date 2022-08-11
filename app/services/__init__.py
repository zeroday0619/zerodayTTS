import asyncio
import os
from abc import ABCMeta
from itertools import cycle
from typing import List

import discord
from discord.ext import tasks
from discord.ext.commands import AutoShardedBot
from discord.flags import Intents

from .logger import generate_log


class ZerodayCore(AutoShardedBot, metaclass=ABCMeta):
    __slots__ = ("message", "intents")

    def __init__(
        self, message: List[str], intents: Intents, discord_token=None, *args, **kwargs
    ):
        self.intents = intents
        super().__init__(*args, intents=self.intents, **kwargs)
        self.logger = generate_log()
        self.message = cycle(message)
        self.discord_token = discord_token or os.environ.get(
            "ZERODAY_TTS_DISCORD_TOKEN"
        )

    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user}")
        await self.change_status.start()

    @tasks.loop(seconds=10)
    async def change_status(self):
        msg = self.message
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                name=next(msg), type=discord.ActivityType.playing
            ),
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
