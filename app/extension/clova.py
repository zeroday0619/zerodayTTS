from io import BytesIO

import os
from AzureTTS import MicrosoftTTS

from app.services.logger import generate_log


class ClovaTTS:
    def __init__(self):
        self.logger = generate_log()

    async def text_to_speech(self, text: str):
        try:
            source = MicrosoftTTS(api_key=os.environ.get("ms_key"))
            msg = BytesIO()
            _ssml = source.create_ssml(
                lang="ko-KR", gender="Female", name="ko-KR-SunHiNeural"
            )
            await source.write_to_fp(ssml_text=_ssml, _io=msg)
            msg.seek(0)
            return msg.read()
        except Exception as e:
            self.logger.error(e)
