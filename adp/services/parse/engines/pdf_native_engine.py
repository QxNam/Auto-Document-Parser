import fitz
import pymupdf4llm
import io

class PDFTextLayerEngine:
    def __init__(self):
        pass

    def to_markdown(self, file_obj: io.BytesIO = None) -> str:
        doc = fitz.open(stream=file_obj.read(), filetype="pdf")
        md_text = pymupdf4llm.to_markdown(doc)
        return md_text

