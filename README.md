# COGNIS: Motor de Decisão de Agentes Autônomos (Subgrupo C)

> **Iniciação Científica - Sistemas Multiagentes & Inteligência Artificial**  
> Arquitetura de Software Empresarial, Resiliente, Tipada e Desacoplada com Pydantic v2.

---

## 🏛️ Visão Geral da Arquitetura

O **COGNIS** foi refatorado seguindo os princípios de **Clean Architecture**, **SOLID** e **Design Patterns** consagrados, atendendo integralmente aos requisitos do **Subgrupo C** e às diretrizes de isolamento de segurança do **Subgrupo D**.

```
COGNIS/
├── cognis/
│   ├── domain/               # Entidades de domínio, Enums e Exceções (Pydantic v2)
│   │   ├── enums.py          # ActionType, UrgencyLevel, RiskLevel
│   │   ├── models.py         # DecisaoAgente, StrategicScratchpad, CycleDecisionRecord
│   │   └── exceptions.py     # Hierarquia de exceções de domínio
│   ├── security/             # Segurança e Mascaramento Tático (Subgrupo D)
│   │   └── redaction.py      # TacticalMasker, SensitiveLogFilter, sanitize_error_message
│   ├── strategies/           # Padrão Strategy para Perfis Táticos
│   │   ├── base.py           # TacticalStrategy (ABC) com auto-mascaramento
│   │   ├── concrete.py       # Agressivo, Defensivo, Explorador, Oportunista
│   │   └── registry.py       # StrategyRegistry (Factory & Catálogo central)
│   ├── providers/            # Padrão Strategy para Conectores de Inferência LLM
│   │   ├── base.py           # LLMProvider (ABC), LLMResponse
│   │   ├── mock.py           # MockLLMProvider (Determinístico com suporte a falhas e cura)
│   │   ├── adapter.py        # CallableLLMAdapter (Retrocompatibilidade 100%)
│   │   ├── openai_provider.py# OpenAILLMProvider (httpx)
│   │   └── ollama_provider.py# OllamaLLMProvider (Modelos locais)
│   ├── resilience/           # Resiliência, Self-Healing e Fallbacks
│   │   ├── retry.py          # SelfHealingManager (Autocorreção guiada por erro de schema)
│   │   └── fallback.py       # FallbackPolicy (Isolamento com status INATIVO)
│   ├── repository/           # Padrão Repository & Unit of Work
│   │   ├── base.py           # DecisionRepository (ABC), UnitOfWork
│   │   └── json_repository.py# JsonDecisionRepository (Gravação atômica segura)
│   ├── core/                 # Orquestração do Ciclo
│   │   ├── prompt_builder.py # DynamicPromptBuilder (Injeção de contexto & CoT)
│   │   └── engine.py         # DecisionEngine (Motor central multiagente)
│   └── compatibility.py      # Facade AgenteCicloIA para retrocompatibilidade
├── tests/                    # Suíte completa de testes unitários (pytest)
│   ├── test_domain_models.py
│   ├── test_security_redaction.py
│   ├── test_resilience_and_self_healing.py
│   ├── test_strategies.py
│   ├── test_decision_engine.py
│   ├── test_repository.py
│   ├── test_providers.py
│   └── test_compatibility.py
├── main.py                   # Ponto de entrada executável e demonstrador
└── Documento_5_Decisoes.json # Relatório de pesquisa estruturado e validado
```

---

## 🚀 Requisitos e Inovações Implementadas

### 1. Montagem Dinâmica do Prompt de Ciclo
- **`DynamicPromptBuilder`**: Estrutura as seções:
  - `[INSTRUÇÃO ESTRATÉGICA]`: Perfil ativo e diretriz tática.
  - `[ESTADO DO MUNDO]`: Relatório de percepção formatado.
  - `[REFLEXÃO ESTRATÉGICA (CHAIN-OF-THOUGHT)]`: Orientação de deliberação antes da ação.
  - `[PERGUNTA DE DECISÃO]`: Pergunta solicitando a tomada de decisão do ciclo.
  - `[REQUISITOS OBRIGATÓRIOS DE RESPOSTA]`: JSON Schema rígido gerado via Pydantic v2.

