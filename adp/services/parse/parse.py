import io
import os

from adp.configs.logger import worker_logger as logger
from adp.configs.settings import settings
from adp.services.parse.parse_registry import ParseRegistry


class Parse:
    """
    Document parsing service with Registry Pattern.
    """

    def parse(self, file_obj: io.BytesIO, file_name: str) -> str:
        try:
            _, extension = os.path.splitext(file_name)

            # register
            parser_instance = ParseRegistry.get_parse(extension)
            logger.debug(f"Using parser: {parser_instance.__class__.__name__} for extension: {extension}")

            # parse
            result = parser_instance.parse(file_obj=file_obj, engine=settings.OCR_ENGINE, output_format="markdown")
            return result

        except Exception as e:
            raise e
