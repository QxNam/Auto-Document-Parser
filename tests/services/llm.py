import os
from base64 import b64encode

import google.generativeai as genai

os.environ["GEMINI_API_KEY"] = ""

genai.configure(api_key=os.environ["GEMINI_API_KEY"])


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return b64encode(image_file.read()).decode("utf-8")


# Tạo một model và run a prompt
model = genai.GenerativeModel("gemini-1.5-pro")

image_path = "path/to/your/image.jpg"

image = encode_image(image_path)

prompt = "Extract the text in the image verbatim"

response = model.generate_content([prompt, ("data:image/jpeg;base64," + image)])

print(response.text)
