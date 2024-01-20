import streamlit as st
import requests
import pandas as pd
import time
import string
from unidecode import unidecode
import numpy as np

@st.cache_data
def converte_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon="✅")
    time.sleep(5)
    sucesso.empty()

st.title('Dados Brutos')

dados = pd.read_csv('https://raw.githubusercontent.com/Lilianeaa08/DataApp/main/dados.csv', usecols= lambda column : column not in ['Unnamed: 0'])

dados['TEMPO'] = pd.to_datetime(dados['TEMPO'])


### aplicar tratamento categorico

condicao = [
    
  dados['STATUS'].str.contains('Não respondida|Não resolvido', case=False, regex=True),
  dados['STATUS'].str.contains('Respondida|Resolvido', case=False, regex=True),
  dados['STATUS'].str.contains('Em réplica', case=False, regex=True)

]
valor = ['Nao Resolvido','Resolvido','Replica']

dados['STATUS'] =np.select(condicao, valor, default=None)


dados.drop(columns=['LOCAL','CASOS'], inplace=True)


#### funções ####

def tratar_texto(texto):
    texto_tratado = texto.lower()
    texto_tratado = unidecode(texto_tratado)
    texto_tratado = ''.join(c for c in texto_tratado if c not in string.punctuation)

    return texto_tratado

dados[['TEMA', 'CIDADE', 'UF', 'DESCRICAO', 'STATUS', 'CATEGORIA','EMPRESA']] = dados[
    ['TEMA', 'CIDADE', 'UF', 'DESCRICAO', 'STATUS', 'CATEGORIA','EMPRESA']].applymap(tratar_texto)

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome da Empresa'):
    empresa = st.multiselect('Selecione a empresa', dados['EMPRESA'].unique(), dados['EMPRESA'].unique())
with st.sidebar.expander('Cidade'):
    cidade = st.multiselect('Selecione a cidade', dados['CIDADE'].unique(), dados['CIDADE'].unique())
with st.sidebar.expander('UF'):
    uf = st.multiselect('Selecione a UF', dados['UF'].unique(), dados['UF'].unique())
with st.sidebar.expander('Data do registro'):
    data = st.date_input('Selecione a data da ocorrência', (dados['TEMPO'].min(), dados['TEMPO'].max()))
with st.sidebar.expander('Status'):
    status = st.multiselect('Selecione o status', dados['STATUS'].unique(), dados['STATUS'].unique())

query = '''
EMPRESA in @empresa and \
CIDADE in @cidade and \
UF in @uf and \
@data[0] <= TEMPO <= @data[1] and \
STATUS in @status
'''

num_ocorrencias = dados.count()

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

# Adicionando filtro de ocorrências
num_ocorrencias = st.slider('Selecione o número de ocorrências a serem exibidas', 1, dados_filtrados.shape[0],
                            dados_filtrados.shape[0])
dados_filtrados = dados_filtrados.head(num_ocorrencias)

st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em csv', data=converte_csv(dados_filtrados), file_name=nome_arquivo,
                       mime='text/csv', on_click=mensagem_sucesso)
