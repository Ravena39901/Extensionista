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
