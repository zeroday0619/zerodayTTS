import os
import discord
from typing import List
from itertools import cycle
from discord.ext import tasks
from discord.ext.commands import Bot



class ZerodayCore(Bot):
    __slots__ = ("message")
    def __init__(self, message: List[str], discord_token=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = cycle(message)
        self.discord_token = (
            discord_token 
            or  
            os.environ.get("DISCORD_TOKEN")
        )
    
    async def on_ready(self):
        print(f"Logged in as {self.user}")
        await self.change_status.start()
    
    @tasks.loop(seconds=10)
    async def change_status(self):
        msg = self.message
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(
                name=next(msg)
                )
            )

    def launch(self):
        try:
            self.run(self.discord_token)
        except KeyboardInterrupt:
            pass
    