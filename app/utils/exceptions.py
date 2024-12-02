class LLMServiceException(Exception):
    pass

class ClientNotFoundException(LLMServiceException):
    pass

class ModelNotFoundException(LLMServiceException):
    pass

class APIKeyNotFoundError(LLMServiceException):
    pass
