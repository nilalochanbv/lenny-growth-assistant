import time
import httpx
from typing import Optional, Dict, Any
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.agents.providers.base import BaseLLMProvider, ProviderResponse, ProviderStatus

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = None, model_name: str = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model_name = model_name or settings.OLLAMA_MODEL

    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> ProviderResponse:
        start_time = time.time()
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_SECONDS) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    err_msg = f"Ollama returned HTTP {res.status_code}: {res.text}"
                    logger.error(err_msg)
                    return ProviderResponse(
                        text="",
                        model_name=self.model_name,
                        provider_type="local",
                        error=err_msg
                    )
                
                data = res.json()
                response_text = data.get("response", "")
                latency = (time.time() - start_time) * 1000

                return ProviderResponse(
                    text=response_text,
                    model_name=self.model_name,
                    provider_type="local",
                    latency_ms=round(latency, 2)
                )

        except httpx.ConnectError:
            err = f"Could not connect to Ollama at {self.base_url}. Ensure Ollama is running ('ollama serve')."
            logger.error(err)
            return ProviderResponse(
                text="",
                model_name=self.model_name,
                provider_type="local",
                error=err
            )
        except httpx.TimeoutException:
            err = f"Ollama generation timed out after {settings.OLLAMA_TIMEOUT_SECONDS}s."
            logger.error(err)
            return ProviderResponse(
                text="",
                model_name=self.model_name,
                provider_type="local",
                error=err
            )
        except Exception as e:
            err = f"Unexpected Ollama provider error: {str(e)}"
            logger.error(err)
            return ProviderResponse(
                text="",
                model_name=self.model_name,
                provider_type="local",
                error=err
            )

    async def health_check(self) -> ProviderStatus:
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    has_model = any(self.model_name in m for m in models)
                    
                    return ProviderStatus(
                        is_available=True,
                        provider_name="ollama",
                        model_name=self.model_name,
                        message="Ollama instance is online." if has_model else f"Ollama is running, but model '{self.model_name}' is not downloaded yet.",
                        details={"installed_models": models, "target_model_installed": has_model}
                    )
                else:
                    return ProviderStatus(
                        is_available=False,
                        provider_name="ollama",
                        model_name=self.model_name,
                        message=f"Ollama returned HTTP {res.status_code}",
                        details={}
                    )
        except Exception as e:
            return ProviderStatus(
                is_available=False,
                provider_name="ollama",
                model_name=self.model_name,
                message=f"Ollama is unreachable at {self.base_url}: {str(e)}",
                details={}
            )
