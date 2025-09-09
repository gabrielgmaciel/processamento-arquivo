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

    # ------------------------
    # Extrair chave:valor
    # ------------------------
    for linha in linhas:
        if ":" in linha and not linha.strip().startswith("|"):
            chave, valor = linha.split(":", 1)
            chave = chave.strip()
            valor = valor.strip()
            if chave and valor:
                resposta_dict[chave] = valor

    # ------------------------
    # Extrair tabelas (markdown -> DataFrame -> JSON)
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
                # fim da tabela
                tabela_md = "\n".join(buffer)
                try:
                    df = pd.read_csv(io.StringIO(tabela_md), sep="|").dropna(axis=1, how="all")
                    # limpar colunas
                    df = df.rename(columns=lambda c: c.strip())
                    # remover linhas inúteis (---- separador)
                    df = df[~df[df.columns[0]].str.contains("-+", regex=True)]
                    tabelas.append(df.to_dict(orient="records"))
                except Exception as e:
                    print("Erro parse tabela:", e)
                buffer = []
                dentro_tabela = False

    if tabelas:
        resposta_dict["Tabelas"] = tabelas

    return resposta_dict