### 2. Validação Rígida & Pydantic v2
- **`DecisaoAgente`**: Garante campos obrigatórios, min_length de justificativa, coordenadas cartesianas e enum estrito de ações permitidas: `AVANCAR`, `RECUAR`, `COLETAR_RECURSO`, `DEFENDER`, `PATRULHAR`, `INATIVO`.

### 3. Raciocínio Estratégico Aprimorado (Inovação CoT)
- Campo estruturado **`scratchpad`** (`StrategicScratchpad`) contendo:
  - `analise_situacional`: Diagnóstico do ambiente e proximidade de ameaças/recursos.
  - `ponderacao_risco`: Classificação (`BAIXO`, `MEDIO`, `ALTO`, `CRITICO`).
  - `hipotese_tatica`: Deliberação lógica preliminar antes do colapso na ação final.

### 4. Resiliência e Auto-Recuperação (Self-Healing / Retry Pattern)
- **`SelfHealingManager`**:
  - Intercepta erros sintáticos de JSON ou violações semânticas de schema.
  - Aciona ciclo de autocorreção enviando o diagnóstico sanitizado do erro de volta ao modelo (`max_retries` configurável).
  - Caso persista a falha, aciona **`FallbackPolicy`**, marcando o agente como `INATIVO` e persistindo o log técnico do motivo.

### 5. Segurança e Isolamento Tático (Requisito Subgrupo D)
- **`TacticalMasker`** e **`SensitiveLogFilter`**:
  - Diretrizes estratégicas confidenciais são automaticamente registradas no catálogo de dados sensíveis.
  - Filtro em nível de logging (`logging.Filter`) mascara qualquer diretriz em mensagens, formatações, telemetria de erro e stack traces com o token `[DIRETRIZ_CONFIDENCIAL_SUBGRUPO_D]`.
  - Representações de objetos (`__repr__`) omitem dados confidenciais.

### 6. Padrão Strategy & Repository
- **Perfis Táticos**: Interface `TacticalStrategy` implementada por `AggressiveStrategy`, `DefensiveStrategy`, `ExplorerStrategy` e `OpportunisticStrategy`.
- **Provedores de Inferência**: Interface `LLMProvider` desacoplada (Mock, OpenAI, Ollama, Adaptador Legado).
- **Persistência**: `JsonDecisionRepository` com gravação atômica via arquivo temporário para evitar corrupção em falhas elétricas/crash, gerenciada por `UnitOfWork`.

---

## 🧪 Como Executar os Testes

```bash
python -m pytest -v
```

Todos os 25 testes cobrem validação de schema, sanitização de segurança, resiliência de retentativa, autocorreção, persistência e retrocompatibilidade.

---

## 💻 Exemplo de Uso Moderno

```python
from cognis import (
    DecisionEngine,
    StrategyRegistry,
    MockLLMProvider,
    JsonDecisionRepository,
    RetryConfig,
    SelfHealingManager
)

# 1. Instanciação com injeção de dependências
engine = DecisionEngine(
    strategy_registry=StrategyRegistry.create_canonical_registry(),
    llm_provider=MockLLMProvider(),
    repository=JsonDecisionRepository("Documento_5_Decisoes.json"),
    self_healing_manager=SelfHealingManager(RetryConfig(max_retries=1))
)

# 2. Execução do ciclo multiperfil
percepcao = {
    "ciclo": 1,
    "posicao_atual": {"x": 12, "y": 8},
    "energia_restante": 78,
    "ameacas_detectadas": [{"tipo": "Inimigo", "distancia": 3}],
    "recursos_no_raio": [{"tipo": "Bateria", "distancia": 1}]
}

resultados = engine.run_multi_profile_cycle(cycle_id=1, perception_state=percepcao)
```
