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
