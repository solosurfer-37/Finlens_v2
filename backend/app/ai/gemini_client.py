from google import genai

from app.config import settings


class GeminiClient:
    """Low-level wrapper around the Gemini API. Sends a prompt, returns raw text."""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.client = genai.Client(api_key=settings.gemini_api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text