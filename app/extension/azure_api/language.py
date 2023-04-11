import os

from azure.ai.textanalytics import DocumentError, TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential


class AzureLanguageService:
    def __init__(self):
        self.ta_credential = AzureKeyCredential(os.environ.get("ms_language_key"))
        self.endpoint = "https://zerodaytts-language.cognitiveservices.azure.com/"

        self.client = self.authenticate_client()

    def authenticate_client(self):
        text_analytics_client = TextAnalyticsClient(
            endpoint=self.endpoint, credential=self.ta_credential
        )
        return text_analytics_client

    def language_detect(self, text: str):
        response = self.client.detect_language(documents=[text], country_hint="kr")[0]
        if isinstance(response, DocumentError):
            raise response
        return str(response.primary_language.iso6391_name)
