import json

class CategoryManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.categories = self.data_manager.load_categories()

    def add_category(self, category_name):
        category_name_formatted = category_name.strip().capitalize()
        if not category_name_formatted:
            return False, "O nome da categoria não pode ser vazio."
        if category_name_formatted in self.categories:
            return False, f"Categoria '{category_name_formatted}' já existente."
        
        self.categories.append(category_name_formatted)
        self.data_manager.save_categories(self.categories)
        return True, f"Categoria '{category_name_formatted}' adicionada com sucesso."

    def list_categories(self):
        return self.categories

    def category_exists(self, category_name):
        return category_name.strip().capitalize() in self.categories

    def delete_category(self, category_name):
        category_name_formatted = category_name.strip().capitalize()
        if category_name_formatted in self.categories:
            self.categories.remove(category_name_formatted)
            self.data_manager.save_categories(self.categories)
            return True, f"Categoria '{category_name_formatted}' excluída com sucesso."
        return False, "Categoria não encontrada."
