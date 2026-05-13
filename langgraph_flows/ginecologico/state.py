"""Estado do fluxo de Triagem Ginecológica."""

from typing import TypedDict, List, Optional


class GinecologicoState(TypedDict, total=False):
    # Entrada
    sintomas: str

    # Etapas intermediárias
    analise_risco: str
    nivel_risco: str          # "baixo" | "moderado" | "alto"
    urgencia: str             # "rotina" | "prioritaria" | "imediata"
    exames_sugeridos: List[str]
    orientacoes_iniciais: str

    # Saída final
    agendamento: str

    # Metadados
    erro: Optional[str]
