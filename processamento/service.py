import requests

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

@service_router.post("/teste")
async def processar_arquivo(file: UploadFile = File(...)):
    import tempfile
    import io

    # --- Salvar arquivo recebido ---
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    converter = DocumentConverter()
    try:
        text = converter.convert(tmp_path)
    except Exception as e:
        return {"erro": str(e)}

    markdown_content = text.document.export_to_markdown()
    file_like = io.StringIO(markdown_content)

    return StreamingResponse(
        file_like,
        media_type="text/markdown",
        headers={
            "Content-Disposition": 'attachment; filename="arquivo_convertido.txt"'
        }
    )
