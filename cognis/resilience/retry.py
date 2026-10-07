"""Estratégia de Resiliência e Auto-Recuperação (Self-Healing / Retry Pattern)."""
import json
import logging
from dataclasses import dataclass
from typing import Optional, List, Tuple
from pydantic import ValidationError

from cognis.domain.models import DecisaoAgente
from cognis.providers.base import LLMProvider
from cognis.resilience.fallback import FallbackPolicy
from cognis.security.redaction import TacticalMasker

logger = logging.getLogger("SubgrupoC_IA")


@dataclass
class RetryConfig:
    """Configurações da política de retentativa e autorrecuperação."""
    max_retries: int = 1
    enable_self_healing: bool = True


@dataclass
class ProcessingResult:
    """Resultado final da validação e recuperação de uma inferência de agente."""
    is_valid: bool
    decision: DecisaoAgente
    failure_reason: Optional[str] = None
    attempts: int = 1
    recovered_by_retry: bool = False


class SelfHealingManager:
    """Gerencia a validação de respostas e o ciclo de autocorreção guiada por feedback."""

    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()

    @staticmethod
    def clean_json_markdown(raw_text: str) -> str:
        """Remove delimitadores markdown (```json ... ```) se gerados pelo modelo."""
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            # Descarta a primeira linha (ex: ```json ou ```)
            if len(lines) > 1:
                lines = lines[1:]
            # Remove a última linha se for delimitador de fechamento
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return text

    def validate_content(self, raw_text: str) -> Tuple[bool, Optional[DecisaoAgente], Optional[str]]:
        """Tenta fazer o parse e a validação estrita com Pydantic v2."""
        cleaned = self.clean_json_markdown(raw_text)
        try:
            data = json.loads(cleaned)
            if not isinstance(data, dict):
                return False, None, "A resposta deve ser um objeto JSON (dicionário), não uma lista ou escalar."

            decision = DecisaoAgente.model_validate(data)
            return True, decision, None

        except json.JSONDecodeError as jde:
            reason = f"Erro de sintaxe JSON: {jde.msg} (linha {jde.lineno}, coluna {jde.colno})"
            return False, None, reason

        except ValidationError as ve:
            errors_summary = []
            for err in ve.errors():
                loc = " -> ".join(str(l) for l in err.get("loc", []))
                msg = err.get("msg", "Inválido")
                errors_summary.append(f"Campo '{loc}': {msg}")
            reason = "Violação de schema Pydantic: " + "; ".join(errors_summary)
            return False, None, reason

        except Exception as ex:
            return False, None, f"Erro inesperado no processamento: {str(ex)}"

    def build_self_healing_prompt(
        self,
        original_prompt: str,
        failed_response: str,
        error_reason: str
    ) -> str:
        """Constrói um prompt de autocorreção contendo o diagnóstico do erro e o contexto original."""
        schema_format = json.dumps(DecisaoAgente.model_json_schema(), indent=2)
        sanitized_error = FallbackPolicy.sanitize_failure_reason(error_reason)

        return f"""
[ALERTA DE FALHA DE CONFORMIDADE DE SCHEMA]
Sua resposta anterior foi rejeitada pelo validador estrito do sistema.

[RESPOSTA ANTERIOR REJEITADA]
{failed_response}

[DIAGNÓSTICO DO ERRO]
{sanitized_error}

[CONTEXTO ORIGINAL DA MISSÃO]
{original_prompt}

[REQUISITOS MANDATÓRIOS DE CORREÇÃO]
1. Corrija o formato e retorne EXCLUSIVAMENTE um objeto JSON válido.
2. Certifique-se de que a ação é uma das permitidas: AVANCAR, RECUAR, COLETAR_RECURSO, DEFENDER, PATRULHAR, INATIVO.
3. Se fornecer 'scratchpad', inclua a reflexão deliberativa interna completa.
4. Schema esperado:
{schema_format}

Responda APENAS com o JSON corrigido, sem qualquer texto introdutório ou markdown.
""".strip()

    def process_with_recovery(
        self,
        llm_provider: LLMProvider,
        initial_prompt: str
    ) -> ProcessingResult:
        """Executa a inferência inicial e gerencia retentativas inteligentes com feedback de erro."""
        masker = TacticalMasker.get_instance()
        total_attempts = 0
        current_prompt = initial_prompt

        while total_attempts <= self.config.max_retries:
            total_attempts += 1

            # 1. Inferência com o provedor desacoplado
            response = llm_provider.generate(current_prompt)
            raw_content = response.content

            # 2. Validação estrita
            is_valid, decision, error_reason = self.validate_content(raw_content)

            if is_valid and decision is not None:
                is_healed = total_attempts > 1
                if is_healed:
                    logger.info("Auto-recuperação (Self-Healing) bem-sucedida após falha de validação.")
                return ProcessingResult(
                    is_valid=True,
                    decision=decision,
                    failure_reason=None,
                    attempts=total_attempts,
                    recovered_by_retry=is_healed
                )

            # Log da falha (com mensagem devidamente sanitizada contra vazamento de diretrizes)
            sanitized_error = masker.mask(f"Tentativa {total_attempts} inválida: {error_reason}")
            logger.warning(sanitized_error)

            # Se ainda houver retentativas permitidas e o self-healing estiver ativado
            if self.config.enable_self_healing and total_attempts <= self.config.max_retries:
                logger.info("Acionando ciclo de auto-recuperação (Self-Healing) com feedback de erro.")
                current_prompt = self.build_self_healing_prompt(
                    original_prompt=initial_prompt,
                    failed_response=raw_content,
                    error_reason=error_reason or "Erro desconhecido"
                )
            else:
                break

        # Fallback definitivo caso todas as tentativas falhem
        motivo_final = f"Formato inválido ou campos ausentes após {total_attempts} tentativa(s): {error_reason}"
        sanitized_motivo_final = FallbackPolicy.sanitize_failure_reason(motivo_final)
        logger.warning(f"Resposta inválida persistente. Acionando fallback: {sanitized_motivo_final}")

        fallback_decision = FallbackPolicy.create_inactive_decision()
        return ProcessingResult(
            is_valid=False,
            decision=fallback_decision,
            failure_reason=sanitized_motivo_final,
            attempts=total_attempts,
            recovered_by_retry=False
        )
