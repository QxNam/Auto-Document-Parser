from docling_core.types.doc.page import TextCellUnit
from docling_parse.pdf_parser import DoclingPdfParser, PdfDocument

parser = DoclingPdfParser()

pdf_doc: PdfDocument = parser.load(
    path_or_stream="1-bctc-hop-nhat-1-10.pdf"
)

text = ""
for page_no, pred_page in pdf_doc.iterate_pages():
    for word in pred_page.iterate_cells(unit_type=TextCellUnit.WORD):
        # print(word.rect, ": ", word.text)
        text += word.text + " "

print(text)
