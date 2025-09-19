import streamlit as st
import json
import math 
import os
import plotly.graph_objects as go 

# Importar suas classes de gerenciamento e modelos
from DataManager import DataManager
from Deputy import Deputy
from Emenda import Emenda
from DeputyManager import DeputyManager
from EmendaManager import EmendaManager
from CategoryManager import CategoryManager
from AllocationOptimizer import AllocationOptimizer
from ReportGenerator import ReportGenerator

# --- Funções Auxiliares para o Streamlit ---
def initialize_session_state():
    """Inicializa os managers e o estado da sessão, garantindo que o DataManager seja compartilhado."""
    try:
        if 'data_manager' not in st.session_state:
            st.session_state.data_manager = DataManager()
        
        if 'category_manager' not in st.session_state:
            st.session_state.category_manager = CategoryManager(st.session_state.data_manager)

        if 'deputy_manager' not in st.session_state:
            st.session_state.deputy_manager = DeputyManager(st.session_state.data_manager)

        if 'emenda_manager' not in st.session_state:
            st.session_state.emenda_manager = EmendaManager(st.session_state.data_manager)

        if 'optimizer' not in st.session_state:
            st.session_state.optimizer = AllocationOptimizer(
                st.session_state.deputy_manager, 
                st.session_state.emenda_manager,
                st.session_state.data_manager 
            )

        if 'report_generator' not in st.session_state:
            st.session_state.report_generator = ReportGenerator(
                st.session_state.deputy_manager, 
                st.session_state.emenda_manager
            )
            
    except Exception as e:
        st.error("Ocorreu um erro crítico durante a inicialização da aplicação.")
        st.exception(e) 
        st.stop() 

# --- Funções para Renderizar as Páginas (Adaptadas para Streamlit) ---

def home_page():
    st.title("Sistema de Gerenciamento de Emendas Parlamentares")
    st.write("""
    Bem-vindo ao sistema de gerenciamento de emendas! 
    Utilize o menu lateral para navegar pelas funcionalidades:
    - **Gerenciar Deputados:** Cadastre, visualize, edite e configure deputados.
    - **Gerenciar Emendas:** Cadastre, visualize e exclua emendas.
    - **Gerenciar Categorias:** Adicione, liste e exclua categorias de emendas.
    - **Otimizar Distribuição:** Execute a otimização das verbas.
    - **Relatórios:** Visualize os resultados da distribuição.
    """)
    st.image("https://images.unsplash.com/photo-1549490159-839556191c78?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", caption="Justiça e Transparência") 
    st.info("Para começar, selecione uma opção no menu à esquerda.")

def manage_deputies_page():
    st.title("Gerenciar Deputados")

    menu_deputies = ["Listar Todos", "Cadastrar Novo", "Visualizar/Editar Detalhes", "Distribuir Verba por Categoria", "Configurar Inclinação", "Excluir"]
    # Usa st.session_state para manter a seleção do submenu de deputados
    if 'deputy_menu_choice' not in st.session_state:
        st.session_state['deputy_menu_choice'] = "Listar Todos"

    choice = st.sidebar.selectbox("Opções de Deputados", menu_deputies, key='deputy_menu_choice') 

    if choice == "Listar Todos":
        display_all_deputies_streamlit()
    elif choice == "Cadastrar Novo":
        add_new_deputy_streamlit()
    elif choice == "Visualizar/Editar Detalhes":
        view_edit_deputy_details_streamlit()
    elif choice == "Distribuir Verba por Categoria":
        distribute_deputy_funds_by_category_streamlit()
    elif choice == "Configurar Inclinação":
        configure_deputy_inclinations_streamlit()
    elif choice == "Excluir":
        delete_deputy_streamlit()

def display_all_deputies_streamlit():
    st.header("Lista de Todos os Deputados")
    deputies = st.session_state.deputy_manager.list_deputies()
    if not deputies:
        st.info("Nenhum deputado cadastrado.")
        return

    for d in deputies:
        st.subheader(f"Deputado: {d.name} (ID: {d.id})")
        st.write(f"Verba Total Disponível: R${d.total_verba_disponivel:,.2f}")
        st.write(f"Intenção de Alocação (Categorias): R${d.get_allocated_total():,.2f}")
        st.write(f"Verba Remanescente (Para Alocação Livre): R${d.get_remaining_verba():,.2f}")
        st.write(f"Verba Efetivamente Gasta em Emendas: R${d.actual_spent_amount:,.2f}")
        st.write(f"Precisa de Realocação: {'Sim' if d.needs_reallocation else 'Não'}")

        if d.profile:
            st.markdown(f"**Perfil:**\n{d.profile}")
        else:
            st.write("Perfil: (Não informado)")

        if d.allocated_by_category:
            st.write("**Alocações por Categoria (Intenção):**")
            for cat, val in d.allocated_by_category.items():
                st.write(f"  - {cat}: R${val:,.2f}")
        
        if d.inclinacao_por_categoria:
            st.write(f"**Inclinação por Categoria (Total: {sum(d.inclinacao_por_categoria.values())}/10):**")
            for cat, score in d.inclinacao_por_categoria.items():
                st.write(f"  - {cat}: {score}/10 ({score*10:.2f}% da inclinação total do deputado)")
        else:
            st.write("Nenhuma inclinação por categoria configurada.")
        st.markdown("---")

