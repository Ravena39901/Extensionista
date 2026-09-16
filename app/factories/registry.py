from typing import Any

from app.adapters.gontijo import GontijoAdapter
from app.adapters.progresso import ProgressoAdapter
from app.adapters.rota import RotaAdapter
from app.adapters.sertao_bus import SertaoBusAdapter
from app.domain.exceptions import PayloadNormalizationError
from app.domain.interfaces import CompanyAdapter


class IntegrationRegistry:

    def __init__(self, adapters=None):
        self._adapters = adapters or []

    @classmethod
    def default(cls):
        return cls([
            ProgressoAdapter(),
            RotaAdapter(),
            GontijoAdapter(),
            SertaoBusAdapter(),
        ])

    def register(self, adapter: CompanyAdapter):
        self._adapters.append(adapter)

    def resolve(self, payload: dict[str, Any], index: int):
        for adapter in self._adapters:
            if adapter.can_handle(payload):
                return adapter

        raise PayloadNormalizationError(
            index,
            None,
            None,
            "O formato do payload não corresponde a nenhuma companhia suportada.",
        )
