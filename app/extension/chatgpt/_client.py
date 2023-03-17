import os
import openai
import discord
from enum import Enum
from dataclasses import dataclass

SEPARATOR_TOKEN = "<|endoftext|>"
MAX_THREAD_MESSAGES = 200
MAX_CHARS_PER_REPLY_MSG = (1500) # discord has a 2k limit, we just break message into 1.5k


@dataclass(frozen=True)
class Message:
    user: str
    text: str | None = None

    def render(self) -> str:
        result = self.user + ":"
        if self.text is not None:
            result += " " + self.text
        return result
    
@dataclass
class Conversation:
    message: list[Message]

    def prepend(self, message: Message):
        self.message.insert(0, message)
        return self
    
    def render(self) -> str:
        return f"\n{SEPARATOR_TOKEN}".join(
            [message.render() for message in self.message]
        )

@dataclass(frozen=True)
class Prompt:
    header: Message
    convo: Conversation

    def render(self):
        return f"\n{SEPARATOR_TOKEN}".join(
            [self.header.render()]
            + [Message("System", "Current conversation:").render()]
            + [self.convo.render()]
        )

class CompletionResult(Enum):
    OK = 0
    TOO_LONG = 1
    INVALID_REQUEST = 2
    OTHER_ERROR = 3


@dataclass
class CompletionData:
    status: CompletionResult
    reply_text: str | None
    status_text: str | None


class OpenAIClient:
    def __init__(self):
        self.openai = openai
        self.openai.organization = os.getenv("ZERODAY_TTS_OPENAPI_ORG")
        self.openai.api_key = os.getenv("ZERODAY_TTS_OPENAPI_TOKEN")

    @staticmethod
    def split_into_shorter_messages(message: str) -> list[str]:
        return [
            message[i : i + MAX_CHARS_PER_REPLY_MSG]
            for i in range(0, len(message), MAX_CHARS_PER_REPLY_MSG)
        ]

    async def generate_completion_response(
            self, message: list[Message]
    ) -> CompletionData:
        try:
            prompt = Prompt(
                header=Message(
                    "System", f"Instructions for Bixby: Powered by OpenAI GPT-3.5 and Microsoft Azure TTS"
                ),
                convo=Conversation(message + [Message("Bixby")]),
            )
            rendered = prompt.render()
            response = await self.openai.Completion.acreate(
                engine="gpt-3.5-turbo",
                prompt=rendered,
                temperature=1.0,
                top_p=0.9,
                max_tokens=512,
                stop=["<|endoftext|>"],
            )
            reply = response.choices[0].text.strip()
            return CompletionData(
                status=CompletionResult.OK,
                reply_text=reply,
                status_text=None
            )
        except openai.error.InvalidRequestError as e:
            if "This model's maximum context length" in e.user_message:
                return CompletionData(
                    status=CompletionResult.TOO_LONG,
                    reply_text=None,
                    status_text=str(e),
                )
            else:
                return CompletionData(
                    status=CompletionResult.INVALID_REQUEST,
                    reply_text=None,
                    status_text=str(e),
                )
        except Exception as e:
            return CompletionData(
                status=CompletionResult.OTHER_ERROR,
                reply_text=None,
                status_text=str(e),
            )