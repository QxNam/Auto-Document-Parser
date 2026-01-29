import io
from adp.services.parse.engines.llm_engine import LLMParseEngine
from adp.services.parse.parse_registry import ParseRegistry
from adp.services.parse.base_parse import BaseParse
from adp.services.parse.engines.docling_engine import DoclingEngine
from adp.configs.logger import worker_logger as logger

@ParseRegistry.register([".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff"])
class ImageParse(BaseParse):
    """
    Image parse
    """

    def __init__(self):
        self.ocr_engine = DoclingEngine()
        self.llm_engine = LLMParseEngine()

    def parse(
        self,
        file_obj: io.BytesIO,
        engine: str = "ocr",
        output_format: str = "markdown",
    ) -> str:
        """
        Parse an Image file.
        Args:
            file_obj (io.BytesIO): The Image file object to be parsed.
            engine (str, optional): The parsing engine to use. Defaults to "auto". Options are "auto", "text_layer", "ocr".
            output_format (str, optional): The desired output format. Defaults to "markdown". Options are "markdown", "plain_text".
        """

        try:
            return self.ocr_engine.image_to_markdown(file_obj)

        except Exception as e:
            logger.error(f"Failed to parse Image: {e}")
