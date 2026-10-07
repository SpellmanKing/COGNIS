"""Interface abstrata para o padrão Repository e Unit of Work de Decisões."""
from abc import ABC, abstractmethod
from typing import List, Sequence, Optional
from cognis.domain.models import CycleDecisionRecord


class DecisionRepository(ABC):
    """Repositório abstrato para persistência e consulta das decisões geradas pelos agentes."""

    @abstractmethod
    def add(self, record: CycleDecisionRecord) -> None:
        """Adiciona um registro de ciclo de decisão."""
        pass

    @abstractmethod
    def add_batch(self, records: Sequence[CycleDecisionRecord]) -> None:
        """Adiciona múltiplos registros de ciclo."""
        pass

    @abstractmethod
    def get_by_cycle(self, cycle_id: int) -> List[CycleDecisionRecord]:
        """Recupera registros filtrados por ID de ciclo."""
        pass

    @abstractmethod
    def list_all(self) -> List[CycleDecisionRecord]:
        """Lista todos os registros acumulados na sessão."""
        pass

    @abstractmethod
    def save(self) -> None:
        """Persiste os dados para a mídia de armazenamento."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Limpa os registros em memória/sessão."""
        pass


class UnitOfWork:
    """Implementação do padrão Unit of Work para controle transacional de ciclo."""

    def __init__(self, repository: DecisionRepository):
        self.repository = repository
        self._committed = False

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            if not self._committed:
                self.commit()

    def commit(self) -> None:
        """Persiste as alterações acumuladas pelo repositório."""
        self.repository.save()
        self._committed = True

    def rollback(self) -> None:
        """Cancela a persistência da transação atual."""
        self._committed = False
