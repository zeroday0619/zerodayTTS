import asyncio
from collections import deque
from collections.abc import MutableMapping
from typing import Optional

from app.error import InvalidVoiceChannel
from app.error import VoiceConnectionError
from app.services.logger import generate_log
from cogs.tts.player import TTSSource
import discord
from discord.channel import VoiceChannel
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands.context import Context
from discord.voice_client import VoiceClient


class CustomDict(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store: dict[int, VoiceClient] = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)


class VoiceObject(CustomDict):
    logger = generate_log()

    def __init__(self):
        super().__init__()
        self.changed = False

    def __setitem__(self, key, item):
        self.logger.info("SET %s %s", key, item)
        self.store[key] = item
        self.changed = True

    def __delitem__(self, key):
        self.logger.info("DEL %s %s", key, self.store[key])
        del self.store[key]
        self.changed = True

    def __getitem__(self, key):
        return self.store[key]

    def __repr__(self):
        return repr(self.store)

    def __len__(self):
        return len(self.store)


class TTSCore(commands.Cog):
    __slots__ = ("bot", "voice", "messageQueue")

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = generate_log()
        self.messageQueue: CustomDict[Optional[dict[int, deque]]] = CustomDict()
        self.voice = VoiceObject()
        self.volume = 150

    @staticmethod
    def func_state(r_func):
        if r_func is None:
            return False
        else:
            return r_func

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.check_voice_ch_active_user.start()

    def is_joined(self, ctx: Context, member: discord.Member):
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

    @tasks.loop(minutes=5)
    async def check_voice_ch_active_user(self):
        for _id in list(self.voice.keys()):
            if _id:
                ch: VoiceChannel = self.voice[_id].channel
                if ch.members.__len__() < 2:
                    try:
                        await self.voice[_id].disconnect()
                        del self.messageQueue[_id]
                        self.voice.__delitem__(_id)
                    except KeyError as e:
                        self.logger.error(msg=e)
                else:
                    pass

    async def join(self, ctx: Context):
        """Joins a voice channel."""
        if self.is_joined(ctx, ctx.author):
            return

        # noinspection PyProtectedMember
        if self.func_state(ctx.author.guild._voice_states[ctx.author.id]):
            channel = ctx.author.guild._voice_states[ctx.author.id].channel
        else:
            await ctx.send(content="fail connect voice channel")
            raise VoiceConnectionError(
                f"Failed to join voice channel on guild {ctx.guild.id}"
            )

        if self.func_state(ctx.guild.voice_client):
            if ctx.guild.voice_client.channel.id == channel.id:
                return

            _voice = self.voice[ctx.author.guild.id]

            try:
                await _voice.move_to(channel)
            except asyncio.TimeoutError:
                await ctx.send(content=f"Moving to channel: <{str(channel)}> timed out")
                raise VoiceConnectionError(
                    f"Moving to channel: <{str(channel)}> timed out"
                )
        else:
            try:
                self.voice[ctx.author.guild.id] = await channel.connect()
            except asyncio.TimeoutError:
                await ctx.send(
                    content=f"Connecting to channel: <{str(channel)}> timed out"
                )
                raise VoiceConnectionError(
                    message=f"Connecting to channel: <{str(channel)}> timed out"
                )
            else:
                self.messageQueue[ctx.author.guild.id] = deque([])

    async def disconnect(self, ctx: Context):
        """Disconnects from voice channel."""
        if not self.voice.get(ctx.author.guild.id):
            return
        await self.voice[ctx.author.guild.id].disconnect()
        self.voice.__delitem__(ctx.author.guild.id)

    async def play(self, ctx: Context, source: discord.AudioSource):
        vc = ctx.guild.voice_client
        if not vc:
            await ctx.invoke(self.join)
        self.voice[ctx.author.guild.id].play(source)

    # async def _tts(self, ctx: Context, text: str, status):
    #    """Text to Speech"""
    #    try:
    #        if not self.voice[ctx.author.guild.id].is_playing():
    #            player = await TTSSource.text_to_speech(text)
    #            await self.play(ctx=ctx, source=player)
    #            return status(True)
    #        else:
    #            self.messageQueue[ctx.author.guild.id].append(text)
    #            while self.voice[ctx.author.guild.id].is_playing():
    #                await asyncio.sleep(1)
    #            q_text = self.message_queue[ctx.author.guild.id].popleft()
    #            q_player = await TTSSource.text_to_speech(q_text)
    #            await self.play(ctx=ctx, source=q_player)
    #            return status(True)
    #    except Exception:
    #        return status(Exception)

    async def _azure_tts(self, ctx: Context, text: str):
        """Text to Speech"""
        try:
            await ctx.send(f"[**{ctx.author.name}**] >> {text}")

            self.messageQueue[ctx.author.guild.id].append(text)
            while self.voice[ctx.author.guild.id].is_playing():
                await asyncio.sleep(0.5)
            else:
                print(self.messageQueue[ctx.author.guild.id])
                if self.messageQueue[ctx.author.guild.id].__len__() < 1:
                    q_player = await TTSSource.microsoft_azure_text_to_speech(text)
                    await asyncio.wait(
                        [asyncio.create_task(self.play(ctx=ctx, source=q_player))]
                    )
                else:
                    for _ in range(self.messageQueue[ctx.author.guild.id].__len__()):
                        q_text = self.messageQueue[ctx.author.guild.id].pop()
                        q_player = await TTSSource.microsoft_azure_text_to_speech(
                            q_text
                        )
                        await asyncio.wait(
                            [asyncio.create_task(self.play(ctx=ctx, source=q_player))]
                        )
        except Exception as e:
            self.logger.warning(msg=f"{str(e)}")
