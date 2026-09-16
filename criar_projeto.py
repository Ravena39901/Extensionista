from pathlib import Path

files = {
    "app/__init__.py": "",
    "app/main.py": """
from fastapi import FastAPI
from app.api.v1.viagens import router

app = FastAPI(
    title="API de Normalização de Viagens",
    version="1.0.0",
)

app.include_router(router)
""",
    "app/api/__init__.py": "",
    "app/api/v1/__init__.py": "",
    "app/api/v1/viagens.py": """
from typing import Any

from fastapi import APIRouter, HTTPException

from app.factories.registry import IntegrationRegistry
from app.services.normalization_service import NormalizationService

router = APIRouter(prefix="/api/v1/viagens", tags=["Viagens"])

_registry = IntegrationRegistry.default()
_service = NormalizationService(_registry)


@router.post("/normalizar")
def normalizar(payload: list[dict[str, Any]]):
    try:
        return _service.normalize(payload)
    except Exception as exc:
        if hasattr(exc, "to_detail"):
            raise HTTPException(status_code=422, detail=exc.to_detail())
        raise
""",
    "app/domain/__init__.py": "",
    "app/domain/exceptions.py": """
class PayloadNormalizationError(Exception):
    def __init__(self, indice, empresa_identificada, campo, mensagem):
        self.indice = indice
        self.empresa_identificada = empresa_identificada
        self.campo = campo
        self.mensagem = mensagem
        super().__init__(mensagem)

    def to_detail(self):
        return {
            "indice": self.indice,
            "empresa_identificada": self.empresa_identificada,
            "campo": self.campo,
            "mensagem": self.mensagem,
        }
""",
    "app/domain/models.py": """
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
""",
    "app/domain/interfaces.py": """
from abc import ABC, abstractmethod
from typing import Any

from app.domain.models import TripData


class CompanyAdapter(ABC):

    name: str

    @abstractmethod
    def can_handle(self, payload: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def normalize(self, payload: dict[str, Any], index: int) -> TripData:
        pass
""",
    "app/domain/rules.py": """
from datetime import datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from app.domain.exceptions import PayloadNormalizationError

BAHIA = ZoneInfo("America/Bahia")

CATEGORY_MAP = {
    "CONV": "convencional",
    "CONVENCIONAL": "convencional",
    "EXEC": "executivo",
    "EXECUTIVO": "executivo",
    "SEMI": "semileito",
    "SEMILEITO": "semileito",
    "SEMI-LEITO": "semileito",
    "LEITO": "leito",
}


def fail(index, company, field, message):
    raise PayloadNormalizationError(index, company, field, message)


def required(payload, field, index, company):
    if field not in payload or payload[field] in (None, ""):
        fail(index, company, field, "Campo obrigatório não informado.")
    return payload[field]


def parse_datetime(value, index, company, field, default_tz=BAHIA):
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        fail(index, company, field, "Data/hora inválida.")

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=default_tz)

    return dt


def validate_interval(saida, chegada, index, company):
    if chegada <= saida:
        fail(
            index,
            company,
            "chegada_em",
            "A data de chegada deve ser posterior à data de saída.",
        )


def parse_positive_decimal(value, index, company, field):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        fail(index, company, field, "Valor monetário inválido.")

    if result <= 0:
        fail(index, company, field, "O valor deve ser maior que zero.")

    return result


def parse_non_negative_int(value, index, company, field):
    try:
        result = int(value)
    except (ValueError, TypeError):
        fail(index, company, field, "O valor deve ser um número inteiro.")

    if result < 0:
        fail(index, company, field, "O valor não pode ser negativo.")

    return result


def parse_uf(value, index, company, field):
    if not isinstance(value, str) or len(value) != 2 or not value.isalpha():
        fail(index, company, field, "A UF deve conter exatamente 2 letras.")

    return value.upper()


def parse_category(value, index, company, field="categoria"):
    if not isinstance(value, str):
        fail(index, company, field, "Categoria inválida.")

    normalized = CATEGORY_MAP.get(value.strip().upper())

    if normalized is None:
        fail(index, company, field, "Categoria inválida.")

    return normalized


def check_duration(expected, actual, index, company):
    if expected is not None:
        try:
            expected = int(expected)
        except (ValueError, TypeError):
            fail(index, company, "duracaoMinutos", "Duração inválida.")

        if expected != actual:
            fail(
                index,
                company,
                "duracaoMinutos",
                "A duração informada não corresponde ao intervalo entre saída e chegada.",
            )
""",
    "app/adapters/__init__.py": "",
    "app/adapters/progresso.py": """
from typing import Any

from app.domain.interfaces import CompanyAdapter
from app.domain.models import LocationData, TripData
from app.domain.rules import (
    BAHIA,
    check_duration,
    parse_category,
    parse_datetime,
    parse_positive_decimal,
    parse_uf,
    parse_non_negative_int,
    required,
    validate_interval,
)


class ProgressoAdapter(CompanyAdapter):

    name = "Progresso"

    def can_handle(self, payload: dict[str, Any]) -> bool:
        return (
            "codigoViagem" in payload
            and "origem" in payload
            and "destino" in payload
            and "dataHoraSaida" in payload
        )

    def normalize(self, payload, index):
        company = self.name

        trip_id = str(required(payload, "codigoViagem", index, company))

        origem = required(payload, "origem", index, company)
        destino = required(payload, "destino", index, company)

        cidade_origem = required(origem, "cidade", index, company)
        uf_origem = parse_uf(
            required(origem, "uf", index, company),
            index,
            company,
            "origem.uf",
        )

        cidade_destino = required(destino, "cidade", index, company)
        uf_destino = parse_uf(
            required(destino, "uf", index, company),
            index,
            company,
            "destino.uf",
        )

        saida = parse_datetime(
            required(payload, "dataHoraSaida", index, company),
            index,
            company,
            "dataHoraSaida",
        )

        chegada = parse_datetime(
            required(payload, "dataHoraChegada", index, company),
            index,
            company,
            "dataHoraChegada",
        )

        validate_interval(saida, chegada, index, company)

        duracao = int((chegada - saida).total_seconds() // 60)

        check_duration(
            payload.get("duracaoMinutos"),
            duracao,
            index,
            company,
        )

        preco = parse_positive_decimal(
            required(payload, "preco", index, company),
            index,
            company,
            "preco",
        )

        assentos = parse_non_negative_int(
            required(payload, "assentosDisponiveis", index, company),
            index,
            company,
            "assentosDisponiveis",
        )

        categoria = parse_category(
            required(payload, "categoria", index, company),
            index,
            company,
        )

        return TripData(
            id=trip_id,
            empresa=company,
            origem=LocationData(cidade_origem, uf_origem),
            destino=LocationData(cidade_destino, uf_destino),
            saida=saida,
            chegada=chegada,
            duracao_minutos=duracao,
            preco=preco,
            moeda="BRL",
            categoria=categoria,
            assentos_disponiveis=assentos,
        )
""",
    "app/adapters/rota.py": """
from typing import Any

from app.domain.interfaces import CompanyAdapter
from app.domain.models import LocationData, TripData
from app.domain.rules import (
    parse_category,
    parse_datetime,
    parse_positive_decimal,
    parse_uf,
    parse_non_negative_int,
    required,
    validate_interval,
)


class RotaAdapter(CompanyAdapter):

    name = "Rota Transportes"

    def can_handle(self, payload: dict[str, Any]) -> bool:
        return (
            "id" in payload
            and "partida" in payload
            and "chegada" in payload
        )

    def normalize(self, payload, index):
        company = self.name

        trip_id = str(required(payload, "id", index, company))

        partida = required(payload, "partida", index, company)
        chegada_data = required(payload, "chegada", index, company)

        origem = required(partida, "origem", index, company)
        destino = required(chegada_data, "destino", index, company)

        origem_cidade = required(origem, "cidade", index, company)
        origem_uf = parse_uf(
            required(origem, "uf", index, company),
            index,
            company,
            "partida.origem.uf",
        )

        destino_cidade = required(destino, "cidade", index, company)
        destino_uf = parse_uf(
            required(destino, "uf", index, company),
            index,
            company,
            "chegada.destino.uf",
        )

        saida = parse_datetime(
            required(partida, "dataHora", index, company),
            index,
            company,
            "partida.dataHora",
        )

        chegada = parse_datetime(
            required(chegada_data, "dataHora", index, company),
            index,
            company,
            "chegada.dataHora",
        )

        validate_interval(saida, chegada, index, company)

        duracao = int((chegada - saida).total_seconds() // 60)

        tarifa = required(payload, "tarifa_centavos", index, company)

        try:
            tarifa = int(tarifa)
        except (ValueError, TypeError):
            from app.domain.rules import fail
            fail(index, company, "tarifa_centavos", "Valor da tarifa inválido.")

        preco = parse_positive_decimal(
            tarifa / 100,
            index,
            company,
            "tarifa_centavos",
        )

        assentos = parse_non_negative_int(
            required(payload, "lugares", index, company),
            index,
            company,
            "lugares",
        )

        categoria = parse_category(
            required(payload, "tipo", index, company),
            index,
            company,
        )

        return TripData(
            id=trip_id,
            empresa=company,
            origem=LocationData(origem_cidade, origem_uf),
            destino=LocationData(destino_cidade, destino_uf),
            saida=saida,
            chegada=chegada,
            duracao_minutos=duracao,
            preco=preco,
            moeda="BRL",
            categoria=categoria,
            assentos_disponiveis=assentos,
        )
""",
    "app/adapters/gontijo.py": """
from typing import Any

from app.domain.interfaces import CompanyAdapter
from app.domain.models import LocationData, TripData
from app.domain.rules import (
    parse_category,
    parse_datetime,
    parse_positive_decimal,
    parse_uf,
    parse_non_negative_int,
    required,
    validate_interval,
)


class GontijoAdapter(CompanyAdapter):

    name = "Gontijo"

    def can_handle(self, payload: dict[str, Any]) -> bool:
        return (
            "serviceCode" in payload
            and "origin" in payload
            and "destination" in payload
            and "departureTimestamp" in payload
        )

    def normalize(self, payload, index):
        company = self.name

        trip_id = str(required(payload, "serviceCode", index, company))

        origin = required(payload, "origin", index, company)
        destination = required(payload, "destination", index, company)

        origem_cidade = required(origin, "city", index, company)
        origem_uf = parse_uf(
            required(origin, "state", index, company),
            index,
            company,
            "origin.state",
        )

        destino_cidade = required(destination, "city", index, company)
        destino_uf = parse_uf(
            required(destination, "state", index, company),
            index,
            company,
            "destination.state",
        )

        saida = parse_datetime(
            required(payload, "departureTimestamp", index, company),
            index,
            company,
            "departureTimestamp",
        )

        chegada = parse_datetime(
            required(payload, "arrivalTimestamp", index, company),
            index,
            company,
            "arrivalTimestamp",
        )

        validate_interval(saida, chegada, index, company)

        segundos = required(payload, "durationSeconds", index, company)

        try:
            segundos = int(segundos)
        except (ValueError, TypeError):
            from app.domain.rules import fail
            fail(index, company, "durationSeconds", "Duração inválida.")

        if segundos <= 0 or segundos % 60 != 0:
            from app.domain.rules import fail
            fail(
                index,
                company,
                "durationSeconds",
                "A duração deve ser positiva e expressa em minutos inteiros.",
            )

        duracao = segundos // 60

        preco = parse_positive_decimal(
            required(payload, "price", index, company),
            index,
            company,
            "price",
        )

        assentos = parse_non_negative_int(
            required(payload, "availableSeats", index, company),
            index,
            company,
            "availableSeats",
        )

        categoria = parse_category(
            required(payload, "category", index, company),
            index,
            company,
        )

        return TripData(
            id=trip_id,
            empresa=company,
            origem=LocationData(origem_cidade, origem_uf),
            destino=LocationData(destino_cidade, destino_uf),
            saida=saida,
            chegada=chegada,
            duracao_minutos=duracao,
            preco=preco,
            moeda="BRL",
            categoria=categoria,
            assentos_disponiveis=assentos,
        )
""",
    "app/adapters/sertao_bus.py": """
from typing import Any

from app.domain.interfaces import CompanyAdapter
from app.domain.models import LocationData, TripData
from app.domain.rules import (
    parse_category,
    parse_datetime,
    parse_positive_decimal,
    parse_uf,
    parse_non_negative_int,
    required,
    validate_interval,
)


class SertaoBusAdapter(CompanyAdapter):

    name = "Sertão Bus"

    def can_handle(self, payload: dict[str, Any]) -> bool:
        return (
            "tripCode" in payload
            and "from" in payload
            and "to" in payload
            and "departure" in payload
        )

    def normalize(self, payload, index):
        company = self.name

        trip_id = str(required(payload, "tripCode", index, company))

        origem = required(payload, "from", index, company)
        destino = required(payload, "to", index, company)

        origem_cidade = required(origem, "city", index, company)
        origem_uf = parse_uf(
            required(origem, "uf", index, company),
            index,
            company,
            "from.uf",
        )

        destino_cidade = required(destino, "city", index, company)
        destino_uf = parse_uf(
            required(destino, "uf", index, company),
            index,
            company,
            "to.uf",
        )

        saida = parse_datetime(
            required(payload, "departure", index, company),
            index,
            company,
            "departure",
        )

        chegada = parse_datetime(
            required(payload, "arrival", index, company),
            index,
            company,
            "arrival",
        )

        validate_interval(saida, chegada, index, company)

        duracao = int((chegada - saida).total_seconds() // 60)

        preco = parse_positive_decimal(
            required(payload, "price", index, company),
            index,
            company,
            "price",
        )

        assentos = parse_non_negative_int(
            required(payload, "seats", index, company),
            index,
            company,
            "seats",
        )

        categoria = parse_category(
            required(payload, "category", index, company),
            index,
            company,
        )

        return TripData(
            id=trip_id,
            empresa=company,
            origem=LocationData(origem_cidade, origem_uf),
            destino=LocationData(destino_cidade, destino_uf),
            saida=saida,
            chegada=chegada,
            duracao_minutos=duracao,
            preco=preco,
            moeda="BRL",
            categoria=categoria,
            assentos_disponiveis=assentos,
        )
""",
    "app/factories/__init__.py": "",
    "app/factories/registry.py": """
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
""",
    "app/services/__init__.py": "",
    "app/services/normalization_service.py": """
from app.factories.registry import IntegrationRegistry


class NormalizationService:

    def __init__(self, registry: IntegrationRegistry):
        self.registry = registry

    def normalize(self, payload):
        viagens = []

        for index, item in enumerate(payload):
            adapter = self.registry.resolve(item, index)
            viagens.append(adapter.normalize(item, index))

        return {
            "viagens": [
                self._serialize(viagem)
                for viagem in viagens
            ]
        }

    @staticmethod
    def _serialize(trip):
        return {
            "id": trip.id,
            "empresa": trip.empresa,
            "origem": {
                "cidade": trip.origem.cidade,
                "uf": trip.origem.uf,
            },
            "destino": {
                "cidade": trip.destino.cidade,
                "uf": trip.destino.uf,
            },
            "saida": trip.saida.isoformat(),
            "chegada": trip.chegada.isoformat(),
            "duracao_minutos": trip.duracao_minutos,
            "preco": {
                "valor": float(trip.preco),
                "moeda": trip.moeda,
            },
            "categoria": trip.categoria,
            "assentos_disponiveis": trip.assentos_disponiveis,
        }
""",
    "tests/__init__.py": "",
    "tests/test_viagens.py": """
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_progresso():
    payload = [{
        "codigoViagem": "PRO-001",
        "origem": {"cidade": "Maceió", "uf": "AL"},
        "destino": {"cidade": "Recife", "uf": "PE"},
        "dataHoraSaida": "2026-10-15T08:00:00",
        "dataHoraChegada": "2026-10-15T12:00:00",
        "duracaoMinutos": 240,
        "preco": "89.90",
        "categoria": "CONV",
        "assentosDisponiveis": 20
    }]

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()["viagens"][0]

    assert data["empresa"] == "Progresso"
    assert data["duracao_minutos"] == 240


def test_rota():
    payload = [{
        "id": "RT-001",
        "partida": {
            "origem": {"cidade": "Maceió", "uf": "AL"},
            "dataHora": "2026-10-15T08:00:00"
        },
        "chegada": {
            "destino": {"cidade": "Aracaju", "uf": "SE"},
            "dataHora": "2026-10-15T12:30:00"
        },
        "tarifa_centavos": 7990,
        "lugares": 12,
        "tipo": "EXEC"
    }]

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()["viagens"][0]

    assert data["empresa"] == "Rota Transportes"
    assert data["duracao_minutos"] == 270


def test_gontijo():
    payload = [{
        "serviceCode": "GON-2026-001",
        "origin": {
            "city": "Belo Horizonte",
            "state": "MG"
        },
        "destination": {
            "city": "Salvador",
            "state": "BA"
        },
        "departureTimestamp": "2026-10-15T16:30:00Z",
        "arrivalTimestamp": "2026-10-16T09:10:00Z",
        "durationSeconds": 60000,
        "price": "199.90",
        "category": "LEITO",
        "availableSeats": 18
    }]

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()["viagens"][0]

    assert data["empresa"] == "Gontijo"
    assert data["duracao_minutos"] == 1000


def test_sertao_bus():
    payload = [{
        "tripCode": "SER-2026-100",
        "from": {
            "city": "Paulo Afonso",
            "uf": "BA"
        },
        "to": {
            "city": "Maceió",
            "uf": "AL"
        },
        "departure": "2026-10-16T08:00:00",
        "arrival": "2026-10-16T13:30:00",
        "price": "105.90",
        "category": "EXEC",
        "seats": 14
    }]

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()["viagens"][0]

    assert data["empresa"] == "Sertão Bus"
    assert data["saida"] == "2026-10-16T08:00:00-03:00"
    assert data["chegada"] == "2026-10-16T13:30:00-03:00"
    assert data["duracao_minutos"] == 330
    assert data["categoria"] == "executivo"
    assert data["assentos_disponiveis"] == 14


def test_formato_desconhecido():
    response = client.post(
        "/api/v1/viagens/normalizar",
        json=[{"empresa": "Desconhecida"}],
    )

    assert response.status_code == 422

    detail = response.json()["detail"]

    assert detail["indice"] == 0
    assert detail["empresa_identificada"] is None


def test_chegada_invalida():
    payload = [{
        "codigoViagem": "PRO-002",
        "origem": {"cidade": "A", "uf": "AL"},
        "destino": {"cidade": "B", "uf": "PE"},
        "dataHoraSaida": "2026-10-15T12:00:00",
        "dataHoraChegada": "2026-10-15T11:00:00",
        "duracaoMinutos": 60,
        "preco": "50",
        "categoria": "CONV",
        "assentosDisponiveis": 10
    }]

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=payload,
    )

    assert response.status_code == 422
    assert response.json()["detail"]["campo"] == "chegada_em"
""",
    "examples/payload.json": """
[
  {
    "codigoViagem": "PRO-001",
    "origem": {
      "cidade": "Maceió",
      "uf": "AL"
    },
    "destino": {
      "cidade": "Recife",
      "uf": "PE"
    },
    "dataHoraSaida": "2026-10-15T08:00:00",
    "dataHoraChegada": "2026-10-15T12:00:00",
    "duracaoMinutos": 240,
    "preco": "89.90",
    "categoria": "CONV",
    "assentosDisponiveis": 20
  }
]
""",
    "README.md": """
# API FastAPI - Normalização de Viagens

## Executar

    .\\.venv\\Scripts\\python.exe -m pytest -q

    .\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload

Swagger:

http://127.0.0.1:8000/docs

Endpoint:

POST /api/v1/viagens/normalizar
""",
    ".gitignore": """
.venv/
__pycache__/
.pytest_cache/
*.pyc
"""
}

for file_name, content in files.items():
    path = Path(file_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")

print("Projeto criado com sucesso!")