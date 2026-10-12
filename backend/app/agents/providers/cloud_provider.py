import time
import os
import httpx
from typing import Optional, Dict, Any
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.agents.providers.base import BaseLLMProvider, ProviderResponse, ProviderStatus

class CloudProvider(BaseLLMProvider):
    def __init__(self, provider_type: str = None, model_name: str = None):
        self.provider_type = (provider_type or settings.CLOUD_PROVIDER).lower()
        self.model_name = model_name or settings.CLOUD_MODEL_NAME

    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> ProviderResponse:
        start_time = time.time()
        
        # Support Gemini
        if self.provider_type == "gemini":
            api_key = settings.GEMINI_API_KEY or os.getenv("GOOGLE_API_KEY", "")
            if not api_key:
                return ProviderResponse(
                    text="",
                    model_name=self.model_name,
                    provider_type="cloud",
                    error="GEMINI_API_KEY environment variable is not set. Please configure it in your .env or settings."
                )
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                
                # Combine system prompt with prompt
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"System Instructions:\n{system_prompt}\n\nUser Request:\n{prompt}"
                    
                model = genai.GenerativeModel(self.model_name)
                # Run synchronous call in thread pool or direct
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                )
                latency = (time.time() - start_time) * 1000
                return ProviderResponse(
                    text=response.text if hasattr(response, "text") else str(response),
                    model_name=self.model_name,
                    provider_type="cloud",
                    latency_ms=round(latency, 2)
                )
            except Exception as e:
                err = f"Gemini API error: {str(e)}"
                logger.error(err)
                return ProviderResponse(
                    text="",
                    model_name=self.model_name,
                    provider_type="cloud",
                    error=err
                )

        # Support Anthropic Claude
        elif self.provider_type == "anthropic":
            api_key = settings.ANTHROPIC_API_KEY
            if not api_key:
                return ProviderResponse(
                    text="",
                    model_name=self.model_name,
                    provider_type="cloud",
                    error="ANTHROPIC_API_KEY environment variable is not set."
                )
            try:
                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
                messages = [{"role": "user", "content": prompt}]
                payload = {
                    "model": self.model_name if "claude" in self.model_name else "claude-3-5-sonnet-20241022",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": messages
                }
                if system_prompt:
                    payload["system"] = system_prompt

                async with httpx.AsyncClient(timeout=60.0) as client:
                    res = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
                    if res.status_code != 200:
                        return ProviderResponse(
                            text="",
                            model_name=self.model_name,
                            provider_type="cloud",
                            error=f"Anthropic API returned {res.status_code}: {res.text}"
                        )
                    data = res.json()
                    text = "".join([c.get("text", "") for c in data.get("content", [])])
                    latency = (time.time() - start_time) * 1000
                    return ProviderResponse(
                        text=text,
                        model_name=self.model_name,
                        provider_type="cloud",
                        latency_ms=round(latency, 2)
                    )
            except Exception as e:
                err = f"Anthropic API call error: {str(e)}"
                logger.error(err)
                return ProviderResponse(
                    text="",
                    model_name=self.model_name,
                    provider_type="cloud",
                    error=err
                )

        # Support OpenAI
        elif self.provider_type == "openai":
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                return ProviderResponse(
                    text="",
                    model_name=self.model_name,
                    provider_type="cloud",
                    error="OPENAI_API_KEY environment variable is not set."
                )
            try:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "content-type": "application/json"
                }
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": self.model_name if "gpt" in self.model_name else "gpt-4o-mini",
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "messages": messages
                }

                async with httpx.AsyncClient(timeout=60.0) as client:
                    res = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                    if res.status_code != 200:
                        return ProviderResponse(
                            text="",
                            model_name=self.model_name,
                            provider_type="cloud",
                            error=f"OpenAI API returned {res.status_code}: {res.text}"
                        )
                    data = res.json()
                    text = data["choices"][0]["message"]["content"]
                    latency = (time.time() - start_time) * 1000
                    return ProviderResponse(
                        text=text,
                        model_name=self.model_name,
                        provider_type="cloud",
                        latency_ms=round(latency, 2)
                    )
            except Exception as e:
                err = f"OpenAI API call error: {str(e)}"
                logger.error(err)
                return ProviderResponse(
                    text="",
                    model_name=self.model_name,
                    provider_type="cloud",
                    error=err
                )

        else:
            return ProviderResponse(
                text="",
                model_name=self.model_name,
                provider_type="cloud",
                error=f"Unsupported cloud provider: '{self.provider_type}'"
            )

    async def health_check(self) -> ProviderStatus:
        if self.provider_type == "gemini":
            has_key = bool(settings.GEMINI_API_KEY or os.getenv("GOOGLE_API_KEY", ""))
            return ProviderStatus(
                is_available=has_key,
                provider_name="gemini",
                model_name=self.model_name,
                message="Gemini API key configured." if has_key else "Missing GEMINI_API_KEY in environment."
            )
        elif self.provider_type == "anthropic":
            has_key = bool(settings.ANTHROPIC_API_KEY)
            return ProviderStatus(
                is_available=has_key,
                provider_name="anthropic",
                model_name=self.model_name,
                message="Anthropic API key configured." if has_key else "Missing ANTHROPIC_API_KEY in environment."
            )
        elif self.provider_type == "openai":
            has_key = bool(settings.OPENAI_API_KEY)
            return ProviderStatus(
                is_available=has_key,
                provider_name="openai",
                model_name=self.model_name,
                message="OpenAI API key configured." if has_key else "Missing OPENAI_API_KEY in environment."
            )
        return ProviderStatus(
            is_available=False,
            provider_name=self.provider_type,
            model_name=self.model_name,
            message="Unknown cloud provider configuration."
        )
