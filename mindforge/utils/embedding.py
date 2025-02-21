import torch
import clip
import base64
from PIL import Image
from io import BytesIO
import numpy as np
from dotenv import load_dotenv
from config import get_qdrant_client
from qdrant_client.models import PointStruct, VectorParams, Distance
from .pdf_processor import extract_data
import logging
import uuid
from sentence_transformers import SentenceTransformer

load_dotenv()
logging.basicConfig(level=logging.INFO)

logging.info("Initializing CLIP model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

logging.info("Initializing TEXT model...")
text_model = SentenceTransformer('all-MiniLM-L6-v2')

qdrant = get_qdrant_client()

def base64_to_image(base64_str):
    """Converts a base64 string to a PIL image"""
    image_data = base64.b64decode(base64_str)
    return Image.open(BytesIO(image_data))

def get_image_embedding(base64_str):
    """Generate embedding for a base64 image"""
    image = base64_to_image(base64_str)
    image = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = model.encode_image(image).cpu().numpy()
    return embedding.flatten().tolist()

def get_text_embedding(text_query):
    """Generate embedding for a text query using SentenceTransformer"""
    embedding = text_model.encode([text_query])  
    return embedding.flatten().tolist()  

def get_text_embedding_clip(text_query, top_k=5):
    """Search for images in Qdrant using a text query"""
    text = clip.tokenize([text_query]).to(device)
    with torch.no_grad():
        embedding = model.encode_text(text).cpu().numpy()
    return embedding.flatten().tolist()


def insert_data(content):

    try:
        if not qdrant.collection_exists("image_collection"):
            qdrant.create_collection(
                collection_name="image_collection",
                vectors_config=VectorParams(
                    size=512,  
                    distance=Distance.COSINE  
                )
            )

        logging.info("Extracting images from PDF...")    
        data = extract_data(content)
        images = data['image_data']
        texts = data['text_data']
        
        logging.info(f"Extracted {len(images)} images.")
        
        image_points = []
        text_points = []

        for image_data in images:
            embedding = get_image_embedding(image_data['img_base64'])
            image_points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={"id": str(uuid.uuid4()), "img_base64": image_data['img_base64'], "text": image_data['text']}  
                )
            )

        logging.info("Inserting images into Qdrant...")
        qdrant.upsert(collection_name="image_collection", points=image_points)

        if not qdrant.collection_exists("text_collection"):
            qdrant.create_collection(
                collection_name="text_collection",
                vectors_config=VectorParams(
                    size=384,  
                    distance=Distance.COSINE  
                )
            )

        for text_data in texts:
            embedding = get_text_embedding(text_data)
            text_points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={"text": text_data}
                )
            )

        qdrant.upsert(collection_name="text_collection", points=text_points)

        logging.info("Data inserted successfully.")
        return True

    except Exception as e:
        logging.error(f"Error inserting data: {e}")
        return False


def search_data(query:str):


    query_vector = get_text_embedding(query)
    query_vector_512 = get_text_embedding_clip(query)

    text_search_results = qdrant.search(
        collection_name="text_collection",
        query_vector=query_vector,
        limit=5, 
        with_payload=True
    )

    text_results = [result.payload['text'] for result in text_search_results]

    image_search_results = qdrant.search(
        collection_name="image_collection",
        query_vector=query_vector_512,
        limit=5,
        with_payload=True
    )

    image_results = [result.payload['img_base64'] for result in image_search_results]

    data = {
        "text_results": text_results,
        "image_results": image_results[0]
    }

    return data 



