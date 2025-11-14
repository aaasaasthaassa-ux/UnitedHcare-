"""
Utility helpers for selecting the default model and building OpenAI/LLM requests.

Place any project-specific wrapper/adapter code here so all model calls use a single
source of truth for the default model (e.g. `settings.DEFAULT_MODEL`).

This file does NOT include a vendor SDK import to avoid forcing a specific provider.
Instead it provides small helpers and examples you can adapt when you integrate the
OpenAI SDK or another LLM provider.
"""
from typing import Any, Dict, Optional
from django.conf import settings


def get_default_model() -> str:
    """Return the configured default model name.

    This reads `settings.DEFAULT_MODEL` (falls back to 'gpt-5-mini').
    Use this function wherever your app constructs AI requests.
    """
    return getattr(settings, 'DEFAULT_MODEL', 'gpt-5-mini')


def build_completion_payload(prompt: str, *, model: Optional[str] = None, max_tokens: int = 512, temperature: float = 0.0) -> Dict[str, Any]:
    """Build a generic payload to send to an LLM.

    - `model` will default to the project's configured default model.
    - This payload shape is intentionally generic; adapt it to the SDK you use.
    """
    model_name = model or get_default_model()

    return {
        'model': model_name,
        'input': prompt,
        'max_tokens': max_tokens,
        'temperature': temperature,
    }


# Example adapter for the OpenAI Responses-like API (pseudo-code)
def send_to_llm(client, prompt: str, model: Optional[str] = None, **kwargs) -> Any:
    """
    Example wrapper showing how to use the default model with a provider client.

    - `client` should be an initialized SDK client (e.g., OpenAI client instance).
    - Adapt the call below to match the SDK you install (this is illustrative).
    """
    payload = build_completion_payload(prompt, model=model, **kwargs)

    # Example for an SDK that provides `responses.create(model=..., input=...)`:
    # return client.responses.create(model=payload['model'], input=payload['input'], max_tokens=payload['max_tokens'], temperature=payload['temperature'])

    # If using the classic `openai.Completion.create` style, adapt accordingly.
    raise NotImplementedError("Integrate this wrapper with your chosen SDK; see file docstring.")
