"""Modelos de dados estritos baseados em Pydantic v2.

Implementa validação estrita, reflexão interna (Scratchpad / Chain-of-Thought)
e registro estruturado do Documento 5.
"""
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from cognis.domain.enums import ActionType, UrgencyLevel, RiskLevel, AcoesValidasLiteral


class Coordenada(BaseModel):
    """Representação cartesiana de alvo ou posição espacial."""
    model_config = ConfigDict(extra="forbid")

    x: int = Field(..., description="Coordenada no eixo X.")
    y: int = Field(..., description="Coordenada no eixo Y.")

    def to_dict(self) -> Dict[str, int]:
        return {"x": self.x, "y": self.y}


class StrategicScratchpad(BaseModel):
    """Reflexão deliberativa preliminar (Chain-of-Thought estruturado).

    Permite que o LLM processe o contexto e avalie riscos antes
    de colapsar sua deliberação em uma ação atômica.
    """
    model_config = ConfigDict(extra="ignore")

    analise_situacional: str = Field(
        ...,
        min_length=5,
        description="Leitura do estado do mundo, identificando recursos imediatos e posições de ameaça."
    )
    ponderacao_risco: RiskLevel = Field(
        default=RiskLevel.MEDIO,
        description="Classificação formal do nível de perigo percebido no ciclo."
    )
    hipotese_tatica: str = Field(
        ...,
        min_length=5,
        description="Hipótese deliberativa conectando a diretriz do perfil ao estado do mundo."
    )


class DecisaoAgente(BaseModel):
    """Contrato estrito de decisão do agente gerado pelo LLM.

    Compatível com Pydantic v2 com validação semântica e suporte
    a Chain-of-Thought estruturado via campo scratchpad.
    """
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        populate_by_name=True,
        extra="forbid"
    )

    scratchpad: Optional[StrategicScratchpad] = Field(
        default=None,
        description="Reflexão interna estruturada (Chain-of-Thought) formulada antes da decisão executável."
    )
    acao: ActionType = Field(
        ...,
        description="Ação escolhida estritamente dentre as opções válidas do simulador."
    )
    justificativa: str = Field(
        ...,
        min_length=10,
        description="Raciocínio lógico ligando o estado do mundo à diretriz estratégica."
    )
    alvo_coordenada: Optional[Coordenada] = Field(
        default=None,
        description="Coordenadas (x, y) caso a ação exija deslocamento ou alvo."
    )
    urgencia: UrgencyLevel = Field(
        default=UrgencyLevel.MEDIA,
        description="Nível de prioridade operacional da ação."
    )

    @field_validator("justificativa")
    @classmethod
    def validar_justificativa_conteudo(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("A justificativa não pode ser vazia ou composta apenas de espaços.")
        return v.strip()

    @model_validator(mode="before")
    @classmethod
    def sanitizar_alvo_coordenada(cls, values: Any) -> Any:
        """Permite que alvo_coordenada seja fornecido como dict {'x': ..., 'y': ...}."""
        if isinstance(values, dict):
            alvo = values.get("alvo_coordenada")
            if alvo is not None and not isinstance(alvo, dict) and not isinstance(alvo, Coordenada):
                # Se for nulo ou tipo inválido que não seja dict
                pass
        return values

    def to_documento_5_dict(self) -> Dict[str, Any]:
        """Serializa em formato compatível com o legado do Documento 5."""
        dados = self.model_dump()
        # Se alvo_coordenada for None, preserva null explícito
        if self.alvo_coordenada is None:
            dados["alvo_coordenada"] = None
        else:
            dados["alvo_coordenada"] = self.alvo_coordenada.to_dict()
        return dados


class CycleDecisionRecord(BaseModel):
    """Entidade de persistência do ciclo de decisão (Registro formal do Documento 5)."""
    model_config = ConfigDict(use_enum_values=True)

    ciclo_id: int = Field(..., description="Identificador incremental do ciclo de simulação.")
    perfil_estrategico: str = Field(..., description="Nome do perfil estratégico ativo.")
    decisao_executada: DecisaoAgente = Field(..., description="Decisão validada ou fallback de inatividade.")
    resposta_valida: bool = Field(..., description="Indica se a inferência do LLM foi válida na primeira tentativa ou após self-healing.")
    motivo_inativo: Optional[str] = Field(default=None, description="Motivo técnico sanitizado da inatividade em caso de fallback.")
    tentativas_executadas: int = Field(default=1, description="Número de tentativas de inferência/self-healing executadas.")
    recuperado_por_retry: bool = Field(default=False, description="Indica se o contrato foi recuperado com sucesso pelo self-healing.")

    def to_document_5_dict(self, legacy_mode: bool = True) -> Dict[str, Any]:
        """Converte para o formato de dicionário do Documento 5.

        Args:
            legacy_mode: Se True, preserva estritamente as chaves clássicas:
                         ciclo_id, perfil_estrategico, decisao_executada, resposta_valida, motivo_inativo.
        """
        base = {
            "ciclo_id": self.ciclo_id,
            "perfil_estrategico": self.perfil_estrategico,
            "decisao_executada": self.decisao_executada.to_documento_5_dict(),
            "resposta_valida": self.resposta_valida,
            "motivo_inativo": self.motivo_inativo,
        }
        if not legacy_mode:
            base["tentativas_executadas"] = self.tentativas_executadas
            base["recuperado_por_retry"] = self.recuperado_por_retry
        return base
