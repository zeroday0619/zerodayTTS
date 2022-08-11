from aiohttp import ClientSession
from app.extension.kakao_error import BAD_GATEWAY_EXCEPTION
from app.extension.kakao_error import BAD_REQUEST_EXCEPTION
from app.extension.kakao_error import FORBIDDEN_EXCEPTION
from app.extension.kakao_error import INTERNAL_SERVER_ERROR_EXCEPTION
from app.extension.kakao_error import SERVICE_UNAVAILABLE_EXCEPTION
from app.extension.kakao_error import TOO_MANY_REQUEST_EXCEPTION
from app.extension.kakao_error import UNAUTHORIZED_EXCEPTION
from app.services.logger import LogDecorator
import kss


class KakaoSpeechAPI:
    def __init__(self, api_key: str) -> None:
        """KaKao Speech API 인스턴스 생성

        Args:
            api_key (str): Kakao Speech API Key
        """
        self.api_key = api_key
        self.api_url = "https://kakaoi-newtone-openapi.kakao.com"

    @staticmethod
    async def status_code(status_code: int) -> None:
        """
        Args:
            status_code (int): HTTP Status Code
        """
        if status_code == 200:
            pass
        elif status_code == 400:
            raise BAD_REQUEST_EXCEPTION()
        elif status_code == 401:
            raise UNAUTHORIZED_EXCEPTION()
        elif status_code == 403:
            raise FORBIDDEN_EXCEPTION()
        elif status_code == 429:
            raise TOO_MANY_REQUEST_EXCEPTION()
        elif status_code == 500:
            raise INTERNAL_SERVER_ERROR_EXCEPTION()
        elif status_code == 502:
            raise BAD_GATEWAY_EXCEPTION()
        elif status_code == 503:
            raise SERVICE_UNAVAILABLE_EXCEPTION()
        else:
            raise Exception("Unknown Error")

    async def set_request_headers(self) -> None:
        headers = {
            "Content-Type": "application/xml",
            "Authorization": f"KakaoAK {self.api_key}",
        }
        return headers

    @staticmethod
    def clean_source(source: str) -> str:
        """
        Args:
            source (str): TTS로 변환 할 문장이나 단어

        Returns:
            str: 정규표현식으로 제거한 문장
        """
        _source = (
            source.replace("[", "")
            .replace("]", "")
            .replace("{", "")
            .replace("}", "")
            .replace("(", "")
            .replace(")", "")
        )
        return _source

    @LogDecorator
    def create_ssml(self, source: str) -> str:
        """SSML 생성

        Args:
            source (str): TTS로 변환 할 문장이나 단어

        Returns:
            str: SSML
        """
        data = []
        _data = data.append

        _source = self.clean_source(source)

        for sentence in kss.split_sentences(_source):
            _data(f'<prosody rate="slow" volume="loud">{sentence}<break/></prosody>')

        ssml = f"""<speak> <voice name="WOMAN_READ_CALM"> {str(''.join(data))} </voice> </speak>"""
        return ssml

    async def text_to_speech(self, source: str):
        _headers = await self.set_request_headers()
        _source = self.create_ssml(source)
        async with ClientSession(headers=_headers) as session:
            async with session.post(
                url=self.api_url + "/v1/synthesize", data=_source
            ) as response:
                await self.status_code(response.status)
                res = await response.read()
                return res
