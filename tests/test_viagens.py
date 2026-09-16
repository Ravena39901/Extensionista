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
