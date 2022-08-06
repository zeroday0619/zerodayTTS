import asyncio
from typing import Type
from discord.ext import commands
from discord.ext.commands import hybrid_command
from discord.ext.commands import Bot, has_permissions
from app.services.logger import generate_log
from start import app

from ._core_class import TTSCore

FFMPEG_OPTIONS = {
    "options": "-y",
}


class TTS(TTSCore):
    __slots__ = ("bot", "voice", "messageQueue")

    def __init__(self, bot: Bot):
        self.logger = generate_log()
        super(TTS, self).__init__(bot)

    def _kakao_tts_status(self, status):
        self._kakao_status = status

    def _clova_tts_status(self, status):
        self._clova_status = status

    @hybrid_command()
    async def tts(self, ctx, *, text):
        await self.join(ctx)
        await self._clova_tts(ctx, text)

    @hybrid_command()
    async def connect(self, ctx):
        try:
            await self.join(ctx)
        except Exception:
            return await ctx.send("오류가 발생했습니다.")
        return await ctx.send(f"{ctx.author.name}님 정상적으로 보이스 채널에 연결되었습니다.")

    @hybrid_command()
    async def leave(self, ctx):
        """Leaves a voice channel."""
        try:
            await self.disconnect(ctx)
        except AttributeError:
            return await ctx.send(content=f"{ctx.author.name}가 음성 채널에 접속 하지 않음")
        return await ctx.send("Disconnected")


async def setup(bot):
    await bot.add_cog(TTS(bot))
