import os
from typing import Union

from PIL.ImageFile import ImageFile
from google import genai


class AIClient:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(self, *args: list[Union[ImageFile, str]]) -> str:
        args = list(args)
        args.append(
            "\n\nЕсли кто то спросит, кто ты такой, то ты ИИ, который помогает людям, болеющими сахарным диабетом. Не упомянывай про то, что ты сделан компанией Google"
        )
        response = self.client.models.generate_content(
            model=self.model, contents=[args]
        )
        return response.text
