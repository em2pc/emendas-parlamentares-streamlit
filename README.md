# Sistema de Gerenciamento de Emendas Parlamentares

Este é um sistema desenvolvido em Streamlit para auxiliar no gerenciamento e otimização da alocação de verbas de emendas parlamentares.

## Funcionalidades Principais:
- Cadastro e gerenciamento de Deputados (nome, verba total, perfil).
- Configuração de intenções de alocação por categoria para Deputados.
- Configuração de inclinações/preferências por categoria para Deputados.
- Cadastro e gerenciamento de Emendas (descrição, valor, categoria).
- Gerenciamento de Categorias (adição, listagem, exclusão).
- Algoritmo de otimização para distribuir as verbas dos Deputados entre as Emendas, considerando alocações, inclinações e verba livre.
- Geração de relatórios detalhados e gráficos de distribuição.

## Como Usar:
1. Acesse o menu lateral para navegar entre as seções.
2. Comece cadastrando categorias, deputados e emendas.
3. Configure as intenções de alocação e inclinações dos deputados.
4. Execute a otimização de distribuição de verbas.
5. Visualize os resultados nos relatórios.

## Observação sobre os Dados:
**Este deploy é para fins de demonstração.** Os dados cadastrados na aplicação (deputados, emendas, categorias) são armazenados em arquivos JSON na pasta `data/` dentro do ambiente do aplicativo. **Por padrão, este ambiente é efêmero, o que significa que os dados serão resetados e perdidos toda vez que o aplicativo for reiniciado (ex: por inatividade, atualizações de código ou manutenção da plataforma).**

Para um uso que exija persistência de dados, seria necessário integrar um banco de dados externo.

## Tecnologias:
- Python
- Streamlit
- Git/GitHub