def add_new_deputy_streamlit():
    st.header("Cadastrar Novo Deputado")

    if st.session_state.get('show_deputy_add_options', False):
        st.success(st.session_state.get('deputy_add_success_message', "Deputado cadastrado com sucesso!"))
        st.warning(st.session_state.get('deputy_add_warning_message', "")) 
        
        st.subheader("O que você gostaria de fazer agora?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cadastrar Outro Deputado"):
                del st.session_state['show_deputy_add_options']
                if 'deputy_add_success_message' in st.session_state: del st.session_state['deputy_add_success_message']
                if 'deputy_add_warning_message' in st.session_state: del st.session_state['deputy_add_warning_message']
                st.rerun() 
        with col2:
            if st.button("Ver Lista de Deputados"):
                # Define flags temporárias para a navegação na próxima execução do script
                st.session_state['__nav_target_main_menu'] = "Gerenciar Deputados"
                st.session_state['__nav_target_deputy_menu'] = "Listar Todos"
                if 'show_deputy_add_options' in st.session_state: del st.session_state['show_deputy_add_options']
                if 'deputy_add_success_message' in st.session_state: del st.session_state['deputy_add_success_message']
                if 'deputy_add_warning_message' in st.session_state: del st.session_state['deputy_add_warning_message']
                st.rerun() 
    else: 
        with st.form("add_deputy_form"):
            name = st.text_input("Nome do Deputado", key="new_deputy_name_input") 
            verba = st.number_input("Verba Total Disponível (R$)", min_value=0.0, format="%.2f", key="new_deputy_verba_input")
            profile_text = st.text_area("Perfil do Deputado (Opcional)", key="new_deputy_profile_input")
            
            submitted = st.form_submit_button("Cadastrar Deputado")

            if submitted:
                if name and verba is not None:
                    profile_to_save = profile_text if profile_text.strip() else None
                    deputy = st.session_state.deputy_manager.add_deputy(name, verba, profile=profile_to_save)
                    st.session_state['deputy_add_success_message'] = f"Deputado '{deputy.name}' (ID: {deputy.id}) cadastrado com sucesso!"
                    
                    for d in st.session_state.deputy_manager.list_deputies():
                        d.needs_reallocation = True
                    st.session_state.data_manager.save_deputies(st.session_state.deputy_manager.deputies)
                    st.session_state['deputy_add_warning_message'] = "Um novo deputado foi adicionado. Todos os deputados foram marcados para uma futura redistribuição de verbas. Você deve executar a opção 'Otimizar Distribuição de Verbas' para aplicar as mudanças."
                    
                    st.session_state['show_deputy_add_options'] = True
                    st.rerun() 
                else:
                    st.error("Nome e Verba são campos obrigatórios.")


