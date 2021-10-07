from discord.app.commands import slash_command
from discord.app.context import ApplicationContext
from discord.ext import commands


class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @slash_command()
    async def ping(self, ctx: ApplicationContext):
        """Latency"""
        await ctx.respond(f"Latency: {round(self.bot.latency * 1000)}ms")
    
    @slash_command(description='reload tts')
    async def reload(self, ctx: ApplicationContext):
        try:
            self.bot.reload_extension("cogs.tts")
        except Exception as e:
            await ctx.respond("reload failed")
        await ctx.respond("reloaded")
    

def setup(bot: commands.Bot):
    bot.add_cog(System(bot))