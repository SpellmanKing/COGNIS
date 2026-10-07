"""Montagem dinâmica de templates de instrução para o ciclo de decisão."""
import json
from typing import Dict, Any, Optional
from cognis.strategies.base import TacticalStrategy
from cognis.domain.models import DecisaoAgente


class DynamicPromptBuilder:
    """Construtor dinâmico de prompts de percepção-decisão.

    Garante a composição estruturada dos requisitos de ciclo:
    1. Diretriz do Perfil Estratégico ativo.
    2. Estado atual do ambiente (Relatório de Percepção).
    3. Pergunta decisória solicitando a ação do agente.
    4. Schema estrito do Pydantic v2 com suporte a Scratchpad (Chain-of-Thought).
    """

    def __init__(self, include_scratchpad_guidance: bool = True):
        self.include_scratchpad_guidance = include_scratchpad_guidance

    def build_cycle_prompt(
        self,
        strategy: TacticalStrategy,
        perception_state: Dict[str, Any],
        custom_query: Optional[str] = None
    ) -> str:
        """Monta o template completo de instrução do ciclo."""
        schema_format = json.dumps(DecisaoAgente.model_json_schema(), indent=2)
        perception_json = json.dumps(perception_state, indent=2, ensure_ascii=False)

        pergunta = (
            custom_query or
            "Com base no seu perfil estratégico e no estado atual do ambiente acima, qual ação você executará neste ciclo?"
        )

        deliberation_block = ""
        if self.include_scratchpad_guidance:
            deliberation_block = f"""
[REFLEXÃO ESTRATÉGICA (CHAIN-OF-THOUGHT)]
Antes de definir sua ação final, preencha o campo 'scratchpad' contendo sua reflexão deliberativa interna:
- analise_situacional: sua interpretação detalhada do cenário atual e ameaças.
- ponderacao_risco: BAIXO, MEDIO, ALTO ou CRITICO.
- hipotese_tatica: {strategy.deliberation_focus}
""".strip() + "\n\n"

        prompt = f"""
Você é um agente autônomo baseado em Inteligência Artificial operando em um ambiente simulado.

[INSTRUÇÃO ESTRATÉGICA]
Perfil ativo: {strategy.name}
Diretriz de atuação: {strategy.directive}

[ESTADO DO MUNDO - RELATÓRIO DE PERCEPÇÃO]
{perception_json}

{deliberation_block}[PERGUNTA DE DECISÃO]
{pergunta}

[REQUISITOS OBRIGATÓRIOS DE RESPOSTA]
Sua saída deve ser EXCLUSIVAMENTE um objeto JSON que siga rigidamente a seguinte estrutura:
{schema_format}

Não adicione saudações, introduções ou explicações fora do JSON.
""".strip()

        return prompt
