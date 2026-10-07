"""Núcleo Orquestrador do Motor de Decisão de Agentes Autônomos (Subgrupo C)."""
import logging
from typing import Dict, Any, List, Optional, Sequence
from pathlib import Path

from cognis.strategies.base import TacticalStrategy
from cognis.strategies.registry import StrategyRegistry
from cognis.providers.base import LLMProvider
from cognis.resilience.retry import SelfHealingManager, RetryConfig
from cognis.repository.base import DecisionRepository, UnitOfWork
from cognis.repository.json_repository import JsonDecisionRepository
from cognis.core.prompt_builder import DynamicPromptBuilder
from cognis.domain.models import CycleDecisionRecord
from cognis.security.redaction import setup_secure_logging

logger = setup_secure_logging()


class DecisionEngine:
    """Motor de Decisão multiagente resiliente, tipado e desacoplado.

    Implementa orquestração do ciclo de percepção-decisão, injeção de dependências,
    execução multiperfil, auto-recuperação por retry guiado e persistência no Documento 5.
    """

    def __init__(
        self,
        strategy_registry: Optional[StrategyRegistry] = None,
        llm_provider: Optional[LLMProvider] = None,
        repository: Optional[DecisionRepository] = None,
        self_healing_manager: Optional[SelfHealingManager] = None,
        prompt_builder: Optional[DynamicPromptBuilder] = None
    ):
        self.registry = strategy_registry or StrategyRegistry.create_canonical_registry()
        self.llm_provider = llm_provider
        self.repository = repository or JsonDecisionRepository()
        self.self_healing = self_healing_manager or SelfHealingManager(RetryConfig(max_retries=1))
        self.prompt_builder = prompt_builder or DynamicPromptBuilder()

    def set_llm_provider(self, provider: LLMProvider) -> "DecisionEngine":
        """Permite configurar ou alternar o provedor de LLM dinamicamente."""
        self.llm_provider = provider
        return self

    def execute_agent_cycle(
        self,
        cycle_id: int,
        strategy: TacticalStrategy,
        perception_state: Dict[str, Any],
        provider_override: Optional[LLMProvider] = None
    ) -> CycleDecisionRecord:
        """Executa o ciclo completo para um perfil estratégico individual."""
        provider = provider_override or self.llm_provider
        if provider is None:
            raise ValueError(
                "Nenhum conector de LLM fornecido. Configure um provedor via set_llm_provider ou no construtor."
            )

        logger.info(f"Iniciando deliberação para o perfil [{strategy.name}] no Ciclo {cycle_id}")

        # 1. Montagem dinâmica do prompt de ciclo
        prompt = self.prompt_builder.build_cycle_prompt(
            strategy=strategy,
            perception_state=perception_state
        )

        # 2. Inferência com política de autorrecuperação e fallback seguro
        result = self.self_healing.process_with_recovery(
            llm_provider=provider,
            initial_prompt=prompt
        )

        # 3. Empacotamento no registro formal do ciclo
        record = CycleDecisionRecord(
            ciclo_id=cycle_id,
            perfil_estrategico=strategy.name,
            decisao_executada=result.decision,
            resposta_valida=result.is_valid,
            motivo_inativo=result.failure_reason,
            tentativas_executadas=result.attempts,
            recuperado_por_retry=result.recovered_by_retry
        )

        return record

    def run_multi_profile_cycle(
        self,
        cycle_id: int,
        perception_state: Dict[str, Any],
        profile_names: Optional[Sequence[str]] = None,
        provider_override: Optional[LLMProvider] = None,
        persist_immediately: bool = True
    ) -> List[CycleDecisionRecord]:
        """Executa simulações comparativas entre os perfis táticos selecionados.

        Args:
            cycle_id: Identificador do ciclo atual.
            perception_state: Dicionário contendo o relatório de percepção do mundo.
            profile_names: Lista opcional de nomes de perfis (se None, roda todos do registro).
            provider_override: Provedor pontual opcional.
            persist_immediately: Se True, adiciona e grava no repositório com Unit of Work.
        """
        if profile_names:
            strategies = [self.registry.get(name) for name in profile_names]
        else:
            strategies = self.registry.list_all()

        cycle_results: List[CycleDecisionRecord] = []

        with UnitOfWork(self.repository) as uow:
            for strategy in strategies:
                record = self.execute_agent_cycle(
                    cycle_id=cycle_id,
                    strategy=strategy,
                    perception_state=perception_state,
                    provider_override=provider_override
                )
                cycle_results.append(record)
                self.repository.add(record)

            if persist_immediately:
                uow.commit()

        return cycle_results

    def save_document_5(self, file_path: Optional[str] = None) -> None:
        """Persiste os registros consolidados para o relatório de pesquisa."""
        if file_path and isinstance(self.repository, JsonDecisionRepository):
            self.repository.file_path = Path(file_path)
        self.repository.save()
        logger.info("Relatório formal do Documento 5 salvo com sucesso.")

    def get_records(self) -> List[CycleDecisionRecord]:
        """Retorna todos os registros salvos no repositório."""
        return self.repository.list_all()
