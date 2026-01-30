import gc
import io

from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import DocumentStream
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
    TesseractOcrOptions,
)
from docling.document_converter import DocumentConverter, ImageFormatOption, PdfFormatOption

from adp.configs.settings import settings

# os.environ["TESSDATA_PREFIX"] = settings.TESSDATA_PREFIX
DOCLING_MODEL_PATH = settings.ARTIFACTS_PATH
PAGE_BREAK_STR = settings.PAGE_BREAK_STR


class DoclingEngine:
    def __init__(self):
        accelerator_options = AcceleratorOptions(num_threads=4, device=AcceleratorDevice.CPU)

        pipeline_options = PdfPipelineOptions()
        pipeline_options.accelerator_options = accelerator_options
        pipeline_options.do_ocr = True
        pipeline_options.images_scale = 2.0
        pipeline_options.do_table_structure = True
        pipeline_options.artifacts_path = DOCLING_MODEL_PATH
        pipeline_options.ocr_options = TesseractOcrOptions(force_full_page_ocr=True, lang=["vie", "eng"])

        self.pdf_converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
        )

        self.image_converter = DocumentConverter(
            format_options={InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options)}
        )

    def pdf_to_markdown(self, file_obj: io.BytesIO = None) -> str:
        if file_obj is None:
            return ""

        doc_stream = DocumentStream(name="abc.pdf", stream=file_obj)

        result = self.pdf_converter.convert(doc_stream)
        md_result = result.document.export_to_markdown(page_break_placeholder=PAGE_BREAK_STR)

        del result
        gc.collect()

        return md_result

    def image_to_markdown(self, file_obj: io.BytesIO = None) -> str:
        if file_obj is None:
            return ""

        doc_stream = DocumentStream(name="abc.pdf", stream=file_obj)

        result = self.image_converter.convert(doc_stream)
        md_result = result.document.export_to_markdown(page_break_placeholder=PAGE_BREAK_STR)

        del result
        gc.collect()

        return md_result
