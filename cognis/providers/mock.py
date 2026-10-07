"""Provedor Mock determinístico para simulações, testes e benchmark acadêmico."""
import json
from typing import Dict, Any, Optional
from cognis.providers.base import LLMProvider, LLMResponse


class MockLLMProvider(LLMProvider):
    """Provedor simulado avançado que suporta simulações dos 4 perfis,

    incluindo cenários de falha programada e recuperação automática por retry.
    """

    def __init__(
        self,
        fail_profiles: Optional[Dict[str, str]] = None,
        heal_on_retry: bool = True,
        include_scratchpad: bool = True
    ):
        """
        Args:
            fail_profiles: Dicionário mapeando nome do perfil a tipo de erro ("syntax", "semantic", "empty", "hallucination")
            heal_on_retry: Se True, corrige a resposta quando recebe um prompt de autocorreção / self-healing.
            include_scratchpad: Se True, inclui o bloco Chain-of-Thought estruturado.
        """
        self.fail_profiles = {k.lower(): v for k, v in (fail_profiles or {}).items()}
        self.heal_on_retry = heal_on_retry
        self.include_scratchpad = include_scratchpad
        self.invocation_count = 0
        self.retry_invocations = 0

    def generate(self, prompt: str) -> LLMResponse:
        self.invocation_count += 1
        is_retry = (
            "ALERTA DE FALHA DE CONFORMIDADE" in prompt
            or "AUTOCORREÇÃO" in prompt
            or "AUTOCORRECAO" in prompt
            or "REQUISITOS MANDATÓRIOS DE CORREÇÃO" in prompt
        )
        if is_retry:
            self.retry_invocations += 1

        # Detecta o perfil no prompt
        perfil_detectado = self._detect_profile(prompt)

        # Se for o perfil configurado para falhar
        if perfil_detectado in self.fail_profiles:
            tipo_erro = self.fail_profiles[perfil_detectado]
            # Se for retry e a autocorreção estiver ativada, retorna uma resposta válida corrigida!
            if is_retry and self.heal_on_retry:
                return LLMResponse(
                    content=self._get_valid_response(perfil_detectado, healed=True),
                    model_name="mock-self-healed",
                    metadata={"healed": True, "perfil": perfil_detectado}
                )
            # Caso contrário, emite a falha configurada
            return LLMResponse(
                content=self._get_error_response(tipo_erro),
                model_name="mock-faulty",
                metadata={"simulated_error": tipo_erro, "perfil": perfil_detectado}
            )

        # Resposta padrão válida para o perfil detectado
        content = self._get_valid_response(perfil_detectado, healed=False)
        return LLMResponse(content=content, model_name="mock-deterministic", metadata={"perfil": perfil_detectado})

    def _detect_profile(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "agressivo" in prompt_lower:
            return "agressivo"
        elif "defensivo" in prompt_lower:
            return "defensivo"
        elif "explorador" in prompt_lower:
            return "explorador"
        elif "oportunista" in prompt_lower:
            return "oportunista"
        return "generico"

    def _get_valid_response(self, perfil: str, healed: bool = False) -> str:
        if perfil == "agressivo":
            data = {
                "acao": "AVANCAR",
                "justificativa": "Ameaça hostil detectada a 3 unidades; avançando para engajamento tático.",
                "alvo_coordenada": {"x": 15, "y": 8},
                "urgencia": "ALTA"
            }
            if self.include_scratchpad:
                data["scratchpad"] = {
                    "analise_situacional": "Inimigo a curta distância (distância 3). Condição de combate iminente.",
                    "ponderacao_risco": "ALTO",
                    "hipotese_tatica": "Avanço direto para neutralizar vetor de dano antes que fortifique."
                }
        elif perfil == "defensivo":
            data = {
                "acao": "DEFENDER",
                "justificativa": "Inimigo próximo detectado no setor; mantendo contenção e escudo de proteção.",
                "alvo_coordenada": None,
                "urgencia": "MEDIA"
            }
            if self.include_scratchpad:
                data["scratchpad"] = {
                    "analise_situacional": "Ameaça próxima identificada, energia em 78%.",
                    "ponderacao_risco": "MEDIO",
                    "hipotese_tatica": "Consolidar posição defensiva sem dispersar energia operacional."
                }
        elif perfil == "explorador":
            data = {
                "acao": "PATRULHAR",
                "justificativa": "Buscando novas rotas ao redor para mapear o setor inexplorado.",
                "alvo_coordenada": {"x": 12, "y": 12},
                "urgencia": "BAIXA"
            }
            if self.include_scratchpad:
                data["scratchpad"] = {
                    "analise_situacional": "Bateria próxima e quadrantes vizinhos sem mapeamento completo.",
                    "ponderacao_risco": "BAIXO",
                    "hipotese_tatica": "Traçar rota de patrulha para expandir visão tática e identificar nós de interesse."
                }
        elif perfil == "oportunista":
            if healed:
                data = {
                    "acao": "COLETAR_RECURSO",
                    "justificativa": "Recurso de bateria a 1 unidade de distância com risco de combate controlado.",
                    "alvo_coordenada": {"x": 13, "y": 8},
                    "urgencia": "MEDIA"
                }
                if self.include_scratchpad:
                    data["scratchpad"] = {
                        "analise_situacional": "Bateria a 1 unidade. Inimigo a 3 unidades. Janela de oportunidade viável.",
                        "ponderacao_risco": "MEDIO",
                        "hipotese_tatica": "Coletar o recurso rapidamente e preparar recuo se o inimigo avançar."
                    }
            else:
                data = {
                    "acao": "COLETAR_RECURSO",
                    "justificativa": "Bateria disponível imediatamente adjacente à posição do agente.",
                    "alvo_coordenada": {"x": 13, "y": 8},
                    "urgencia": "MEDIA"
                }
        else:
            data = {
                "acao": "DEFENDER",
                "justificativa": "Postura padrão de segurança adotada para manutenção de ciclo.",
                "alvo_coordenada": None,
                "urgencia": "BAIXA"
            }

        return json.dumps(data, ensure_ascii=False)

    def _get_error_response(self, tipo_erro: str) -> str:
        if tipo_erro == "syntax":
            # JSON quebrado ou texto livre
            return "Eu prefiro não tomar nenhuma decisão agora. Vamos esperar um pouco."
        elif tipo_erro == "markdown_broken":
            return "```json\n{ 'acao': 'AVANCAR', erro_aspas: 123"
        elif tipo_erro == "semantic":
            # Violação de schema (ação inválida e justificativa muito curta)
            return json.dumps({
                "acao": "DORMIR_NO_PONTO",
                "justificativa": "curto",
                "urgencia": "BAIXA"
            })
        elif tipo_erro == "empty":
            return ""
        else:
            return "Não compreendi a instrução."