def view_edit_deputy_details_streamlit():
    st.header("Visualizar/Editar Detalhes de Deputado")
    deputies = st.session_state.deputy_manager.list_deputies()
    if not deputies:
        st.info("Nenhum deputado cadastrado para visualizar/editar.")
        return

    deputy_options = {f"{d.name} (ID: {d.id})": d.id for d in deputies}
    selected_deputy_display = st.selectbox("Selecione um Deputado", list(deputy_options.keys()), key='select_deputy_edit')
    
    if selected_deputy_display:
        selected_deputy_id = deputy_options[selected_deputy_display]
        deputy = st.session_state.deputy_manager.get_deputy_by_id(selected_deputy_id)

        if deputy:
            st.subheader(f"Detalhes de: {deputy.name}")

            with st.form(f"edit_deputy_form_{deputy.id}"):
                new_name = st.text_input("Nome", value=deputy.name, key=f"edit_name_{deputy.id}")
                new_verba = st.number_input("Verba Total Disponível (R$)", value=float(deputy.total_verba_disponivel), min_value=0.0, format="%.2f", key=f"edit_verba_{deputy.id}")
                new_profile = st.text_area("Perfil do Deputado", value=deputy.profile if deputy.profile else "", key=f"edit_profile_{deputy.id}")
                
                edit_submitted = st.form_submit_button("Atualizar Dados do Deputado")

                if edit_submitted:
                    old_total_verba = deputy.total_verba_disponivel
                    profile_to_save = new_profile if new_profile.strip() else None

                    success, message, _ = st.session_state.deputy_manager.update_deputy(
                        deputy.id, new_name, new_verba, profile_to_save
                    )
                    
                    if success:
                        st.success(message)
                        if not math.isclose(old_total_verba, new_verba):
                            deputy.needs_reallocation = True
                            st.session_state.data_manager.save_deputies(st.session_state.deputy_manager.deputies)
                            st.warning("!!! ATENÇÃO: A verba total do deputado foi alterada. Este deputado foi marcado para uma futura redistribuição de verbas. Você deve executar a opção 'Otimizar Distribuição de Verbas' no menu principal para aplicar as mudanças. !!!")
                        st.rerun() 
                    else:
                        st.error(message)

            st.markdown("---")
            st.subheader("Informações Atuais do Deputado")
            st.write(f"ID: {deputy.id}")
            st.write(f"Nome: {deputy.name}")
            st.write(f"Verba Total Disponível: R${deputy.total_verba_disponivel:,.2f}")
            st.write(f"Verba Alocada por Categorias (Intenção): R${deputy.get_allocated_total():,.2f}")
            st.write(f"Verba Remanescente (para Alocação Livre): R${deputy.get_remaining_verba():,.2f}")
            st.write(f"Verba Efetivamente Usada em Emendas: R${deputy.actual_spent_amount:,.2f}")
            st.write(f"Precisa de Realocação: {'Sim' if deputy.needs_reallocation else 'Não'}")

            if deputy.profile:
                st.markdown(f"**Perfil:**\n{deputy.profile}")
            else:
                st.write("Perfil: (Não informado)")

            st.write("**Intenção de Alocação por Categoria:**")
            if deputy.allocated_by_category:
                for cat, val in deputy.allocated_by_category.items():
                    st.write(f"  - {cat}: R${val:,.2f}")
            else:
                st.write("Nenhuma verba alocada por categoria como intenção.")

            st.write("**Inclinação por Categoria:**")
            if deputy.inclinacao_por_categoria:
                total_inclination = sum(deputy.inclinacao_por_categoria.values())
                st.write(f"Total de Pontos de Inclinação Distribuídos: {total_inclination}/10")
                for cat, score in deputy.inclinacao_por_categoria.items():
                    st.write(f"  - {cat}: {score}/10 ({score*10:.2f}% da inclinação total do deputado)")
            else:
                st.write("Nenhuma inclinação por categoria configurada.")

            st.write("**Emendas Contribuídas:**")
            emenda_status_all, _, _, _ = st.session_state.report_generator._get_current_allocation_state()
            contributions_by_category_for_display = {}
            for emenda_id, status_info in emenda_status_all.items():
                if str(deputy.id) in status_info['contributors']: # IDs são strings nas chaves de contributors
                    contrib_detail = status_info['contributors'][str(deputy.id)]
                    emenda = status_info['emenda']
                    contributions_by_category_for_display.setdefault(emenda.categoria, []).append({
                        'emenda': emenda,
                        'contrib_detail': contrib_detail,
                        'status': status_info['status']
                    })

            if contributions_by_category_for_display: 
                for category in sorted(contributions_by_category_for_display.keys()):
                    st.markdown(f"**▶ Categoria: {category}**")
                    for contrib_info in contributions_by_category_for_display[category]:
                        emenda = contrib_info['emenda']
                        contrib_detail = contrib_info['contrib_detail']
                        total_contrib = contrib_detail['total']
                        from_alloc = contrib_detail['from_allocated_intention']
                        from_free = contrib_detail['from_free_verba']
                        
                        percent_of_emenda = (total_contrib / emenda.valor_necessario) * 100 if emenda.valor_necessario > 0 else 0

                        st.write(f"  - Emenda: '{emenda.description}' (ID: {emenda.id})")
                        st.write(f"    Valor Necessário da Emenda: R${emenda.valor_necessario:,.2f}")
                        st.write(f"    Contribuição deste Deputado: R${total_contrib:,.2f} ({percent_of_emenda:.2f}% da emenda)")
                        if from_alloc > 0:
                            st.write(f"      (Da Alocação por Categoria: R${from_alloc:,.2f})")
                        if from_free > 0:
                            st.write(f"      (Da Verba Livre: R${from_free:,.2f})")
                        st.write(f"    Status Final da Emenda: {contrib_info['status']}")
            else:
                st.write("Este deputado não contribuiu para nenhuma emenda até o momento.")

            st.subheader("Gráficos de Distribuição")
            
            # Gráfico 1: Verba Alocada por Categoria (Intenção)
            allocated_verba_chart_json = generate_allocated_verba_chart_json_streamlit(deputy)
            if allocated_verba_chart_json:
                st.markdown("### Gráfico 1: Verba Alocada por Categoria (Intenção)")
                labels = [s['name'] for s in allocated_verba_chart_json['series']]
                values = [s['data'] for s in allocated_verba_chart_json['series']]
                fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
                fig.update_layout(title_text=allocated_verba_chart_json['title']['text'])
                st.plotly_chart(fig, use_container_width=True)
                st.json(allocated_verba_chart_json) 
            else:
                st.info("Gráfico 1: Verba Alocada por Categoria (Intenção) - Sem dados para exibir.")

            # Gráfico 2: Pontos de Inclinação por Categoria
            inclination_chart_json = generate_inclination_chart_json_streamlit(deputy)
            if inclination_chart_json:
                st.markdown("### Gráfico 2: Pontos de Inclinação por Categoria")
                labels = [s['name'] for s in inclination_chart_json['series']]
                values = [s['data'] for s in inclination_chart_json['series']]
                fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
                fig.update_layout(title_text=inclination_chart_json['title']['text'])
                st.plotly_chart(fig, use_container_width=True)
                st.json(inclination_chart_json) 
            else:
                st.info("Gráfico 2: Pontos de Inclinação por Categoria - Sem dados para exibir.")

            # Gráfico 3: Verba Efetivamente Contribuída para Emendas (por Categoria)
            contributed_emendas_chart_json = generate_contributed_emendas_chart_json_streamlit(deputy, contributions_by_category_for_display)
            if contributed_emendas_chart_json:
                st.markdown("### Gráfico 3: Verba Efetivamente Contribuída para Emendas (por Categoria)")
                labels = [s['name'] for s in contributed_emendas_chart_json['series']]
                values = [s['data'] for s in contributed_emendas_chart_json['series']]
                fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
                fig.update_layout(title_text=contributed_emendas_chart_json['title']['text'])
                st.plotly_chart(fig, use_container_width=True)
                st.json(contributed_emendas_chart_json) 
            else:
                st.info("Gráfico 3: Verba Efetivamente Contribuída para Emendas (por Categoria) - Sem dados para exibir.")


