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
            return False
        return ctx.channel.id == tts_channel_id

    return commands.check(predicate)


class TTS(TTSCore):
    __slots__ = ("bot", "voice")

    def __init__(self, bot: Bot):
        super(TTS, self).__init__(bot)
        self.database = app.database()
        self.logger = generate_log()

    async def cleanup(self):
        await self.check_voice_ch_active_user()

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
    @check_channel()
    async def tts(
        self, ctx: ApplicationContext, *, text: Option(str, "text", required=True)
    ):
        await self.join(ctx)
        status = await self._tts(ctx, text)
        if status == Type[Exception]:
            await ctx.respond("오류가 발생했습니다.")
        if status:
            await ctx.respond(f"[**{ctx.author.name}**] >> {text}")

    @slash_command()
    @check_channel()
    async def connect(self, ctx: ApplicationContext):
        try:
            await self.join(ctx)
        except Exception:
            return await ctx.respond("오류가 발생했습니다.")
        await ctx.respond(f"{ctx.author.name}님 정상적으로 보이스 채널에 연결되었습니다.")

    @slash_command()
    @check_channel()
    async def leave(self, ctx: ApplicationContext):
        """Leaves a voice channel."""
        try:
            await self.disconnect(ctx)
        except AttributeError:
            await ctx.respond(content=f"{ctx.author.name}가 음성 채널에 접속하지 않음")
            return
        await ctx.respond("Disconnected")


def setup(bot):
    bot.add_cog(TTS(bot))
