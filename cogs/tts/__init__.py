import asyncio
from typing import Type

import discord
from discord.app import Option
from discord.app.commands import slash_command
from discord.app.context import ApplicationContext
from discord.ext import commands

from app.error import InvalidVoiceChannel, VoiceConnectionError

from .player import TTSSource

FFMPEG_OPTIONS = {
    "options": "-y",
}


class TTS(commands.Cog):
    __slots__ = (
        "bot"
    )
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice = None
        self.volume = 150

    def is_joined(self, member: discord.Member):
        if not member.voice:
            raise

        return self.voice and self.voice.channel.id == member.voice.channel.id

    async def join(self, ctx: ApplicationContext):
        """Joins a voice channel."""
        if self.is_joined(ctx.author):
            return
        
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.respond(
                content="'Voice channel'에 연결하지 못하였습니다.\n 유효한 'Voice channel'에 자신이 들어와 있는지 확인바랍니다."
            )
            raise InvalidVoiceChannel(
                message="'Voice channel'에 연결하지 못하였습니다."
            )
        
        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                await ctx.respond(content=f"Moving to channel: <{str(channel)}> timed out")
                raise VoiceConnectionError(f"Moving to channel: <{str(channel)}> timed out")
        else:
            try:
                self.voice = await channel.connect()
            except asyncio.TimeoutError:
                await ctx.respond(content=f"Connecting to channel: <{str(channel)}> timed out")
                raise VoiceConnectionError(message=f"Connecting to channel: <{str(channel)}> timed out")

    async def _tts(self, ctx: ApplicationContext, text: str):
        """Text to Speech"""
        try:
            if not self.voice.is_playing():
                player = await TTSSource.text_to_speech(text)
                await self.play(ctx=ctx, source=player)
                return True
            else:
                return False
        except Exception:
            return Exception

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
    async def leave(self, ctx: ApplicationContext):
        """Leaves a voice channel."""
        try:
            await self.voice.disconnect()
        except AttributeError:
            await ctx.respond(content=f"{ctx.author.name}가 음성 채널에 접속하지 않음")
            return
        await ctx.respond("Disconnected")

    async def play(self, ctx: ApplicationContext, source: discord.AudioSource):
        vc = ctx.voice_client
        if not vc:
            await ctx.invoke(self.join)
        self.voice.play(source)

    @slash_command()
    async def volume(
        self, ctx: ApplicationContext, volume: Option(int, "volume", required=True)
    ):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.respond("Not connected to a voice channel.")

        self.voice.source.volume = volume / 100
        await ctx.respond(f"Changed volume to {volume}%")


def setup(bot):
    bot.add_cog(TTS(bot))
