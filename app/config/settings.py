# app/config/settings.py

import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

class Settings:
    # Supabase 配置
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    # AWS 配置
    AWS_REGION: str = os.getenv("AWS_REGION")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME: str = os.getenv("AWS_BUCKET_NAME")
    STORAGE_URL: str = os.getenv("STORAGE_URL")
    
    # LLM 配置
    AZURE_OPENAI_API_KEY_AUSTRALIAEAST: str = os.getenv("AZURE_OPENAI_API_KEY_AUSTRALIAEAST")
    AZURE_OPENAI_API_ENDPOINT_AUSTRALIAEAST: str = os.getenv("AZURE_OPENAI_API_ENDPOINT_AUSTRALIAEAST")
    AZURE_OPENAI_API_KEY_EASTUS: str = os.getenv("AZURE_OPENAI_API_KEY_EASTUS")
    AZURE_OPENAI_API_ENDPOINT_EASTUS: str = os.getenv("AZURE_OPENAI_API_ENDPOINT_EASTUS")
    
    # AZURE TTS 配置
    AZURE_SUBSCRIPTION_KEY: str = os.getenv("AZURE_SUBSCRIPTION_KEY")
    AZURE_SERVICE_REGION: str = os.getenv("AZURE_SERVICE_REGION")
    MAX_THREADS: int = int(os.getenv("MAX_THREADS", "10"))
    
    # STEP-1 配置
    STEP_API_KEY: str = os.getenv("STEP_API_KEY")
    STEP_API_BASE_URL: str = os.getenv("STEP_API_BASE_URL")
    
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
    
    # timeout
    MODEL_TIMEOUT: int = int(os.getenv("MODEL_TIMEOUT", "20"))
    PROCESS_TIMEOUT: int = int(os.getenv("PROCESS_TIMEOUT", "30"))


# 创建一个全局的 settings 实例
settings = Settings()
