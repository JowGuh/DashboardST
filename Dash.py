import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px


st.set_page_config(layout="wide", page_title="DOSTIUS")

# Conectar ao banco de dados
conn = mysql.connector.connect(
    host='br1064.hostgator.com.br',
    user='dostiu26_jonathangustavo',
    password='Gmarley2908',
    database='dostiu26_bdDostius'
)

cursor = conn.cursor()

# Executar a consulta
cursor.execute("SELECT * FROM PEDIDOS")
results = cursor.fetchall()

df = pd.DataFrame(results, columns=[i[0] for i in cursor.description])

cursor.execute("SELECT * FROM NF")
results_nf = cursor.fetchall()

df_nf = pd.DataFrame(results_nf, columns=[i[0] for i in cursor.description])

cursor.execute("SELECT * FROM PRODUTOS")
results_produtos = cursor.fetchall()

df_produtos = pd.DataFrame(results_produtos, columns=[i[0] for i in cursor.description])

cursor.execute("SELECT * FROM ESTOQUE")
results_estoque = cursor.fetchall()

df_estoque = pd.DataFrame(results_estoque, columns=[i[0] for i in cursor.description])

# Fechar o cursor e a conexão
cursor.close()
conn.close()

traduzir_meses = {
    'January': 'Janeiro',
    'February': 'Fevereiro',
    'March': 'Março',
    'April': 'Abril',
    'May': 'Maio',
    'June': 'Junho',
    'July': 'Julho',
    'August': 'Agosto',
    'September': 'Setembro',
    'October': 'Outubro',
    'November': 'Novembro',
    'December': 'Dezembro'
}

