import os
import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
request_lock = asyncio.Lock()  # Lock để tránh rate limit khi gửi đồng thời


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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        async with request_lock:  # Xử lý tuần tự để tránh Groq rate limit
            inputs = {"question": req.question}
            result = await rag_system.app.ainvoke(inputs)
            answer = result.get("generation")
        
        if answer is None:
            answer = "Không thể xử lý câu hỏi. Vui lòng thử lại."
        
        return ChatResponse(answer=answer)
    except Exception as e:
        print(f"[ERROR] chat_endpoint: {e}")
        return ChatResponse(answer=f"Lỗi server: {str(e)}")
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1, reload=False)
