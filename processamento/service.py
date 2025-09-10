import tempfile

import requests
import io

from docling.document_converter import DocumentConverter
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from huggingface_hub import configure_http_backend

service_router = APIRouter(prefix="/arquivo")

def backend_factory() -> requests.Session:
    session = requests.Session()
    session.verify = False
    return session

configure_http_backend(backend_factory=backend_factory)

@service_router.post("/converter")
async def processar_arquivo(file: UploadFile = File(...)):

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        converter = DocumentConverter()
        text = converter.convert(tmp_path)
        markdown_content = text.document.export_to_markdown()
    except Exception as e:
        return {"erro": str(e)}

    return StreamingResponse(
        io.StringIO(markdown_content),
        media_type="text/markdown",
        headers={
            "Content-Disposition": 'attachment; filename="arquivo_convertido.txt"'
        }
    )
