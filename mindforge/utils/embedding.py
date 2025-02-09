from sentence_transformers import SentenceTransformer

def create_embeddings(sentences, model_name='all-MiniLM-L6-v2'):

    model = SentenceTransformer(model_name)
    embeddings = model.encode(sentences)
    return embeddings