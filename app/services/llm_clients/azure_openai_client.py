from typing import List, Dict, Any
from openai import AsyncAzureOpenAI
from app.services.llm_clients.base import BaseLLMClient
from app.config.settings import settings
from app.core.logger import app_logger


class AzureOpenAIClient(BaseLLMClient):
    def __init__(self, region: str):
        if region == "australiaeast":
            self.client = AsyncAzureOpenAI(
                api_version="2024-06-01",
                azure_endpoint=settings.AZURE_OPENAI_API_ENDPOINT_AUSTRALIAEAST,
                api_key=settings.AZURE_OPENAI_API_KEY_AUSTRALIAEAST,
            )
        elif region == "eastus":
            self.client = AsyncAzureOpenAI(
                api_version="2024-06-01",
                azure_endpoint=settings.AZURE_OPENAI_API_ENDPOINT_EASTUS,
                api_key=settings.AZURE_OPENAI_API_KEY_EASTUS,
            )
        else:
            raise ValueError(f"Unsupported Azure region: {region}")

    async def generate(
        self, messages: List[Dict[str, Any]], model: str, temperature: float = 0.7
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=model, messages=messages, temperature=temperature, response_format={"type": "json_object"}
            )
            # app_logger.info(f"Azure OpenAI API response: {response}")
            return response.choices[0].message.content
        except Exception as e:
            app_logger.error(f"Azure OpenAI API error: {str(e)}")
            raise

    async def get_embedding(self, text: str) -> List[float]:
        try:
            response = await self.client.embeddings.create(
                input=text, model="text-embedding-3-small", dimensions=512
            )
            return response.data[0].embedding
        except Exception as e:
            app_logger.error(f"Azure OpenAI Embedding API error: {str(e)}")
            raise

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            response = await self.client.embeddings.create(
                input=texts, model="text-embedding-3-small", dimensions=512
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            app_logger.error(f"Azure OpenAI Embedding API error: {str(e)}")
            raise
