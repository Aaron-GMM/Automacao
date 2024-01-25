from bs4 import BeautifulSoup
import pandas as pd
import re
import os
def coletar():

    arquivos = [
        "arquivos.html",
    ]
    diretorio = "caminho/para/arquivo.html"

    arquivos_existentes = [os.path.join(diretorio, arquivo) for arquivo in arquivos if
                           os.path.exists(os.path.join(diretorio, arquivo))]

    if arquivos_existentes:
        print("Arquivo Encontrado",arquivos_existentes)
        arquivo_a_abrir = arquivos_existentes[0]

        with open(arquivo_a_abrir, "r", encoding="ISO-8859-1") as file:
            soup = BeautifulSoup(file, "html.parser")

        table = soup.find("table", {"id": "id_do_elemento_html"})

        headers = []
        data = []

        header_row = table.find("tr")

        for header_cell in header_row.find_all("th"):
            headers.append(header_cell.get_text(strip=True))

        for row in table.find_all("tr")[1:]:
            row_data = [cell.get_text(strip=True) for cell in row.find_all("td")]
            data.append(row_data)


        df = pd.DataFrame(data, columns=headers)

        df = df.replace("", "-")

        periodo_acompanhamento = soup.find('select', {"id": "periodoAcompanhamntoId"})

        periodo = periodo_acompanhamento.find('option', {"selected": True})

        periodo = periodo.get_text(strip=True)
        if "(" in periodo:
            posicao_parentese = periodo.find('(')
            valor_antes_parentese = int(periodo[:posicao_parentese].strip())
            print("Quadrimestre",valor_antes_parentese)
            df['Quadrimestre'] = valor_antes_parentese
            df.to_csv("dados.csv", index=False)
        else:
            print("Quadrimestre:",periodo)
            df['Periodo'] = periodo
            df.to_csv("dados.csv", index=False)

    else:
        print("Nenhum dos arquivos desejados foi encontrado na pasta.")

def formatando_arquivo():

    df = pd.read_csv("dados.csv")
    for coluna in df.columns:
        if df[coluna].dtype == 'object':
            df[coluna] = df[coluna].apply(lambda x: re.sub(r'\s+', ' ', str(x)).strip())

    df = df.replace("nan", "")

    df.to_csv("dados.csv", index=False)

def normalizar():
    df = pd.read_csv("dados.csv")
    new_df = pd.DataFrame()

    for index, row in df.iterrows():

        if index in [0, 1, len(df) - 1]:
            new_df = pd.concat([new_df, row.to_frame().T], ignore_index=True)
            continue

        previsto_info = row["Previsto (%)"]


        if isinstance(previsto_info, str):
            previsto_info = previsto_info.split(')')

            previsto_info = [info.strip() for info in previsto_info if info.strip()]
        else:
            previsto_info = [str(previsto_info)]


        for info in previsto_info:
            new_row = row.copy()
            new_row["Previsto (%)"] = info + ')'
            new_df = pd.concat([new_df, new_row.to_frame().T], ignore_index=True)


    new_df.to_csv("dados.csv", index=False)


def duplicar():

    df = pd.read_csv("dados.csv")

    new_data = []


    for index, row in df.iterrows():
        previsto_info = row["Previsto (%)"]


        if index in [0, 1, len(df) - 1]:
            new_data.append(row)
            continue

        match = re.search(r'\((\d+)\)', previsto_info)

        if match:

            count = int(match.group(1))

            for i in range(count):
                new_row = row.copy()
                new_row["Previsto (%)"] = previsto_info[:previsto_info.find('(')].strip()
                new_data.append(new_row)

        else:
            new_data.append(row)
    new_df = pd.DataFrame(new_data)
    new_df.to_csv("dados.csv", index=False)

    df = pd.read_csv("dados.csv")
    new_data2 = []

    for index2, row2 in df.iterrows():
        pre_info = row2["Executado (%)"]


        if index2 in [0, 1, len(df) - 1]:
            new_data2.append(row2)
            continue

        if isinstance(pre_info, str):

            match = re.search(r'\((\d+)\)', pre_info)

            if match:
                count = int(match.group(1))
                for i in range(count):
                    new_row2 = row2.copy()
                    new_row2["Executado (%)"] = pre_info[:pre_info.find('(')].strip()
                    new_data2.append(new_row2)
            else:
                new_data2.append(row2)
        else:
            new_data2.append(row2)


    new_df = pd.DataFrame(new_data2)
    new_df = new_df.replace("nan)", "")

    new_df.to_csv("dados.csv", index=False)
    dados = pd.read_csv("dados.csv")
    linhas_para_reposicionar = dados[(dados['Executado (%)'].notnull()) & (dados['Previsto (%)'].isnull())]

    dados.loc[linhas_para_reposicionar.index, 'Previsto (%)'] = linhas_para_reposicionar['Executado (%)']
    dados.loc[linhas_para_reposicionar.index, 'Executado (%)'] = None

    dados.to_csv("dados.csv", index=False)

    print("Valores reposicionados com sucesso.")

if __name__ == '__main__':
    coletar()
    formatando_arquivo()
    normalizar()
    duplicar()
