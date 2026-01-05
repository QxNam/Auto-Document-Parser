import logging
import os
import time
from adp.services.parser.parser_registry import ParserRegistry

logger = logging.getLogger(__name__)

class Parser:
    """
    Document parsing service with Registry Pattern.
    """

    def parse_document(
        self, file_path
    ):
        try:
            _, extension = os.path.splitext(file_path)

            # register
            parser = ParserRegistry.get_parser(extension)

            # parse
            result = parser.parse(...)
            return result

        except Exception as e:
            raise e