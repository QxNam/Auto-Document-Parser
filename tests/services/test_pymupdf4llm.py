import fitz
import pymupdf4llm
import io

from adp.services.data_source.S3 import s3_pull_service


def extract_with_pymupdf4llm():
    # Đảm bảo con trỏ đang ở đầu file "s3://pbl-bulk/upload/20260121_153647_Kết quả học tập.pdf",
    file_obj = s3_pull_service.pull(s3_uri="s3://pbl-bulk/upload/20260121_153647_Kết quả học tập.pdf")
    print("File object pulled from S3.")

    doc = fitz.open(stream=file_obj.read(), filetype="pdf")
    md_text = pymupdf4llm.to_markdown(doc)
    
    return md_text

if __name__ == "__main__":
    markdown_content = extract_with_pymupdf4llm()
    print(markdown_content)
