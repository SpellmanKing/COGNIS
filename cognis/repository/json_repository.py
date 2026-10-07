"""Implementação concreta de repositório baseado em JSON com escrita atômica."""
import json
import os
import tempfile
from pathlib import Path
from typing import List, Sequence, Optional, Union
from cognis.domain.models import CycleDecisionRecord
from cognis.repository.base import DecisionRepository


class JsonDecisionRepository(DecisionRepository):
    """Repositório de persistência em arquivo JSON para o Documento 5.

    Utiliza gravação atômica para prevenir corrupção de dados em caso de falhas
    de energia ou interrupções de processo durante simulações extensas.
    """

    def __init__(
        self,
        file_path: Union[str, Path] = "Documento_5_Decisoes.json",
        legacy_mode: bool = True,
        load_existing: bool = False
    ):
        """
        Args:
            file_path: Caminho de saída do relatório JSON formal.
            legacy_mode: Se True, preserva estritamente as chaves clássicas do Documento 5.
            load_existing: Se True, carrega registros prévios do arquivo caso ele já exista.
        """
        self.file_path = Path(file_path)
        self.legacy_mode = legacy_mode
        self._records: List[CycleDecisionRecord] = []

        if load_existing and self.file_path.exists():
            self._load_from_disk()

    def add(self, record: CycleDecisionRecord) -> None:
        self._records.append(record)

    def add_batch(self, records: Sequence[CycleDecisionRecord]) -> None:
        self._records.extend(records)

    def get_by_cycle(self, cycle_id: int) -> List[CycleDecisionRecord]:
        return [r for r in self._records if r.ciclo_id == cycle_id]

    def list_all(self) -> List[CycleDecisionRecord]:
        return list(self._records)

    def clear(self) -> None:
        self._records.clear()

    def save(self) -> None:
        """Persiste os registros em JSON utilizando substituição atômica de arquivo."""
        dados_serializados = [
            r.to_document_5_dict(legacy_mode=self.legacy_mode)
            for r in self._records
        ]

        # Garante que o diretório de destino existe
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Escrita atômica: grava primeiro em arquivo temporário no mesmo diretório
        temp_dir = self.file_path.parent
        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as tf:
            json.dump(dados_serializados, tf, indent=2, ensure_ascii=False)
            temp_name = tf.name

        # Substituição atômica no sistema de arquivos
        os.replace(temp_name, self.file_path)

    def _load_from_disk(self) -> None:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
            self._records = [CycleDecisionRecord.model_validate(item) for item in raw_list]
        except Exception:
            # Em caso de arquivo vazio ou inválido, inicia com lista limpa
            self._records = []
