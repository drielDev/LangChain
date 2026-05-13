"""Estado do fluxo de Prevenção."""

from typing import TypedDict, List, Optional


class PrevencaoState(TypedDict, total=False):
    # Entrada — histórico da paciente
    idade: int
    historico_familiar: str
    ultimos_exames: str       # texto livre: "papanicolau 2022, mamografia 2023"
    fatores_risco: str        # texto livre: "tabagismo, obesidade"

    # Etapas
    exames_devidos: List[str]
    orientacoes_preventivas: str
    agendamento_automatico: str
    lembretes: List[str]

    # Metadados
    erro: Optional[str]
