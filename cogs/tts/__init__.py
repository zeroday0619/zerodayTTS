from typing import Type

import discord
from discord.app import Option
from discord.app.commands import slash_command
from discord.app.context import ApplicationContext
from discord.ext import commands

from ._core_class import TTSCore

FFMPEG_OPTIONS = {
    "options": "-y",
}



class TTS(TTSCore):
    __slots__ = ("bot", "voice")
    def __init__(self, bot: commands.Bot):
        super(TTS, self).__init__(bot)

    @slash_command()
    async def tts(
        self, ctx: ApplicationContext, *, text: Option(str, "text", required=True)
    ):
        await self.join(ctx)

        status = await self._tts(ctx, text)
        if status == Type[Exception]:
            await ctx.respond("오류가 발생했습니다.")
        if status:
            await ctx.respond(f"[**{ctx.author.name}**] >> {text}")
        else:
            await ctx.respond(f"{ctx.author.name}님이 TTS가 이미 사용중입니다.")

    @slash_command()
    async def connect(self, ctx: ApplicationContext):
        try:
            await self.join(ctx)
        except Exception as e:
            print(e)
            return await ctx.respond("오류가 발생했습니다.")
        await ctx.respond(f"{ctx.author.name}님 정상적으로 보이스 채널에 연결되었습니다.")
        

    @slash_command()
    async def leave(self, ctx: ApplicationContext):
        """Leaves a voice channel."""
        try:
            await self.disconnect(ctx)
        except AttributeError:
            await ctx.respond(content=f"{ctx.author.name}가 음성 채널에 접속하지 않음")
            return
        await ctx.respond("Disconnected")

    @slash_command()
    async def volume(
        self, ctx: ApplicationContext, volume: Option(int, "volume", required=True)
    ):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.respond("Not connected to a voice channel.")

        self.voice[ctx.author.guild.id].source.volume = volume / 100
        await ctx.respond(f"Changed volume to {volume}%")


def setup(bot):
    bot.add_cog(TTS(bot))
