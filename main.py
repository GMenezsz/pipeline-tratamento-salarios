# ---------------------------------------------------------------
# IMPORTAÇÃO
# ---------------------------------------------------------------
import pandas as pd   # biblioteca para trabalhar com tabelas (DataFrame)


# ---------------------------------------------------------------
# 1. LEITURA DO ARQUIVO
# ---------------------------------------------------------------
# Lê a aba "CSV" do Excel.
# header=None -> não usa nenhuma linha como cabeçalho (o cabeçalho vem junto com os dados)
# dtype=str   -> lê tudo como texto, para o pandas não "adivinhar" tipos errados
bruto = pd.read_excel("Aula 1.xlsx", sheet_name="CSV", header=None, dtype=str)


# ---------------------------------------------------------------
# 2. SEPARAÇÃO DAS COLUNAS
# ---------------------------------------------------------------
# Tudo estava na coluna A, separado por vírgula.
# bruto[0] = a coluna A; .str.split(",") quebra o texto em cada vírgula;
# expand=True espalha os pedaços em colunas separadas.
df = bruto[0].str.split(",", expand=True)

df.columns = df.iloc[0]                       # a 1ª linha (Nome, Sobrenome...) vira o nome das colunas
df.columns.name = None                        # remove aquele "0" que aparecia ao lado do cabeçalho no print
df = df.iloc[1:].reset_index(drop=True)       # tira a linha do cabeçalho (que virou nome de coluna)
                                              # e refaz a numeração das linhas: 0, 1, 2...


# ---------------------------------------------------------------
# 3. NASCIMENTO: NÚMERO DO EXCEL -> DATA
# ---------------------------------------------------------------
# O Excel guarda datas como número de dias desde 30/12/1899.
# astype(int)  -> converte o texto "26753" em número inteiro
# unit="D"     -> cada número representa dias
# origin       -> o "dia zero" do Excel
df["Nascimento"] = pd.to_datetime(df["Nascimento"].astype(int), unit="D", origin="1899-12-30")

# Deixa a data no formato brasileiro dia/mês/ano (a coluna vira texto)
df["Nascimento"] = df["Nascimento"].dt.strftime("%d/%m/%Y")


# ---------------------------------------------------------------
# 4. LIMPEZA DOS TEXTOS
# ---------------------------------------------------------------
for col in ["Nome", "Sobrenome"]:
    # strip() -> tira espaços do início e do fim
    # title() -> 1ª letra de cada palavra em maiúscula ("maria clara" -> "Maria Clara")
    df[col] = df[col].str.strip().str.title()

for col in ["Setor", "Filial"]:
    df[col] = df[col].str.strip()             # aqui só tira os espaços, sem mexer nas maiúsculas


# ---------------------------------------------------------------
# 5. SALÁRIO: TEXTO -> NÚMERO
# ---------------------------------------------------------------
# Precisa ser número para poder somar. errors="coerce" troca valores inválidos por vazio (NaN)
# em vez de dar erro.
df["Salário"] = pd.to_numeric(df["Salário"], errors="coerce")


# ---------------------------------------------------------------
# 6. TOTAL POR FILIAL
# ---------------------------------------------------------------
# groupby("Filial") agrupa os funcionários por filial;
# transform("sum") soma os salários de cada filial e REPETE o resultado em cada linha dela
# (assim a coluna nova tem o mesmo tamanho do df, sem perder nenhuma linha).
df["Salário Total Filial"] = df.groupby("Filial")["Salário"].transform("sum")

# Ordena a tabela: filiais com maior gasto aparecem primeiro (ascending=False = decrescente)
df = df.sort_values(by="Salário Total Filial", ascending=False)


# ---------------------------------------------------------------
# 7. COLUNA "SALÁRIO TOTAL FILIAL" COM NOME DA CIDADE + TOTAL
# ---------------------------------------------------------------
# Nome da cidade + total, uma linha por filial, nas primeiras linhas

# resumo = soma de salários por filial, da maior para a menor.
# É uma lista com 1 valor por filial; o nome da filial fica no índice.
resumo = df.groupby("Filial")["Salário"].sum().sort_values(ascending=False)

# Apaga o conteúdo da coluna (que tinha o total repetido em todas as linhas)
df["Salário Total Filial"] = None

# df.iloc[linhas, coluna] seleciona por POSIÇÃO:
#   :len(resumo)                         -> as primeiras linhas (uma para cada filial)
#   df.columns.get_loc("Salário Total Filial") -> a posição dessa coluna
# O valor guardado é o texto "Filial: R$ total", montado juntando:
#   resumo.index               -> nome da filial
#   ": R$"                     -> texto fixo
#   resumo.map("{:,.2f}".format) -> total com milhar e 2 casas decimais
# .values entrega só os valores (sem o índice), para encaixar por posição.
# As linhas restantes da coluna ficam vazias.
df.iloc[:len(resumo), df.columns.get_loc("Salário Total Filial")] = (
    resumo.index + ": R$" + resumo.map("{:,.2f}".format)
).values


# ---------------------------------------------------------------
# 8. SALÁRIO TOTAL (GASTO BRUTO DE TODA A EMPRESA)
# ---------------------------------------------------------------
# Soma de todos os salários, colocada em todas as linhas...
df["Salário Total"] = df["Salário"].sum()

# ...e depois apagada nas repetidas. duplicated() marca como True toda linha cujo valor
# já apareceu antes; como todas têm o mesmo total, só a 1ª linha sobra com o valor.
df.loc[df.duplicated(subset="Salário Total"), "Salário Total"] = None


# ---------------------------------------------------------------
# 9. FORMATAÇÃO EM R$ (SEMPRE POR ÚLTIMO)
# ---------------------------------------------------------------
# "Salário Total Filial" já é texto, então não entra aqui
for col in ["Salário", "Salário Total"]:
    # "R${:,.2f}".format -> coloca R$, separador de milhar e 2 casas decimais (vira texto)
    # na_action="ignore" -> pula as células vazias, evitando o texto "R$nan"
    df[col] = df[col].map("R${:,.2f}".format, na_action="ignore")


# ---------------------------------------------------------------
# 10. SAÍDA
# ---------------------------------------------------------------
df.to_excel("Df tratado.xlsx", index=False)   # salva o resultado em Excel, sem a coluna de índice
print(df)                                     # mostra a tabela no terminal