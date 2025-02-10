import pdfplumber
import fitz  # PyMuPDF
import io
import base64
from PIL import Image

def extract_text_and_images(pdf_path):
    """Extracts text and images from the PDF."""
    text_data = []
    image_data = []

    # ✅ Convert bytes to BytesIO for pdfplumber, keep raw bytes for PyMuPDF
    if isinstance(pdf_path, bytes):
        pdf_bytes = pdf_path  # Keep raw bytes for fitz
        pdf_path = io.BytesIO(pdf_path)  # Convert for pdfplumber
    else:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()  # Read raw bytes for fitz

    with pdfplumber.open(pdf_path) as pdf:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")  # ✅ Use raw bytes

        for page_num, page in enumerate(pdf.pages):
            # ✅ Extract text properly
            text = page.extract_text()
            if text:
                text_data.append((page_num, text))

            # ✅ Extract images (including rendered vector graphics)
            pdf_page = doc[page_num]
            img_list = pdf_page.get_images(full=True)

            if not img_list:
                # If no embedded images, render the page as an image
                pix = pdf_page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                image_data.append((page_num, img_base64))

            else:
                # Extract embedded images
                for img_index, img in enumerate(img_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes))
                    if image.mode == "CMYK":
                        image = image.convert("RGB")
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

                    image_data.append((page_num, img_base64))

    return text_data, image_data
