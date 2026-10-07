"""Testes para garantir 100% de retrocompatibilidade com a API de AgenteCicloIA."""
from cognis.compatibility import AgenteCicloIA


def test_agente_ciclo_ia_legacy_lifecycle(tmp_path):
    arquivo_saida = tmp_path / "Documento_5_Legacy.json"

    perfis_ic = {
        "Agressivo": "Priorize o confronto imediato e avanço sobre posições de ameaça.",
        "Defensivo": "Priorize a segurança da posição atual, evitando confrontos e acumulando defesas.",
        "Explorador": "Priorize a busca de novos pontos e recursos em áreas desconhecidas do mapa.",
        "Oportunista": "Colete recursos disponíveis quando o risco for baixo; se ameaçado, recue."
    }

    sistema_ia = AgenteCicloIA(
        perfis_estrategicos=perfis_ic,
        nome_arquivo_saida=str(arquivo_saida),
        max_retries=1
    )

    percepcao_simulada = {
        "ciclo": 1,
        "posicao_atual": {"x": 12, "y": 8},
        "energia_restante": 78,
        "ameacas_detectadas": [{"tipo": "Inimigo", "distancia": 3}],
        "recursos_no_raio": [{"tipo": "Bateria", "distancia": 1}]
    }

    # Callback de modelo idêntico ao antigo main.py
    def conector_modelo_llm(prompt: str) -> str:
        if "Agressivo" in prompt:
            return '{"acao": "AVANCAR", "justificativa": "Ameaça a 3 unidades de distância; avançar para combate.", "alvo_coordenada": {"x": 15, "y": 8}, "urgencia": "ALTA"}'
        elif "Defensivo" in prompt:
            return '{"acao": "DEFENDER", "justificativa": "Inimigo próximo detectado; mantendo postura de contenção.", "urgencia": "MEDIA"}'
        elif "Explorador" in prompt:
            return '{"acao": "PATRULHAR", "justificativa": "Buscando novas rotas ao redor para mapear o setor.", "alvo_coordenada": {"x": 12, "y": 12}, "urgencia": "BAIXA"}'
        else:
            return "Eu prefiro não tomar nenhuma decisão agora."

    # 1. Teste de montagem de instrução
    prompt_agressivo = sistema_ia.montar_instrucao_ciclo("Agressivo", percepcao_simulada)
    assert "[INSTRUÇÃO ESTRATÉGICA]" in prompt_agressivo
    assert "Agressivo" in prompt_agressivo
    assert "[ESTADO DO MUNDO - RELATÓRIO DE PERCEPÇÃO]" in prompt_agressivo

    # 2. Teste de validação direta
    resp_valida = '{"acao": "DEFENDER", "justificativa": "Segurança máxima do setor.", "urgencia": "MEDIA"}'
    proc_valido = sistema_ia.validar_e_processar_resposta(resp_valida)
    assert proc_valido["valido"] is True
    assert proc_valido["decisao"]["acao"] == "DEFENDER"

    resp_invalida = 'Texto desconexo'
    proc_invalido = sistema_ia.validar_e_processar_resposta(resp_invalida)
    assert proc_invalido["valido"] is False
    assert proc_invalido["decisao"]["acao"] == "INATIVO"
    assert proc_invalido["motivo_inativo"] is not None

    # 3. Teste de rodar teste dos 4 perfis
    resultados = sistema_ia.rodar_teste_quatro_perfis(
        ciclo_id=1,
        estado_mundo=percepcao_simulada,
        conector_llm_callback=conector_modelo_llm
    )

    assert len(resultados) == 4
    assert len(sistema_ia.registro_documento_5) == 4

    # 4. Teste de salvar Documento 5
    sistema_ia.salvar_documento_5(nome_arquivo=str(arquivo_saida))
    assert arquivo_saida.exists()
