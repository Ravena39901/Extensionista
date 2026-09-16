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
