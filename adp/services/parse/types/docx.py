import io

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from adp.configs.logger import worker_logger as logger
from adp.services.parse.base_parse import BaseParse
from adp.services.parse.parse_registry import ParseRegistry


@ParseRegistry.register([".docx", ".doc"])
class MsWordParse(BaseParse):
    """
    Microsoft Word Parse
    """

    def __init__(
        self,
    ):
        pass

    def parse(
        self,
        file_obj: io.BytesIO,
        engine: str = "auto",
        output_format: str = "markdown",
    ) -> str:
        """
        Parse a Microsoft Word (.docx or .doc).
        """
        try:
            # Load document
            doc = Document(docx=file_obj)
            full_text = []

            for element in doc.element.body:
                if isinstance(element, CT_P):
                    para = Paragraph(element, doc)
                    if para.text.strip():
                        full_text.append(para.text.strip())

                elif isinstance(element, CT_Tbl):
                    table = Table(element, doc)
                    markdown_table = self._table_to_markdown(table)
                    full_text.append("\n" + markdown_table + "\n")

            content = "\n\n".join(full_text)
            return content

        except Exception as e:
            logger.error(f"Failed to parse Word document: {e}")

    def _table_to_markdown(self, table) -> str:
        rows = []
        if not table.rows:
            return ""

        for i, row in enumerate(table.rows):
            cells = []
            for cell in row.cells:
                clean_text = cell.text.strip().replace("\n", " ")
                cells.append(clean_text)

            row_str = f"| {' | '.join(cells)} |"
            rows.append(row_str)

            if i == 0:
                cols = len(row.cells)
                separator = f"| {' | '.join(['---'] * cols)} |"
                rows.append(separator)

        return "\n".join(rows)
