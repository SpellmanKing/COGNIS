"""Política de fallback para agentes autônomos em caso de falha irreversível."""
from typing import Optional
from cognis.domain.models import DecisaoAgente
from cognis.domain.enums import ActionType, UrgencyLevel
from cognis.security.redaction import TacticalMasker


class FallbackPolicy:
    """Implementa o padrão de contenção de falhas do Subgrupo C.

    Caso ocorra alucinação sintática, quebra de JSON ou violação de regras semânticas,
    o agente DEVE ser marcado como INATIVO naquele ciclo, preservando o log do motivo exato.
    """

    DEFAULT_JUSTIFICATION = (
        "Agente mantido inativo devido a erro de validação sintática ou lógica na IA."
    )

    @classmethod
    def create_inactive_decision(
        cls,
        custom_justification: Optional[str] = None
    ) -> DecisaoAgente:
        """Cria uma instância de DecisaoAgente configurada como INATIVO."""
        return DecisaoAgente(
            acao=ActionType.INATIVO,
            justificativa=custom_justification or cls.DEFAULT_JUSTIFICATION,
            alvo_coordenada=None,
            urgencia=UrgencyLevel.BAIXA
        )

    @classmethod
    def sanitize_failure_reason(cls, raw_error: str) -> str:
        """Sanitiza o motivo da falha para impedir vazamento de diretrizes confidenciais."""
        masker = TacticalMasker.get_instance()
        return masker.mask(raw_error)
