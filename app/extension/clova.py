import os

from AzureTTS import MicrosoftTTS

from app.services.logger import generate_log


class MSAzureTTS:
    def __init__(self):
        self.logger = generate_log()

    async def text_to_speech(self, text: str):
        try:
            source = MicrosoftTTS(api_key=os.environ.get("ms_key"))

            _ssml = source.create_ssml(
                lang="ko-KR", gender="Female", name="ko-KR-SunHiNeural", text=text
            )
            return await source.speach(ssml_text=_ssml)
        except Exception as e:
            self.logger.error(e)
