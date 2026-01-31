import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="BioMap Batatais - Analisador PETR4", layout="wide")
st.title("📊 Analisador de Tendências: Petrobras (PETR4)")

# Sidebar para configurações
st.sidebar.header("Parâmetros")
ticker = "PETR4.SA"
inicio = st.sidebar.date_input("Data de Início", value=pd.to_datetime("2024-11-18"))
fim = st.sidebar.date_input("Data Final", value=pd.to_datetime("2026-01-30"))

# Coleta de dados
@st.cache_data
def carregar_dados(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    return df

data = carregar_dados(ticker, inicio, fim)

# Cálculos de Análise Técnica
data['MA20'] = data['Close'].rolling(window=20).mean()
data['MA50'] = data['Close'].rolling(window=50).mean()

# Lógica das Setas
# Azul (Compra): Preço cruza acima da MA20
# Vermelha (Venda): Preço cruza abaixo da MA20
# Verde (Correção): Preço cai mas está acima da MA50 (tendência de alta mantida)
data['Sinal'] = 0
data.loc[data['Close'] > data['MA20'], 'Sinal'] = 1  # Alta
data.loc[data['Close'] < data['MA20'], 'Sinal'] = -1 # Queda

# Plotagem
fig = go.Figure()

# Candles
fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'], name='PETR4'))

# Médias
fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], name='Média 20', line=dict(color='orange', width=1)))
fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], name='Média 50', line=dict(color='blue', width=1)))

# Adicionando as Setas (Anotações)
for i in range(1, len(data)):
    # Exemplo de Seta Azul (Compra)
    if data['Sinal'].iloc[i] == 1 and data['Sinal'].iloc[i-1] == -1:
        fig.add_annotation(x=data.index[i], y=data['Low'].iloc[i], text="▲", showarrow=False, font=dict(color="blue", size=15))
    
    # Exemplo de Seta Vermelha (Venda)
    if data['Sinal'].iloc[i] == -1 and data['Sinal'].iloc[i-1] == 1:
        fig.add_annotation(x=data.index[i], y=data['High'].iloc[i], text="▼", showarrow=False, font=dict(color="red", size=15))

fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

st.write("### Resumo Técnico")
st.info("Setas Azuis indicam entrada de força compradora. Setas Vermelhas indicam perda de suporte.")
