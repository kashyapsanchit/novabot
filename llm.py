# # from langchain_groq import ChatGroq


# # def get_llm():
# #     llm = ChatGroq(
# #         model="llama-3.1-8b-instant",
# #         api_key="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"
# #     )
# #     return llm

# # llm = get_llm()
# # res = llm.invoke("What is the capital of France?")

# # print(res.content)

# from transformers import CLIPProcessor, CLIPModel
# from sentence_transformers import SentenceTransformer
# # from utils.pdf_processor import extract_text_and_images
# from PIL import Image
# import torch
# import base64
# from io import BytesIO
# import numpy as np


# from sentence_transformers import SentenceTransformer
# from transformers import CLIPProcessor, CLIPModel
# from PIL import Image
# from io import BytesIO
# import base64
# import torch
# import torch.nn as nn

# class Embedding:
#     def __init__(self):
#         self.text_model = SentenceTransformer("sentence-transformers/msmarco-MiniLM-L12-cos-v5")
#         self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
#         self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        
#         # Linear projection layer to match dimensions
#         self.text_projection = nn.Linear(384, 512)
        
#     def encode_text(self, text):
#         """Encodes text into a 512-dim vector."""

#         text_embedding = self.text_model.encode(text)
        
#         if not isinstance(text_embedding, torch.Tensor):
#             text_embedding = torch.tensor(text_embedding, dtype=torch.float32)
        
#         with torch.no_grad():
#             projected_embedding = self.text_projection(text_embedding)

#             normalized_embedding = torch.nn.functional.normalize(projected_embedding, p=2, dim=0)
            
#         return normalized_embedding.tolist()

#     def encode_image(self, image_base64):
#         """Encodes an image into a 512-dim vector using CLIP."""
#         image_data = base64.b64decode(image_base64)
#         image = Image.open(BytesIO(image_data)).convert("RGB")

#         inputs = self.clip_processor(images=image, return_tensors="pt")
#         with torch.no_grad():
#             outputs = self.clip_model.get_image_features(**inputs)
#             # Normalize the image embedding
#             normalized_outputs = torch.nn.functional.normalize(outputs.squeeze(), p=2, dim=0)

#         return normalized_outputs.tolist()

#     # def create_manual_embeddings(self, content):
#     #     text_data, image_data = extract_text_and_images(content)
#     #     vectors = []

#     #     for page_num, text in text_data:
#     #         text_vector = self.encode_text(text)
#     #         vectors.append(text_vector)
                
#     #     for page_num, image_base64 in image_data:
#     #         image_vector = self.encode_image(image_base64)
#     #         vectors.append(image_vector)

#     #     combined_vector = np.mean(vectors, axis=0)
        
#     #     # Normalize the final vector
#     #     final_vector = combined_vector / np.linalg.norm(combined_vector)
        
#     #     return final_vector.tolist() 

#     def query_manual(self,query):
#         """Retrieves relevant text and images from Qdrant."""

#         query_vector = self.text_model.encode(query).tolist()

#         search_results = self.qdrant.search(collection_name='product_manuals', query_vector=query_vector, limit=5)

#         response = []
#         for result in search_results:
#             payload = result.payload
#             if payload["type"] == "text":
#                 response.append(f"Page {payload['page']} - {payload['text']}")
#             elif payload["type"] == "image":
#                 response.append(f"Page {payload['page']} - Image (Base64): {payload['image']}")

#         return response




# from qdrant_client import QdrantClient
# from qdrant_client.models import Filter, ScoredPoint
from dotenv import load_dotenv
# import os

load_dotenv()
# embedding = Embedding()
# # Connect to your Qdrant instance (change host/port if needed)
# client = QdrantClient(url=os.getenv('QDRANT_HOST'),api_key=os.getenv('QDRANT_KEY'))  # Use the correct URL if running remotely

# query  = "What is Attention Mechanism in Deep Learning?"
# # Define your query vector
# queryvector = embedding.encode_text(query)  # Replace with your vector

# collection_info = client.get_collection(collection_name="product_manuals")
# print(collection_info)

# # Perform search in a specific collection (assuming it's named "my_collection")
# search_results = client.search(
#     collection_name="product_manuals",
#     query_vector=queryvector,
#     limit=5,  # Number of closest matches to return
# )

# # Print results
# for result in search_results:
#     print(f"ID: {result.id}, Score: {result.score}, Result: {result}")


from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams
import os

client = QdrantClient(url=os.getenv('QDRANT_HOST'),api_key=os.getenv('QDRANT_KEY'))

vectors_config =VectorParams(size=512, distance="Cosine")

# Create (or recreate) the collection with the specified vectors configuration
client.recreate_collection(
    collection_name="product_manuals",
    vectors_config=vectors_config
)