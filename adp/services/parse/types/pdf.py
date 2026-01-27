import io
from typing import Any, BinaryIO, Dict, Tuple, Union
import fitz
from pymupdf4llm.helpers import check_ocr
# import pymupdf.layout
import pymupdf4llm

from adp.services.parse.parse_registry import ParseRegistry
from adp.services.parse.base_parse import BaseParse
from adp.services.parse.engines.pdf_native_engine import PDFTextLayerEngine
from adp.services.parse.engines.llm_engine import GeminiPDFParserEngine
from adp.configs.logger import worker_logger as logger
from adp.configs.settings import settings

DEFAULT_DPI = 150
MAX_INSPECT_PAGES = 50
TEXT_FLAGS = (
    fitz.TEXT_COLLECT_STYLES
    | fitz.TEXT_COLLECT_VECTORS
    | fitz.TEXT_PRESERVE_IMAGES
    | fitz.TEXT_ACCURATE_BBOXES
    | fitz.TEXT_MEDIABOX_CLIP
)

@ParseRegistry.register([".pdf"])
class PDFParse(BaseParse):
    def __init__(self):
        self.local_engine = PDFTextLayerEngine()
        self.llm_engine = GeminiPDFParserEngine()

    def parse(
        self,
        file_obj: io.BytesIO,
        engine: str = "text_layer",
        output_format: str = "markdown",
    ) -> str:
        try:
            file_obj.seek(0)
            
            md_text = self.local_engine.to_markdown(file_obj)

            # is_poor_quality = len(md_text.strip()) < 100 ## should be replaced with better quality check
            # should_use_llm = engine == "auto" and settings.ENGINE == "auto" and is_poor_quality

            # if should_use_llm:
            #     try:
            #         logger.info(f"Switching to LLM OCR engine (Reason: engine={engine}, poor_quality={is_poor_quality})")
            #         file_obj.seek(0)
            #         llm_text = self.llm_engine.to_markdown(file_obj)
                    
            #         if llm_text:
            #             md_text = llm_text
            #         else:
            #             logger.warning("LLM engine returned empty text, staying with local output.")
            #     except Exception as e:
            #         logger.error(f"Failed to parse PDF with LLM engine: {e}")

            return md_text

        except Exception as e:
            logger.error(f"Failed to parse PDF: {e}")
            return ""


    def _decide_should_ocr_file(
        self,
        pdf_path: Union[str, BinaryIO],
        *,
        min_ocr_page_ratio: float = 0.3,
        min_ocr_page_count: int = 1,
        dpi: int = DEFAULT_DPI,
    ) -> Dict[str, Any]:
        """
        Fast, production-ready OCR decision for entire PDF.
        """

        def decide_should_ocr_page(d: Dict[str, Any]) -> bool:
            """
            Fast short-circuit OCR decision for a single page.
            """

            # OCR rồi nhưng text không đọc được → OCR lại
            if d.get("has_ocr_text") and not d.get("readable_text"):
                return True

            # Có text số và đọc được → không OCR
            if d.get("has_text") and d.get("readable_text"):
                return False

            # Không có text layer → OCR
            if not d.get("has_text"):
                return True

            # Trang scan ảnh → OCR
            if d.get("image_covers_page"):
                return True

            # Text vector → không OCR
            if d.get("has_vector_chars"):
                return False

            return bool(d.get("should_ocr", False))

        total_pages = 0
        inspected_pages = 0

        ocr_pages: list[int] = []
        scan_pages: list[int] = []
        unreadable_pages: list[int] = []

        with self._open_pdf(pdf_path) as doc:
            for page in doc:
                total_pages += 1
                inspected_pages += 1

                if inspected_pages > MAX_INSPECT_PAGES:
                    break

                raw = check_ocr.should_ocr_page(page, dpi=dpi)

                if raw.get("has_text") or raw.get("has_ocr_text"):
                    textpage = page.get_textpage(flags=TEXT_FLAGS)
                    raw["blocks"] = textpage.extractDICT().get("blocks", [])
                else:
                    raw["blocks"] = []

                should_ocr = decide_should_ocr_page(raw)

                if should_ocr:
                    ocr_pages.append(page.number)

                if raw.get("image_covers_page"):
                    scan_pages.append(page.number)

                if raw.get("has_ocr_text") and not raw.get("readable_text"):
                    unreadable_pages.append(page.number)

        if total_pages == 0:
            return {
                "should_ocr_file": False,
                "total_pages": 0,
                "reason": "Empty document",
            }

        inspected = max(inspected_pages, 1)
        ocr_ratio = len(ocr_pages) / inspected

        should_ocr_file = (
            len(ocr_pages) >= min_ocr_page_count and ocr_ratio >= min_ocr_page_ratio
        )

        reason = (
            f"{len(ocr_pages)}/{inspected} inspected pages need OCR "
            f"({ocr_ratio:.0%})"
            if should_ocr_file
            else "Majority of pages contain readable digital text"
        )

        return {
            "should_ocr_file": should_ocr_file,
            "total_pages": total_pages,
            "inspected_pages": inspected,
            "ocr_pages": ocr_pages,
            "scan_pages": scan_pages,
            "unreadable_pages": unreadable_pages,
            "ocr_ratio": round(ocr_ratio, 2),
            "reason": reason,
        }