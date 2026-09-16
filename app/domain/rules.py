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
