import io
import re

import fitz
import pymupdf4llm

from adp.configs.settings import settings

PAGE_BREAK_STR = settings.PAGE_BREAK_STR


class PDFTextLayerEngine:
    def __init__(self):
        pass

    def to_markdown(self, file_obj: io.BytesIO = None) -> str:
        if file_obj is None:
            return ""

        doc = fitz.open(stream=file_obj.read(), filetype="pdf")
        md_text = pymupdf4llm.to_markdown(
            doc,
            page_separators=True,
            write_images=False,
            force_layer=True,
            graphics_limit=None,
            use_ocr=False,
            ocr_dpi=300,
            dpi=300,
        )
        pattern = r"-{3}\s*end of page.page_number=\d+\s*-{3}"
        md_text = re.sub(pattern, PAGE_BREAK_STR, md_text)

        doc.close()
        return md_text
