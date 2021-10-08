from discord import Intents

from app import ZerodayTTS

app = ZerodayTTS(
    message=["pre-release 1.0.1", "문의: @zeroday0619#2080"],
    command_prefix="=",
    intents=Intents(
        bans=False,
        emojis=False,
        guilds=True,
        members=True,
        messages=True,
        reactions=True,
        typing=True,
        presences=False,
        voice_states=True,
        invites=False,
        webhooks=False,
        integrations=True,
    )
)
app.load_extensions(["cogs.system", "cogs.tts"])
app.launch()
