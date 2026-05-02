# backend/utils/file_reader.py
import io
from adapters.base import AttachedFile
from utils.logging import get_logger

log = get_logger("utils.file_reader")

# MIME types suportados
SUPPORTED_MIMES = {
    # Imagens (passadas direto para o modelo visual)
    "image/png", "image/jpeg", "image/gif", "image/webp",
    # Texto extraído e injetado no prompt
    "application/pdf",
    "text/plain", "text/csv", "text/markdown",
    "application/json",
}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


async def process_attachment(filename: str, data: bytes, mime: str) -> AttachedFile:
    """Recebe bytes brutos de um attachment do Discord e retorna AttachedFile pronto."""

    if len(data) > MAX_FILE_SIZE:
        raise ValueError(
            f"Arquivo muito grande: {len(data)/1024/1024:.1f}MB (máx 20MB)")

    mime = mime.lower().split(";")[0].strip()

    if mime not in SUPPORTED_MIMES:
        raise ValueError(
            f"Tipo de arquivo não suportado: `{mime}`\n"
            f"Suportados: imagens (PNG/JPG/GIF/WEBP), PDF, TXT, CSV, JSON, Markdown"
        )

    text_content = None

    if mime == "application/pdf":
        text_content = _extract_pdf(data, filename)
    elif mime in {"text/plain", "text/csv", "text/markdown", "application/json"}:
        text_content = _extract_text(data, filename)
    # imagens não extraem texto — vão como base64

    return AttachedFile(
        filename=filename,
        mime_type=mime,
        data=data,
        text_content=text_content,
    )


def _extract_pdf(data: bytes, filename: str) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
            text = "\n\n".join(pages).strip()
            # limita a 30k chars para não estourar o contexto
            if len(text) > 30_000:
                text = text[:30_000] + "\n\n[... arquivo truncado ...]"
            return text
    except Exception as e:
        log.warning(f"Erro ao extrair PDF {filename}: {e}")
        return f"[Erro ao ler PDF: {e}]"


def _extract_text(data: bytes, filename: str) -> str:
    try:
        text = data.decode("utf-8", errors="replace")
        if len(text) > 30_000:
            text = text[:30_000] + "\n\n[... arquivo truncado ...]"
        return text
    except Exception as e:
        log.warning(f"Erro ao ler texto {filename}: {e}")
        return f"[Erro ao ler arquivo: {e}]"
