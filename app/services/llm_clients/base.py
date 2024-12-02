from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLMClient(ABC):
    @abstractmethod
    async def generate(self, messages: List[Dict[str, Any]], model: str, temperature: float = 0.7) -> str:
        pass

    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        pass
