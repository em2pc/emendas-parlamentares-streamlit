import json

class Deputy:
    def __init__(self, name, total_verba_disponivel, profile=None):
        self.id = None 
        self.name = name
        self.total_verba_disponivel = float(total_verba_disponivel) # Garante que seja float
        self.allocated_by_category = {}
        self.inclinacao_por_categoria = {} 
        self.profile = profile
        self.actual_spent_amount = 0.0 
        self.needs_reallocation = True 

    def get_allocated_total(self):
        return sum(self.allocated_by_category.values())

    def get_remaining_verba(self):
        return self.total_verba_disponivel - self.get_allocated_total()

    def get_inclination_score(self, category):
        return self.inclinacao_por_categoria.get(category, 0)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'total_verba_disponivel': self.total_verba_disponivel,
            'allocated_by_category': self.allocated_by_category,
            'inclinacao_por_categoria': self.inclinacao_por_categoria,
            'profile': self.profile,
            'actual_spent_amount': self.actual_spent_amount,
            'needs_reallocation': self.needs_reallocation
        }

    @classmethod
    def deserialize(cls, data):
        # Tenta converter total_verba_disponivel para float de forma mais segura
        # Se não for possível, define como 0.0
        try:
            total_verba_disponivel = float(data.get('total_verba_disponivel', 0.0))
        except (ValueError, TypeError):
            print(f"AVISO: 'total_verba_disponivel' para deputado {data.get('name', 'desconhecido')} não é um número válido. Usando 0.0.")
            total_verba_disponivel = 0.0
            
        # Tenta converter actual_spent_amount para float de forma mais segura
        try:
            actual_spent_amount = float(data.get('actual_spent_amount', 0.0))
        except (ValueError, TypeError):
            print(f"AVISO: 'actual_spent_amount' para deputado {data.get('name', 'desconhecido')} não é um número válido. Usando 0.0.")
            actual_spent_amount = 0.0

        deputy = cls(
            data['name'], 
            total_verba_disponivel, 
            data.get('profile') # Pega o profile. Se não existir, é None.
        )
        deputy.id = data['id']
        deputy.allocated_by_category = data.get('allocated_by_category', {})
        deputy.inclinacao_por_categoria = data.get('inclinacao_por_categoria', {})
        deputy.actual_spent_amount = actual_spent_amount
        deputy.needs_reallocation = data.get('needs_reallocation', True)
        return deputy