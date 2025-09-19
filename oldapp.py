import streamlit as st
import pandas as pd
import json
st.title('Otimização de Emendas Impositivas')
st.write('teste')

from main import DeputyManager, EmendaManager, ReportGenerator, CategoryManager, AllocationOptimizer, Deputy, app 

st.markdown('Éder Marcelo')
st.markdown('---')




#--- Inicialização da Aplicação ---
if __name__ == "__main__":
   



with open('data/deputies.json', 'r', encoding='utf-8') as f:
    deputies_data = json.load(f)

from main import main   
# Chama dados do Json
df_json_string = pd.DataFrame(deputies_data)
st.write("dados criados via json")
st.dataframe(df_json_string)

st.markdown("---")


