# Pipeline de Tratamento de Salários

Pipeline ETL em Python (pandas) que trata uma planilha de funcionários e calcula o gasto com salários por filial. O projeto também tem um app em Streamlit com ranking em Plotly, para tratar o arquivo direto no navegador.

## O que o projeto faz

**Extract (extrair)**
- Lê a aba `CSV` do Excel, onde todos os dados vêm na coluna A separados por vírgula.
- Separa em colunas (Nome, Sobrenome, Registro, Nascimento, Setor, Salário, Filial).

**Transform (transformar)**
- Converte o Nascimento do número serial do Excel para data (`dd/mm/aaaa`).
- Limpa os textos: `strip` em todos e `title` em Nome e Sobrenome.
- Converte o Salário para número.
- Calcula o **Salário Total Filial**: soma por filial, com o nome da cidade e o valor, da filial que mais gasta para a que menos gasta.
- Calcula o **Salário Total**: o gasto bruto de toda a empresa.
- Formata os valores em moeda (`R$`).

**Load (carregar)**
- Salva o resultado em `Df tratado.xlsx`.

## Tecnologias

- Python 3
- pandas
- openpyxl
- Streamlit
- Plotly

## Como rodar

1. Clone o repositório:

```bash
git clone https://github.com/SEU-USUARIO/pipeline-tratamento-salarios.git
cd pipeline-tratamento-salarios
```

2. Instale as dependências:

```bash
pip install pandas openpyxl streamlit plotly
```

### Opção 1: script de tratamento

Deixe o arquivo `Aula 1.xlsx` na mesma pasta do script e rode:

```bash
python main.py
```

O arquivo `Df tratado.xlsx` é gerado na pasta.

### Opção 2: app em Streamlit

```bash
python -m streamlit run app.py
```

Na página, arraste o Excel ou clique em **Carregar arquivo**. O app mostra:

- gasto bruto total;
- quantidade de funcionários;
- filial com maior gasto;
- ranking de filiais por gasto com salário (gráfico em Plotly);
- tabela tratada;
- botão para baixar o Excel tratado.

## Formato esperado do arquivo

O arquivo precisa ter as colunas:

`Nome`, `Sobrenome`, `Registro`, `Nascimento`, `Setor`, `Salário`, `Filial`

A coluna `Nascimento` deve estar como número serial do Excel (dias desde 30/12/1899).

## Estrutura do projeto

```
.
├── main.py      # script de tratamento (ETL)
├── app.py       # app em Streamlit
└── README.md
```

## Próximos passos

- Aceitar também datas já formatadas na coluna `Nascimento`.
- Filtros por filial e setor no app.
- Novos gráficos: salário por setor, média por filial e faixa etária.
- Validação dos dados (colunas faltando, salários inválidos, duplicados).
- Separar o tratamento em funções reutilizáveis.

## Autor

Gabriel Guedes — [GitHub](https://github.com/SEU-USUARIO)
