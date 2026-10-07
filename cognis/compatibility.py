"""Camada de compatibilidade retroativa para a classe legado AgenteCicloIA."""
from typing import Dict, Any, List, Callable, Optional
from pathlib import Path

from cognis.strategies.registry import StrategyRegistry
from cognis.providers.adapter import CallableLLMAdapter
from cognis.repository.json_repository import JsonDecisionRepository
from cognis.resilience.retry import SelfHealingManager, RetryConfig
from cognis.core.engine import DecisionEngine
from cognis.core.prompt_builder import DynamicPromptBuilder
from cognis.domain.models import DecisaoAgente, CycleDecisionRecord


class AgenteCicloIA:
    """Facade retrocompatível que preserva a API original de AgenteCicloIA

    mas delega a execução internamente para a nova arquitetura desacoplada e modular do COGNIS.
    """

    def __init__(
        self,
        perfis_estrategicos: Dict[str, str],
        nome_arquivo_saida: str = "Documento_5_Decisoes.json",
        max_retries: int = 1
    ):
        self.perfis = perfis_estrategicos
        self.registry = StrategyRegistry.from_dict(perfis_estrategicos)
        self.repository = JsonDecisionRepository(file_path=nome_arquivo_saida, legacy_mode=True)
        self.self_healing = SelfHealingManager(RetryConfig(max_retries=max_retries))
        self.prompt_builder = DynamicPromptBuilder(include_scratchpad_guidance=True)
        self.engine = DecisionEngine(
            strategy_registry=self.registry,
            repository=self.repository,
            self_healing_manager=self.self_healing,
            prompt_builder=self.prompt_builder
        )
        self.registro_documento_5: List[Dict[str, Any]] = []

    def montar_instrucao_ciclo(
        self,
        perfil_nome: str,
        estado_mundo: Dict[str, Any]
    ) -> str:
        """Monta o template de ciclo mantendo a interface pública original."""
        strategy = self.registry.get(perfil_nome)
        return self.prompt_builder.build_cycle_prompt(strategy, estado_mundo)

    def validar_e_processar_resposta(self, resposta_bruta_llm: str) -> Dict[str, Any]:
        """Garante validação estrita com Pydantic v2 e fallback consistente."""
        is_valid, decision, error_reason = self.self_healing.validate_content(resposta_bruta_llm)

        if is_valid and decision is not None:
            return {
                "valido": True,
                "decisao": decision.to_documento_5_dict(),
                "motivo_inativo": None
            }
        else:
            motivo_falha = f"Formato inválido ou campos ausentes: {error_reason}"
            from cognis.resilience.fallback import FallbackPolicy
            fallback_decisao = FallbackPolicy.create_inactive_decision()
            return {
                "valido": False,
                "decisao": fallback_decisao.to_documento_5_dict(),
                "motivo_inativo": motivo_falha
            }

    def rodar_teste_quatro_perfis(
        self,
        ciclo_id: int,
        estado_mundo: Dict[str, Any],
        conector_llm_callback: Callable[[str], str]
    ) -> List[Dict[str, Any]]:
        """Executa os 4 perfis táticos utilizando a nova arquitetura e popula o Documento 5."""
        provider = CallableLLMAdapter(conector_llm_callback)
        self.engine.set_llm_provider(provider)

        records = self.engine.run_multi_profile_cycle(
            cycle_id=ciclo_id,
            perception_state=estado_mundo,
            provider_override=provider,
            persist_immediately=False
        )

        resultados_ciclo = [r.to_document_5_dict(legacy_mode=True) for r in records]
        self.registro_documento_5.extend(resultados_ciclo)
        return resultados_ciclo

    def salvar_documento_5(self, nome_arquivo: str = "Documento_5_Decisoes.json") -> None:
        """Exporta os registros compilados para a entrega acadêmica."""
        self.repository.file_path = Path(nome_arquivo)
        self.repository.save()
