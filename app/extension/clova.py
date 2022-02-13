from io import BytesIO

from langdetect import detect
from navertts import NaverTTS

from app.services.logger import generate_log


class ClovaTTS:
    def __init__(self):
        self.logger = generate_log()

    async def text_to_speech(self, text: str):
        try:
            source = NaverTTS(text=text, lang=detect(text), lang_check=True)
            msg = BytesIO()
            source.write_to_fp(msg)
            msg.seek(0)
            return msg.read()
        except Exception as e:
            self.logger.error(e)
