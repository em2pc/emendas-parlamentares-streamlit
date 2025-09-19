import math
from Deputy import Deputy
from Emenda import Emenda
from DeputyManager import DeputyManager
from EmendaManager import EmendaManager
from DataManager import DataManager # Importar DataManager

class AllocationOptimizer:
    def __init__(self, deputy_manager: DeputyManager, emenda_manager: EmendaManager, data_manager: DataManager): 
        self.deputy_manager = deputy_manager
        self.emenda_manager = emenda_manager
        self.data_manager = data_manager

    def _reset_all_emenda_contributions(self):
        """
        Zera todas as contribuições de todas as emendas e o valor total financiado.
        """
        for emenda in self.emenda_manager.list_emendas():
            emenda.current_funded_amount = 0.0
            emenda.current_contributions = {}
        # Não precisamos salvar aqui, pois será salvo ao final da otimização.

    def _reset_specific_deputy_contributions(self, deputy_id):
        """
        Remove todas as contribuições de um deputado específico de todas as emendas.
        Ajusta o valor financiado e as contribuições das emendas.
        """
        for emenda in self.emenda_manager.list_emendas():
            if deputy_id in emenda.current_contributions:
                removed_amount = emenda.current_contributions[deputy_id]['total']
                emenda.current_funded_amount = max(0, emenda.current_funded_amount - removed_amount)
                del emenda.current_contributions[deputy_id]
        # Não precisamos salvar aqui, pois será salvo ao final da otimização.

    def _distribute_funds_from_deputies(self, deputies_to_distribute: list[Deputy], all_emendas: list[Emenda]):
        """
        Aplica a lógica de distribuição de fundos para uma lista de deputados
        e emendas, atualizando o estado _real_ das emendas e quanto cada deputado gastou.
        """
        
        deputy_effective_available_funds = {}
        for deputy in deputies_to_distribute:
             deputy_effective_available_funds[deputy.id] = deputy.total_verba_disponivel
             deputy.actual_spent_amount = 0.0 

        # --- FASE 1: Verba ALOCADA POR CATEGORIA (INTENÇÃO) ---
        for deputy in deputies_to_distribute:
            for category, allocated_amount_from_deputy_intention in deputy.allocated_by_category.items():
                if allocated_amount_from_deputy_intention <= 0 or deputy_effective_available_funds[deputy.id] <= 0:
                    continue

                emendas_in_category = [e for e in all_emendas if e.categoria == category]
                emendas_in_category.sort(key=lambda e: e.valor_necessario) 

                current_deputy_funds_for_category = min(allocated_amount_from_deputy_intention, deputy_effective_available_funds[deputy.id])
                
                for emenda_obj in emendas_in_category:
                    needed_by_emenda = emenda_obj.valor_necessario - emenda_obj.current_funded_amount
                    
                    if needed_by_emenda <= 0: 
                        continue

                    amount_to_contribute = min(current_deputy_funds_for_category, needed_by_emenda)

                    if amount_to_contribute > 0:
                        emenda_obj.current_funded_amount += amount_to_contribute
                        
                        if deputy.id not in emenda_obj.current_contributions:
                            emenda_obj.current_contributions[deputy.id] = {'total': 0, 'from_allocated_intention': 0, 'from_free_verba': 0}
                        
                        emenda_obj.current_contributions[deputy.id]['total'] += amount_to_contribute
                        emenda_obj.current_contributions[deputy.id]['from_allocated_intention'] += amount_to_contribute
                        
                        current_deputy_funds_for_category -= amount_to_contribute
                        deputy_effective_available_funds[deputy.id] -= amount_to_contribute 
                        deputy.actual_spent_amount += amount_to_contribute 
                    
                    if current_deputy_funds_for_category <= 0 or deputy_effective_available_funds[deputy.id] <= 0:
                        break

        # --- FASE 2: Verba REMANESCENTE/LIVRE do deputado ---
        for deputy in deputies_to_distribute:
            remaining_verba_for_deputy = deputy_effective_available_funds[deputy.id] 
            
            if remaining_verba_for_deputy <= 0:
                continue

            potential_emendas_for_free_funds = []
            for emenda_obj in all_emendas: 
                if emenda_obj.valor_necessario - emenda_obj.current_funded_amount > 0: 
                    inclination_score = deputy.get_inclination_score(emenda_obj.categoria)
                    is_partially_funded_weight = 1 if emenda_obj.current_funded_amount > 0 else 0 
                    
                    potential_emendas_for_free_funds.append((emenda_obj, inclination_score, is_partially_funded_weight))
            
            potential_emendas_for_free_funds.sort(key=lambda x: (x[2], x[1], x[0].valor_necessario), reverse=True)

            for emenda_obj, inclination_score, _ in potential_emendas_for_free_funds:
                needed_by_emenda = emenda_obj.valor_necessario - emenda_obj.current_funded_amount

                if needed_by_emenda <= 0 or remaining_verba_for_deputy <= 0:
                    break 

                amount_to_contribute = min(remaining_verba_for_deputy, needed_by_emenda)

                if amount_to_contribute > 0:
                    emenda_obj.current_funded_amount += amount_to_contribute
                    
                    if deputy.id not in emenda_obj.current_contributions:
                        emenda_obj.current_contributions[deputy.id] = {'total': 0, 'from_allocated_intention': 0, 'from_free_verba': 0}
                    
                    emenda_obj.current_contributions[deputy.id]['total'] += amount_to_contribute
                    emenda_obj.current_contributions[deputy.id]['from_free_verba'] += amount_to_contribute
                    
                    remaining_verba_for_deputy -= amount_to_contribute
                    deputy_effective_available_funds[deputy.id] -= amount_to_contribute 
                    deputy.actual_spent_amount += amount_to_contribute 
        
        self.data_manager.save_emendas(all_emendas) 
        self.data_manager.save_deputies(self.deputy_manager.list_deputies())


    def perform_full_redistribution(self):
        """
        Executa uma redistribuição completa de todas as verbas de todos os deputados para todas as emendas.
        """
        all_emendas = self.emenda_manager.list_emendas()
        all_deputies = self.deputy_manager.list_deputies()

        self._reset_all_emenda_contributions() 

        for deputy in all_deputies:
            deputy.actual_spent_amount = 0.0
        self.data_manager.save_deputies(all_deputies) 

        self._distribute_funds_from_deputies(all_deputies, all_emendas)
        
        self.deputy_manager.clear_needs_reallocation_flags() 
        return "Redistribuição completa de verbas realizada com sucesso."

    def perform_partial_redistribution(self, deputy_ids_to_reallocate: list[int]):
        """
        Executa uma redistribuição parcial de verbas apenas para os deputados especificados.
        As contribuições de outros deputados (não especificados) permanecem inalteradas.
        """
        if not deputy_ids_to_reallocate:
            return "Nenhum deputado selecionado para redistribuição parcial."

        all_emendas = self.emenda_manager.list_emendas()
        all_deputies = self.deputy_manager.list_deputies()
        
        deputies_to_reallocate_objs = [d for d in all_deputies if d.id in deputy_ids_to_reallocate]
        
        for dep_id in deputy_ids_to_reallocate:
            self._reset_specific_deputy_contributions(dep_id)
            deputy = self.deputy_manager.get_deputy_by_id(dep_id)
            if deputy:
                deputy.actual_spent_amount = 0.0
        
        self.data_manager.save_emendas(all_emendas)
        self.data_manager.save_deputies(all_deputies) 

        self._distribute_funds_from_deputies(deputies_to_reallocate_objs, all_emendas)
        
        self.deputy_manager.clear_needs_reallocation_flags(deputy_ids_to_reallocate) 
        
        return f"Redistribuição parcial de verbas realizada para {len(deputy_ids_to_reallocate)} deputado(s)."

