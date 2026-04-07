"""LLM abstraction layer — supports Anthropic (ChatAnthropic) and Ollama (ChatOllama)."""

import json
import re
from typing import Any

import structlog
from langchain_core.messages import HumanMessage, SystemMessage

from cloudops_ai.config import settings

log = structlog.get_logger()


def get_llm_client() -> Any:
    """
    Factory: returns configured LLM client based on LLM_BACKEND setting.
    
    Backends:
      - "anthropic" (default): ChatAnthropic (requires ANTHROPIC_API_KEY)
      - "ollama": ChatOllama (requires OLLAMA_BASE_URL)
    """
    backend = settings.llm_backend.lower()

    if backend == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.0,  # deterministic for classification
        )

    elif backend == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=settings.classifier_model,
            api_key=settings.anthropic_api_key,
        )

    else:
        raise ValueError(
            f"Unknown LLM backend: {backend}. "
            "Supported: 'anthropic', 'ollama'"
        )


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int | None = None,
) -> str:
    """
    Async LLM call wrapper. Returns the raw response text.
    
    Args:
        system_prompt: System message content
        user_prompt: User message content
        max_tokens: Max output tokens (may be ignored by Ollama)
    
    Returns:
        Raw LLM response text
    """
    llm = get_llm_client()

    # For Anthropic, set max_tokens on the client
    if settings.llm_backend.lower() == "anthropic" and max_tokens:
        llm.max_tokens = max_tokens

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    response = await llm.ainvoke(messages)
    return str(response.content)


def extract_json_from_response(raw_response: str) -> dict[str, Any]:
    """
    Extract JSON from LLM response (handles markdown code blocks).
    
    Args:
        raw_response: Raw response text from LLM
    
    Returns:
        Parsed JSON dict
    
    Raises:
        ValueError: If no valid JSON found
    """
    # Try extracting from markdown code block first
    code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_response, re.DOTALL)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1))
        except json.JSONDecodeError:
            pass

    # Fall back to raw JSON anywhere in response
    json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
    if not json_match:
        raise ValueError(f"No JSON found in LLM response: {raw_response}")

    return json.loads(json_match.group())
