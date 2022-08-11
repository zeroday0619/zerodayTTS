import os
from io import BytesIO
from shlex import split
from subprocess import PIPE, Popen

import discord
from discord.opus import Encoder

from app.extension import KakaoSpeechAPI
from app.extension.clova import MSAzureTTS

KSA = KakaoSpeechAPI(os.environ.get("ZERODAY_TTS_KAKAO_API_KEY"))


class FFmpegPCMAudio(discord.AudioSource):
    """Reimplementation of discord.FFmpegPCMAudio with source: bytes support
    Original Source: https://github.com/Rapptz/discord.py/issues/5192"""

    def __init__(
        self,
        source,
        *,
        executable="ffmpeg",
        pipe=False,
        stderr=None,
        before_options=None,
        options=None
    ):
        args = [executable]
        if isinstance(before_options, str):
            args.extend(split(before_options))

        args.append("-i")
        args.append("-" if pipe else source)
        args.extend(("-f", "s16le", "-ar", "48000", "-ac", "2", "-loglevel", "warning"))

        if isinstance(options, str):
            args.extend(split(options))

        args.append("pipe:1")

        self._stdout = None
        self._process = None
        self._stderr = stderr
        self._process_args = args
        self._stdin = source if pipe else None

    def _create_process(self) -> BytesIO:
        stdin, stderr, args = self._stdin, self._stderr, self._process_args
        self._process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=stderr)
        return BytesIO(self._process.communicate(input=stdin)[0])

    def read(self) -> bytes:
        if self._stdout is None:
            # This function runs in a voice thread, so we can afford to block
            # it and make the process now instead of in the main thread
            self._stdout = self._create_process()

        ret = self._stdout.read(Encoder.FRAME_SIZE)
        return ret if len(ret) == Encoder.FRAME_SIZE else b""

    def cleanup(self):
        process = self._process
        if process is None:
            return

        process.kill()
        if process.poll() is None:
            process.communicate()

        self._process = None


class TTSSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, volume=0.5):
        super().__init__(source, volume)

    @classmethod
    async def text_to_speech(cls, text):
        data = await KSA.text_to_speech(source=text)
        return cls(
            FFmpegPCMAudio(data, pipe=True, options='-loglevel "quiet"'), volume=0.5
        )

    @classmethod
    async def microsoft_azure_text_to_speech(cls, text):
        source = MSAzureTTS()
        data = await source.text_to_speech(text)
        return cls(
            FFmpegPCMAudio(data, pipe=True, options='-loglevel "quiet"'), volume=0.5
        )
