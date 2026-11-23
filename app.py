import io

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Tratamento de Salários", page_icon="📊", layout="wide")


def ler_arquivo(arquivo):
    xls = pd.ExcelFile(arquivo)
    aba = "CSV" if "CSV" in xls.sheet_names else xls.sheet_names[0]
    bruto = pd.read_excel(xls, sheet_name=aba, header=None, dtype=str)

    # Se tudo veio na coluna A separado por vírgula, separa em colunas
    if bruto.shape[1] == 1:
        df = bruto[0].str.split(",", expand=True)
    else:
        df = bruto

    df.columns = df.iloc[0]
    df.columns.name = None
    df = df.iloc[1:].reset_index(drop=True)
    return df


def tratar(df):
    df["Nascimento"] = pd.to_datetime(
        pd.to_numeric(df["Nascimento"], errors="coerce"), unit="D", origin="1899-12-30"
    )
    df["Nascimento"] = df["Nascimento"].dt.strftime("%d/%m/%Y")

    for col in ["Nome", "Sobrenome"]:
        df[col] = df[col].str.strip().str.title()
    for col in ["Setor", "Filial"]:
        df[col] = df[col].str.strip()

    df["Salário"] = pd.to_numeric(df["Salário"], errors="coerce")

    # Ranking numérico (usado no gráfico)
    ranking = (
        df.groupby("Filial")["Salário"].sum().sort_values(ascending=False).reset_index()
    )
    salario_total = df["Salário"].sum()

    df["Salário Total Filial"] = df.groupby("Filial")["Salário"].transform("sum")
    df = df.sort_values(by="Salário Total Filial", ascending=False)

    # Nome da cidade + total, uma linha por filial, nas primeiras linhas
    resumo = df.groupby("Filial")["Salário"].sum().sort_values(ascending=False)
    df["Salário Total Filial"] = None
    df.iloc[:len(resumo), df.columns.get_loc("Salário Total Filial")] = (
        resumo.index + ": R$" + resumo.map("{:,.2f}".format)
    ).values

    df["Salário Total"] = df["Salário"].sum()
    df.loc[df.duplicated(subset="Salário Total"), "Salário Total"] = None

    for col in ["Salário", "Salário Total"]:
        df[col] = df[col].map("R${:,.2f}".format, na_action="ignore")

    return df, ranking, salario_total


def para_excel(df):
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    return buffer.getvalue()


st.title("📊 Tratamento de Salários")
st.write("Arraste o arquivo Excel abaixo ou clique em **Carregar arquivo**.")

arquivo = st.file_uploader(
    "Carregar arquivo", type=["xlsx", "xls"], label_visibility="collapsed"
)

if arquivo is None:
    st.info("Aguardando o arquivo Excel...")
    st.stop()

try:
    df = ler_arquivo(arquivo)

    colunas = ["Nome", "Sobrenome", "Registro", "Nascimento", "Setor", "Salário", "Filial"]
    faltando = [c for c in colunas if c not in df.columns]
    if faltando:
        st.error(f"O arquivo não tem as colunas: {', '.join(faltando)}")
        st.stop()

    df, ranking, salario_total = tratar(df)
except Exception as erro:
    st.error(f"Não foi possível tratar o arquivo: {erro}")
    st.stop()

st.success("Arquivo tratado com sucesso!")

c1, c2, c3 = st.columns(3)
c1.metric("Gasto bruto total", f"R$ {salario_total:,.2f}")
c2.metric("Funcionários", len(df))
c3.metric("Filial com maior gasto", ranking.iloc[0]["Filial"])

st.subheader("Ranking de filiais por gasto com salário")
grafico = px.bar(
    ranking,
    x="Salário",
    y="Filial",
    orientation="h",
    text="Salário",
    labels={"Salário": "Gasto total com salário (R$)"},
)
grafico.update_traces(texttemplate="R$ %{x:,.2f}", textposition="outside")
grafico.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
st.plotly_chart(grafico, use_container_width=True)

st.subheader("Tabela tratada")
st.dataframe(df.fillna(""), use_container_width=True)

st.download_button(
    "⬇️ Baixar arquivo tratado",
    data=para_excel(df),
    file_name="Df tratado.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)