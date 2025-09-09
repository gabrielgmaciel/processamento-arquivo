import ctypes

from docling.document_converter import DocumentConverter
from fastapi import APIRouter, File, UploadFile
import tempfile

controller_router = APIRouter(prefix="/arquivo")

@controller_router.post("/teste")
async def processar_arquivo(file: UploadFile = File(...)):
    import tempfile
    import pandas as pd
    import io

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    converter = DocumentConverter()
    try:
        text = converter.convert(tmp_path)
    except Exception as e:
        return {"erro": str(e)}

    # Exportar markdown
    markdown = text.document.export_to_markdown()
    linhas = markdown.splitlines()

    resposta_dict = {}
    i = 0
    while i < len(linhas):
        linha = linhas[i].strip()

        if ":" in linha and not linha.startswith("|"):
            chave, valor = linha.split(":", 1)
            chave = chave.strip()
            valor = valor.strip()

            if valor:
                # Caso normal: chave e valor na mesma linha
                resposta_dict[chave] = valor
            else:
                # Caso especial: valor na(s) próxima(s) linha(s)
                j = i + 1
                while j < len(linhas) and not linhas[j].strip():
                    j += 1  # pula linhas em branco
                if j < len(linhas):
                    resposta_dict[chave] = linhas[j].strip()
                    i = j  # pula a linha já usada

        i += 1

    # ------------------------
    # Extrair tabelas
    # ------------------------
    tabelas = []
    buffer = []
    dentro_tabela = False

    for linha in linhas:
        if linha.strip().startswith("|"):
            dentro_tabela = True
            buffer.append(linha)
        else:
            if dentro_tabela:
                tabela_md = "\n".join(buffer)
                try:
                    df = pd.read_csv(io.StringIO(tabela_md), sep="|").dropna(axis=1, how="all")
                    df = df.rename(columns=lambda c: c.strip())
                    df = df[~df[df.columns[0]].str.contains("-+", regex=True)]
                    tabelas.append(df.to_dict(orient="records"))
                except Exception as e:
                    print("Erro parse tabela:", e)
                buffer = []
                dentro_tabela = False

    if tabelas:
        resposta_dict["Tabelas"] = tabelas

    return resposta_dict
