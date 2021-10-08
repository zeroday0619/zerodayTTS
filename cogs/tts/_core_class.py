import asyncio
import discord

from typing import Optional, Dict
from discord.ext import commands
from discord.app.context import ApplicationContext
from discord.voice_client import VoiceClient
from app.error import InvalidVoiceChannel
from app.error import VoiceConnectionError
from cogs.tts.player import TTSSource


class TTSCore(commands.Cog):
    __slots__ = ("bot", "voice")
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice: Optional[Dict[int, VoiceClient]] = {}
        self.volume = 150

    def is_joined(self, ctx: ApplicationContext, member: discord.Member):
        """
        Checks if member is in a voice channel.

        Args:
            ctx: ApplicationContext
            member: ctx.author or discord.Member
        """
        if not member.voice:
            raise

        return self.voice.get(ctx.author.guild.id) and self.voice.channel.id == member.voice.channel.id

    async def join(self, ctx: ApplicationContext):
        """Joins a voice channel."""
        if self.is_joined(ctx, ctx.author):
            return
        
        try:
            channel = ctx.author.guild._voice_states[ctx.author.id].channel
        except AttributeError:
            await ctx.respond(
                content="'Voice channel'에 연결하지 못하였습니다.\n 유효한 'Voice channel'에 자신이 들어와 있는지 확인바랍니다."
            )
            raise InvalidVoiceChannel(
                message="'Voice channel'에 연결하지 못하였습니다."
            )
        
        vc = ctx.guild.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                _voice = self.voice[ctx.author.guild.id]
                await _voice.move_to(channel)
            except asyncio.TimeoutError:
                await ctx.respond(content=f"Moving to channel: <{str(channel)}> timed out")
                raise VoiceConnectionError(f"Moving to channel: <{str(channel)}> timed out")
        else:
            try:
                self.voice[ctx.author.guild.id] = await channel.connect()
            except asyncio.TimeoutError:
                await ctx.respond(content=f"Connecting to channel: <{str(channel)}> timed out")
                raise VoiceConnectionError(message=f"Connecting to channel: <{str(channel)}> timed out")

    async def disconnect(self, ctx: ApplicationContext):
        """Disconnects from voice channel."""
        if not self.voice.get(ctx.author.guild.id):
            return
        await self.voice[ctx.author.guild.id].disconnect()
        del self.voice[ctx.author.guild.id]

    async def play(self, ctx: ApplicationContext, source: discord.AudioSource):
        vc = ctx.guild.voice_client
        if not vc:
            await ctx.invoke(self.join)
        self.voice[ctx.author.guild.id].play(source)

    async def _tts(self, ctx: ApplicationContext, text: str):
        """Text to Speech"""
        try:
            if not self.voice[ctx.author.guild.id].is_playing():
                player = await TTSSource.text_to_speech(text)
                await self.play(ctx=ctx, source=player)
                return True
            else:
                return False
        except Exception:
            return Exception