import os
import time

import io, os, gc
from docling.backend.docling_parse_v4_backend import DoclingParseV4DocumentBackend
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TesseractOcrOptions,
    AcceleratorDevice,
    AcceleratorOptions,
)
# os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/5/tessdata" #"./weights/tessdata" # "
DOCLING_MODEL_PATH = "./weights/models_docling"

def docling_process_cpu(path: str) -> str:
    """Chạy Docling OCR sử dụng CPU để kiểm chứng tốc độ."""
    
    # 1. Cấu hình thiết bị sử dụng CPU
    accelerator_options = AcceleratorOptions(
        num_threads= 4,
        device=AcceleratorDevice.CPU
    )

    pipeline_options = PdfPipelineOptions()
    pipeline_options.generate_page_images = True
    pipeline_options.do_ocr = True
    pipeline_options.images_scale = 2.0
    pipeline_options.do_table_structure = True
    pipeline_options.artifacts_path = DOCLING_MODEL_PATH
    
    # 2. Cấu hình Tesseract (Tối ưu nhất cho CPU)
    pipeline_options.ocr_options = TesseractOcrOptions(
        force_full_page_ocr=True,
        lang=["vie", "eng"]
    )

    pipeline_options.accelerator_options = accelerator_options

    # 3. Khởi tạo Converter
    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options, backend=DoclingParseV4DocumentBackend)
            
        }
    )

    # 4. Xử lý file
    with open(path, "rb") as f:
        docs = DocumentStream(
            name=os.path.basename(path), 
            stream=io.BytesIO(f.read())
        )
        conv_result = doc_converter.convert(docs)
    result = conv_result.document.export_to_markdown(
        page_break_placeholder="\n<PAGE_BREAK>\n"
    )

    # Giải phóng bộ nhớ
    del conv_result
    gc.collect()
    
    return result

if __name__ == "__main__":
    # Đường dẫn tới file pdf của bạn
    pdf_path = "./tests/services/1-bctc-hop-nhat-1-10.pdf"
    
    # Kiểm tra xem file có tồn tại không trước khi chạy
    if os.path.exists(pdf_path):
        print(f"🚀 Bắt đầu xử lý: {pdf_path}")
        start_time = time.time()
        
        try:
            # Gọi hàm xử lý
            markdown_content = docling_process_cpu(pdf_path)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # In một đoạn ngắn kết quả để kiểm tra
            print("\n✅ Xử lý hoàn tất!")
            print(f"⏱️ Thời gian thực thi: {duration:.2f} giây")
            print("\n--- Nội dung Markdown (500 ký tự đầu) ---")
            print(markdown_content[:500] + "...")
            
            # # Lưu kết quả ra file để xem cho kỹ
            output_file = f"./tests/services/bctc_{duration:.0f}s.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"\n📂 Kết quả chi tiết đã được lưu tại: {output_file}")
            
        except Exception as e:
            print(f"❌ Có lỗi xảy ra: {e}")
    else:
        print(f"⚠️ File '{pdf_path}' không tồn tại. Vui lòng kiểm tra lại đường dẫn.")