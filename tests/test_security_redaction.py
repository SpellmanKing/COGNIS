"""Testes unitários para isolamento e proteção de diretrizes confidenciais (Subgrupo D)."""
import logging
from cognis.security.redaction import (
    TacticalMasker,
    SensitiveLogFilter,
    sanitize_error_message
)
from cognis.strategies.concrete import AggressiveStrategy, DefensiveStrategy


def test_tactical_masker_replaces_directive():
    masker = TacticalMasker()
    diretriz_secreta = "OPERACAO_SECRETA_ALPHA: Eliminar alvos prioritários sem negociar."
    masker.register_directive(diretriz_secreta)

    texto_com_vazamento = f"Ocorreu um erro no prompt contendo: {diretriz_secreta} durante o ciclo."
    texto_seguro = masker.mask(texto_com_vazamento)

    assert diretriz_secreta not in texto_seguro
    assert "[DIRETRIZ_CONFIDENCIAL_SUBGRUPO_D]" in texto_seguro


def test_strategy_repr_does_not_leak_directive():
    strat = AggressiveStrategy(directive="DIRETRIZ_ULTRA_SECRETA_NAO_LOGAR")
    repr_str = repr(strat)
    assert "DIRETRIZ_ULTRA_SECRETA_NAO_LOGAR" not in repr_str
    assert "[CONFIDENCIAL_SUBGRUPO_D]" in repr_str


def test_sensitive_log_filter_intercepts_logs():
    masker = TacticalMasker.get_instance()
    diretriz = "DIRETRIZ_CONFIDENCIAL_DEFENSIVA_XYZ"
    masker.register_directive(diretriz)

    filtro = SensitiveLogFilter(masker=masker)

    # Cria record com diretriz vazada
    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=1,
        msg=f"Falha de validação processando a instrução: {diretriz}",
        args=(),
        exc_info=None
    )

    filtro.filter(record)
    assert diretriz not in record.msg
    assert "[DIRETRIZ_CONFIDENCIAL_SUBGRUPO_D]" in record.msg


def test_sanitize_error_message():
    masker = TacticalMasker.get_instance()
    segredo = "PLANO_TÁTICO_EVASÃO_SETOR_4"
    masker.register_directive(segredo)

    erro = ValueError(f"Dados incorretos ao avaliar a diretriz {segredo}")
    msg_sanitizada = sanitize_error_message(erro, masker=masker)

    assert segredo not in msg_sanitizada
    assert "[DIRETRIZ_CONFIDENCIAL_SUBGRUPO_D]" in msg_sanitizada
