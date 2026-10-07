"""Módulo de segurança para proteção de dados do Subgrupo D."""
from cognis.security.redaction import (
    TacticalMasker,
    SensitiveLogFilter,
    sanitize_error_message,
    setup_secure_logging
)

__all__ = [
    "TacticalMasker",
    "SensitiveLogFilter",
    "sanitize_error_message",
    "setup_secure_logging"
]
