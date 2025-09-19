import math
from Deputy import Deputy
from Emenda import Emenda
from DeputyManager import DeputyManager
from EmendaManager import EmendaManager
# Removida a importação de DataManager aqui pois não é utilizada diretamente

class ReportGenerator:
    def __init__(self, deputy_manager: DeputyManager, emenda_manager: EmendaManager):
        self.deputy_manager = deputy_manager
        self.emenda_manager = emenda_manager

    def _get_current_allocation_state(self):
        """
        Coleta o estado atual de alocação das emendas e deputados (após otimização)
        lendo os atributos current_funded_amount e current_contributions das emendas.
        Retorna: (emenda_report_status, total_verba_efetivamente_usada_em_emendas_no_report,
                    total_deputy_budget_available, total_deputy_budget_intended_allocation)
        """
        emenda_report_status = {}
        total_verba_efetivamente_usada_em_emendas_no_report = 0.0
        total_deputy_budget_available = 0.0
        total_deputy_budget_intended_allocation = 0.0

        for emenda in self.emenda_manager.list_emendas():
            total_verba_efetivamente_usada_em_emendas_no_report += emenda.current_funded_amount
            
            if math.isclose(emenda.current_funded_amount, emenda.valor_necessario) or emenda.current_funded_amount > emenda.valor_necessario:
                status = 'TOTALMENTE CONTEMPLADA'
                funded_amount = emenda.valor_necessario 
                missing_amount = 0.0
            elif emenda.current_funded_amount > 0:
                status = 'PARCIALMENTE CONTEMPLADA'
                funded_amount = emenda.current_funded_amount
                missing_amount = emenda.valor_necessario - emenda.current_funded_amount
            else:
                status = 'NÃO CONTEMPLADA'
                funded_amount = 0.0
                missing_amount = emenda.valor_necessario

            emenda_report_status[emenda.id] = {
                'emenda': emenda,
                'funded_amount': funded_amount,
                'status': status,
                'contributors': emenda.current_contributions.copy(), 
                'missing_amount': missing_amount
            }
        
        for deputy in self.deputy_manager.list_deputies():
            total_deputy_budget_available += deputy.total_verba_disponivel
            total_deputy_budget_intended_allocation += deputy.get_allocated_total()

        return emenda_report_status, total_verba_efetivamente_usada_em_emendas_no_report, total_deputy_budget_available, total_deputy_budget_intended_allocation


    def generate_report(self):
        report_lines = []
        report_lines.append("="*60)
        report_lines.append("RELATÓRIO DE DISTRIBUIÇÃO DE VERBAS E STATUS DAS EMENDAS")
        report_lines.append("="*60)

        emenda_status, total_verba_efetivamente_usada_em_emendas_no_report, \
            total_deputy_budget_available, total_deputy_budget_intended_allocation = \
            self._get_current_allocation_state() 
        
        deputy_by_id = {d.id: d for d in self.deputy_manager.list_deputies()}

        # --- SEÇÃO DE RELATÓRIO POR DEPUTADO ---
        report_lines.append("\n" + "═"*60)
        report_lines.append("RELATÓRIO DE DISTRIBUIÇÃO DE VERBAS POR DEPUTADO")
        report_lines.append("═"*60)
        
        for deputy in self.deputy_manager.list_deputies():
            actual_spent_by_deputy = deputy.actual_spent_amount 
            
            deputy_contributions_by_category = {}
            for emenda_id, status_info in emenda_status.items():
                # Converte dep_id para string para corresponder às chaves do dicionário current_contributions
                if str(deputy.id) in status_info['contributors']:
                    emenda = status_info['emenda']
                    contrib_detail = status_info['contributors'][str(deputy.id)]
                    deputy_contributions_by_category.setdefault(emenda.categoria, []).append((emenda, contrib_detail, status_info['status']))
            
            report_lines.append(f"\n" + "═"*60) 
            report_lines.append(f"  Deputado: {deputy.name} (ID: {deputy.id})")
            report_lines.append(f"  Verba Total Disponível:           R\${deputy.total_verba_disponivel:,.2f}")
            report_lines.append(f"  Verba Alocada por Categorias (Intenção): R\${deputy.get_allocated_total():,.2f}")
            report_lines.append(f"  Verba Remanescente (Para Alocação Livre): R\${deputy.get_remaining_verba():,.2f}")
            report_lines.append(f"  ---------------------------------------------------------------------")
            report_lines.append(f"  Verba Efetivamente Usada em Emendas:  R\${actual_spent_by_deputy:,.2f}")
            report_lines.append(f"  Verba Remanescente Final do Deputado: R\${deputy.total_verba_disponivel - actual_spent_by_deputy:,.2f}")
            report_lines.append(f"\n  Detalhes das Contribuições para Emendas:")
            
            if deputy_contributions_by_category:
                for category in sorted(deputy_contributions_by_category.keys()):
                    report_lines.append(f"    ▶ Categoria: {category}\n")
                    for emenda, contrib_detail, emenda_final_status in deputy_contributions_by_category[category]:
                        total_contrib = contrib_detail['total']
                        from_alloc = contrib_detail['from_allocated_intention']
                        from_free = contrib_detail['from_free_verba']
                        
                        percent_of_emenda = (total_contrib / emenda.valor_necessario) * 100 if emenda.valor_necessario > 0 else 0
                        report_lines.append(f"      - Emenda '{emenda.description}' (ID: {emenda.id})")
                        report_lines.append(f"        Valor Necessário da Emenda: R\${emenda.valor_necessario:,.2f}")
                        report_lines.append(f"        Contribuição Total deste Deputado: R\${total_contrib:,.2f} ({percent_of_emenda:.2f}% da emenda)")
                        if from_alloc > 0:
                            report_lines.append(f"          (Da Alocação por Categoria: R\${from_alloc:,.2f})")
                        if from_free > 0:
                            report_lines.append(f"          (Da Verba Livre: R\${from_free:,.2f})")
                        report_lines.append(f"        Status Final da Emenda: {emenda_final_status}\n")
            else:
                report_lines.append("    Nenhuma contribuição direta para emendas.\n")
            report_lines.append("═"*60) 

        # --- SEÇÃO DE SUMÁRIO FINAL DAS EMENDAS (com detalhes de contribuição) ---
        report_lines.append("\n\n" + "═"*60)
        report_lines.append("SUMÁRIO FINAL DO STATUS DAS EMENDAS")
        report_lines.append("═"*60)
        
        non_contemplated = []
        partially_contemplated = []
        fully_contemplated = []

        for emenda_id, status_info in emenda_status.items():
            emenda = status_info['emenda']
            if status_info['status'] == 'NÃO CONTEMPLADA':
                non_contemplated.append(emenda)
            elif status_info['status'] == 'PARCIALMENTE CONTEMPLADA':
                partially_contemplated.append(emenda)
            else:
                fully_contemplated.append(emenda)
        
        report_lines.append("\n--- Emendas Totalmente Contempladas ---\n")
        if fully_contemplated:
            for emenda in fully_contemplated:
                status_info = emenda_status[emenda.id]
                report_lines.append(f"  ✔ Emenda '{emenda.description}' (Cat: {emenda.categoria}, Valor Necessário: R\${emenda.valor_necessario:,.2f})")
                report_lines.append(f"    Contemplado: R\${status_info['funded_amount']:,.2f}")
                for dep_id_str, contrib_detail in status_info['contributors'].items():
                    dep_id = int(dep_id_str) 
                    deputy_obj = deputy_by_id.get(dep_id)
                    deputy_name = deputy_obj.name if deputy_obj else f"Deputado ID {dep_id} (Não encontrado)" 
                    
                    total_contrib = contrib_detail['total']
                    from_alloc = contrib_detail['from_allocated_intention']
                    from_free = contrib_detail['from_free_verba']
                    
                    percent = (total_contrib / emenda.valor_necessario) * 100 if emenda.valor_necessario > 0 else 0
                    
                    contrib_str = f"    - {deputy_name}: R\${total_contrib:,.2f} ({percent:.2f}% da emenda)"
                    if from_alloc > 0:
                        contrib_str += f" (Intenção: R\${from_alloc:,.2f})"
                    if from_free > 0:
                        contrib_str += f" (Livre: R\${from_free:,.2f})"
                    report_lines.append(contrib_str)
                report_lines.append("\n") 
        else:
            report_lines.append("(Nenhuma emenda totalmente contemplada.)\n")

        report_lines.append("\n--- Emendas Parcialmente Contempladas ---\n")
        if partially_contemplated:
            for emenda in partially_contemplated:
                status_info = emenda_status[emenda.id]
                report_lines.append(f"  ◐ Emenda '{emenda.description}' (Cat: {emenda.categoria}, Valor Necessário: R\${emenda.valor_necessario:,.2f})")
                report_lines.append(f"    Contemplado: R\${status_info['funded_amount']:,.2f}, Faltam: R\${status_info['missing_amount']:,.2f}")
                for dep_id_str, contrib_detail in status_info['contributors'].items():
                    dep_id = int(dep_id_str) 
                    deputy_obj = deputy_by_id.get(dep_id)
                    deputy_name = deputy_obj.name if deputy_obj else f"Deputado ID {dep_id} (Não encontrado)" 

                    total_contrib = contrib_detail['total']
                    from_alloc = contrib_detail['from_allocated_intention']
                    from_free = contrib_detail['from_free_verba']
                    
                    percent = (total_contrib / emenda.valor_necessario) * 100 if emenda.valor_necessario > 0 else 0
                    
                    contrib_str = f"    - {deputy_name}: R\${total_contrib:,.2f} ({percent:.2f}% da emenda)"
                    if from_alloc > 0:
                        contrib_str += f" (Intenção: R\${from_alloc:,.2f})"
                    if from_free > 0:
                        contrib_str += f" (Livre: R\${from_free:,.2f})"
                    report_lines.append(contrib_str)
                report_lines.append("\n") 
        else:
            report_lines.append("(Nenhuma emenda parcialmente contemplada.)\n")

        report_lines.append("\n--- Emendas Não Contempladas ---\n")
        if non_contemplated:
            for emenda in non_contemplated:
                report_lines.append(f"  ✖ Emenda '{emenda.description}' (Cat: {emenda.categoria}, Valor Necessário: R\${emenda.valor_necessario:,.2f})")
                report_lines.append("\n") 
        else:
            report_lines.append("(Nenhuma emenda não contemplada.)\n")
        
        # --- SEÇÃO DE RESUMO GERAL DO USO DAS VERBAS DOS DEPUTADOS ---
        report_lines.append("\n\n" + "═"*60)
        report_lines.append("RESUMO GERAL DO USO DAS VERBAS DOS DEPUTADOS")
        report_lines.append("═"*60)
        
        total_verba_efetivamente_usada_em_emendas_from_deputies = sum(d.actual_spent_amount for d in self.deputy_manager.list_deputies())
        remaining_deputy_budget_after_actual_spending = total_deputy_budget_available - total_verba_efetivamente_usada_em_emendas_from_deputies
        
        report_lines.append(f"\nVerba Total Disponível dos Deputados (Soma): R\${total_deputy_budget_available:,.2f}")
        report_lines.append(f"Verba Total Intenção de Alocação por Deputados (em categorias): R\${total_deputy_budget_intended_allocation:,.2f}")
        report_lines.append(f"Verba Total Efetivamente Usada em Emendas: R\${total_verba_efetivamente_usada_em_emendas_from_deputies:,.2f}")
        report_lines.append(f"Verba Total Remanescente (não utilizada em emendas): R\${remaining_deputy_budget_after_actual_spending:,.2f}")
        
        percentage_used = 0
        if total_deputy_budget_available > 0:
            percentage_used = (total_verba_efetivamente_usada_em_emendas_from_deputies / total_deputy_budget_available) * 100
        report_lines.append(f"Percentual da Verba Total Disponível Efetivamente Usada: {percentage_used:.2f}%\n")

        report_lines.append("\n\n" + "═"*80)
        return "\n".join(report_lines) # Retorna uma única string com quebras de linha para st.text

    def get_summary_for_chart(self):
        emenda_status, total_verba_efetivamente_usada_em_emendas_no_report, \
            total_deputy_budget_available, total_deputy_budget_intended_allocation = \
            self._get_current_allocation_state()

        remaining_deputy_budget_after_actual_spending = total_deputy_budget_available - total_verba_efetivamente_usada_em_emendas_no_report

        chart_data = {
          "type": "pie",
          "title": {
            "text": "Percentual de Uso da Verba Total dos Deputados"
          },
          "series": [
            {
              "name": "Verba Efetivamente Usada",
              "data": total_verba_efetivamente_usada_em_emendas_no_report
            },
            {
              "name": "Verba Remanescente (não usada)",
              "data": remaining_deputy_budget_after_actual_spending
            }
          ]
        }
        return chart_data