def distribute_deputy_funds_by_category_streamlit():
    st.header("Distribuir Verba por Categoria para Deputado")
    deputies = st.session_state.deputy_manager.list_deputies()
    if not deputies:
        st.info("Nenhum deputado cadastrado.")
        return

    deputy_options = {f"{d.name} (ID: {d.id})": d.id for d in deputies}
    selected_deputy_display = st.selectbox("Selecione um Deputado", list(deputy_options.keys()), key='select_deputy_distribute')

    if selected_deputy_display:
        selected_deputy_id = deputy_options[selected_deputy_display]
        deputy = st.session_state.deputy_manager.get_deputy_by_id(selected_deputy_id)

        if deputy:
            st.write(f"Verba Total Disponível: R${deputy.total_verba_disponivel:,.2f}")
            st.write(f"Verba Já Alocada (Intenção): R${deputy.get_allocated_total():,.2f}")
            st.write(f"Verba Remanescente para Distribuição Livre: R${deputy.get_remaining_verba():,.2f}")

            new_allocations = deputy.allocated_by_category.copy()

            if new_allocations:
                st.subheader("Alocações por Categoria Atuais (Intenção):")
                for cat, val in sorted(new_allocations.items()):
                    st.write(f"  - {cat}: R${val:,.2f}")
            else:
                st.info("Nenhuma alocação por categoria definida ainda.")

            st.markdown("---")
            st.subheader("Definir Novas Alocações/Ajustes")
            
            categories_available = st.session_state.category_manager.list_categories()
            if not categories_available:
                st.warning("Nenhuma categoria cadastrada. Por favor, adicione categorias na seção 'Gerenciar Categorias'.")
                return

            st.write("Ajuste os valores para as categorias abaixo. Digite 0 para remover uma categoria da alocação.")
            
            updated_allocations = {}
            for cat in categories_available:
                current_value = new_allocations.get(cat, 0.0)
                new_value = st.number_input(f"Valor para '{cat}' (R$)", value=float(current_value), min_value=0.0, format="%.2f", key=f"alloc_{deputy.id}_{cat}")
                if new_value > 0: 
                    updated_allocations[cat] = new_value
            
            current_allocated_sum = sum(updated_allocations.values())
            st.info(f"Total alocado (Intenção) até agora: R${current_allocated_sum:,.2f}. Remanescente para distribuição livre: R${deputy.total_verba_disponivel - current_allocated_sum:,.2f}")

            if st.button("Salvar Alocações"):
                if current_allocated_sum > deputy.total_verba_disponivel and not math.isclose(current_allocated_sum, deputy.total_verba_disponivel):
                    st.error(f"AVISO: A soma alocada (R${current_allocated_sum:,.2f}) excede a verba total disponível do deputado (R${deputy.total_verba_disponivel:,.2f}). Por favor, ajuste.")
                else:
                    success, message = st.session_state.deputy_manager.update_deputy_allocations(deputy.id, updated_allocations)
                    if success:
                        deputy.needs_reallocation = True
                        st.session_state.data_manager.save_deputies(st.session_state.deputy_manager.deputies)
                        st.success(message)
                        st.warning("!!! ATENÇÃO: As intenções de verba foram alteradas. Este deputado foi marcado para uma futura redistribuição de verbas. Você deve executar a opção 'Otimizar Distribuição de Verbas' no menu principal para aplicar as mudanças. !!!")
                        st.rerun()
                    else:
                        st.error(message)

