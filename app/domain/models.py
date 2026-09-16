from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class LocationData:
    cidade: str
    uf: str


@dataclass
class TripData:
    id: str
    empresa: str
    origem: LocationData
    destino: LocationData
    saida: datetime
    chegada: datetime
    duracao_minutos: int
    preco: Decimal
    moeda: str
    categoria: str
    assentos_disponiveis: int
