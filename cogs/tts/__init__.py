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

        _voice_state = ctx.author.guild._voice_states.get(ctx.author.id)
        if type(_voice_state) == discord.VoiceState:
            ch = _voice_state.channel
            if type(ch) == discord.VoiceChannel:
                self.voice = await ch.connect()
            else:
                raise Exception("Not supported channel")
        else:
            return await ctx.send("You are not in a voice channel.")

    async def _tts(self, ctx: commands.Context, text: str):
        """Text to Speech"""
        try:
            if not self.voice.is_playing():
                player = await TTSSource.text_to_speech(text)
                self.play(source=player)
                return True
            else:
                await ctx.send(content=f"{ctx.author.name}가 TTS 사용함", delete_after=10)
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
            await ctx.send("오류가 발생했습니다.")
        if status:
            await ctx.send(f"{ctx.author.nick}님이 TTS 사용함.", delete_after=10)
        else:
            await ctx.send(f"{ctx.author.nick}님이 TTS가 이미 사용중입니다.", delete_after=10)

    @slash_command()
    async def leave(self, ctx: commands.Context):
        """Leaves a voice channel."""

        await self.voice.disconnect()
        await ctx.send("Disconnected", delete_after=5)

    def play(self, source: discord.AudioSource):

        self.voice.play(source)

    @slash_command()
    async def volume(
        self, ctx: commands.Context, volume: Option(int, "volume", required=True)
    ):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        self.voice.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")


def setup(bot):
    bot.add_cog(TTS(bot))
