from discord import Intents

from app import ZerodayTTS

app = ZerodayTTS(
    message=[
        "pre-release 1.0.4",
        "문의: @zeroday0619#2080",
        "후원: https://toss.me/zeroday",
        "zerodayTTS 프로필 => 서버에 추가로 기술 지원 혜택을 받아보세요!",
    ],
    command_prefix="=",
    intents=Intents(
        bans=False,
        emojis=False,
        guilds=True,
        members=True,
        messages=True,
        reactions=True,
        typing=True,
        presences=True,
        voice_states=True,
        invites=False,
        webhooks=False,
        integrations=True,
    ),
)
app.launch()
