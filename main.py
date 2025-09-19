import os
import math
import json 

from DeputyManager import DeputyManager
from EmendaManager import EmendaManager
from ReportGenerator import ReportGenerator
from CategoryManager import CategoryManager
from AllocationOptimizer import AllocationOptimizer 
from Deputy import Deputy

class App:
    def __init__(self):
        self.category_manager = CategoryManager()
        self.deputy_manager = DeputyManager()
        self.emenda_manager = EmendaManager()
        self.optimizer = AllocationOptimizer(self.deputy_manager, self.emenda_manager) 
        self.report_generator = ReportGenerator(self.deputy_manager, self.emenda_manager)

    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _get_input(self, prompt, type_func=str, validation_func=None):
        while True:
            value = input(prompt).strip()
            if not value and type_func != str:
                print("Erro: Entrada não pode ser vazia. Por favor, tente novamente.")
                continue
            try:
                converted_value = type_func(value)
                if validation_func and not validation_func(converted_value):
                    raise ValueError("Valor inválido.")
                return converted_value
            except ValueError:
                print(f"Erro: Entrada inválida. Por favor, tente novamente.")

    def _get_input_optional(self, prompt, current_value=None, type_func=str, validation_func=None):
        display_value = f" (Atual: {current_value})" if current_value is not None else ""
        while True:
            raw_value = input(prompt + display_value + " (Deixe vazio para manter, digite 'limpar' para remover): ").strip()
            
            if not raw_value: 
                return current_value
            elif raw_value.lower() == 'limpar' and type_func == str: 
                return "" 
            elif raw_value.lower() == 'limpar' and type_func != str:
                print("Erro: Não é possível 'limpar' um campo numérico com esta opção. Digite um valor válido ou deixe vazio.")
                continue
            
            try:
                converted_value = type_func(raw_value)
                if validation_func and not validation_func(converted_value):
                    raise ValueError("Valor inválido.")
                return converted_value
            except ValueError:
                print(f"Erro: Entrada inválida para {type_func.__name__}. Por favor, tente novamente.")

    def _select_or_create_category(self, prompt_text, allow_empty_to_finish=False):
        categories = self.category_manager.list_categories()
        
        if not categories:
            if allow_empty_to_finish:
                print(f"Nenhuma categoria cadastrada ainda. Você precisará criar uma nova, ou ENTER para cancelar.")
                new_category_name = self._get_input(f"{prompt_text} (digite o nome da nova categoria): ")
                if not new_category_name:
                    return None 
            else:
                print("Nenhuma categoria cadastrada ainda. Você precisará criar uma nova.")
                new_category_name = self._get_input(f"{prompt_text} (digite o nome da nova categoria): ")
                if not new_category_name: 
                    print("Nome da categoria não pode ser vazio. Tente novamente.")
                    return self._select_or_create_category(prompt_text, allow_empty_to_finish) 

            self.category_manager.add_category(new_category_name)
            return new_category_name.strip().capitalize()
        
        print("\n--- Categorias Existentes ---")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        print("-----------------------------")
        
        while True:
            choice_prompt = f"{prompt_text} (digite o NÚMERO da categoria, um NOVO NOME, ou ENTER para finalizar): " if allow_empty_to_finish else f"{prompt_text} (digite o NÚMERO da categoria ou um NOVO NOME): "
            choice = self._get_input(choice_prompt)
            
            if not choice and allow_empty_to_finish: 
                return None
            
            try:
                choice_int = int(choice)
                if 1 <= choice_int <= len(categories):
                    return categories[choice_int - 1]
                else:
                    print("Número de categoria inválido. Tente novamente ou digite um novo nome.")
            except ValueError:
                chosen_category_name = choice.strip().capitalize()
                if self.category_manager.category_exists(chosen_category_name):
                    return chosen_category_name
                else:
                    add_confirm = self._get_input(f"Categoria '{chosen_category_name}' não encontrada. Deseja cadastrá-la como nova? (s/n): ").lower()
                    if add_confirm == 's':
                        self.category_manager.add_category(chosen_category_name)
                        return chosen_category_name
                    else:
                        print("Por favor, selecione uma categoria existente ou digite um novo nome para cadastrar.")

    def _display_deputy_selection_list(self):
        deputies = self.deputy_manager.list_deputies()
        if not deputies:
            print("Nenhum deputado cadastrado.")
            return False 
        
        print("\n" + "═"*30)
        print("SELECIONE UM DEPUTADO")
        print("═"*30 + "\n")
        for d in deputies:
            needs_realloc_str = " (PRECISA REALOCAR)" if d.needs_reallocation else "" 
            print(f"  ID: {d.id:<5} | Nome: {d.name}{needs_realloc_str}")
        print("\n" + "═"*30 + "\n")
        return True 

    def _display_deputies(self):
        deputies = self.deputy_manager.list_deputies()
        if not deputies:
            print("Nenhum deputado cadastrado.")
            return
        print("\n" + "═"*60)
        print("LISTAGEM GERAL DE DEPUTADOS")
        print("═"*60 + "\n")
        for d in deputies:
            print(f"  ID: {d.id}")
            print(f"  Nome: {d.name}")
            print(f"  Verba Total Disponível:           R${d.total_verba_disponivel:,.2f}")
            print(f"  Intenção de Alocação (Categorias): R${d.get_allocated_total():,.2f}")
            print(f"  Verba Remanescente (Para Alocação Livre): R${d.get_remaining_verba():,.2f}")
            print(f"  Verba Efetivamente Gasta em Emendas: R${d.actual_spent_amount:,.2f}") 
            print(f"  Precisa de Realocação: {'Sim' if d.needs_reallocation else 'Não'}") 
            
            if d.profile:
                print(f"  Perfil:\n    {d.profile}")
            else:
                print("  Perfil: (Não informado)")

            if d.allocated_by_category:
                print("  Alocações por Categoria (Intenção):")
                for cat, val in d.allocated_by_category.items():
                    print(f"    - {cat}: R${val:,.2f}")
            
            if d.inclinacao_por_categoria:
                print(f"  Inclinação por Categoria (Total: {sum(d.inclinacao_por_categoria.values())}/10):")
                for cat, score in d.inclinacao_por_categoria.items():
                    print(f"    - {cat}: {score}/10 ({score*10:.2f}% da inclinação total do deputado)")
            else:
                print("  Nenhuma inclinação por categoria configurada.")
            print("\n" + "─"*60 + "\n") 
        print("═"*60 + "\n")

    def _display_emendas(self):
        emendas = self.emenda_manager.list_emendas()
        if not emendas:
            print("Nenhuma emenda cadastrada.")
            return

        emendas_by_category = {}
        for emenda in emendas:
            emendas_by_category.setdefault(emenda.categoria, []).append(emenda)
        
        print("\n" + "═"*60)
        print("EMENDAS CADASTRADAS POR CATEGORIA")
        print("═"*60 + "\n")
        total_geral_emendas = 0
        for category in sorted(emendas_by_category.keys()):
            category_emendas = emendas_by_category[category]
            total_category_value = sum(e.valor_necessario for e in category_emendas)
            total_geral_emendas += total_category_value
            
            print(f"  ## CATEGORIA: {category} (Total: R${total_category_value:,.2f}) ##\n")
            for e in category_emendas:
                print(f"    ID: {e.id}")
                print(f"    Descrição: {e.description}")
                print(f"    Valor Necessário: R${e.valor_necessario:,.2f}")
                print(f"    Valor Contemplado Atualmente: R${e.current_funded_amount:,.2f}") 
                status = "TOTALMENTE" if math.isclose(e.current_funded_amount, e.valor_necessario) or e.current_funded_amount > e.valor_necessario else ("PARCIALMENTE" if e.current_funded_amount > 0 else "NÃO")
                print(f"    Status: {status} CONTEMPLADA") 
                print("    " + "─"*30 + "\n") 
            print("\n" + "═"*60 + "\n") 
        
        print("\n" + "═"*(60))
        print(f"TOTAL GERAL DE TODAS AS EMENDAS: R${total_geral_emendas:,.2f}")
        print("═"*60 + "\n")

    def _generate_allocated_verba_chart_json(self, deputy: Deputy):
        series_data = []
        for cat, value in deputy.allocated_by_category.items():
            if value > 0:
                series_data.append({"name": cat, "data": value})
        
        if not series_data:
            return None # Retorna None se não houver dados para o gráfico
            
        chart = {
            "type": "pie",
            "title": {"text": "Verba Alocada por Categoria (Intenção)"},
            "series": series_data
        }
        return chart

    def _generate_inclination_chart_json(self, deputy: Deputy):
        series_data = []
        for cat, score in deputy.inclinacao_por_categoria.items():
            if score > 0:
                series_data.append({"name": cat, "data": score})

        if not series_data:
            return None # Retorna None se não houver dados para o gráfico
            
        chart = {
            "type": "pie",
            "title": {"text": "Pontos de Inclinação por Categoria"},
            "series": series_data
        }
        return chart

    def _generate_contributed_emendas_chart_json(self, contributions_by_category_for_display):
        series_data = []
        category_totals = {}
        for category, contrib_list in contributions_by_category_for_display.items():
            total_for_category = sum(item['contrib_detail']['total'] for item in contrib_list)
            if total_for_category > 0:
                category_totals[category] = total_for_category
        
        for cat, total in category_totals.items():
            series_data.append({"name": cat, "data": total})

        if not series_data:
            return None # Retorna None se não houver dados para o gráfico
            
        chart = {
            "type": "pie",
            "title": {"text": "Verba Efetivamente Contribuída para Emendas (por Categoria)"},
            "series": series_data
        }
        return chart

    def _display_single_deputy_details(self, deputy_id):
        self._clear_screen()
        deputy = self.deputy_manager.get_deputy_by_id(deputy_id)
        if not deputy:
            print("Deputado não encontrado.")
            return

        emenda_status_all, _, _, _ = self.report_generator._get_current_allocation_state()

        actual_spent_by_deputy = deputy.actual_spent_amount 
        contributions_by_category_for_display = {}
        for emenda_id, status_info in emenda_status_all.items():
            if deputy.id in status_info['contributors']:
                contrib_detail = status_info['contributors'][deputy.id] 
                emenda = status_info['emenda']
                
                contributions_by_category_for_display.setdefault(emenda.categoria, []).append({
                    'emenda': emenda,
                    'contrib_detail': contrib_detail,
                    'status': status_info['status']
                })
        
        final_remaining_deputy_verba = deputy.total_verba_disponivel - actual_spent_by_deputy

        print("\n" + "═"*60)
        print(f"DETALHES DO DEPUTADO: {deputy.name} (ID: {deputy.id})")
        print("═"*60 + "\n")

        if deputy.profile:
            print("\n  >> PERFIL DO DEPUTADO <<\n")
            print(f"    {deputy.profile}\n")
            print("  " + "─"*56 + "\n")
        else:
            print("\n  >> PERFIL DO DEPUTADO <<\n")
            print("    (Não informado)\n")
            print("  " + "─"*56 + "\n")

        print(f"\n  >> INFORMAÇÕES FINANCEIRAS GERAIS <<\n")
        print(f"    Verba Total Disponível:           R${deputy.total_verba_disponivel:,.2f}")
        print(f"    Verba Alocada por Categorias (Intenção): R${deputy.get_allocated_total():,.2f}")
        print(f"    Verba Remanescente (para Alocação Livre): R${deputy.get_remaining_verba():,.2f}\n")
        print(f"    ------------------------------------------")
        print(f"    Verba Efetivamente Usada em Emendas:  R${actual_spent_by_deputy:,.2f}")
        print(f"    Verba Final Remanescente do Deputado: R${final_remaining_deputy_verba:,.2f}\n")
        print(f"    Precisa de Realocação: {'Sim' if deputy.needs_reallocation else 'Não'}\n") 

        print("\n  >> INTENÇÃO DE ALOCAÇÃO POR CATEGORIA <<\n")
        if deputy.allocated_by_category:
            for cat, val in deputy.allocated_by_category.items():
                print(f"    - {cat}: R${val:,.2f}")
        else:
            print("    Nenhuma verba alocada por categoria como intenção.\n")

        print("\n  >> INCLINAÇÃO POR CATEGORIA <<\n")
        if deputy.inclinacao_por_categoria:
            total_inclination = sum(deputy.inclinacao_por_categoria.values())
            print(f"    Total de Pontos de Inclinação Distribuídos: {total_inclination}/10 ({total_inclination*10:.2f}% do total)\n")
            for cat, score in deputy.inclinacao_por_categoria.items():
                print(f"    - {cat}: {score}/10 ({score*10:.2f}% da inclinação total do deputado)")
        else:
            print("    Nenhuma inclinação por categoria configurada.\n")

        print("\n  >> EMENDAS CONTRIBUÍDAS <<\n")
        if contributions_by_category_for_display:
            for category in sorted(contributions_by_category_for_display.keys()):
                print(f"    ▶ Categoria: {category}\n")
                for contrib_info in contributions_by_category_for_display[category]:
                    emenda = contrib_info['emenda']
                    contrib_detail = contrib_info['contrib_detail']
                    total_contrib = contrib_detail['total']
                    from_alloc = contrib_detail['from_allocated_intention']
                    from_free = contrib_detail['from_free_verba']
                    
                    percent_of_emenda = (total_contrib / emenda.valor_necessario) * 100 if emenda.valor_necessario > 0 else 0

                    print(f"      - Emenda: '{emenda.description}' (ID: {emenda.id})")
                    print(f"        Valor Necessário da Emenda: R${emenda.valor_necessario:,.2f}")
                    print(f"        Contribuição deste Deputado: R${total_contrib:,.2f} ({percent_of_emenda:.2f}% da emenda)")
                    if from_alloc > 0:
                        print(f"          (Da Alocação por Categoria: R${from_alloc:,.2f})")
                    if from_free > 0:
                        print(f"          (Da Verba Livre: R${from_free:,.2f})")
                    print(f"        Status Final da Emenda: {contrib_info['status']}\n")
        else:
            print("    Este deputado não contribuiu para nenhuma emenda até o momento.\n")

        print("═"*60 + "\n")
        
        # --- SEÇÃO DE GRÁFICOS (JSON) ---
        print("\n" + "═"*80)
        print("DADOS PARA GRÁFICOS (FORMATO JSON)")
        print("═"*80)

        # Gráfico 1: Verba Alocada por Categoria (Intenção)
        allocated_verba_chart_json = self._generate_allocated_verba_chart_json(deputy)
        if allocated_verba_chart_json:
            print("\n### Gráfico 1: Verba Alocada por Categoria (Intenção) ###")
            print(json.dumps(allocated_verba_chart_json, indent=2, ensure_ascii=False))
        else:
            print("\n### Gráfico 1: Verba Alocada por Categoria (Intenção) - Sem dados ###")

        # Gráfico 2: Pontos de Inclinação por Categoria
        inclination_chart_json = self._generate_inclination_chart_json(deputy)
        if inclination_chart_json:
            print("\n### Gráfico 2: Pontos de Inclinação por Categoria ###")
            print(json.dumps(inclination_chart_json, indent=2, ensure_ascii=False))
        else:
            print("\n### Gráfico 2: Pontos de Inclinação por Categoria - Sem dados ###")

        # Gráfico 3: Verba Efetivamente Contribuída para Emendas (por Categoria)
        contributed_emendas_chart_json = self._generate_contributed_emendas_chart_json(contributions_by_category_for_display)
        if contributed_emendas_chart_json:
            print("\n### Gráfico 3: Verba Efetivamente Contribuída para Emendas (por Categoria) ###")
            print(json.dumps(contributed_emendas_chart_json, indent=2, ensure_ascii=False))
        else:
            print("\n### Gráfico 3: Verba Efetivamente Contribuída para Emendas (por Categoria) - Sem dados ###")
        
        print("═"*80 + "\n")

        input("Pressione Enter para voltar ao menu de Gerenciar Deputados...\n")

    # --- Opções do Menu ---

    def _menu_cadastro_deputados(self):
        while True:
            self._clear_screen()
            print("--- GERENCIAR DEPUTADOS ---")
            print("1. Cadastrar Novo Deputado")
            print("2. Visualizar Detalhes de Deputado") 
            print("3. Alterar Dados do Deputado") 
            print("4. Listar Todos os Deputados")     
            print("5. Distribuir Verba por Categoria para Deputado")
            print("6. Configurar Inclinação por Categoria")
            print("7. Excluir Deputado")
            print("8. Voltar ao Menu Principal") 
            choice = self._get_input("Escolha uma opção: ", int, lambda x: 1 <= x <= 8) 

            if choice == 1:
                self._clear_screen()
                name = self._get_input("Nome do Deputado: ")
                verba = self._get_input("Verba Total Disponível (R$): ", float, lambda x: x >= 0)
                profile_text = self._get_input("Perfil do Deputado (Opcional): ", str) 
                
                if profile_text == "":
                    profile_text = None
                
                deputy = self.deputy_manager.add_deputy(name, verba, profile=profile_text)
                print(f"Deputado '{deputy.name}' (ID: {deputy.id}) cadastrado com sucesso!")
            elif choice == 2: 
                self._clear_screen()
                if self._display_deputy_selection_list(): 
                    deputy_id = self._get_input("Digite o ID do deputado para visualizar os detalhes: ", int)
                    self._display_single_deputy_details(deputy_id)
                else:
                    input("\nPressione Enter para continuar...") 
            elif choice == 3: 
                self._clear_screen()
                if not self._display_deputy_selection_list():
                    input("\nPressione Enter para continuar...")
                    continue
                
                deputy_id = self._get_input("Digite o ID do deputado para alterar: ", int)
                deputy = self.deputy_manager.get_deputy_by_id(deputy_id)
                if not deputy:
                    print("Deputado não encontrado.")
                    input("\nPressione Enter para continuar...")
                    continue

                self._clear_screen()
                print(f"--- ALTERAR DADOS DO DEPUTADO: {deputy.name} (ID: {deputy.id}) ---")
                print("Deixe o campo em branco para manter o valor atual. Digite 'limpar' para remover perfis.")

                new_name = self._get_input_optional("Novo Nome", deputy.name)
                
                new_verba = self._get_input_optional("Nova Verba Total Disponível (R$)", deputy.total_verba_disponivel, type_func=float, validation_func=lambda x: x >= 0)
                
                new_profile = self._get_input_optional("Novo Perfil do Deputado (Opcional)", deputy.profile)
                
                success, message, old_total_verba_for_comparison = self.deputy_manager.update_deputy(
                    deputy.id, new_name, new_verba, new_profile
                )
                
                print(f"\n{message}")
                if success and not math.isclose(old_total_verba_for_comparison, new_verba):
                    print("\n!!! ATENÇÃO: A verba total do deputado foi alterada.")
                    print("             Este deputado foi marcado para uma futura redistribuição de verbas.")
                    print("             Você deve executar a opção 'Otimizar Distribuição de Verbas' no menu principal para aplicar as mudanças. !!!")

            elif choice == 4: 
                self._clear_screen()
                self._display_deputies()
            elif choice == 5: 
                self._clear_screen()
                if self._display_deputy_selection_list():
                    deputy_id = self._get_input("Digite o ID do deputado para distribuir a verba por categoria: ", int)
                    deputy = self.deputy_manager.get_deputy_by_id(deputy_id)
                    if deputy:
                        self._clear_screen()
                        print(f"--- DISTRIBUIR VERBA PARA DEPUTADO: {deputy.name} (ID: {deputy.id}) ---")
                        print(f"Verba Total Disponível: R${deputy.total_verba_disponivel:,.2f}")
                        print(f"Verba Já Alocada (Intenção): R${deputy.get_allocated_total():,.2f}")
                        print(f"Verba Remanescente para Distribuição Livre: R${deputy.get_remaining_verba():,.2f}\n")

                        new_allocations = deputy.allocated_by_category.copy() 
                        
                        # NOVO: Exibe as alocações atuais antes de iniciar o loop
                        if new_allocations:
                            print("\nAlocações por Categoria Atuais (Intenção):")
                            for cat, val in sorted(new_allocations.items()): 
                                print(f"  - {cat}: R${val:,.2f}")
                            print("------------------------------------------")
                        else:
                            print("\nNenhuma alocação por categoria definida ainda.")

                        print("\nDigite a distribuição da verba por categoria (deixe a categoria em branco para FINALIZAR):\n")
                        print("  (Você pode ajustar categorias existentes ou adicionar novas. Digite 0 para remover uma categoria.)")
                        
                        while True:
                            category = self._select_or_create_category("Selecione ou digite a Categoria", allow_empty_to_finish=True) 
                            if category is None: 
                                break
                            
                            current_amount_for_category = new_allocations.get(category, 0.0)
                            amount_prompt = f"Valor para '{category}' (R$) (Atual: R${current_amount_for_category:,.2f}): "
                            amount = self._get_input(amount_prompt, float, lambda x: x >= 0)
                            
                            temp_allocations = new_allocations.copy() 
                            if math.isclose(amount, 0):
                                if category in temp_allocations:
                                    del temp_allocations[category]
                            else:
                                temp_allocations[category] = amount 
                            
                            current_temp_total = sum(temp_allocations.values())

                            if current_temp_total > deputy.total_verba_disponivel and not math.isclose(current_temp_total, deputy.total_verba_disponivel):
                                print(f"AVISO: A soma alocada até agora (R${current_temp_total:,.2f}) excederá a verba total disponível do deputado (R${deputy.total_verba_disponivel:,.2f}). Por favor, ajuste.")
                                continue 
                            
                            new_allocations = temp_allocations 
                            current_allocated_sum = sum(new_allocations.values())
                            print(f"Total alocado (Intenção) até agora: R${current_allocated_sum:,.2f}. Remanescente para distribuição livre: R${deputy.total_verba_disponivel - current_allocated_sum:,.2f}")
                        
                        if not new_allocations and not deputy.allocated_by_category: 
                            print("Nenhuma alteração na alocação de verbas foi feita.")
                        else:
                            save_confirm = self._get_input("Deseja salvar estas alterações na distribuição de verbas (intenção)? (s/n): ").lower()
                            if save_confirm == 's':
                                success, message = self.deputy_manager.update_deputy_allocations(deputy_id, new_allocations)
                                print(f"\n{message}")
                                if success: 
                                    deputy.needs_reallocation = True 
                                    self.deputy_manager.data_manager.save_deputies(self.deputy_manager.deputies) 
                                    print("!!! ATENÇÃO: As intenções de verba foram alteradas. Este deputado foi marcado para uma futura redistribuição de verbas.")
                                    print("             Você deve executar a opção 'Otimizar Distribuição de Verbas' no menu principal para aplicar as mudanças. !!!")
                            else:
                                print("Alterações descartadas. Nenhuma distribuição de verbas foi salva.")
                    else:
                        print("Deputado não encontrado.")
                else: 
                    input("\nPressione Enter para continuar...")
            elif choice == 6: 
                self._clear_screen()
                if self._display_deputy_selection_list():
                    deputy_id = self._get_input("Digite o ID do deputado para configurar a inclinação por categoria: ", int)
                    deputy = self.deputy_manager.get_deputy_by_id(deputy_id)
                    if deputy:
                        self._clear_screen()
                        print(f"--- CONFIGURAR INCLINAÇÃO POR CATEGORIA PARA: {deputy.name} (ID: {deputy.id}) ---")
                        print("A soma das inclinações por categoria não pode exceder 10 pontos.")
                        
                        new_inclinations = deputy.inclinacao_por_categoria.copy()
                        current_total_inclination_score = sum(new_inclinations.values())

                        if new_inclinations:
                            print("\nInclinações atuais:")
                            for cat, score in new_inclinations.items():
                                print(f"  - {cat}: {score}/10 ({score*10:.2f}% da inclinação total do deputado)")
                        else:
                            print("\nNenhuma inclinação configurada ainda.")
                        
                        print(f"\nPontos totais distribuídos: {current_total_inclination_score}/10 ({current_total_inclination_score*10:.2f}% do total). Pontos restantes para distribuir: {10 - current_total_inclination_score}.")
                        print("\nDigite a inclinação por categoria (deixe a categoria em branco para FINALIZAR):\n")
                        print("  (Você pode ajustar categorias existentes ou adicionar novas. Digite 0 para remover uma categoria.)")

                        while True:
                            categoria = self._select_or_create_category("Selecione ou digite a Categoria para inclinação", allow_empty_to_finish=True)
                            if categoria is None: 
                                break
                            
                            score = self._get_input(f"Inclinação para '{categoria}' (1-10, ou 0 para remover): ", int, lambda x: 0 <= x <= 10)
                            
                            temp_inclinations = new_inclinations.copy()
                            if score == 0:
                                if categoria in temp_inclinations:
                                    del temp_inclinations[categoria]
                            else:
                                temp_inclinations[categoria] = score
                            
                            temp_total_score = sum(temp_inclinations.values())

                            if temp_total_score > 10:
                                print(f"AVISO: A soma das inclinações ({temp_total_score}) excederá o limite de 10 pontos. Pontos restantes: {10 - current_total_inclination_score}. Por favor, ajuste.")
                                continue
                            
                            new_inclinations = temp_inclinations
                            current_total_inclination_score = sum(new_inclinations.values())
                            
                            print(f"Pontos totais distribuídos: {current_total_inclination_score}/10 ({current_total_inclination_score*10:.2f}% do total). Pontos restantes para distribuir: {10 - current_total_inclination_score}.")
                        
                        if not new_inclinations and not deputy.inclinacao_por_categoria: 
                             print("Nenhuma alteração na inclinação por categorias foi feita.")
                        else:
                            save_confirm = self._get_input("Deseja salvar estas alterações nas inclinações por categoria? (s/n): ").lower()
                            if save_confirm == 's':
                                success, message = self.deputy_manager.update_deputy_inclinations(deputy_id, new_inclinations)
                                print(f"\n{message}")
                                if success: 
                                    deputy.needs_reallocation = True 
                                    self.deputy_manager.data_manager.save_deputies(self.deputy_manager.deputies) 
                                    print("!!! ATENÇÃO: As inclinações foram alteradas. Este deputado foi marcado para uma futura redistribuição de verbas.")
                                    print("             Você deve executar a opção 'Otimizar Distribuição de Verbas' no menu principal para aplicar as mudanças. !!!")
                            else:
                                print("Alterações descartadas. Nenhuma inclinação por categoria foi salva.")
                    else:
                        print("Deputado não encontrado.")
                else: 
                    input("\nPressione Enter para continuar...")
            elif choice == 7: 
                self._clear_screen()
                if self._display_deputy_selection_list():
                    deputy_id = self._get_input("Digite o ID do deputado para excluir: ", int)
                    success, message = self.deputy_manager.delete_deputy(deputy_id)
                    print(message)
                else: 
                    input("\nPressione Enter para continuar...")
            else: 
                break
            input("Pressione Enter para continuar...")

    def _menu_cadastro_emendas(self):
        while True:
            self._clear_screen()
            print("--- GERENCIAR EMENDAS PARLAMENTARES ---")
            print("1. Cadastrar Nova Emenda")
            print("2. Listar Emendas")
            print("3. Excluir Emenda")
            print("4. Voltar ao Menu Principal")
            choice = self._get_input("Escolha uma opção: ", int, lambda x: 1 <= x <= 4)

            if choice == 1:
                self._clear_screen()
                description = self._get_input("Descrição da Emenda: ")
                valor = self._get_input("Valor Necessário (R$): ", float, lambda x: x > 0)
                categoria = self._select_or_create_category("Selecione ou digite a Categoria da Emenda", allow_empty_to_finish=False)
                if categoria is None: 
                    print("Cadastro de emenda cancelado.")
                else:
                    emenda = self.emenda_manager.add_emenda(description, valor, categoria)
                    print(f"Emenda '{emenda.description}' (ID: {emenda.id}) cadastrada com sucesso!")
                    
                    for deputy in self.deputy_manager.list_deputies():
                        deputy.needs_reallocation = True
                    self.deputy_manager.data_manager.save_deputies(self.deputy_manager.deputies) 
                    
                    print("!!! ATENÇÃO: Uma nova emenda foi adicionada. Todos os deputados foram marcados para uma futura redistribuição de verbas.")
                    print("             Você deve executar a opção 'Otimizar Distribuição de Verbas' no menu principal para aplicar as mudanças. !!!")
            elif choice == 2:
                self._clear_screen()
                self._display_emendas()
            elif choice == 3:
                self._clear_screen() # CORRIGIDO: Era _clear_clear_screen
                self._display_emendas()
                emenda_id = self._get_input("Digite o ID da emenda para excluir: ", int)
                success, message = self.emenda_manager.delete_emenda(emenda_id)
                print(message)
                if success: 
                    for deputy in self.deputy_manager.list_deputies():
                        deputy.needs_reallocation = True
                    self.deputy_manager.data_manager.save_deputies(self.deputy_manager.deputies) 
                    print("!!! ATENÇÃO: Uma emenda foi excluída. Todos os deputados foram marcados para uma futura redistribuição de verbas.")
                    print("             Você deve executar a opção 'Otimizar Distribuição de Verbas' no menu principal para aplicar as mudanças. !!!")
            else: 
                break
            input("Pressione Enter para continuar...")

    def _menu_otimizar_distribuicao(self): 
        self._clear_screen()
        deputies_needing_reallocation = self.deputy_manager.get_deputies_needing_reallocation()
        
        if not self.deputy_manager.list_deputies():
            print("Nenhum deputado cadastrado para otimizar distribuição.")
            input("\nPressione Enter para continuar...")
            return
        if not self.emenda_manager.list_emendas():
            print("Nenhuma emenda cadastrada para otimizar distribuição.")
            input("Pressione ENTER para continuar...") 
            return

        print("--- OTIMIZAR DISTRIBUIÇÃO DE VERBAS ---")
        if deputies_needing_reallocation:
            print("\nDeputados marcados para realocação:")
            for d in deputies_needing_reallocation:
                print(f"- ID: {d.id} | Nome: {d.name}")
            print("\n")
            
            while True:
                choice = self._get_input("Deseja realizar uma otimização [G]eral ou [P]arcial (apenas para deputados marcados)? (G/P): ").upper()
                if choice == 'G':
                    print("\nRealizando otimização geral...")
                    self.optimizer.perform_full_redistribution()
                    break
                elif choice == 'P':
                    print("\nRealizando otimização parcial para deputados marcados...")
                    deputy_ids_to_reallocate = [d.id for d in deputies_needing_reallocation]
                    self.optimizer.perform_partial_redistribution(deputy_ids_to_reallocate)
                    break
                else:
                    print("Opção inválida. Por favor, escolha G ou P.")
        else:
            print("Nenhum deputado marcado para realocação específica.")
            print("Deseja realizar uma otimização [G]eral de todas as verbas, ou [C]ancelar? (G/C): ")
            while True:
                choice = self._get_input("Escolha uma opção: ").upper()
                if choice == 'G':
                    print("\nRealizando otimização geral...")
                    self.optimizer.perform_full_redistribution()
                    break
                elif choice == 'C':
                    print("Otimização cancelada.")
                    break
                else:
                    print("Opção inválida. Por favor, escolha G ou C.")
        
        input("\nPressione Enter para continuar...")


    def _visualizar_relatorios(self):
        self._clear_screen()
        if not self.deputy_manager.list_deputies() or not self.emenda_manager.list_emendas():
            print("É necessário cadastrar deputados e emendas para gerar um relatório.")
        else:
            report = self.report_generator.generate_report()
            print(report)
            
            input("\nPressione Enter para ver os dados do gráfico (JSON)...\n")
            
            summary_chart_data = self.report_generator.get_summary_for_chart()
            print("\n" + "═"*80)
            print("DADOS PARA GRÁFICO DE PERCENTUAL DE USO (FORMATO JSON)")
            print("═"*80)
            print(json.dumps(summary_chart_data, indent=2, ensure_ascii=False)) 
        input("\nPressione Enter para continuar...\n")

    def run(self):
        while True:
            self._clear_screen()
            print("═"*40)
            print("SISTEMA DE GERENCIAMENTO DE EMENDAS")
            print("═"*40)
            print("1. Gerenciar Deputados")
            print("2. Gerenciar Emendas Parlamentares")
            print("3. Otimizar Distribuição de Verbas") 
            print("4. Gerar Relatório de Distribuição") 
            print("5. Sair") 
            print("═"*40)
            choice = self._get_input("Escolha uma opção: ", int, lambda x: 1 <= x <= 5) 

            if choice == 1:
                self._menu_cadastro_deputados()
            elif choice == 2:
                self._menu_cadastro_emendas()
            elif choice == 3: 
                self._menu_otimizar_distribuicao()
            elif choice == 4: 
                self._visualizar_relatorios()
            elif choice == 5: 
                print("Saindo da aplicação. Até logo!")
                break

# --- Inicialização da Aplicação ---
if __name__ == "__main__":
    app = App()
    app.run()