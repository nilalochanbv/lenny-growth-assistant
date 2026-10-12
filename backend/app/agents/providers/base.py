from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel

class ProviderResponse(BaseModel):
    text: str
    model_name: str
    provider_type: str  # "local" or "cloud"
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
    error: Optional[str] = None

class ProviderStatus(BaseModel):
    is_available: bool
    provider_name: str
    model_name: str
    message: str
    details: Optional[Dict[str, Any]] = None

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> ProviderResponse:
        pass

    @abstractmethod
    async def health_check(self) -> ProviderStatus:
        pass