def configure_deputy_inclinations_streamlit():
    st.header("Configurar Inclinação por Categoria para Deputado")
    deputies = st.session_state.deputy_manager.list_deputies()
    if not deputies:
        st.info("Nenhum deputado cadastrado.")
        return

    deputy_options = {f"{d.name} (ID: {d.id})": d.id for d in deputies}
    selected_deputy_display = st.selectbox("Selecione um Deputado", list(deputy_options.keys()), key='select_deputy_inclination')

    if selected_deputy_display:
        selected_deputy_id = deputy_options[selected_deputy_display]
        deputy = st.session_state.deputy_manager.get_deputy_by_id(selected_deputy_id)

        if deputy:
            st.write(f"A soma das inclinações por categoria não pode exceder 10 pontos.")
            
            new_inclinations = deputy.inclinacao_por_categoria.copy()
            current_total_inclination_score = sum(new_inclinations.values())

            if new_inclinations:
                st.subheader("Inclinações Atuais:")
                for cat, score in new_inclinations.items():
                    st.write(f"  - {cat}: {score}/10 ({score*10:.2f}% da inclinação total do deputado)")
            else:
                st.info("Nenhuma inclinação configurada ainda.")
            
            st.info(f"Pontos totais distribuídos: {current_total_inclination_score}/10. Pontos restantes para distribuir: {10 - current_total_inclination_score}.")

            st.markdown("---")
            st.subheader("Definir Novas Inclinações/Ajustes")

            categories_available = st.session_state.category_manager.list_categories()
            if not categories_available:
                st.warning("Nenhuma categoria cadastrada. Por favor, adicione categorias na seção 'Gerenciar Categorias'.")
                return
            
            st.write("Ajuste as pontuações de inclinação para as categorias abaixo (0 para remover).")

            updated_inclinations = {}
            for cat in categories_available:
                current_score = new_inclinations.get(cat, 0)
                new_score = st.slider(f"Inclinação para '{cat}'", min_value=0, max_value=10, value=current_score, key=f"incl_{deputy.id}_{cat}", help="Pontuação de 0 a 10. 0 para remover a inclinação desta categoria.")
                if new_score > 0:
                    updated_inclinations[cat] = new_score
            
            current_total_score = sum(updated_inclinations.values())
            st.info(f"Pontos totais distribuídos agora: {current_total_score}/10.")

            if st.button("Salvar Inclinações"):
                if current_total_score > 10:
                    st.error(f"AVISO: A soma das inclinações ({current_total_score}) excede o limite de 10 pontos. Por favor, ajuste.")
                else:
                    success, message = st.session_state.deputy_manager.update_deputy_inclinations(deputy.id, updated_inclinations)
                    if success:
                        deputy.needs_reallocation = True
                        st.session_state.data_manager.save_deputies(st.session_state.deputy_manager.deputies)
                        st.success(message)
                        st.warning("!!! ATENÇÃO: As inclinações foram alteradas. Este deputado foi marcado para uma futura redistribuição de verbas. Você deve executar a opção 'Otimizar Distribuição de Verbas' no menu principal para aplicar as mudanças. !!!")
                        st.rerun()
                    else:
                        st.error(message)

def delete_deputy_streamlit():
    st.header("Excluir Deputado")
    deputies = st.session_state.deputy_manager.list_deputies()
    if not deputies:
        st.info("Nenhum deputado cadastrado.")
        return
    
    deputy_options = {f"{d.name} (ID: {d.id})": d.id for d in deputies}
    selected_deputy_display = st.selectbox("Selecione o Deputado para Excluir", list(deputy_options.keys()), key='select_deputy_delete')

    if selected_deputy_display:
        deputy_id_to_delete = deputy_options[selected_deputy_display]
        deputy_name = st.session_state.deputy_manager.get_deputy_by_id(deputy_id_to_delete).name

        st.warning(f"Você tem certeza que deseja excluir o deputado '{deputy_name}' (ID: {deputy_id_to_delete})?")
        if st.button(f"Confirmar Exclusão de {deputy_name}"):
            success, message = st.session_state.deputy_manager.delete_deputy(deputy_id_to_delete)
            if success:
                st.success(message)
                for d in st.session_state.deputy_manager.list_deputies():
                    d.needs_reallocation = True
                st.session_state.data_manager.save_deputies(st.session_state.deputy_manager.deputies)
                st.warning("Um deputado foi excluído. Todos os deputados foram marcados para uma futura redistribuição de verbas. Você deve executar a opção 'Otimizar Distribuição de Verbas' para aplicar as mudanças.")
                st.rerun()
            else:
                st.error(message)


