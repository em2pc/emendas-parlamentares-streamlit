import json

class Emenda:
    def __init__(self, description, valor_necessario, categoria):
        self.id = None
        self.description = description
        self.valor_necessario = float(valor_necessario) # Garante que seja float
        self.categoria = categoria
        self.current_funded_amount = 0.0
        self.current_contributions = {} # {deputy_id: {'total': X, 'from_allocated_intention': Y, 'from_free_verba': Z}}

    def serialize(self):
        return {
            'id': self.id,
            'description': self.description,
            'valor_necessario': self.valor_necessario,
            'categoria': self.categoria,
            'current_funded_amount': self.current_funded_amount,
            'current_contributions': self.current_contributions
        }

    @classmethod
    def deserialize(cls, data):
        # Tenta converter valor_necessario para float de forma mais segura
        try:
            valor_necessario = float(data.get('valor_necessario', 0.0))
        except (ValueError, TypeError):
            print(f"AVISO: 'valor_necessario' para emenda {data.get('description', 'desconhecida')} não é um número válido. Usando 0.0.")
            valor_necessario = 0.0

        # Tenta converter current_funded_amount para float de forma mais segura
        try:
            current_funded_amount = float(data.get('current_funded_amount', 0.0))
        except (ValueError, TypeError):
            print(f"AVISO: 'current_funded_amount' para emenda {data.get('description', 'desconhecida')} não é um número válido. Usando 0.0.")
            current_funded_amount = 0.0

        emenda = cls(
            data['description'],
            valor_necessario,
            data.get('categoria', 'Sem Categoria') # Garante que 'categoria' sempre exista, mesmo que vazia no JSON
        )
        emenda.id = data['id']
        emenda.current_funded_amount = current_funded_amount
        emenda.current_contributions = data.get('current_contributions', {})
        return emenda