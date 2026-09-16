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
