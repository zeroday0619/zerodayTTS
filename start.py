from app import ZerodayTTS

app = ZerodayTTS(message=["pre-release 1.0.0", "문의: @zeroday0619#2080"], command_prefix="=")
app.load_extensions(["cogs.tts"])
app.launch()
