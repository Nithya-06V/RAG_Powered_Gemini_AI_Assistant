from google import genai
from google.genai import types


class GeminiServiceError(Exception):
    def __init__(self, message, category="service"):
        super().__init__(message)
        self.category = category


def create_client(api_key=None):
    key = api_key or __import__("os").getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise GeminiServiceError(
            "Add your Gemini API key in Settings to enable AI answers and document indexing.",
            "missing_key",
        )
    return genai.Client(api_key=key)


def explain_api_error(error):
    message = str(error).lower()
    status = getattr(error, "code", None) or getattr(error, "status_code", None)
    if status in (401, 403) or "api key not valid" in message or "unauthenticated" in message:
        return GeminiServiceError("The API key was rejected. Check the key in Settings.", "invalid_key")
    if status == 429 or "quota" in message or "resource_exhausted" in message:
        return GeminiServiceError("Gemini quota was reached. Check your API project limits and try again later.", "quota")
    if status == 404 or "model" in message and ("not found" in message or "unsupported" in message):
        return GeminiServiceError("The configured Gemini model is unavailable. Update GEMINI_MODEL in .env.", "model")
    if "timeout" in message or "connection" in message or "network" in message:
        return GeminiServiceError("Could not reach Gemini. Check your internet connection and try again.", "network")
    return GeminiServiceError("Gemini could not complete the request. Check Settings and try again.", "service")


def generate_text(prompt, api_key=None):
    client = create_client(api_key)
    try:
        response = client.models.generate_content(
            model=__import__("os").getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            contents=prompt,
        )
        if not response.text:
            raise GeminiServiceError("Gemini returned an empty response. Please try again.")
        return response.text
    except GeminiServiceError:
        raise
    except Exception as error:
        raise explain_api_error(error) from error


def embed_texts(texts, task_type, api_key=None):
    client = create_client(api_key)
    import os

    try:
        response = client.models.embed_content(
            model=os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"),
            contents=texts,
            config=types.EmbedContentConfig(task_type=task_type),
        )
        return [embedding.values for embedding in response.embeddings]
    except Exception as error:
        raise explain_api_error(error) from error


def test_api_key(api_key):
    client = create_client(api_key)
    import os

    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            contents="Reply with OK.",
            config=types.GenerateContentConfig(max_output_tokens=8),
        )
        return bool(response.text)
    except Exception as error:
        raise explain_api_error(error) from error
