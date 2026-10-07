"""Exceções de domínio do sistema COGNIS."""

class CognisException(Exception):
    """Exceção base do sistema COGNIS."""
    pass


class ContractValidationError(CognisException):
    """Lançada quando a resposta da LLM viola o schema estrito Pydantic v2."""
    def __init__(self, message: str, raw_response: str = "", details: list = None):
        super().__init__(message)
        self.raw_response = raw_response
        self.details = details or []


class TacticalLeakageSecurityError(CognisException):
    """Lançada quando uma diretriz confidencial é exposta inadvertidamente."""
    pass


class ProviderInferenceError(CognisException):
    """Lançada em caso de falha de comunicação ou timeout no conector de inferência."""
    pass


class StrategyNotFoundError(CognisException):
    """Lançada quando um perfil tático requisitado não está cadastrado no registro."""
    pass
