from langchain_huggingface import HuggingFaceEmbeddings

def get_embeddings():
    embeddings=HuggingFaceEmbeddings(
        model_name='bkai-foundation-models/vietnamese-bi-encoder',
        model_kwargs={'device':'cpu'},
        encode_kwargs={"normalize_embeddings": True}
    )
    return embeddings
