import json
import os
from Deputy import Deputy
from Emenda import Emenda

class DataManager: # <-- AQUI DEVE SER 'DataManager' EXATAMENTE ASSIM
    def __init__(self):
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
        self.deputies_file = os.path.join(self.data_dir, 'deputies.json')
        self.emendas_file = os.path.join(self.data_dir, 'emendas.json')
        self.categories_file = os.path.join(self.data_dir, 'categories.json')

    def _load_json(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return [] # Retorna lista vazia se o JSON estiver malformado
        return []

    def _save_json(self, data, filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_deputies(self):
        deputy_data = self._load_json(self.deputies_file)
        return [Deputy.deserialize(d) for d in deputy_data]

    def save_deputies(self, deputies):
        deputy_data = [d.serialize() for d in deputies]
        self._save_json(deputy_data, self.deputies_file)

    def load_emendas(self):
        emenda_data = self._load_json(self.emendas_file)
        return [Emenda.deserialize(e) for e in emenda_data]

    def save_emendas(self, emendas):
        emenda_data = [e.serialize() for e in emendas]
        self._save_json(emenda_data, self.emendas_file)

    def load_categories(self):
        return self._load_json(self.categories_file)

    def save_categories(self, categories):
        self._save_json(categories, self.categories_file)