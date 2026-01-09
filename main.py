import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from rag.load_split import load_split         
from rag.embedding import get_embeddings  
from rag.retriever import retriever        
from rag.graph import RAGGraph

load_dotenv()
api_key=os.getenv('GROQ_API_KEY')
if not api_key:
    raise ValueError('Not key')

rag_system = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_system

    current_dir=os.path.dirname(os.path.abspath(__file__))
    data_path=os.path.join(current_dir,'data')

    docs=load_split(data_path)
    embeddings=get_embeddings()
    retriever_chain=retriever(docs,embeddings)
    rag_system=RAGGraph(retriever_chain)

    yield #startup-shutdown

app = FastAPI(lifespan=lifespan)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
        inputs = {"question": req.question}
        result = await rag_system.app.ainvoke(inputs)
        answer = result.get("generation", "Lỗi xử lý")
        return ChatResponse(answer=answer)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
