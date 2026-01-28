from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, StateGraph
from rag.state import GraphState
import os
import re

# Các pattern để nhận diện câu chào hỏi
GREETING_PATTERNS = [
    r'^(hi|hello|hey|xin chào|chào|chào bạn|alo|xin lỗi|cảm ơn|thank|thanks)[\s!?.]*$',
    r'^(bạn là ai|bạn tên gì|giới thiệu|help|trợ giúp|hướng dẫn)[\s!?.]*$',
    r'^(ok|okay|được|tốt|good|nice|great)[\s!?.]*$',
]

# Response cho greeting
GREETING_RESPONSES = {
    'greeting': """Xin chào! 👋 Tôi là **Trợ lý AI Luật** - chuyên tư vấn pháp luật công nghệ thông tin.

Tôi có thể giúp bạn về:
• Luật Công nghệ thông tin
• Luật Khoa học công nghệ  
• Luật Trí tuệ nhân tạo
• Luật An toàn thông tin mạng

**Hãy đặt câu hỏi pháp lý** để tôi hỗ trợ bạn! 

Ví dụ: "Điều 5 Luật Công nghệ thông tin quy định gì?" """,
    
    'identity': """Tôi là **Trợ lý AI Luật** - một hệ thống AI được thiết kế để tư vấn pháp luật về công nghệ thông tin.

Tôi sử dụng công nghệ RAG (Retrieval-Augmented Generation) để trích xuất thông tin chính xác từ các văn bản pháp luật.

Hãy đặt câu hỏi về luật để tôi hỗ trợ bạn!""",

    'thanks': """Không có gì! 😊 Nếu bạn có thêm câu hỏi pháp lý nào, hãy hỏi tôi nhé!""",
    
    'help': """**Hướng dẫn sử dụng:**

1. Đặt câu hỏi cụ thể về pháp luật công nghệ thông tin
2. Tôi sẽ tìm kiếm trong văn bản luật và trả lời với trích dẫn chính xác
3. Mỗi câu trả lời đều có nguồn gốc từ văn bản pháp luật

**Ví dụ câu hỏi:**
- "Điều 10 Luật An toàn thông tin mạng là gì?"
- "Trách nhiệm của tổ chức theo Luật Khoa học công nghệ?"
- "Hành vi bị cấm trong Luật Công nghệ thông tin?"
"""
}

def classify_input(question: str) -> str:
    """Phân loại input: greeting, identity, thanks, help, hoặc legal_question"""
    q = question.lower().strip()
    
    # Check greeting
    if re.match(r'^(hi|hello|hey|xin chào|chào|chào bạn|alo)[\s!?.]*$', q, re.IGNORECASE):
        return 'greeting'
    
    # Check identity question
    if re.match(r'^(bạn là ai|bạn tên gì|bạn là gì|giới thiệu về bạn)[\s!?.]*$', q, re.IGNORECASE):
        return 'identity'
    
    # Check thanks
    if re.match(r'^(cảm ơn|thank|thanks|cám ơn|ok|okay|được rồi|tốt)[\s!?.]*$', q, re.IGNORECASE):
        return 'thanks'
    
    # Check help
    if re.match(r'^(help|trợ giúp|hướng dẫn|cách sử dụng)[\s!?.]*$', q, re.IGNORECASE):
        return 'help'
    
    # Default: legal question
    return 'legal_question'


class RAGGraph:
    def __init__(self,retriever_chain):
        self.retriever=retriever_chain
        models='llama-3.3-70b-versatile'
        # models='llama-3.1-8b-instant'
        self.llm=ChatGroq(
            model=models,
            temperature=0,
            model_kwargs={
                "presence_penalty": 0.6,  
                "frequency_penalty": 1.2
                }
            )
        self.app=self.build_graph()

    async def retriever_node(self, state:GraphState):
        question=state['question']
        document=await self.retriever.ainvoke(question)
        return ({'document':document})
    async def generation_node(self, state:GraphState):
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

            answer=await chain.ainvoke({'question':question,'context':context_text})

            return ({'generation':answer})
        except Exception as e:
            msg = str(e).lower()
            print(f"[ERROR] generation_node exception: {e}")  # Log để debug

            if 'rate limit' in msg or '429' in msg or 'quota' in msg:
                return {
                    'generation': 'Hệ thống đang quá tải. Vui lòng thử lại sau ít phút.'
                }
            else:
                return {
                    'generation': f'Đã xảy ra lỗi trong quá trình xử lý. Chi tiết: {str(e)}'
                }
    
    async def classifier_node(self, state: GraphState):
        """Node phân loại input: greeting hay legal question"""
        question = state['question']
        input_type = classify_input(question)
        return {'input_type': input_type}
    
    async def greeting_node(self, state: GraphState):
        """Node xử lý greeting - không cần query RAG"""
        input_type = state.get('input_type', 'greeting')
        response = GREETING_RESPONSES.get(input_type, GREETING_RESPONSES['greeting'])
        return {'generation': response}
    
    def route_by_input_type(self, state: GraphState) -> str:
        """Router: greeting/thanks/help → greeting_node, legal → retriever"""
        input_type = state.get('input_type', 'legal_question')
        if input_type in ['greeting', 'identity', 'thanks', 'help']:
            return 'greeting_node'
        return 'retriever'
    
    def build_graph(self):
        workflow = StateGraph(GraphState)

        # Thêm các nodes
        workflow.add_node('classifier', self.classifier_node)
        workflow.add_node('greeting_node', self.greeting_node)
        workflow.add_node('retriever', self.retriever_node)  
        workflow.add_node('generation', self.generation_node)

        # Entry point là classifier
        workflow.set_entry_point('classifier')
        
        # Conditional edge: sau classifier, route theo loại input
        workflow.add_conditional_edges(
            'classifier',
            self.route_by_input_type,
            {
                'greeting_node': 'greeting_node',
                'retriever': 'retriever'
            }
        )
        
        # greeting_node → END
        workflow.add_edge('greeting_node', END)
        
        # retriever → generation → END
        workflow.add_edge('retriever', 'generation')
        workflow.add_edge('generation', END)     
        
        return workflow.compile()