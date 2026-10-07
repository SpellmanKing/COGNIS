"""Módulo de Segurança e Isolamento Tático (Requisito Subgrupo D).

Garante que diretrizes táticas confidenciais não vazem em logs gerais do sistema,
telemetria de erro, saídas de console ou stack traces de exceções.
"""
import logging
import re
from typing import Set, Optional, List


class TacticalMasker:
    """Registrador e sanitizador de termos e diretrizes táticas confidenciais."""

    _instance: Optional["TacticalMasker"] = None

    def __init__(self):
        self._confidential_directives: Set[str] = set()
        self._compiled_pattern: Optional[re.Pattern] = None

    @classmethod
    def get_instance(cls) -> "TacticalMasker":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_directive(self, directive: str) -> None:
        """Registra uma diretriz estratégica sensível para mascaramento automático."""
        clean = directive.strip()
        if len(clean) >= 5:  # Evita mascarar palavras curtas comuns
            self._confidential_directives.add(clean)
            self._recompile()

    def register_directives(self, directives: List[str]) -> None:
        for d in directives:
            self.register_directive(d)

    def _recompile(self) -> None:
        if not self._confidential_directives:
            self._compiled_pattern = None
            return
        # Escapa termos para regex e ordena por tamanho descrescente
        sorted_terms = sorted(self._confidential_directives, key=len, reverse=True)
        escaped = [re.escape(t) for t in sorted_terms]
        pattern_str = "|".join(escaped)
        self._compiled_pattern = re.compile(pattern_str, flags=re.IGNORECASE)

    def mask(self, text: str, placeholder: str = "[DIRETRIZ_CONFIDENCIAL_SUBGRUPO_D]") -> str:
        """Substitui ocorrências de diretrizes sensíveis pelo placeholder de segurança."""
        if not text or not self._compiled_pattern:
            return text
        return self._compiled_pattern.sub(placeholder, text)

    def clear(self) -> None:
        """Limpa o registro de diretrizes confidenciais."""
        self._confidential_directives.clear()
        self._compiled_pattern = None


class SensitiveLogFilter(logging.Filter):
    """Filtro de logging do Python que sanitiza mensagens e stack traces em tempo real."""

    def __init__(self, masker: Optional[TacticalMasker] = None):
        super().__init__()
        self.masker = masker or TacticalMasker.get_instance()

    def filter(self, record: logging.LogRecord) -> bool:
        # 1. Sanitiza a mensagem principal
        if isinstance(record.msg, str):
            record.msg = self.masker.mask(record.msg)

        # 2. Sanitiza argumentos de formatação se existirem
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: (self.masker.mask(str(v)) if isinstance(v, str) else v)
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    self.masker.mask(str(a)) if isinstance(a, str) else a
                    for a in record.args
                )

        # 3. Sanitiza representações de exceção e stack trace
        if record.exc_text:
            record.exc_text = self.masker.mask(record.exc_text)

        return True


def sanitize_error_message(error: Exception | str, masker: Optional[TacticalMasker] = None) -> str:
    """Sanitiza mensagens de erro e exceções para evitar vazamento em telemetria e registros."""
    masker = masker or TacticalMasker.get_instance()
    msg = str(error)
    return masker.mask(msg)


def setup_secure_logging(
    logger_name: str = "SubgrupoC_IA",
    level: int = logging.INFO
) -> logging.Logger:
    """Configura um logger seguro com o filtro de privacidade do Subgrupo D acoplado."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Evita duplicação de handlers se já configurado
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Aplica o filtro em todos os handlers do logger
    masker = TacticalMasker.get_instance()
    log_filter = SensitiveLogFilter(masker=masker)
    logger.addFilter(log_filter)
    for h in logger.handlers:
        h.addFilter(log_filter)

    return logger
