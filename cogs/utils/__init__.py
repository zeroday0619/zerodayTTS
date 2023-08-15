import discord
from discord.ext import commands
from discord.ext.commands import Context, hybrid_command
from app.services.logger import generate_log
from app.extension.facebook import FacebookParser

class UrlFlags(commands.FlagConverter):
    _url: str = commands.flag(description="Facebook public post url")


class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = generate_log()

    @hybrid_command(name="facebook", with_app_command=True)
    async def facebook(self, ctx: Context, url: UrlFlags):
        """License"""

        url = url._url
        FP = FacebookParser()
        resp = await FP.parse(url=url)

        embed = discord.Embed(
            title="Facebook Public Post Preview",
        )
        embed.set_author(
            name=resp["author"],
        )
        embed.add_field(
            name="Title",
            value=resp["title"],
        )
        embed.add_field(
            name="Description",
            value=resp["description"],
        )
        embed.set_footer(text="Facebook Public Post Parser v1.0.0")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utils(bot))