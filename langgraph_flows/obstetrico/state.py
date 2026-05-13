"""Estado do fluxo Obstétrico."""

from typing import TypedDict, List, Optional


class ObstetricoState(TypedDict, total=False):
    # Entrada — dados da gestante
    idade: int
    semanas_gestacao: int
    paridade: str            # ex.: "G2P1A0"
    queixas: str
    comorbidades: str        # ex.: "hipertensão, diabetes"

    # Etapas
    avaliacao_risco_gestacional: str
    classificacao_risco: str  # "habitual" | "alto"
    orientacoes_especificas: str
    exames_agendados: List[str]
    alerta_urgencia: bool
    motivo_alerta: str

    # Saída
    acompanhamento: str

    # Metadados
    erro: Optional[str]
