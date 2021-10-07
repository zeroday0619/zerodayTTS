from discord.ext import commands
from discord.app.commands import slash_command
from discord.app.context import ApplicationContext


class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @slash_command()
    async def ping(self, ctx: ApplicationContext):
        """Latency"""
        await ctx.respond(f"Latency: {round(self.bot.latency * 1000)}ms")
    

def setup(bot: commands.Bot):
    bot.add_cog(System(bot))