def manage_emendas_page():
    st.title("Gerenciar Emendas Parlamentares")

    menu_emendas = ["Listar Todas", "Cadastrar Nova", "Excluir"]
    # Usa st.session_state para manter a seleção do submenu de emendas
    if 'emenda_menu_choice' not in st.session_state:
        st.session_state['emenda_menu_choice'] = "Listar Todas"

    choice = st.sidebar.selectbox("Opções de Emendas", menu_emendas, key='emenda_menu_choice')

    if choice == "Listar Todas":
        display_all_emendas_streamlit()
    elif choice == "Cadastrar Nova":
        add_new_emenda_streamlit()
    elif choice == "Excluir":
        delete_emenda_streamlit()

def display_all_emendas_streamlit():
    st.header("Lista de Todas as Emendas")
    emendas = st.session_state.emenda_manager.list_emendas()
    if not emendas:
        st.info("Nenhuma emenda cadastrada.")
        return

    emendas_by_category = {}
    for emenda in emendas:
        emendas_by_category.setdefault(emenda.categoria, []).append(emenda)
    
    total_geral_emendas = 0
    for category in sorted(emendas_by_category.keys()):
        category_emendas = emendas_by_category[category]
        total_category_value = sum(e.valor_necessario for e in category_emendas)
        total_geral_emendas += total_category_value
        
        st.subheader(f"Categoria: {category} (Total: R${total_category_value:,.2f})")
        for e in category_emendas:
            status = "TOTALMENTE" if math.isclose(e.current_funded_amount, e.valor_necessario) or e.current_funded_amount > e.valor_necessario else ("PARCIALMENTE" if e.current_funded_amount > 0 else "NÃO")
            st.write(f"  - ID: {e.id}, Descrição: {e.description}, Valor Necessário: R${e.valor_necessario:,.2f}, Contemplado: R${e.current_funded_amount:,.2f}, Status: {status} CONTEMPLADA")
        st.markdown("---")
    
    st.markdown(f"**TOTAL GERAL DE TODAS AS EMENDAS: R${total_geral_emendas:,.2f}**")

def add_new_emenda_streamlit():
    st.header("Cadastrar Nova Emenda")
    
    categories_available = st.session_state.category_manager.list_categories()
    if not categories_available:
        st.warning("Nenhuma categoria cadastrada. Por favor, adicione categorias na seção 'Gerenciar Categorias'.")
        return

    # Verifica se há uma mensagem de sucesso para exibir as opções pós-cadastro
    if st.session_state.get('show_emenda_add_options', False):
        st.success(st.session_state.get('emenda_add_success_message', "Emenda cadastrada com sucesso!"))
        st.warning(st.session_state.get('emenda_add_warning_message', "")) 
        
        st.subheader("O que você gostaria de fazer agora?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cadastrar Outra Emenda"):
                del st.session_state['show_emenda_add_options']
                if 'emenda_add_success_message' in st.session_state: del st.session_state['emenda_add_success_message']
                if 'emenda_add_warning_message' in st.session_state: del st.session_state['emenda_add_warning_message']
                st.rerun() # Força a re-renderização para mostrar o formulário limpo
        with col2:
            if st.button("Ver Lista de Emendas"):
                # Define flags temporárias para a navegação na próxima execução do script
                st.session_state['__nav_target_main_menu'] = "Gerenciar Emendas"
                st.session_state['__nav_target_emenda_menu'] = "Listar Todas"
                if 'show_emenda_add_options' in st.session_state: del st.session_state['show_emenda_add_options']
                if 'emenda_add_success_message' in st.session_state: del st.session_state['emenda_add_success_message']
                if 'emenda_add_warning_message' in st.session_state: del st.session_state['emenda_add_warning_message']
                st.rerun() # Força a re-renderização para a nova página
    else: # Exibe o formulário de cadastro
        with st.form("add_emenda_form"):
            description = st.text_input("Descrição da Emenda")
            valor = st.number_input("Valor Necessário (R$)", min_value=0.01, format="%.2f")
            categoria_name = st.selectbox("Selecione a Categoria", categories_available)
            
            submitted = st.form_submit_button("Cadastrar Emenda")
            if submitted:
                if description and valor > 0 and categoria_name:
                    emenda = st.session_state.emenda_manager.add_emenda(description, valor, categoria_name)
                    st.session_state['emenda_add_success_message'] = f"Emenda '{emenda.description}' (ID: {emenda.id}) cadastrada com sucesso!"
                    
                    for deputy in st.session_state.deputy_manager.list_deputies():
                        deputy.needs_reallocation = True
                    st.session_state.data_manager.save_deputies(st.session_state.deputy_manager.deputies)
                    st.session_state['emenda_add_warning_message'] = "Uma nova emenda foi adicionada. Todos os deputados foram marcados para uma futura redistribuição de verbas. Você deve executar a opção 'Otimizar Distribuição de Verbas' para aplicar as mudanças."
                    
                    # Seta a flag para exibir as opções pós-submissão
                    st.session_state['show_emenda_add_options'] = True
                    st.rerun()
                else:
                    st.error("Todos os campos são obrigatórios e o valor deve ser maior que zero.")

