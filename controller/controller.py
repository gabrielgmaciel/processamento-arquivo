from docling.document_converter import DocumentConverter
from fastapi import APIRouter, File, UploadFile
import tempfile

controller_router = APIRouter(prefix="/arquivo")


@controller_router.post("/teste")
async def processar_arquivo(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    converter = DocumentConverter()
    text = converter.convert(tmp_path)
    return {"message": text}
