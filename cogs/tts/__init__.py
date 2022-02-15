import asyncio
from typing import Type

from discord import ApplicationContext, Option
from discord.ext import commands
from discord.ext.commands import Bot, has_permissions, slash_command
from pymysql.err import IntegrityError, ProgrammingError

from app.extension import servers
from app.services.logger import generate_log
from start import app

from ._core_class import TTSCore

FFMPEG_OPTIONS = {
    "options": "-y",
}


def check_channel():
    async def predicate(ctx):
        logger = generate_log()
        database = app.database()
        try:
            query = servers.select().where(servers.c.guild_id == ctx.guild.id)
            source = await database.fetch_one(query=query)

            tts_channel_id = source[3]
        except Exception as e:
            logger.error(msg=f"ERROR: {e}")
            await ctx.respond("DATABASE ERROR - 지원 => @zeroday0619#2080")
            return False
        status = ctx.channel.id == tts_channel_id
        if not status:
            await ctx.respond("권한이 없는 채널 입니다.")
            return status
        return status

    return commands.check(predicate)


class TTS(TTSCore):
    __slots__ = ("bot", "voice", "messageQueue")

    def __init__(self, bot: Bot):
        self.database = app.database()
        self.logger = generate_log()
        super(TTS, self).__init__(bot)

    @slash_command()
    @has_permissions(administrator=True)
    async def register(self, ctx: ApplicationContext):
        """TTS 전용 채널 등록"""
        try:
            query = servers.insert()
            await self.database.execute(
                query=query,
                values={
                    "user_id": int(ctx.author.id),
                    "guild_id": int(ctx.author.guild.id),
                    "tts_channel_id": int(ctx.channel.id),
                },
            )
            return await ctx.respond("성공")
        except IntegrityError as code:
            co = list(code.args)
            self.logger.warning(msg=f"{co[1]} | ERROR CODE: {co[0]}")
            return await ctx.respond(f"이미 등록된 서버입니다.")
        except ProgrammingError as code:
            co = list(code.args)
            self.logger.warning(msg=f"{co[1]} | ERROR CODE: {co[0]}")
            return await ctx.respond("등록 실패")
        except AssertionError as code:
            co = list(code.args)
            self.logger.error(msg=f"{' '.join(co)}")
            return await ctx.respond("System Error")

    @slash_command()
    @has_permissions(administrator=True)
    async def unregister(self, ctx: ApplicationContext):
        """TTS 전용 채널 삭제"""
        try:
            delete = servers.delete()
            query = delete.where(servers.c.tts_channel_id == ctx.channel.id)
            await self.database.execute(query=query)
            return await ctx.respond("등록 해제 성공")
        except IntegrityError as code:
            co = list(code.args)
            self.logger.warning(msg=f"{co[1]} | ERROR CODE: {co[0]}")
            return await ctx.respond("등록 데이터가 없습니다.")
        except ProgrammingError as code:
            self.logger.error(f"ERROR: {code}")
            return await ctx.respond("등록 해제 실패")
        except AssertionError as code:
            co = list(code.args)
            self.logger.error(msg=f"{' '.join(co)}")
            return await ctx.respond("System Error")

    def _kakao_tts_status(self, status):
        self._kakao_status = status

    def _clova_tts_status(self, status):
        self._clova_status = status

    @slash_command()
    @check_channel()
    async def tts(
        self, ctx: ApplicationContext, *, text: Option(str, "text", required=True)
    ):
        await self.join(ctx)
        proc = asyncio.gather(self._tts(ctx, text, self._kakao_tts_status))
        await proc
        if self._kakao_status == Type[Exception]:
            return await ctx.respond("오류가 발생했습니다.")
        if self._kakao_status:
            return await ctx.respond(f"[**{ctx.author.name}**] >> {text}")

    @slash_command()
    @check_channel()
    async def clova(
        self, ctx: ApplicationContext, *, text: Option(str, "text", required=True)
    ):
        await self.join(ctx)
        proc = asyncio.gather(
            self._clova_tts(ctx, text, self._clova_tts_status), return_exceptions=True
        )
        await proc
        if self._clova_status == Type[Exception]:
            return await ctx.respond("오류가 발생했습니다.")
        if self._clova_status:
            return await ctx.respond(f"[**{ctx.author.name}**] >> {text}")

    @slash_command()
    @check_channel()
    async def connect(self, ctx: ApplicationContext):
        try:
            await self.join(ctx)
        except Exception:
            return await ctx.respond("오류가 발생했습니다.")
        return await ctx.respond(f"{ctx.author.name}님 정상적으로 보이스 채널에 연결되었습니다.")

    @slash_command()
    @check_channel()
    async def leave(self, ctx: ApplicationContext):
        """Leaves a voice channel."""
        try:
            await self.disconnect(ctx)
        except AttributeError:
            return await ctx.respond(content=f"{ctx.author.name}가 음성 채널에 접속 하지 않음")
        return await ctx.respond("Disconnected")


def setup(bot):
    bot.add_cog(TTS(bot))
