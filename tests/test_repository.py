"""Testes unitários para o padrão Repository e persistência do Documento 5."""
import json
from cognis.repository.json_repository import JsonDecisionRepository
from cognis.domain.models import CycleDecisionRecord, DecisaoAgente
from cognis.domain.enums import ActionType


def test_json_repository_saves_and_preserves_document_5_format(tmp_path):
    file_path = tmp_path / "Documento_5_Decisoes.json"
    repo = JsonDecisionRepository(file_path=file_path, legacy_mode=True)

    record = CycleDecisionRecord(
        ciclo_id=1,
        perfil_estrategico="Agressivo",
        decisao_executada=DecisaoAgente(
            acao=ActionType.AVANCAR,
            justificativa="Avanço estratégico para combate imediato.",
            alvo_coordenada={"x": 15, "y": 8},
            urgencia="ALTA"
        ),
        resposta_valida=True,
        motivo_inativo=None
    )

    repo.add(record)
    repo.save()

    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 1
    item = data[0]

    # Verifica conformidade estrita das chaves do Documento 5
    assert set(item.keys()) == {
        "ciclo_id",
        "perfil_estrategico",
        "decisao_executada",
        "resposta_valida",
        "motivo_inativo"
    }

    assert item["ciclo_id"] == 1
    assert item["perfil_estrategico"] == "Agressivo"
    assert item["decisao_executada"]["acao"] == "AVANCAR"
    assert item["decisao_executada"]["alvo_coordenada"] == {"x": 15, "y": 8}
    assert item["resposta_valida"] is True
    assert item["motivo_inativo"] is None
