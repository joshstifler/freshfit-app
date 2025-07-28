
# Código completo do app Fresh & Fit
# Salve como freshfit_app.py

import streamlit as st
from datetime import datetime
import requests
import base64

# ---------------- CONFIGURAÇÕES ----------------
SENHA_ACESSO = "ism"
PRECO_ENERGETICO = 350

# Inicializa estado
if "vendas" not in st.session_state:
    st.session_state.vendas = []
if "pontos" not in st.session_state:
    st.session_state.pontos = {}
if "ranking" not in st.session_state:
    st.session_state.ranking = {"vendas": {}, "horas": {}}

# ---------------- FUNÇÕES ----------------
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

def show_logo(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"<div style='text-align:center'><img src='data:image/png;base64,{encoded}' width='200'></div>",
        unsafe_allow_html=True
    )

def calcular_horas(entrada, saida):
    delta = saida - entrada
    return round(delta.total_seconds() / 3600, 2)

# ---------------- SEGURANÇA ----------------
if not st.session_state.get("autenticado"):
    st.title("🔒 Acesso Fresh & Fit")
    senha = st.text_input("Senha de acesso:", type="password")
    if st.button("Entrar"):
        if senha == SENHA_ACESSO:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    st.stop()

# ---------------- INTERFACE ----------------
set_background("freshfit_background_generated.png")
show_logo("logo.png")

st.title("🥤 Fresh & Fit - Sistema de Controle")
menu = st.sidebar.radio("Menu", ["Bate-Ponto", "Registro de Vendas", "Ranking", "Reset Ranking"])

# ---------------- BATE-PONTO ----------------
if menu == "Bate-Ponto":
    st.header("📍 Controle de Ponto")
    nome = st.text_input("Seu nome:")
    if st.button("✅ Marcar Entrada"):
        st.session_state.pontos[nome] = {"entrada": datetime.now()}
        st.success(f"{nome} marcou ENTRADA às {datetime.now().strftime('%H:%M:%S')}")
    if st.button("🚪 Marcar Saída"):
        if nome in st.session_state.pontos and "entrada" in st.session_state.pontos[nome]:
            entrada = st.session_state.pontos[nome]["entrada"]
            saida = datetime.now()
            horas = calcular_horas(entrada, saida)
            st.session_state.ranking["horas"][nome] = st.session_state.ranking["horas"].get(nome, 0) + horas
            st.success(f"{nome} marcou SAÍDA - {horas} horas trabalhadas")
            del st.session_state.pontos[nome]
        else:
            st.error("Nenhuma entrada registrada!")

# ---------------- REGISTRO DE VENDAS ----------------
if menu == "Registro de Vendas":
    st.header("🛒 Registro de Vendas")
    vendedor = st.text_input("Seu nome:")
    passaporte = st.text_input("Passaporte do cliente:")
    qtd = st.number_input("Quantidade de energéticos:", min_value=1, step=1)
    if st.button("💾 Registrar Venda"):
        total = qtd * PRECO_ENERGETICO
        st.session_state.vendas.append({"vendedor": vendedor, "passaporte": passaporte, "quantidade": qtd, "total": total})
        st.session_state.ranking["vendas"][vendedor] = st.session_state.ranking["vendas"].get(vendedor, 0) + total
        st.success(f"Venda registrada: R$ {total}")

# ---------------- RANKING ----------------
if menu == "Ranking":
    st.header("🏆 Ranking de Funcionários")
    st.subheader("🔝 Top Vendas")
    for nome, valor in sorted(st.session_state.ranking["vendas"].items(), key=lambda x: x[1], reverse=True):
        st.write(f"{nome}: R$ {valor}")
    st.subheader("⏳ Top Horas")
    for nome, horas in sorted(st.session_state.ranking["horas"].items(), key=lambda x: x[1], reverse=True):
        st.write(f"{nome}: {horas}h")

# ---------------- RESET RANKING ----------------
if menu == "Reset Ranking":
    if st.button("⚠ Resetar Ranking Global"):
        st.session_state.ranking = {"vendas": {}, "horas": {}}
        st.success("Ranking resetado com sucesso!")

# ---------------- ENVIAR RELATÓRIO PARA DISCORD ----------------
if st.sidebar.button("📤 Enviar Relatório para Discord"):
    hoje = datetime.now().strftime('%d/%m/%Y %H:%M')
    relatorio = f"📊 RELATÓRIO Fresh & Fit - {hoje}\n\n"
    relatorio += "🏆 Ranking Vendas:\n"
    for nome, valor in sorted(st.session_state.ranking["vendas"].items(), key=lambda x: x[1], reverse=True):
        relatorio += f"{nome}: R$ {valor}\n"
    relatorio += "\n⏳ Ranking Horas:\n"
    for nome, horas in sorted(st.session_state.ranking["horas"].items(), key=lambda x: x[1], reverse=True):
        relatorio += f"{nome}: {horas}h\n"
    try:
        webhook_url = st.secrets["discord"]["webhook_url"]
        requests.post(webhook_url, json={"content": f"```{relatorio}```"})
        st.success("Relatório enviado para o Discord!")
    except:
        st.error("Erro ao enviar relatório")
