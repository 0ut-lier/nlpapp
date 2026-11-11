"""OpenRouter API client for the NLP tasks."""
from __future__ import annotations

import os
from typing import Any

import requests


class APIError(RuntimeError):
    """A safe, user-displayable error from the NLP API."""


class API:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = model or os.environ.get(
            "OPENROUTER_MODEL", "liquid/lfm-3-1.7b:free"
        )
        self.timeout = timeout

    def api_call(self, system_message: str, text: str) -> str:
        if not self.api_key.strip():
            raise APIError(
                "OpenRouter API key is not configured. Set OPENROUTER_API_KEY and restart the app."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": text},
            ],
        }

        try:
            response = requests.post(
                self.url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
        except requests.Timeout as exc:
            raise APIError("The NLP service timed out. Please try again.") from exc
        except requests.RequestException as exc:
            raise APIError(
                "Could not connect to the NLP service. Check your internet connection."
            ) from exc

        if response.status_code == 401:
            raise APIError("OpenRouter rejected the API key. Check OPENROUTER_API_KEY.")
        if response.status_code == 402:
            raise APIError(
                "OpenRouter reports insufficient credits or a billing restriction (HTTP 402)."
            )
        if response.status_code == 429:
            raise APIError(
                "The selected model is rate-limited. Wait briefly or choose another available model."
            )
        if response.status_code >= 500:
            raise APIError("The NLP provider is temporarily unavailable. Try again later.")
        if not response.ok:
            raise APIError(
                f"The NLP request failed (HTTP {response.status_code}). Check the model and request settings."
            )

        try:
            body = response.json()
            result = body["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise APIError("The NLP provider returned an unexpected response.") from exc

        if not isinstance(result, str) or not result.strip():
            raise APIError("The NLP provider returned an empty result.")
        return result.strip()

    def sentiment_analysis(self, text: str, system_message: str) -> str:
        return self.api_call(system_message, text)

    def nlp_task(self, task: str, text: str) -> str:
        prompts = {
            "sentiment-analysis": (
                "Perform sentiment analysis of this sentence in one word:"
            ),
            "ner": (
                "Perform named entity recognition on this sentence and classify "
                "the entities into categories like person, organization, location, etc. "
                "Return the entities in this way `entity` -> `category` and write each "
                "of them in new line:"
            ),
            "emotion-detection": (
                "Perform emotion detection on this sentence and return the most closely "
                "related emotion from the following list: happy, sad, angry, surprised, "
                "disgusted, fearful. Return only the emotion and nothing else:"
            ),
        }
        if task not in prompts:
            raise ValueError(f"Unsupported NLP task: {task}")
        if not text.strip():
            raise ValueError("Please enter some text to analyze.")
        return self.api_call(prompts[task], text.strip())
