import json
import langid
from discord.ext import commands
from discord.ext.commands import Bot, hybrid_command
from app.services.logger import generate_log
from cogs.tts._core_class import TTSCore
from app.extension.clova import MSAzureTTS
from textblob import TextBlob


FFMPEG_OPTIONS = {
    "options": "-y",
}

class TextFlags(commands.FlagConverter):
    text: str = commands.flag(description="text")

class GenderFlags(commands.FlagConverter):
    value: str = commands.flag(description="Female, Male", default="f")

class TTS(TTSCore):
    __slots__ = ("bot", "voice", "messageQueue")

    def __init__(self, bot: Bot):
        self.logger = generate_log()
        super(TTS, self).__init__(bot)

    def _kakao_tts_status(self, status):
        self._kakao_status = status

    def _clova_tts_status(self, status):
        self._clova_status = status

    @hybrid_command(name="language", with_app_command=True)
    async def select_language(self, ctx: commands.Context, gender: GenderFlags):
        ms_azure_tts = MSAzureTTS()
        gender = gender.value.lower()
        if gender == "f":
            gen = "female"
        elif gender == "m":
            gen = "male"
        else:
            await ctx.send(f"not support: {gender}")
            return
        
        listd_json = await ms_azure_tts.select_language("ko-KR", gender=gen)
        pp_listd_json = json.dumps(listd_json, indent=4, ensure_ascii=False)
        await ctx.send(
            f"```json\n{pp_listd_json}\n```"
        )
        

    @hybrid_command(name="tts", with_app_command=True)
    async def tts(self, ctx, *, flags: TextFlags):
        """TTS Powered by Microsoft Azure Cognitive Speech Services"""
        text = flags.text
        if len(text) > 3:
            u_lang = TextBlob(text).detect_language()
        else:
            u_lang = langid.classify(text)[0]
        await self.join(ctx)
        match u_lang:
            case "ko":
                await self._azure_tts(ctx=ctx, text=text, lang="ko-KR")
            case "en":
                await self._azure_tts(ctx=ctx, text=text, lang="en-US")
            case "ja":
                await self._azure_tts(ctx=ctx, text=text, lang="ja-JP")
            case "zh":
                await self._azure_tts(ctx=ctx, text=text, lang="zh-CN")
            case "fr":
                await self._azure_tts(ctx=ctx, text=text, lang="fr-FR")
            case _:
                await self._azure_tts(
                    ctx=ctx, text="unknown language", lang="en-US", pass_text=text
                )

    @hybrid_command("ptts", with_app_command=True)
    async def ptts(self, ctx, *, text: str):
        """Private TTS Powered by Microsoft Azure Cognitive Speech Services"""
        if len(text) > 3:
            u_lang = TextBlob(text).detect_language()
        else:
            u_lang = langid.classify(text)[0]
        await self.join(ctx)
        match u_lang:
            case "ko":
                await self._azure_tts(
                    ctx=ctx, text=text, lang="ko-KR", delete_after=5.0
                )
            case "en":
                await self._azure_tts(
                    ctx=ctx, text=text, lang="en-US", delete_after=5.0
                )
            case "ja":
                await self._azure_tts(
                    ctx=ctx, text=text, lang="ja-JP", delete_after=5.0
                )
            case "zh":
                await self._azure_tts(
                    ctx=ctx, text=text, lang="zh-CN", delete_after=5.0
                )
            case "fr":
                await self._azure_tts(
                    ctx=ctx, text=text, lang="fr-FR", delete_after=5.0
                )
            case _:
                await self._azure_tts(
                    ctx=ctx,
                    text="unknown language",
                    lang="en-US",
                    pass_text=text,
                    delete_after=5.0,
                )

    @hybrid_command(name="bixby", with_app_command=True)
    async def bixby(self, ctx, *, message: str):
        """Powered by Open AI"""
        await self.join(ctx)
        await self._bixby(ctx, message)

    @hybrid_command(name="connect", with_app_command=True)
    async def connect(self, ctx):
        try:
            await self.join(ctx)
        except Exception:
            return await ctx.send("오류가 발생했습니다.")
        return await ctx.send(f"{ctx.author.name}님 정상적으로 보이스 채널에 연결되었습니다.")

    @hybrid_command(name="leave", with_app_command=True)
    async def leave(self, ctx):
        """Leaves a voice channel."""
        try:
            await self.disconnect(ctx)
        except AttributeError:
            return await ctx.send(content=f"{ctx.author.name}가 음성 채널에 접속 하지 않음")
        return await ctx.send("Disconnected")


async def setup(bot):
    await bot.add_cog(TTS(bot))
