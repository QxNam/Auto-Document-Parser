import io
from google import genai
from google.genai import types
from adp.configs.settings import settings
from adp.configs.logger import worker_logger as logger

class GeminiPDFParserEngine:
    def __init__(self, model: str = "gemini-2.5-flash"):
        if not settings.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is missing from environment variables!")
            
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = model

    def to_markdown(self, file_obj: io.BytesIO) -> str:
        file_obj.seek(0)
        pdf_bytes = file_obj.read()

        if not pdf_bytes:
            logger.error("Input file_obj is empty.")
            return ""

        # English Prompt for better structural adherence
        prompt = (
            "Extract the content of this PDF into high-quality Markdown format.\n"
            "- Maintain all hierarchical structures (headings, subheadings, lists).\n"
            "- Convert tables to standard Markdown tables. If a table is too complex or wide, "
            "represent it as a CSV within a code block.\n"
            "- Preserve the original reading order across pages.\n"
            "- Do not include any conversational preamble or comments, output ONLY the markdown content."
        )

        try:
            contents = [
                types.Part.from_bytes(
                    data=pdf_bytes,
                    mime_type="application/pdf",
                ),
                prompt
            ]

            logger.info(f"Sending request to Gemini model: {self.model}")
            
            resp = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                )
            )

            logger.info(f"Successfully generated markdown using {self.model}.")
            return resp.text
            
        except Exception as e:
            logger.error(f"Failed to generate content via Gemini API: {str(e)}")
            raise e