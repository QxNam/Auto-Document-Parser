import io

import pandas as pd

from adp.configs.logger import worker_logger as logger
from adp.services.parse.base_parse import BaseParse
from adp.services.parse.parse_registry import ParseRegistry


@ParseRegistry.register([".xlsx", ".xls"])
class ExcelParse(BaseParse):
    """
    Excel Parser using pandas
    """

    def __init__(self, table_output: str = "markdown"):
        self.table_output = table_output

    def parse(
        self,
        file_obj: io.BytesIO,
        engine: str = "auto",
        output_format: str = "markdown",
    ) -> str:
        try:
            xls_dict = pd.read_excel(io=file_obj)

            output = []
            for sheet_name, df in xls_dict.items():
                if df.empty:
                    continue

                output.append(f"\n--- Sheet: {sheet_name} ---\n")
                markdown_table = df.fillna("").to_markdown(index=False, tablefmt="github")
                output.append(markdown_table)
                output.append("\n")

            content = "\n".join(output)
            return content
        except Exception as e:
            logger.error(f"Failed to parse Excel: {e}")
