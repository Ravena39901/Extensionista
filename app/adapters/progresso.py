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
