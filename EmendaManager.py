from Emenda import Emenda
# A linha abaixo deve estar REMOVIDA, pois DataManager será passado no construtor
# from DataManager import DataManager 

class EmendaManager:
    # O construtor **DEVE** receber uma instância de DataManager
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.emendas = self.data_manager.load_emendas()
        self.next_emenda_id = max([e.id for e in self.emendas] or [0]) + 1

    def add_emenda(self, description, valor_necessario, categoria):
        new_emenda = Emenda(description, valor_necessario, categoria)
        new_emenda.id = self.next_emenda_id
        self.emendas.append(new_emenda)
        self.next_emenda_id += 1
        self.data_manager.save_emendas(self.emendas)
        return new_emenda

    def list_emendas(self):
        return self.emendas

    def get_emenda_by_id(self, emenda_id):
        return next((e for e in self.emendas if e.id == emenda_id), None)

    def delete_emenda(self, emenda_id):
        initial_len = len(self.emendas)
        self.emendas = [e for e in self.emendas if e.id != emenda_id]
        if len(self.emendas) < initial_len:
            self.data_manager.save_emendas(self.emendas)
            return True, "Emenda excluída com sucesso."
        return False, "Emenda não encontrada."
