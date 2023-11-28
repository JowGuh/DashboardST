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

# Fechar o cursor e a conexão
cursor.close()
conn.close()

df["DATA-HORA-PEDIDO"] = pd.to_datetime(df["DATA-HORA-PEDIDO"])
df["Date"] = df["DATA-HORA-PEDIDO"].dt.date
df["Month"] = df["DATA-HORA-PEDIDO"].dt.strftime('%B')  # Converter diretamente para o nome do mês
df["Origem"] = df["STATUS-TRANSPORTE"]
df_nf['Estado'] = df_nf['ESTADO-DE-DESTINO']

df = df.sort_values("DATA-HORA-PEDIDO")

# Agrupar por mês
pedidos_por_mes = df.groupby("Month").size().reset_index(name="Pedidos")

col1, col2 = st.columns(2)
col3, col4, col5 = st.columns(3)

# Criar um gráfico de barras com cores diferentes para cada mês
cor_palette1 = px.colors.sequential.Teal
fig_Month = px.bar(
    pedidos_por_mes,
    x="Month",
    y="Pedidos",
    title="Pedidos em 2023",
    color="Month",
    color_discrete_sequence=cor_palette1,
    orientation="v",
)
col2.plotly_chart(fig_Month)

# Adicionar gráfico de barras para o número de pedidos por dia do mês selecionado
with col1:
    selected_month_name = st.sidebar.selectbox("Selecione o mês", df["Month"].unique())
    filtered_df = df[df["Month"] == selected_month_name]
    pedidos_por_dia = filtered_df["Date"].value_counts().reset_index()
    pedidos_por_dia.columns = ["Date", "Pedidos por Dia"]

    # Especificar a paleta de cores desejada
    cor_palette2 = px.colors.sequential.Teal
    fig_Day = px.bar(
        pedidos_por_dia,
        x="Pedidos por Dia",
        y="Date",
        title=f"Pedidos por dia em {selected_month_name}",
        orientation="h",
        color="Date",
        color_discrete_sequence=cor_palette2,
    )
    fig_Day.update_layout(xaxis_title="Dia do Mês", yaxis_title="Pedidos por Dia")
    col1.plotly_chart(fig_Day)


fig_Origem = px.pie(
    df,
    names="Origem",
    title="Origem do Pedido",
    color="Origem",
    color_discrete_sequence=cor_palette2,
)
col1.plotly_chart(fig_Origem)





pedidos_em_cada_estado = df_nf.groupby("Estado").size().reset_index(name="QTD de Pedidos")

cor_palette3 = px.colors.sequential.Teal

fig_estado = px.bar(
    pedidos_em_cada_estado,
    x="Estado",
    y="QTD de Pedidos",
    title="Vendas por Estado",
    color= "Estado",
    color_discrete_sequence=cor_palette3,
)
col2.plotly_chart(fig_estado)

with col3:
 marcas_disponiveis = df_produtos['MARCA'].unique()
 marca_selecionada = st.sidebar.selectbox("Selecione a Marca", ["Todas"] + list(marcas_disponiveis))

# Filtre os dados da tabela PRODUTOS com base na marca selecionada
if marca_selecionada != "Todas":
    df_produtos_filtrado_marca = df_produtos[df_produtos['MARCA'] == marca_selecionada]
else:
    df_produtos_filtrado_marca = df_produtos  # Não aplique filtro

# Adicione um widget de seleção para o modelo apenas se uma marca for selecionada
if marca_selecionada != "Todas":
    modelos_disponiveis = df_produtos_filtrado_marca['NOME-PRODUTO'].unique()
    modelo_selecionado = st.sidebar.selectbox("Selecione o Modelo", ["Todos"] + list(modelos_disponiveis))

    # Filtre ainda mais os dados com base no modelo selecionado
    if modelo_selecionado != "Todos":
        df_produtos_filtrado_modelo = df_produtos_filtrado_marca[df_produtos_filtrado_marca['NOME-PRODUTO'] == modelo_selecionado]

        # Agrupe os dados filtrados por derivação e conte a quantidade de ocorrências
        df_produtos_grouped_modelo = df_produtos_filtrado_modelo.groupby(['COR']).size().reset_index(name='Quantidade')

        cor_palette4 = px.colors.sequential.Teal
        fig_produtos_modelo = px.bar(
            df_produtos_grouped_modelo,
            x='COR',
            y='Quantidade',
            color='COR',
            title=f'Vendas de Derivações do Modelo {modelo_selecionado} da Marca {marca_selecionada}',
        )
        col4.plotly_chart(fig_produtos_modelo)

# Agrupe os dados filtrados por derivação e conte a quantidade de ocorrências para todos os modelos
df_produtos_grouped = df_produtos_filtrado_marca.groupby(['NOME-PRODUTO', 'COR']).size().reset_index(name='Quantidade')

cor_palette4 = px.colors.sequential.Teal
fig_produtos = px.bar(
    df_produtos_grouped,
    x='NOME-PRODUTO',
    y='Quantidade',
    color='COR',
    title=f'Vendas de Derivações para Todas as Marcas e Modelos',
)
col3.plotly_chart(fig_produtos)

