import os

from AzureTTS import MicrosoftTTS

from app.services.logger import generate_log


class MSAzureTTS:
    def __init__(self):
        self.logger = generate_log()

    async def select_language(self, language_code: str, gender: str):
        voices = await MicrosoftTTS(api_key=os.environ.get("ms_key")).get_voice_list()
        """
        Get voice list structure

        [
            {
                "Name": "Microsoft Server Speech Text to Speech Voice (en-US, JennyNeural)",
                "DisplayName": "Jenny",
                "LocalName": "Jenny",
                "ShortName": "en-US-JennyNeural",
                "Gender": "Female",
                "Locale": "en-US",
                "StyleList": [
                    "chat",
                    "customerservice",
                    "newscast-casual",
                    "assistant",
                ],
                "SampleRateHertz": "24000",
                "VoiceType": "Neural",
                "Status": "GA"
            },
        ]
        """
        vc_list: list[str] = []
        for voice in voices:
            if voice["Locale"] == language_code:
                if str(voice["Gender"]).lower() == str(gender).lower():
                    vc_list.append(voice["ShortName"])
        return vc_list

    async def text_to_speech(self, text: str, language_code: str = "ko-KR"):
        try:
            source = MicrosoftTTS(api_key=os.environ.get("ms_key"))
            names = await self.select_language(
                language_code=language_code, gender="Female"
            )
            _ssml = source.create_ssml(
                text=text, lang=language_code, gender="Female", name=names[0]
            )
            return await source.speach(ssml_text=_ssml)
        except Exception as e:
            self.logger.error(e)
