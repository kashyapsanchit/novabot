import base64
import uuid
from io import BytesIO
from PIL import Image
from llama_index.core import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.schema import TextNode, ImageNode
from llama_index.core.indices import MultiModalVectorStoreIndex
from config import get_qdrant_client
from fastembed import TextEmbedding, ImageEmbedding

class VectorStore:
    def __init__(self):
        """
        Initializes Qdrant client and vector stores for text and images.
        """
        self.client = get_qdrant_client()

        # Initialize Qdrant vector stores
        self.text_store = QdrantVectorStore(
            client=self.client, collection_name="product_manual_text"
        )
        self.image_store = QdrantVectorStore(
            client=self.client, collection_name="product_manual_image"
        )

        self.storage_context = StorageContext.from_defaults(
            vector_store=self.text_store,
            image_store=self.image_store
        )

        self.text_embedder = TextEmbedding()
        self.image_embedder = ImageEmbedding("Qdrant/resnet50-onnx")

    def _decode_base64_image(self, base64_string):
        """
        Converts a base64-encoded string into a PIL image.
        """
        image_data = base64.b64decode(base64_string)
        return Image.open(BytesIO(image_data))

    def embed_text(self, text_list):
        """
        Generates embeddings for a list of text data.
        :param text_list: List of strings
        :return: List of embeddings
        """
        return list(self.text_embedder.embed(text_list))

    def embed_image(self, image_base64_list):
        """
        Generates embeddings for a list of base64-encoded images.
        :param image_base64_list: List of base64 strings
        :return: List of embeddings
        """
        images = [self._decode_base64_image(img) for img in image_base64_list]
        return list(self.image_embedder.embed(images))

    def store_text_embeddings(self, text_list, ids=None):
        """
        Stores text embeddings into Qdrant.
        :param text_list: List of strings
        :param ids: Optional list of IDs for storage
        """
        embeddings = self.embed_text(text_list)
        if not ids:
            ids = [str(uuid.uuid4()) for _ in range(len(text_list))]

        nodes = [
        TextNode(id_=ids[i], embedding=emb, metadata={"text": text_list[i]})
        for i, emb in enumerate(embeddings) ] 

        self.text_store.add(
            nodes=nodes
        )

    def store_image_embeddings(self, image_base64_list, ids=None):
        """
        Stores image embeddings into Qdrant.
        :param image_base64_list: List of base64-encoded images
        :param ids: Optional list of IDs for storage
        """
        embeddings = self.embed_image(image_base64_list)
        if not ids:
            ids = [str(uuid.uuid4()) for _ in range(len(image_base64_list))]

        nodes = [
        ImageNode(id_=ids[i], embedding=emb, metadata={"image": image_base64_list[i]})
        for i, emb in enumerate(embeddings) ] 
    

        self.image_store.add(
            nodes=nodes
        )

    def retrieve_text_embeddings(self, query, top_k=3):
        """
        Retrieves relevant text embeddings based on a query.
        :param query: Query string
        :param top_k: Number of results to retrieve
        :return: List of retrieved text results
        """
        import pdb; pdb.set_trace() 
        query_embedding = self.embed_text([query])

        if isinstance(query_embedding, list) and len(query_embedding) > 0:
            query_embedding = query_embedding[0]

        vectors = query_embedding.tolist()

        results = self.client.search(collection_name="product_manual_text", query_vector=vectors, limit=top_k)

        return [res.payload["text"] for res in results]

    def retrieve_image_embeddings(self, query_image_base64, top_k=3):
        """
        Retrieves relevant images based on an input image.
        :param query_image_base64: Base64-encoded image
        :param top_k: Number of results to retrieve
        :return: List of retrieved image results
        """
        query_embedding = self.embed_image([query_image_base64])

        if isinstance(query_embedding, list) and len(query_embedding) > 0:
            query_embedding = query_embedding[0]
        
        query_bundle = VectorStoreQuery(query_str=query_image_base64, query_embedding=query_embedding.tolist())

        results = self.image_store.query(query_bundle, top_k=top_k)

        return [(res.metadata["image_base64"], res.score) for res in results]

    def create_multimodal_index(self):
        """
        Creates a multimodal index that supports both text and image embeddings.
        """
        return MultiModalVectorStoreIndex.from_documents(
            vector_store=self.text_store,
            image_store=self.image_store,
            storage_context=self.storage_context,
            embed_model=self.text_embedder,
        )

class VectorStoreQuery:
    def __init__(self, query_str: str, query_embedding: list):
        self.query_str = query_str
        self.query_embedding = query_embedding