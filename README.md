# Chatbot Luật Việt Nam - RAG Web Application

Hệ thống chatbot tư vấn pháp luật công nghệ thông tin sử dụng RAG (Retrieval-Augmented Generation) và LLM.

## 🚀 Tính năng

- ✅ **Chat AI thông minh**: Trả lời câu hỏi về luật công nghệ thông tin
- ✅ **RAG Pipeline**: Hybrid retrieval (ChromaDB + BM25)
- ✅ **Web Interface hiện đại**: React + Vite với glassmorphism design
- ✅ **Dark/Light Mode**: Chuyển đổi theme dễ dàng
- ✅ **Responsive Design**: Hoạt động tốt trên mọi thiết bị
- ✅ **Markdown Support**: Hiển thị câu trả lời định dạng đẹp
- ✅ **Desktop App**: Giao diện CustomTkinter (tùy chọn)

## 📦 Cài đặt

### Backend

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Tạo file .env
cp .env.example .env
# Chỉnh sửa .env và thêm GROQ_API_KEY

# Chạy server
python main.py
```

Server sẽ chạy tại: `http://localhost:8000`

### Frontend Web

```bash
# Di chuyển vào thư mục frontend
cd frontend

# Cài đặt dependencies
npm install

# Chạy development server
npm run dev
```

Web interface sẽ chạy tại: `http://localhost:5173`

## 🏗️ Cấu trúc dự án

```
DO_AN_RAG_Ve_Luat/
├── main.py                   # FastAPI backend
├── rag/                      # RAG pipeline modules
│   ├── load_split.py        # Document loader
│   ├── embedding.py         # Vietnamese embeddings
│   ├── retriever.py         # Hybrid retrieval
│   ├── chain.py             # LLM chain
│   ├── graph.py             # RAG graph workflow
│   └── state.py             # State management
├── data/                     # Law documents (.docx)
├── chroma_db/               # Vector database
├── frontend/                # React web interface
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── ChatInterface.tsx
│   │   │   └── MessageBubble.tsx
│   │   ├── services/        # API service
│   │   └── index.css        # Global styles
│   └── package.json
└── client_chatbox_app.py    # Desktop app (CustomTkinter)
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Web framework
- **LangChain**: RAG orchestration
- **ChromaDB**: Vector database
- **BM25**: Sparse retrieval
- **Groq**: LLM provider (Llama 3.1)
- **HuggingFace**: Vietnamese embeddings

### Frontend
- **React 18**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Axios**: HTTP client
- **react-markdown**: Markdown rendering
- **lucide-react**: Icons

## 📚 Văn bản luật được hỗ trợ

1. Luật An ninh mạng
2. Luật An toàn thông tin mạng
3. Luật Chuyển giao công nghệ
4. Luật Công nghệ thông tin
5. Luật Khoa học công nghệ
6. Luật Trí tuệ nhân tạo

## 🎨 UI Features

- **Glassmorphism Design**: Giao diện hiện đại với hiệu ứng kính mờ
- **Gradient Accents**: Màu sắc gradient đẹp mắt
- **Smooth Animations**: Chuyển động mượt mà
- **Auto-scroll**: Tự động cuộn xuống tin nhắn mới
- **Loading States**: Hiển thị trạng thái đang xử lý
- **Copy Message**: Sao chép câu trả lời
- **Keyboard Shortcuts**: Enter để gửi, Shift+Enter để xuống dòng

## 🔧 Cấu hình

### Environment Variables

```env
# Backend (.env)
GROQ_API_KEY=your_groq_api_key_here

# Frontend (.env)
VITE_API_URL=http://localhost:8000
```

## 🚀 Deployment

### Build Frontend

```bash
cd frontend
npm run build
```

### Production Backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📝 API Documentation

Truy cập `http://localhost:8000/docs` để xem API documentation (Swagger UI)

### Endpoint

- `POST /chat`: Gửi câu hỏi và nhận câu trả lời

**Request:**
```json
{
  "question": "Tuổi nghỉ hưu theo luật lao động là bao nhiêu?"
}
```

**Response:**
```json
{
  "answer": "Theo quy định tại Điều X, Luật Lao động..."
}
```

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo pull request hoặc mở issue.

## 📄 License

MIT License

## 👨‍💻 Tác giả

Dự án đồ án về RAG cho tư vấn luật Việt Nam
