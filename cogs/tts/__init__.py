import asyncio
from typing import Type

import discord
from discord.app import Option
from discord.app.commands import slash_command
from discord.ext import commands

from .player import TTSSource

FFMPEG_OPTIONS = {
    "options": "-y",
}


class TTS(commands.Cog):
    __slots__ = ("bot", "voice")

    def __init__(self, bot: commands.Bot):
        self.voice = None
        self.players = {}
        self.bot = bot

    def get_player(self, ctx: commands.Context):
        try:
            return self.players[ctx.guild.id]
        except KeyError:
            raise KeyError("Player not found")

    def is_joined(self, member: discord.Member):
        if not member.voice:
            raise

        return self.voice and self.voice.channel.id == member.voice.channel.id

    async def join(self, ctx: commands.Context):
        """Joins a voice channel."""
        if self.is_joined(ctx.author):
            return
        
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.respond(content=f"{ctx.author.name}가 음성 채널에 접속하지 않음", delete_after=10)
            raise Exception(f"{ctx.author.name}가 음성 채널에 접속하지 않음")
        
        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                await ctx.respond(content=f"Moving to channel: <{str(channel)}> timed out", delete_after=10)
                raise Exception(f"Moving to channel: <{str(channel)}> timed out")
        else:
            try:
                self.voice = await channel.connect()
            except asyncio.TimeoutError:
                await ctx.respond(content=f"Moving to channel: <{str(channel)}> timed out", delete_after=10)
                raise Exception(f"Moving to channel: <{str(channel)}> timed out")

    async def _tts(self, ctx: commands.Context, text: str):
        """Text to Speech"""
        try:
            if not self.voice.is_playing():
                player = await TTSSource.text_to_speech(text)
                await self.play(ctx=ctx, source=player)
                return True
            else:
                await ctx.respond(content=f"{ctx.author.name}가 TTS 사용함", delete_after=10)
                return False
        except Exception:
            return Exception

    @slash_command()
    async def tts(
        self, ctx: commands.Context, *, text: Option(str, "text", required=True)
    ):
        await self.join(ctx)
        status = await self._tts(ctx, text)
        if status == Type[Exception]:
            await ctx.respond("오류가 발생했습니다.")
        if status:
            await ctx.respond(f"{ctx.author.name}님이 TTS 사용함.", delete_after=10)
        else:
            await ctx.respond(f"{ctx.author.name}님이 TTS가 이미 사용중입니다.", delete_after=10)

    @slash_command()
    async def leave(self, ctx: commands.Context):
        """Leaves a voice channel."""

        await self.voice.disconnect()
        await ctx.respond("Disconnected", delete_after=5)

    async def play(self, ctx: commands.Context, source: discord.AudioSource):
        vc = ctx.voice_client
        if not vc:
            await ctx.invoke(self.join)
        self.voice.play(source)

    @slash_command()
    async def volume(
        self, ctx: commands.Context, volume: Option(int, "volume", required=True)
    ):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.respond("Not connected to a voice channel.")

        self.voice.source.volume = volume / 100
        await ctx.respond(f"Changed volume to {volume}%")


def setup(bot):
    bot.add_cog(TTS(bot))
