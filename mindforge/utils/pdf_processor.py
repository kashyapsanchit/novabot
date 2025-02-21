import base64
from io import BytesIO
from unstructured.partition.pdf import partition_pdf

def extract_data(file_bytes: bytes):
    
    with BytesIO(file_bytes) as pdf_file:
        elements = partition_pdf(
            file=pdf_file,  
            extract_image_block_types=['Image'], 
            extract_image_block_to_payload=True,
            strategy="hi_res"
        )
        
    image_data = []
    text_data = []

    for element in elements:
        if element.category == "Image":
            page_num = getattr(element, 'page_number', 0)
            img_base64 = element.metadata.image_base64                
            text = element.text

            image_data.append({
                'img_base64': img_base64,
                'page_num': page_num,  
                'text': text,
            })

        elif element.category in ["UncategorizedText", "Text", "NarrativeText"]:
            text_data.append(element.text)

    return {
        'image_data': image_data,
        'text_data': text_data,
    }
