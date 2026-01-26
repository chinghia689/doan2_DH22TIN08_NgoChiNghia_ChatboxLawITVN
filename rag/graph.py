from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, StateGraph
from rag.state import GraphState
import os

class RAGGraph:
    def __init__(self,retriever_chain):
        self.retriever=retriever_chain
        # models='llama-3.3-70b-versatile'
        models='llama-3.1-8b-instant'
        self.llm=ChatGroq(
            model=models,
            temperature=0.1,
            model_kwargs={
                "presence_penalty": 0.6,  
                "frequency_penalty": 1.2
                }
            )
        self.app=self.build_graph()

    def retriever_node(self, state:GraphState):
        question=state['question']
        document=self.retriever.invoke(question)
        return ({'document':document})
    def generation_node(self, state:GraphState):
        try:
            question=state['question']
            document=state['document']

            context_parts=[]
            for doc in document:
                full_source=doc.metadata.get('source','Tai lieu khong ten')
                file_name=os.path.basename(full_source)
                formatted_chunks = (
                    f"---\n"
                    f"[TÀI LIỆU]: {file_name}\n"
                    f"[NỘI DUNG]: {doc.page_content}\n"
                    f"---"
                )
                context_parts.append(formatted_chunks)

            context_text='\n\n'.join(context_parts)

            template="""Bạn là Trợ lý Pháp lý AI chuyên nghiệp. Trả lời câu hỏi pháp luật CHÍNH XÁC dựa vào tài liệu được cung cấp.

### CONTEXT
{context}

### CÂU HỎI
{question}

### QUY TẮC TRÍCH DẪN (BẮT BUỘC)

1. **ĐỌC KỸ CÂU HỎI:**
   - Xác định CHÍNH XÁC câu hỏi: hỏi về Điều mấy? Khoản mấy? 
   - CHỈ trả lời ĐÚNG nội dung được hỏi
   - **QUAN TRỌNG:** Nếu hỏi "Điều X" mà Context KHÔNG có Điều X → trả lời "không có thông tin"

2. **Kiểm tra số Điều/Khoản:**
   - Nếu câu hỏi về Điều 5 → CHỈ tìm và trích dẫn Điều 5
   - TUYỆT ĐỐI KHÔNG trích dẫn Điều khác (Điều 4, 6...) để trả lời về Điều 5
   - Nếu Context có Điều 4, 6 nhưng KHÔNG có Điều 5 → "Tài liệu không chứa Điều 5"

3. **Xác định nguồn:** 
   - Mỗi đoạn có dòng "[TÀI LIỆU]: ..."
   - Khi trích dẫn PHẢI ghi rõ tên văn bản

4. **Trích dẫn chính xác:**
   - Có đầy đủ số điều → "Theo Điều X, [Tên luật]: '...nội dung...'"
   - Có khoản → "Theo khoản Y, Điều X, [Tên luật]: '...'"
   - KHÔNG đoán số Điều/Khoản

5. **Không có thông tin:** 
   - Trả lời: "Tài liệu không chứa thông tin về [nội dung câu hỏi cụ thể]."
   - KHÔNG viết phần "Căn cứ pháp lý" nếu không có thông tin

6. **Chống hallucination:**
   - TUYỆT ĐỐI chỉ dùng thông tin từ Context
   - KHÔNG suy đoán, KHÔNG dùng kiến thức bên ngoài
   - Tránh: "theo hiểu biết", "thông thường", "có thể"

### VÍ DỤ

**Câu hỏi:** "Điều 15 của Luật Khoa học và Công nghệ quy định gì?"

**Trả lời:**
Điều 15 quy định về trách nhiệm của tổ chức khoa học trong việc đảm bảo chất lượng hoạt động nghiên cứu và tuân thủ pháp luật.

**Căn cứ pháp lý:**
- Theo Điều 15, Luật Khoa học và Công nghệ: "Tổ chức phải chịu trách nhiệm về chất lượng sản phẩm khoa học và tuân thủ các quy chuẩn..." _(Nguồn: LUATKHOAHOCCONGNGHE.docx)_

---

**Câu hỏi:** "Điều 100 của Luật An toàn thông tin mạng là gì?"

**Trả lời:**
Tài liệu không chứa thông tin về Điều 100 của Luật An toàn thông tin mạng.

---

### ĐỊNH DẠNG TRẢ LỜI

**Câu trả lời:**
(Ngắn gọn, đúng trọng tâm, 2-4 câu)

**Căn cứ pháp lý:**
- [Trích dẫn chính xác với số điều] _(Nguồn: tên file)_

---

Hãy trả lời:
"""

            prompt=ChatPromptTemplate.from_template(template)

            chain= prompt | self.llm | StrOutputParser()

            answer=chain.invoke({'question':question,'context':context_text})

            return ({'generation':answer})
        except Exception as e:
            msg = str(e).lower()

            if 'rate limit' in msg or '429' in msg or 'quota' in msg:
                return {
                    'generation': 'Your tokens have expired'
                }
    
    def build_graph(self):
        workflow=StateGraph(GraphState)

        workflow.add_node('retriever',self.retriever_node)  
        workflow.add_node('generation',self.generation_node)

        workflow.set_entry_point('retriever')
        workflow.add_edge('retriever','generation')
        workflow.add_edge('generation',END)     
        
        return workflow.compile()