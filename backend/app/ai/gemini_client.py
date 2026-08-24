import google.generativeai as genai

from app.config import settings

genai.configure(api_key=settings.gemini_api_key)


class GeminiClient:
    """Low-level wrapper around the Gemini API. Sends a prompt, returns raw text."""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text