traduzir_dias_semana = {
    'Monday': 'Segunda-feira',
    'Tuesday': 'Terça-feira',
    'Wednesday': 'Quarta-feira',
    'Thursday': 'Quinta-feira',
    'Friday': 'Sexta-feira',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

df["DATA-HORA-PEDIDO"] = pd.to_datetime(df["DATA-HORA-PEDIDO"])
df["Date"] = df["DATA-HORA-PEDIDO"].dt.date
df["Mes"] = df["DATA-HORA-PEDIDO"].dt.strftime('%B').map(traduzir_meses)
df["Origem"] = df["STATUS-TRANSPORTE"]
df_nf['Estado'] = df_nf['ESTADO-DE-DESTINO']
df_produtos['DATA'] = pd.to_datetime(df_produtos['DATA'])
df_produtos["Mes"] = df_produtos['DATA'].dt.strftime('%B').map(traduzir_meses)
df_produtos["DiaSemana"] = df_produtos['DATA'].dt.strftime('%A').map(traduzir_dias_semana)
df = df.sort_values("DATA-HORA-PEDIDO")

# Agrupar por mês
pedidos_por_mes = df.groupby("Mes").size().reset_index(name="Pedidos")

ordem_meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

# Sidebar para seleção de gráficos
st.sidebar.markdown("# Selecione o gráfico que você deseja")

# Adicionar checkboxes para selecionar quais gráficos mostrar
mostrar_pedidos_mes = st.sidebar.checkbox("Pedidos por Mês", value=True)
mostrar_vendas_derivacoes = st.sidebar.checkbox("Vendas de Derivações", value=True)
mostrar_Marketplace = st.sidebar.checkbox("Marketplace", value=True)
mostrar_origem_pedido = st.sidebar.checkbox("Origem do Pedido", value=True)
mostrar_vendas_estado = st.sidebar.checkbox("Vendas por Estado", value=True)
mostrar_estoque_marca = st.sidebar.checkbox("Estoque por Marca", value=True)
mostrar_pedidos_dia = st.sidebar.checkbox("Pedidos por Dia", value=True)
# Exibir o gráfico correspondente à opção selecionada
with st.expander("Pedidos por Mês", expanded=mostrar_pedidos_mes):
    if mostrar_pedidos_mes:
        cor_palette3 = px.colors.qualitative.Bold
        fig_Month = px.bar(
            pedidos_por_mes,
            x="Mes",
            y="Pedidos",
            title="Pedidos em 2023",
            color="Mes",
            orientation="v",
            color_discrete_sequence=cor_palette3,
        )
        fig_Month.update_layout(xaxis={"categoryorder": "array", "categoryarray": ordem_meses})
        st.plotly_chart(fig_Month, use_container_width=True)

with st.expander("Vendas de Derivações", expanded=mostrar_vendas_derivacoes):
    if mostrar_vendas_derivacoes:
        col1, col2, col3, col4 = st.columns(4)
        data_inicio = col1.date_input("Data de Início", min_value=df_produtos['DATA'].min().date(), max_value=df_produtos['DATA'].max().date(), value=df_produtos['DATA'].min().date())
        data_fim = col2.date_input("Data de Fim", min_value=df_produtos['DATA'].min().date(), max_value=df_produtos['DATA'].max().date(), value=df_produtos['DATA'].max().date())

        # Filtrando os dados com base nas datas selecionadas
        df_produtos_filtrado_por_periodo = df_produtos[
            (df_produtos['DATA'] >= pd.to_datetime(data_inicio)) & (df_produtos['DATA'] <= pd.to_datetime(data_fim))
        ]
        marcas_disponiveis = df_produtos_filtrado_por_periodo['MARCA'].unique()
        marca_selecionada = col3.selectbox("Selecione a Marca", ["Todas"] + list(marcas_disponiveis), key="vendas_derivacoes")

        if marca_selecionada != "Todas":
            df_produtos_filtrado_marca = df_produtos_filtrado_por_periodo[df_produtos_filtrado_por_periodo['MARCA'] == marca_selecionada]
        else:
            df_produtos_filtrado_marca = df_produtos_filtrado_por_periodo  # Não aplique filtro

        # Adicione um widget de seleção para o modelo apenas se uma marca for selecionada
        if df_produtos_filtrado_marca is not None:
            modelos_disponiveis = df_produtos_filtrado_marca['NOME-PRODUTO'].unique()
            modelos_selecionados = col4.multiselect("Selecione o(s) Modelo(s)", list(modelos_disponiveis), key="vendas_derivacoes_modelos")

            # Filtre ainda mais os dados com base nos modelos selecionados
            if modelos_selecionados:
                df_produtos_filtrado_modelo = df_produtos_filtrado_marca[
                    df_produtos_filtrado_marca['NOME-PRODUTO'].isin(modelos_selecionados)]

                # Agrupe os dados filtrados por derivação e conte a quantidade de ocorrências
                df_produtos_grouped_modelo = df_produtos_filtrado_modelo.groupby(['COR']).size().reset_index(
                    name='Quantidade')

                cor_palette4 = px.colors.sequential.Teal
                fig_produtos_modelo = px.bar(
                    df_produtos_grouped_modelo,
                    x='COR',
                    y='Quantidade',
                    color='COR',
                    title=f'Vendas de Derivações dos Modelos Selecionados da Marca {marca_selecionada}',
                )
                st.plotly_chart(fig_produtos_modelo, use_container_width=True)

                # Verifique se há modelos selecionados antes de mostrar o gráfico de derivações
                if not df_produtos_filtrado_modelo.empty:
                    # Adicione um widget de seleção para a cor apenas se um modelo for selecionado
                    cores_disponiveis = df_produtos_filtrado_modelo['COR'].unique()
                    cor_selecionada = col4.selectbox("Selecione a Cor", ["Todas"] + list(cores_disponiveis), key="vendas_derivacoes_cores")

                    # Filtre ainda mais os dados com base nos modelos e na cor selecionados
                    if cor_selecionada != "Todas":
                        df_produtos_filtrado_cor = df_produtos_filtrado_modelo[
                            df_produtos_filtrado_modelo['COR'] == cor_selecionada]

                        # Verifique se há dados filtrados antes de mostrar o gráfico
                        if not df_produtos_filtrado_cor.empty:
                            # Agrupe os dados filtrados por derivação e conte a quantidade de ocorrências
                            df_produtos_grouped_modelo = df_produtos_filtrado_cor.groupby(['TAMANHO']).size().reset_index(
                                name='Quantidade')

                            cor_palette4 = px.colors.sequential.Teal
                            fig_produtos_modelo = px.bar(
                                df_produtos_grouped_modelo,
                                x='TAMANHO',
                                y='Quantidade',
                                color='TAMANHO',
                                title=f'Vendas de Tamanhos para o Modelo e Cor Selecionados',
                            )
                            st.plotly_chart(fig_produtos_modelo, use_container_width=True)

        # Agrupe os dados filtrados por derivação e conte a quantidade de ocorrências para todos os modelos  
        if df_produtos_filtrado_marca is not None:
            df_produtos_grouped = df_produtos_filtrado_marca.groupby(['NOME-PRODUTO', 'COR']).size().reset_index(
                name='Quantidade')

            cor_palette4 = px.colors.sequential.Teal
            fig_produtos = px.bar(
                df_produtos_grouped,
                x='NOME-PRODUTO',
                y='Quantidade',
                color='COR',
                title=f'Vendas de Derivações para Todas as Marcas e Modelos',
            )
            st.plotly_chart(fig_produtos, use_container_width=True)

with st.expander("", expanded=mostrar_Marketplace):
    if mostrar_Marketplace:
        col1, col2 = st.columns(2)
        # Contar a quantidade de ocorrências para cada valor único em "Origem"
        origem_counts = df_produtos["ORIGEM"].value_counts()

        # Criar um DataFrame para o gráfico de donut
        df_origem = pd.DataFrame({
            "Origem": origem_counts.index,
            "Quantidade": origem_counts.values
        })

        # Criar um gráfico de donut
        fig_donut = px.pie(df_origem, names="Origem", values="Quantidade", hole=0.3)

        # Adicionar porcentagens aos setores do donut
        

        # Configurar o layout do gráfico
        fig_donut.update_layout(title="Marketplace")
                                

        # Exibir o gráfico no Streamlit
        col1.plotly_chart(fig_donut, use_container_width=True)

with st.expander("", expanded=mostrar_Marketplace):
    origem_selecionada = col2.selectbox("Selecione o Marketplace", df_produtos["ORIGEM"].unique(), key="origem_pedido")

    # Filtrar o DataFrame com base na origem selecionada
    df_filtrado = df_produtos[df_produtos["ORIGEM"] == origem_selecionada]
    df_grouped_modelo = df_filtrado.groupby("NOME-PRODUTO").size().reset_index(name="QTD")
    # Criar o gráfico de barras
    fig_modelos = px.bar(
        df_grouped_modelo,
        x="NOME-PRODUTO",
        y="QTD",
        title=f"Quantidade de Vendas por Modelo no Marketplace {origem_selecionada}",
        orientation="v",
        color="NOME-PRODUTO"
    )

    col2.plotly_chart(fig_modelos, use_container_width=True)



with st.expander("Origem do Pedido", expanded=mostrar_origem_pedido):
    if mostrar_origem_pedido:
        fig_Origem = px.pie(
            df,
            names="Origem",
            title="Origem do Pedido",
            color="Origem",
        )
        st.plotly_chart(fig_Origem, use_container_width=True)

with st.expander("Vendas por Estado", expanded=mostrar_vendas_estado):
    if mostrar_vendas_estado:
        pedidos_em_cada_estado = df_nf.groupby("Estado").size().reset_index(name="QTD de Pedidos")
        cor_palette3 = px.colors.qualitative.Bold
        fig_estado = px.bar(
            pedidos_em_cada_estado,
            x="Estado",
            y="QTD de Pedidos",
            title="Vendas por Estado",
            color="Estado",
            color_discrete_sequence=cor_palette3,
        )
        st.plotly_chart(fig_estado, use_container_width=True)



with st.expander("Estoque por Marca", expanded=mostrar_estoque_marca):
    col1, col2 = st.columns(2)

    # Contar a quantidade de ocorrências para cada marca na tabela de estoque
    contagem_marcas_estoque = df_estoque['MARCA'].value_counts()

    # Criar um DataFrame para o gráfico de donut
    df_contagem_marcas_estoque = pd.DataFrame({
        "Marca": contagem_marcas_estoque.index,
        "Quantidade": contagem_marcas_estoque.values
    })

    # Criar um gráfico de donut
    fig_donut_estoque = px.pie(
        df_contagem_marcas_estoque,
        names="Marca",
        values="Quantidade",
        hole=0.3,
        title="Estoque por Marca"
    )

    # Configurar o layout do gráfico
    fig_donut_estoque.update_layout(title="Estoque por Marca")

    # Exibir o gráfico no Streamlit
    col1.plotly_chart(fig_donut_estoque, use_container_width=True)

    

    # Criar um widget de seleção para a marca apenas se houver dados
    if not contagem_marcas_estoque.empty:
        marca_selecionada_estoque = col2.selectbox("Selecione a Marca", contagem_marcas_estoque.index)

        # Filtrar o DataFrame com base na marca selecionada
        df_filtrado_por_marca_estoque = df_estoque[df_estoque['MARCA'] == marca_selecionada_estoque]
        quantidae_estoque = df_filtrado_por_marca_estoque.groupby("PRODUTO").size().reset_index(name="QTD ESTOQUE")

        

        # Criar um gráfico de barras
        fig_quantidade_por_produto_estoque = px.bar(
            quantidae_estoque,
            x='PRODUTO',
            y='QTD ESTOQUE',
            title=f'Quantidade de Produtos por Marca - {marca_selecionada_estoque}',
            orientation="v",
            color="PRODUTO"
        )

        # Exibir o gráfico de barras no Streamlit
        col2.plotly_chart(fig_quantidade_por_produto_estoque, use_container_width=True)

with st.expander("Pedidos por Dia", expanded=mostrar_pedidos_dia):
    if mostrar_pedidos_dia:
        selected_month_name = st.multiselect("Selecione o(s) Mês(es)", df["Mes"].unique(), key="pedidos_dia")
        filtered_df = df[df["Mes"].isin(selected_month_name)]
        pedidos_por_dia = filtered_df["Date"].value_counts().reset_index()
        pedidos_por_dia.columns = ["Date", "Pedidos por Dia"]
        cor_palette2 = px.colors.sequential.Teal
        fig_Day = px.bar(
            pedidos_por_dia,
            x="Pedidos por Dia",
            y="Date",
            orientation="h",
            color="Date",
        )
        fig_Day.update_layout(xaxis_title="Dia do Mês", yaxis_title="Pedidos por Dia")
        st.plotly_chart(fig_Day, use_container_width=True)

