import json
from Deputy import Deputy
# A linha abaixo deve estar REMOVIDA, pois DataManager será passado no construtor
# from DataManager import DataManager 

class DeputyManager:
    # O construtor **DEVE** receber uma instância de DataManager
    def __init__(self, data_manager): 
        self.data_manager = data_manager
        self.deputies = self.data_manager.load_deputies()
        self.next_deputy_id = max([d.id for d in self.deputies] or [0]) + 1

    def add_deputy(self, name, total_verba_disponivel, profile=None):
        new_deputy = Deputy(name, total_verba_disponivel, profile)
        new_deputy.id = self.next_deputy_id
        self.deputies.append(new_deputy)
        self.next_deputy_id += 1
        self.data_manager.save_deputies(self.deputies)
        return new_deputy

    def list_deputies(self):
        return self.deputies

    def get_deputy_by_id(self, deputy_id):
        return next((d for d in self.deputies if d.id == deputy_id), None)

    def update_deputy(self, deputy_id, new_name=None, new_verba=None, new_profile=None):
        deputy = self.get_deputy_by_id(deputy_id)
        if not deputy:
            return False, "Deputado não encontrado.", None
        
        old_total_verba = deputy.total_verba_disponivel # Para comparação posterior

        if new_name is not None:
            deputy.name = new_name
        if new_verba is not None:
            deputy.total_verba_disponivel = new_verba
        if new_profile is not None:
            deputy.profile = new_profile

        self.data_manager.save_deputies(self.deputies)
        return True, "Deputado atualizado com sucesso.", old_total_verba

    def update_deputy_allocations(self, deputy_id, new_allocations):
        deputy = self.get_deputy_by_id(deputy_id)
        if not deputy:
            return False, "Deputado não encontrado."
        
        # Validar se o total das novas alocações não excede a verba total
        total_allocated = sum(new_allocations.values())
        if total_allocated > deputy.total_verba_disponivel:
            return False, "Soma das alocações excede a verba total disponível do deputado."

        deputy.allocated_by_category = new_allocations
        self.data_manager.save_deputies(self.deputies)
        return True, "Distribuição de verbas atualizada com sucesso."

    def update_deputy_inclinations(self, deputy_id, new_inclinations):
        deputy = self.get_deputy_by_id(deputy_id)
        if not deputy:
            return False, "Deputado não encontrado."
        
        # Validar se a soma das inclinações não excede 10
        total_inclination_score = sum(new_inclinations.values())
        if total_inclination_score > 10:
            return False, "Soma das inclinações excede o limite de 10 pontos."

        deputy.inclinacao_por_categoria = new_inclinations
        self.data_manager.save_deputies(self.deputies)
        return True, "Inclinação por categoria atualizada com sucesso."

    def delete_deputy(self, deputy_id):
        initial_len = len(self.deputies)
        self.deputies = [d for d in self.deputies if d.id != deputy_id]
        if len(self.deputies) < initial_len:
            self.data_manager.save_deputies(self.deputies)
            return True, "Deputado excluído com sucesso."
        return False, "Deputado não encontrado."

    def get_deputies_needing_reallocation(self):
        return [d for d in self.deputies if d.needs_reallocation]

    def clear_needs_reallocation_flags(self, deputy_ids=None):
        if deputy_ids is None: # Limpa todos
            for d in self.deputies:
                d.needs_reallocation = False
        else: # Limpa apenas os IDs específicos
            for d in self.deputies:
                if d.id in deputy_ids:
                    d.needs_reallocation = False
        self.data_manager.save_deputies(self.deputies)
