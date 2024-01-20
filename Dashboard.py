import streamlit as st
import pandas as pd
import numpy as np
from unidecode import unidecode
import string
import plotly.express as px

st.set_page_config(layout= 'wide')
st.title('Análise de Reclamações')

dados = pd.read_csv('https://raw.githubusercontent.com/Lilianeaa08/datasets_testes/main/dados.csv', usecols=lambda column: column not in ['Unnamed: 0'])

# Aplicar tratamento categórico
condicoes = [
    dados['STATUS'].str.contains('não', case=False, regex=True),
    dados['STATUS'].str.contains('respondida|resolvido', case=False, regex=True),
    dados['STATUS'].str.contains('em réplica', case=False, regex=True)
]
valores = ['Nao Resolvido', 'Resolvido', 'Replica']

dados['STATUS'] = np.select(condicoes, valores, default='Outro')

dados['TEMPO'] = pd.to_datetime(dados['TEMPO'])

dados.drop(columns=['LOCAL', 'CASOS'], inplace=True)

def tratar_texto(texto):
    texto_tratado = texto.lower()
    texto_tratado = unidecode(texto_tratado)
    texto_tratado = ''.join(c for c in texto_tratado if c not in string.punctuation)
    return texto_tratado

dados[['TEMA', 'CIDADE', 'UF', 'DESCRICAO', 'STATUS', 'CATEGORIA', 'EMPRESA']] = dados[
    ['TEMA', 'CIDADE', 'UF', 'DESCRICAO', 'STATUS', 'CATEGORIA', 'EMPRESA']].applymap(tratar_texto)

df = dados.copy()

menu = st.sidebar.expander("Expandir Menu")
with menu:
    # Configurando o título do aplicativo
    st.title('Análise de Reclamações')

    selected_empresa = st.multiselect('Selecione a empresa', df['EMPRESA'].unique(), df['EMPRESA'].unique())

    selected_estado = st.multiselect('Selecione o estado', df['UF'].unique(), df['UF'].unique())

    selected_status = st.multiselect('Selecione o status', df['STATUS'].unique(), df['STATUS'].unique())

# Aplicando filtros dinâmicos
filtered_df = df[df['EMPRESA'].isin(selected_empresa) &
                 df['UF'].isin(selected_estado) &
                 df['STATUS'].isin(selected_status)]

# Série temporal do número de reclamações
st.subheader('Série temporal do número de reclamações')
fig_temporal = px.line(filtered_df, x='TEMPO', y=filtered_df.index, color='EMPRESA', line_group='EMPRESA', labels={'EMPRESA': 'Empresa'})

fig_temporal.update_layout(yaxis_title='Número de Reclamações')
fig_temporal.update_layout(xaxis_title='Ano das Reclamações')

st.plotly_chart(fig_temporal)

# Frequência de reclamações por estado
st.subheader('Frequência de reclamações por estado')
fig_estado = px.bar(filtered_df['UF'].value_counts(), x=filtered_df['UF'].value_counts().index, y=filtered_df['UF'].value_counts().values,color_discrete_sequence=['#9FB4ED'])
fig_estado.update_layout(yaxis_title='Frequência')
fig_estado.update_layout(xaxis_title='Estados')
st.plotly_chart(fig_estado)

# Frequência de cada tipo de STATUS
st.subheader('Frequência de cada tipo de status')
fig_status = px.bar(filtered_df['STATUS'].value_counts(), x=filtered_df['STATUS'].value_counts().index, y=filtered_df['STATUS'].value_counts().values,color_discrete_sequence=['#9FB4ED'])
fig_status.update_layout(yaxis_title='Frequência')
fig_status.update_layout(xaxis_title='Status')
st.plotly_chart(fig_status)

# Distribuição do tamanho do texto
st.subheader('Distribuição do tamanho do texto')

# Adicione um controle deslizante para escolher o intervalo do tamanho do texto
texto_size_range = st.slider('Escolha o intervalo de tamanho do texto', min_value=0, max_value=500, value=(0, 500))

# Aplicar filtros dinâmicos para o tamanho do texto
filtered_texto_size = filtered_df[(filtered_df['DESCRICAO'].apply(len) >= texto_size_range[0]) & (filtered_df['DESCRICAO'].apply(len) <= texto_size_range[1])]

fig_texto_size = px.histogram(filtered_texto_size, x=filtered_texto_size['DESCRICAO'].apply(len),color_discrete_sequence=['#9FB4ED'],opacity=0.7)
fig_texto_size.update_layout(yaxis_title='Frequência')
fig_texto_size.update_layout(xaxis_title='Tamanho do Texto')
st.plotly_chart(fig_texto_size)

