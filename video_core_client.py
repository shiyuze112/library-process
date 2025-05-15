from one2x_sdk.medeo.core_api.core_api_client import CoreApiClient

dev_core_api_client = CoreApiClient(
    base_url="https://medeo-core-api.dev.one2x.ai",
    token="token",
    enable_requests=True
)

test_core_api_client = CoreApiClient(
    base_url="https://medeo-core-api.test.one2x.ai", 
    token="token",
    enable_requests=True
)

prod_core_api_client = CoreApiClient(
    base_url="https://medeo-core-api.prod.one2x.ai", 
    token="YHUseTEvWno",
    enable_requests=True
)