import asyncio
from typing import Deque, Dict, Optional

import discord
from discord import ApplicationContext
from discord.channel import VoiceChannel
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient

from app.error import InvalidVoiceChannel, VoiceConnectionError
from app.services.logger import generate_log
from cogs.tts.player import TTSSource
from collections import deque

class TTSCore(commands.Cog):
    __slots__ = ("bot", "voice", "messageQueue")

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = generate_log()
        self.messageQueue: Optional[Dict[int, deque]] = {}
        self.voice: Optional[Dict[int, VoiceClient]] = {}
        self.volume = 150

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.check_voice_ch_active_user.start()

    def is_joined(self, ctx: ApplicationContext, member: discord.Member):
        """
        Checks if member is in a voice channel.

        Args:
            ctx: ApplicationContext
            member: ctx.author or discord.Member
        """
        if not member.voice:
            raise

        return (
            self.voice.get(ctx.author.guild.id)
            and self.voice.get(ctx.author.guild.id) is not None
            and self.voice.get(ctx.author.guild.id).channel.id
            == member.voice.channel.id
        )

    @tasks.loop(minutes=1)
    async def check_voice_ch_active_user(self):
        for _id in list(self.voice.keys()):
            if _id:
                ch: VoiceChannel = self.voice[_id].channel
                if ch.members.__len__() < 2:
                    try:
                        await self.voice[_id].disconnect()
                        del self.messageQueue[_id]
                        del self.voice[_id]
                    except KeyError as e:
                        self.logger.error(msg=e)
                else:
                    pass

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
            raise InvalidVoiceChannel(message="'Voice channel'에 연결하지 못하였습니다.")
        vc = ctx.guild.voice_client
        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                _voice = self.voice[ctx.author.guild.id]
                await _voice.move_to(channel)
            except asyncio.TimeoutError:
                await ctx.respond(
                    content=f"Moving to channel: <{str(channel)}> timed out"
                )
                raise VoiceConnectionError(
                    f"Moving to channel: <{str(channel)}> timed out"
                )
        else:
            try:
                self.voice[ctx.author.guild.id] = await channel.connect()
                self.messageQueue[ctx.author.guild.id] = deque([])
            except asyncio.TimeoutError:
                await ctx.respond(
                    content=f"Connecting to channel: <{str(channel)}> timed out"
                )
                raise VoiceConnectionError(
                    message=f"Connecting to channel: <{str(channel)}> timed out"
                )

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
    
    @commands.Cog.listener()
    async def on_message(self, ctx: ApplicationContext, message: discord.Message):
        if self.is_joined(ctx, ctx.author):
            return
            
        if message.channel.id == self.voice[ctx.author.guild.id].channel.id:
            if message.author.bot:
                return

            msg = message.content
            if not self.voice[ctx.author.guild.id].is_playing():
                player = await TTSSource.text_to_speech(msg)
                await self.play(ctx=ctx, source=player)
            else:
                self.messageQueue[ctx.author.guild.id].append(msg)
                while self.voice[ctx.author.guild.id].is_playing():
                    await asyncio.sleep(1)
                q_text = self.messageQueue[ctx.author.guild.id].popleft()
                q_player = await TTSSource.text_to_speech(q_text)
                await self.play(ctx=ctx, source=q_player)

 
    async def _tts(self, ctx: ApplicationContext, text: str):
        """Text to Speech"""
        try:
            if not self.voice[ctx.author.guild.id].is_playing():
                player = await TTSSource.text_to_speech(text)
                await self.play(ctx=ctx, source=player)
                return True
            else:
                self.messageQueue[ctx.author.guild.id].append(text)
                while self.voice[ctx.author.guild.id].is_playing():
                    await asyncio.sleep(1)
                q_text = self.message_queue[ctx.author.guild.id].popleft()
                q_player = await TTSSource.text_to_speech(q_text)
                await self.play(ctx=ctx, source=q_player)
                return True

        except Exception:
            return Exception
