# import io, os
# from docling.datamodel.base_models import InputFormat
# from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions
# from docling.document_converter import DocumentConverter, PdfFormatOption

# class DoclingEngine:
#     def __init__(self):
#         # 1. Cấu hình OCR sử dụng Tesseract
#         pipeline_options = PdfPipelineOptions()
#         pipeline_options.ocr_options = TesseractOcrOptions()  # Mặc định sử dụng tesseract
        
#         # 2. Khởi tạo DocumentConverter với cấu hình OCR
#         self.converter = DocumentConverter(
#             format_options={
#                 InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
#             }
#         )

#     def to_markdown(self, file_obj: io.BytesIO = None) -> str:
#         if file_obj is None:
#             return ""

#         # Docling Converter có thể nhận BytesIO trực tiếp thông qua DocumentStream
#         from docling.datamodel.document import DocumentStream
        
#         # Tạo stream để converter xử lý
#         doc_stream = DocumentStream(name="input.pdf", stream=file_obj)
        
#         # Thực hiện chuyển đổi
#         result = self.converter.convert(doc_stream)
        
#         # Xuất kết quả dưới định dạng Markdown
#         return result.document.export_to_markdown()
    
# def test_pdf_conversion(file_path):
#     # 1. Kiểm tra file có tồn tại không
#     if not os.path.exists(file_path):
#         print(f"Lỗi: Không tìm thấy file tại {file_path}")
#         return

#     print(f"--- Đang xử lý file: {file_path} ---")

#     # 2. Đọc file vào BytesIO
#     with open(file_path, "rb") as f:
#         pdf_stream = io.BytesIO(f.read())

#     # 3. Khởi tạo Engine và chuyển đổi
#     try:
#         engine = DoclingEngine()
#         markdown_output = engine.to_markdown(pdf_stream)

#         # 4. In kết quả hoặc lưu ra file .md
#         print("\n--- Kết quả Markdown --- \n")
#         print(markdown_output)
        
#         with open("output_test.md", "w", encoding="utf-8") as out_f:
#             out_f.write(markdown_output)
#         print("\n--- Đã lưu kết quả vào file output_test.md ---")

#     except Exception as e:
#         print(f"Có lỗi xảy ra trong quá trình convert: {e}")

# if __name__ == "__main__":
#     # Thay 'abc.pdf' bằng đường dẫn thực tế của bạn
#     test_pdf_conversion("dkgdc-cho-khcn-vay-tung-lan-va-khoan-vay-duoc-dam-bao-bang-chung-chi-tien-gui.pdf")

import os
import time

import io, os, gc
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TesseractCliOcrOptions,
    AcceleratorDevice,
    AcceleratorOptions,
)
os.environ["TESSDATA_PREFIX"] = "./weights/tessdata" # "/usr/share/tesseract-ocr/5/tessdata"
DOCLING_MODEL_PATH = "./weights/models_docling"

def docling_process_cpu(path: str) -> str:
    """Chạy Docling OCR sử dụng Tesseract CLI để tối ưu độ ổn định trong Docker."""
    
    # 1. Cấu hình thiết bị sử dụng CPU
    accelerator_options = AcceleratorOptions(
        num_threads=4,
        device=AcceleratorDevice.CPU
    )

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.images_scale = 2.0
    pipeline_options.do_table_structure = True
    pipeline_options.artifacts_path = DOCLING_MODEL_PATH
    
    # 2. Cấu hình Tesseract CLI
    # TesseractCliOcrOptions sẽ gọi trực tiếp lệnh 'tesseract' từ hệ thống
    pipeline_options.ocr_options = TesseractCliOcrOptions(
        force_full_page_ocr=True,
        lang=["vie", "eng"],
        # path_to_tesseract="tesseract" # Mặc định là "tesseract", nếu bạn cài ở chỗ lạ thì điền vào đây
    )

    pipeline_options.accelerator_options = accelerator_options

    # 3. Khởi tạo Converter
    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
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
            page_break_placeholder="<PAGE_BREAK>"
        )

    # Giải phóng bộ nhớ
    del conv_result
    gc.collect()
    
    return result

if __name__ == "__main__":
    # Đường dẫn tới file pdf của bạn
    pdf_path = "./tests/services/dkgdc-cho-khcn-vay-tung-lan-va-khoan-vay-duoc-dam-bao-bang-chung-chi-tien-gui.pdf"
    
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
            
            # Lưu kết quả ra file để xem cho kỹ
            output_file = f"./tests/services/dkgdc_2_{duration:.0f}s.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"\n📂 Kết quả chi tiết đã được lưu tại: {output_file}")
            
        except Exception as e:
            print(f"❌ Có lỗi xảy ra: {e}")
    else:
        print(f"⚠️ File '{pdf_path}' không tồn tại. Vui lòng kiểm tra lại đường dẫn.")