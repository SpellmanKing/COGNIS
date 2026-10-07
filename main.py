"""COGNIS: Motor de Decisão de Agentes Autônomos (Subgrupo C).

Pipeline refatorado em Arquitetura Limpa, modular, desacoplada, tipada e resiliente.

Padrões Implementados:
- Strategy: Perfis táticos e Provedores de Inferência (LLM).
- Repository & Unit of Work: Persistência transacional atômica (Documento 5).
- Self-Healing / Retry Pattern: Auto-recuperação guiada com feedback de schema.
- Fallback Gracioso: Isolamento e status INATIVO em falhas críticas.
- Segurança e Mascaramento (Subgrupo D): Isolamento estrito de diretrizes confidenciais.
- Chain-of-Thought Estruturado: Scratchpad deliberativo preliminar.
"""
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Garante compatibilidade de encoding UTF-8 no terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Exportações de Domínio e Compatibilidade Retroativa
from cognis.domain.models import (
    DecisaoAgente,
    StrategicScratchpad,
    Coordenada,
    CycleDecisionRecord
)
from cognis.domain.enums import ActionType, UrgencyLevel, RiskLevel, AcoesValidasLiteral
from cognis.strategies.concrete import (
    AggressiveStrategy,
    DefensiveStrategy,
    ExplorerStrategy,
    OpportunisticStrategy
)
from cognis.strategies.registry import StrategyRegistry
from cognis.providers.base import LLMProvider, LLMResponse
from cognis.providers.mock import MockLLMProvider
from cognis.providers.adapter import CallableLLMAdapter
from cognis.repository.json_repository import JsonDecisionRepository
from cognis.resilience.retry import SelfHealingManager, RetryConfig
from cognis.resilience.fallback import FallbackPolicy
from cognis.core.prompt_builder import DynamicPromptBuilder
from cognis.core.engine import DecisionEngine
from cognis.security.redaction import setup_secure_logging, TacticalMasker
from cognis.compatibility import AgenteCicloIA

# Alias retrocompatível para scripts antigos que importavam AcoesValidas diretamente
AcoesValidas = AcoesValidasLiteral

logger = setup_secure_logging("SubgrupoC_IA")


def demonstrar_execucao_modular():
    """Executa a simulação multiagente demonstrando a arquitetura refatorada."""
    print("=" * 80)
    print("  COGNIS: MOTOR DE DECISÃO DE AGENTES AUTÔNOMOS (SUBGRUPO C - IC)")
    print("  Arquitetura Limpa, Pydantic v2, Self-Healing & Mascaramento Subgrupo D")
    print("=" * 80)

    # 1. Configuração do Repositório de Persistência (Padrão Repository)
    caminho_doc_5 = "Documento_5_Decisoes.json"
    repositorio = JsonDecisionRepository(file_path=caminho_doc_5, legacy_mode=True)

    # 2. Catálogo de Perfis Táticos (Padrão Strategy & Registry)
    registro_estrategias = StrategyRegistry.create_canonical_registry()
    print(f"\n[+] Perfis táticos registrados: {registro_estrategias.list_names()}")

    # 3. Estado do Mundo (Relatório de Percepção do Ciclo)
    percepcao_simulada = {
        "ciclo": 1,
        "posicao_atual": {"x": 12, "y": 8},
        "energia_restante": 78,
        "ameacas_detectadas": [{"tipo": "Inimigo", "distancia": 3}],
        "recursos_no_raio": [{"tipo": "Bateria", "distancia": 1}]
    }

    # 4. Provedor de Inferência com Simulação de Cenário Real
    # Simulamos o perfil 'Oportunista' falhando na sintaxe inicial e
    # se auto-recuperando no ciclo de retry guiado por feedback de schema.
    provedor_simulado = MockLLMProvider(
        fail_profiles={"oportunista": "syntax"},
        heal_on_retry=True,
        include_scratchpad=True
    )

    # 5. Inicialização do Motor Decisório (Dependency Injection)
    politica_retry = RetryConfig(max_retries=1, enable_self_healing=True)
    gerenciador_resiliencia = SelfHealingManager(config=politica_retry)
    construtor_prompt = DynamicPromptBuilder(include_scratchpad_guidance=True)

    motor = DecisionEngine(
        strategy_registry=registro_estrategias,
        llm_provider=provedor_simulado,
        repository=repositorio,
        self_healing_manager=gerenciador_resiliencia,
        prompt_builder=construtor_prompt
    )

    print("\n--- INICIANDO CICLO COMPARATIVO DOS 4 PERFIS TÁTICOS (CICLO 1) ---")
    resultados = motor.run_multi_profile_cycle(
        cycle_id=1,
        perception_state=percepcao_simulada,
        persist_immediately=True
    )

    print("\n--- RELATÓRIO DE DELIBERAÇÃO CONSOLIDADO ---")
    for r in resultados:
        dec = r.decisao_executada
        status = "VÁLIDO" if r.resposta_valida else "INATIVO (FALLBACK)"
        healed_tag = " [RECUPERADO VIA SELF-HEALING]" if r.recuperado_por_retry else ""
        print(f"\n* Perfil: {r.perfil_estrategico:<12} | Status: {status}{healed_tag}")
        print(f"  - Ação:          {dec.acao} (Urgência: {dec.urgencia})")
        print(f"  - Justificativa: {dec.justificativa}")
        if dec.alvo_coordenada:
            print(f"  - Alvo:          ({dec.alvo_coordenada.x}, {dec.alvo_coordenada.y})")
        if dec.scratchpad:
            print(f"  - Scratchpad CoT: [{dec.scratchpad.ponderacao_risco}] {dec.scratchpad.analise_situacional}")
        if r.motivo_inativo:
            print(f"  - Motivo Falha:  {r.motivo_inativo}")

    print(f"\n[OK] Persistência executada com sucesso no arquivo: '{caminho_doc_5}'")


if __name__ == "__main__":
    demonstrar_execucao_modular()