import discord
from discord.app.commands import (SlashCommand, application_command, command,
                                  slash_command)
from discord.app.context import ApplicationContext
from discord.app.errors import ApplicationCommandError
from discord.ext import commands
from discord.ext.commands.errors import CommandError

from app.services.logger import generate_log


class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = generate_log()

    @slash_command()
    async def ping(self, ctx: ApplicationContext):
        """Latency"""
        await ctx.respond(f"Latency: {round(self.bot.latency * 1000)}ms")


    @slash_command()
    async def license(self, ctx: ApplicationContext):
        """License"""
        embed = discord.Embed(
                title="License",
        )
        embed.add_field(name="License", value="[MIT](https://github.com/zeroday0619/zerodayTTS/blob/main/LICENSE)")
        embed.add_field(name="Author", value="zeroday0619#2080")
        embed.add_field(name="Email", value="[zeroday0619_dev@outlook.com](mailto:zeroday0619_dev@outlook.com)")
        embed.add_field(name="Github", value="[github.com/zeroday0619](https://github.com/zeroday0619)")
        embed.set_footer(text="Powered by Kakao Speech API")
        await ctx.respond(embed=embed)
    
    
def setup(bot: commands.Bot):
    bot.add_cog(System(bot))