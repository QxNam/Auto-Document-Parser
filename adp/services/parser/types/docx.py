from adp.services.parser.parser_registry import ParserRegistry
from adp.services.parser.base_parser import Parser


@ParserRegistry.register([".docx", ".doc"])
class MsWordParser(Parser):
    """
    Microsoft Word Parser
    """

    def __init__(self, table_output: str = "markdown"):
        self.table_output = table_output

    def parse(
        self,
    ) -> None:
        """
        Parse a Microsoft Word (.docx or .doc).
        """
        # code here
        pass
