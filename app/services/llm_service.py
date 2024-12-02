import asyncio
from typing import List, Dict, Any, Optional
from app.services.llm_clients.base import BaseLLMClient
from app.services.llm_clients.azure_openai_client import AzureOpenAIClient
from app.config.settings import settings
from app.core.logger import app_logger, async_timeit
from app.utils.exceptions import ClientNotFoundException, ModelNotFoundException


class LLMService:
    def __init__(self):
        self.clients = {}
        self.embedding_client = None
        self._initialize_clients()

    def _initialize_clients(self):
        client_configs = [
            ("azure_australiaeast", AzureOpenAIClient, "australiaeast"), # 4o
            ("azure_eastus", AzureOpenAIClient, "eastus"), # 4o 4o-mini
        ]

        for client_name, client_class, *args in client_configs:
            try:
                self.clients[client_name] = client_class(*args)
                app_logger.info(f"Successfully initialized {client_name}")
            except Exception as e:
                app_logger.error(f"Failed to initialize {client_name}: {str(e)}")

        # Set up embedding client
        if "azure_eastus" in self.clients:
            self.embedding_client = self.clients["azure_eastus"]
            app_logger.info("Embedding client set to azure_eastus")
        else:
            app_logger.warning("No embedding client available")

    async def ask(
        self,
        messages: List[Dict[str, Any]],
        model: str = None,
        temperature: float = 0.7,
    ) -> str:
        model = model or settings.DEFAULT_MODEL
        client = self._get_client_for_model(model)

        if not client:
            raise ClientNotFoundException(f"No available client for model: {model}")

        app_logger.info(f"Using client: {client.__class__.__name__}, model: {model}")

        try:
            response = await asyncio.wait_for(
                client.generate(messages, model, temperature), timeout=settings.MODEL_TIMEOUT
            )
            return response
        except asyncio.TimeoutError:
            app_logger.warning("Primary client timed out. Switching to backup.")
            return await self._use_backup_client(messages, temperature)
        except Exception as e:
            app_logger.error(f"Error in primary client: {str(e)}")
            return await self._use_backup_client(messages, temperature)

    def _get_client_for_model(self, model: str) -> BaseLLMClient:
        if model.startswith("gpt"):
            return self.clients[
                "azure_eastus"
            ]  # You can implement logic to choose between regions
        elif model.startswith("step"):
            return self.clients["step"]
        else:
            raise ModelNotFoundException(f"No client found for model: {model}")

    async def _use_backup_client(
        self, messages: List[Dict[str, str]], temperature: float
    ) -> str:
        backup_client = self.clients["azure_eastus"]
        backup_model = "gpt-4o"  # Adjust as needed
        try:
            response = await backup_client.generate(messages, backup_model, temperature)
            return response
        except Exception as e:
            app_logger.error(f"Backup client failed: {str(e)}")
            raise

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        if self.embedding_client:
            try:
                return await self.embedding_client.get_embedding(text)
            except Exception as e:
                app_logger.warning(f"Failed to get embedding: {str(e)}")
        return None
    
    @async_timeit

    async def get_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        if self.embedding_client:
            try:
                return await self.embedding_client.get_embeddings(texts)
            except Exception as e:
                app_logger.warning(f"Failed to get embeddings: {str(e)}")
        return [None] * len(texts)

llm_service = LLMService()