def delete_emenda_streamlit():
    st.header("Excluir Emenda")
    emendas = st.session_state.emenda_manager.list_emendas()
    if not emendas:
        st.info("Nenhuma emenda cadastrada.")
        return

    emenda_options = {f"ID: {e.id} - {e.description} (R${e.valor_necessario:,.2f})": e.id for e in emendas}
    selected_emenda_display = st.selectbox("Selecione a Emenda para Excluir", list(emenda_options.keys()), key='select_emenda_delete')

    if selected_emenda_display:
        emenda_id_to_delete = emenda_options[selected_emenda_display]
        emenda_desc = st.session_state.emenda_manager.get_emenda_by_id(emenda_id_to_delete).description

        st.warning(f"Você tem certeza que deseja excluir a emenda '{emenda_desc}' (ID: {emenda_id_to_delete})?")
        if st.button(f"Confirmar Exclusão de Emenda {emenda_desc}"):
            success, message = st.session_state.emenda_manager.delete_emenda(emenda_id_to_delete)
            if success:
                st.success(message)
                for d in st.session_state.deputy_manager.list_deputies():
                    d.needs_reallocation = True
                st.session_state.data_manager.save_deputies(st.session_state.deputy_manager.deputies)
                st.warning("Uma emenda foi excluída. Todos os deputados foram marcados para uma futura redistribuição de verbas. Você deve executar a opção 'Otimizar Distribuição de Verbas' para aplicar as mudanças.")
                st.rerun()
            else:
                st.error(message)

def manage_categories_page():
    st.title("Gerenciar Categorias")

    # Seção para Adicionar Categoria
    st.subheader("Adicionar Nova Categoria")
    with st.form("add_category_form"):
        new_category_name = st.text_input("Nome da Categoria:", key="new_category_input")
        submitted = st.form_submit_button("Adicionar Categoria")

        if submitted:
            success, message = st.session_state.category_manager.add_category(new_category_name)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    st.markdown("---")

    # Seção para Listar e Excluir Categorias
    st.subheader("Categorias Existentes")
    categories = st.session_state.category_manager.list_categories()

    if not categories:
        st.info("Nenhuma categoria cadastrada ainda.")
        return

    # Helper function to check if category is in use
    def _is_category_in_use(category_name_to_check):
        # Check if used by any deputy for allocation intention
        for deputy in st.session_state.deputy_manager.list_deputies():
            if category_name_to_check in deputy.allocated_by_category:
                return True, f"Deputado '{deputy.name}' tem verba alocada para esta categoria."
            if category_name_to_check in deputy.inclinacao_por_categoria:
                return True, f"Deputado '{deputy.name}' tem inclinação configurada para esta categoria."
        
        # Check if used by any emenda
        for emenda in st.session_state.emenda_manager.list_emendas():
            if emenda.categoria == category_name_to_to_check: # <<-- CORRIGIDO AQUI TBM
                return True, f"Emenda '{emenda.description}' pertence a esta categoria."
        return False, None

    for cat in sorted(categories):
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.write(f"- {cat}")
        with col2:
            is_in_use, reason = _is_category_in_use(cat)
            if is_in_use:
                st.button("Excluir", key=f"delete_cat_{cat}", disabled=True, help=f"Não pode excluir: {reason}")
            else:
                if st.button("Excluir", key=f"delete_cat_{cat}"):
                    success, message = st.session_state.category_manager.delete_category(cat)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

def optimize_distribution_page():
    st.title("Otimizar Distribuição de Verbas")

    deputies_needing_reallocation = st.session_state.deputy_manager.get_deputies_needing_reallocation()

    if not st.session_state.deputy_manager.list_deputies():
        st.info("Nenhum deputado cadastrado para otimizar distribuição.")
        return
    if not st.session_state.emenda_manager.list_emendas():
        st.info("Nenhuma emenda cadastrada para otimizar distribuição.")
        return

    if deputies_needing_reallocation:
        st.subheader("Deputados marcados para realocação:")
        for d in deputies_needing_reallocation:
            st.write(f"- ID: {d.id} | Nome: {d.name}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Otimização Geral", help="Reinicia toda a distribuição de verbas."):
                with st.spinner('Realizando otimização geral...'):
                    message = st.session_state.optimizer.perform_full_redistribution()
                st.success(message)
                st.rerun()
        with col2:
            if st.button("Otimização Parcial", help="Otimiza apenas a verba dos deputados marcados."):
                with st.spinner('Realizando otimização parcial...'):
                    deputy_ids_to_reallocate = [d.id for d in deputies_needing_reallocation]
                    message = st.session_state.optimizer.perform_partial_redistribution(deputy_ids_to_reallocate)
                st.success(message)
                st.rerun()
    else:
        st.info("Nenhum deputado marcado para realocação específica.")
        st.write("Você pode executar uma otimização geral para recalcular toda a distribuição.")
        if st.button("Executar Otimização Geral"):
            with st.spinner('Realizando otimização geral...'):
                message = st.session_state.optimizer.perform_full_redistribution()
            st.success(message)
            st.rerun()

