"""Interface abstrata para Provedores de Inferência de LLM (Strategy Pattern)."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    """Encapsulamento da resposta bruta gerada pelo provedor com metadados."""
    content: str
    model_name: str = "unknown"
    tokens_prompt: Optional[int] = None
    tokens_completion: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    """Interface abstrata (Strategy) para conectores de Modelos de Linguagem.

    Desacopla completamente a lógica de tomada de decisão do motor de inferência,
    permitindo alternar entre OpenAI API, Ollama Local, LangChain, Hugging Face
    ou Mocks de teste sem alterar uma única linha da lógica de negócios.
    """

    @abstractmethod
    def generate(self, prompt: str) -> LLMResponse:
        """Gera uma resposta síncrona a partir do prompt de ciclo."""
        pass

    def __call__(self, prompt: str) -> str:
        """Permite que o provedor seja chamado diretamente como callable."""
        return self.generate(prompt).content
