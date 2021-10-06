from app import ZerodayTTS

app = ZerodayTTS(message=["TEST", "TEST2"], command_prefix="=")
app.load_extensions(["cogs.tts"])
app.launch()
