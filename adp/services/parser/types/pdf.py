from adp.services.parser.parser_registry import ParserRegistry
from adp.services.parser.base_parser import Parser


@ParserRegistry.register([".pdf"])
class PDFParser(Parser):
    """
    PDF parser
    """

    def __init__(self, table_output: str = "markdown"):
        self.table_output = table_output

    def parse(
        self,
    ) -> None:
        """
        Parse a PDF (.pdf) file.
        """
        # code here
        pass
