import discord
from discord.ext import commands
from discord.ext.commands import Context, hybrid_command

from app.services.logger import generate_log


class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = generate_log()

    @hybrid_command(with_app_command=True)
    async def reset(self, ctx: Context):
        self.tree.clear_commands(guild=ctx.guild)
        self.logger.info(f"Cleared commands for {str(ctx.guild.id)}-{ctx.guild.name}")
        await self.bot.__tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced commands for {ctx.guild.name}")

    @hybrid_command(with_app_command=True)
    async def ping(self, ctx: Context):
        """Latency"""
        await ctx.send(f"Latency: {round(self.bot.latency * 1000)}ms")

    @hybrid_command(with_app_command=True)
    async def license(self, ctx: Context):
        """License"""
        embed = discord.Embed(
            title="zerodayTTS",
        )
        embed.add_field(
            name="License",
            value="[MIT](https://github.com/zeroday0619/zerodayTTS/blob/main/LICENSE)",
        )
        embed.add_field(name="Author", value="zeroday0619#2080")
        embed.add_field(
            name="Email",
            value="[zeroday0619_dev@outlook.com](mailto:zeroday0619_dev@outlook.com)",
        )
        embed.add_field(
            name="Github",
            value="[github.com/zeroday0619](https://github.com/zeroday0619)",
        )
        embed.set_footer(text="Powered by Kakao Speech API")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(System(bot))
