import io

from docling_core.types.doc.page import TextCellUnit
from docling_parse.pdf_parser import DoclingPdfParser, PdfDocument

from adp.configs.settings import settings

PAGE_BREAK_STR = settings.PAGE_BREAK_STR


class DoclingParseEngine:
    def __init__(self):
        self.parser = DoclingPdfParser()

    def to_markdown(self, file_obj: io.BytesIO = None) -> str:
        """Convert PDF file to markdown text using OCR."""
        if file_obj is None:
            return ""

        pdf_doc: PdfDocument = self.parser.load(path_or_stream=file_obj)

        content = []
        for _, pred_page in pdf_doc.iterate_pages():
            for word in pred_page.iterate_cells(unit_type=TextCellUnit.WORD):
                content.append(word.text)

        return PAGE_BREAK_STR.join(content)
