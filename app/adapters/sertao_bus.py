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
