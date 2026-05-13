"""Estado do fluxo de Detecção de Violência Doméstica.

Fluxo extremamente sensível — todos os logs são em modo confidencial,
e o estado mantém uma flag para reforçar essa proteção.
"""

from typing import TypedDict, List, Optional


class ViolenciaState(TypedDict, total=False):
    # Entrada
    relato: str

    # Etapas
    sinais_alerta: List[str]
    nivel_risco: str           # "baixo" | "moderado" | "alto"
    protocolo_seguranca: str
    equipe_acionada: bool
    documentacao: str
    seguimento: str

    # Sempre True neste fluxo
    modo_confidencial: bool

    # Metadados
    erro: Optional[str]