def reports_page():
    st.title("Relatórios de Distribuição")
    if not st.session_state.deputy_manager.list_deputies() or not st.session_state.emenda_manager.list_emendas():
        st.info("É necessário cadastrar deputados e emendas para gerar um relatório.")
        return

    st.subheader("Relatório Detalhado")
    report_text = st.session_state.report_generator.generate_report()
    st.text(report_text) 

    st.subheader("Gráfico de Sumário de Uso de Verba (JSON)")
    summary_chart_data = st.session_state.report_generator.get_summary_for_chart()
    
    if summary_chart_data:
        labels = [s['name'] for s in summary_chart_data['series']]
        values = [s['data'] for s in summary_chart_data['series']]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        fig.update_layout(title_text=summary_chart_data['title']['text'])
        st.plotly_chart(fig, use_container_width=True)
        st.json(summary_chart_data) 
    else:
        st.info("Gráfico de Sumário de Uso de Verba - Sem dados para exibir.")


# --- Funções para Geração de Gráficos (JSON) ---
def generate_allocated_verba_chart_json_streamlit(deputy: Deputy):
    series_data = []
    for cat, value in deputy.allocated_by_category.items():
        if value > 0:
            series_data.append({"name": cat, "data": value})
    
    if not series_data:
        return None
            
    chart = {
        "type": "pie",
        "title": {"text": f"Verba Alocada por Categoria (Intenção) - {deputy.name}"}, 
        "series": series_data
    }
    return chart

def generate_inclination_chart_json_streamlit(deputy: Deputy):
    series_data = []
    for cat, score in deputy.inclinacao_por_categoria.items():
        if score > 0:
            series_data.append({"name": cat, "data": score})

    if not series_data:
        return None
            
    chart = {
        "type": "pie",
        "title": {"text": f"Pontos de Inclinação por Categoria - {deputy.name}"}, 
        "series": series_data
    }
    return chart

def generate_contributed_emendas_chart_json_streamlit(deputy: Deputy, contributions_by_category_for_display):
    series_data = []
    category_totals = {}
    for category, contrib_list in contributions_by_category_for_display.items():
        total_for_category = sum(item['contrib_detail']['total'] for item in contrib_list)
        if total_for_category > 0:
            category_totals[category] = total_for_category
    
    for cat, total in category_totals.items():
        series_data.append({"name": cat, "data": total})

    if not series_data:
        return None
            
    chart = {
        "type": "pie",
        "title": {"text": f"Verba Efetivamente Contribuída para Emendas (por Categoria) - {deputy.name}"}, 
        "series": series_data
    }
    return chart


# --- Aplicação Principal Streamlit ---
def main_streamlit_app():
    initialize_session_state()

    # --- Lógica de navegação centralizada para evitar StreamlitAPIException ---
    if '__nav_target_main_menu' in st.session_state:
        st.session_state['main_menu_selection'] = st.session_state.pop('__nav_target_main_menu')
        # Limpa também os submenus para evitar inconsistências, se eles existirem na flag
        if '__nav_target_deputy_menu' in st.session_state:
            st.session_state['deputy_menu_choice'] = st.session_state.pop('__nav_target_deputy_menu')
        if '__nav_target_emenda_menu' in st.session_state:
            st.session_state['emenda_menu_choice'] = st.session_state.pop('__nav_target_emenda_menu')
        # Força o Streamlit a re-executar com o novo estado de navegação
        st.rerun()
    # --- Fim da lógica de navegação centralizada ---

    st.sidebar.title("Navegação")
    if 'main_menu_selection' not in st.session_state:
        st.session_state['main_menu_selection'] = "Home"

    menu_options = ["Home", "Gerenciar Deputados", "Gerenciar Emendas", "Gerenciar Categorias", "Otimizar Distribuição", "Relatórios"]
    page = st.sidebar.selectbox("Ir para", menu_options, key='main_menu_selection', index=menu_options.index(st.session_state['main_menu_selection']))


    if page == "Home":
        home_page()
    elif page == "Gerenciar Deputados":
        # O 'deputy_menu_choice' é inicializado dentro de manage_deputies_page, antes do seu selectbox ser criado
        manage_deputies_page()
    elif page == "Gerenciar Emendas":
        # O 'emenda_menu_choice' é inicializado dentro de manage_emendas_page, antes do seu selectbox ser criado
        manage_emendas_page()
    elif page == "Gerenciar Categorias":
        manage_categories_page()
    elif page == "Otimizar Distribuição":
        optimize_distribution_page()
    elif page == "Relatórios":
        reports_page()

if __name__ == "__main__":
    main_streamlit_app()