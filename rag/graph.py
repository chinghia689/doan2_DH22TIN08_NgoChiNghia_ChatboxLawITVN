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
            temperature=0
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

            template="""
            ### VAI TRÒ
            Bạn là Trợ lý Pháp lý AI chuyên sâu (Senior Legal AI Assistant).
            Nhiệm vụ của bạn là tra cứu và trả lời câu hỏi pháp luật dựa trên dữ liệu được cung cấp.
            Phong cách trả lời: Chuyên nghiệp – Khách quan – Chính xác từng từ ngữ.

            ### DỮ LIỆU ĐẦU VÀO (CONTEXT)
            {context}

            ### CÂU HỎI
            {question}

            ### HƯỚNG DẪN XỬ LÝ (BẮT BUỘC)

            1. **XÁC ĐỊNH NGUỒN LUẬT**
            - Mỗi đoạn Context đều được đánh dấu bằng dòng "[TÀI LIỆU]: ...".
            - Khi trích dẫn, BẮT BUỘC phải nhắc đến tên văn bản này (Ví dụ: "Theo Luật Khoa học Công nghệ...").
            - Tuyệt đối không trích dẫn râu ông nọ cắm cằm bà kia.

            2. **TRÍCH DẪN PHÁP LÝ**
            - Nếu xác định rõ: "Theo quy định tại khoản X, Điều Y, [Tên luật]..."
            - Nếu không xác định rõ: "Theo quy định trong [Tên luật]..."
            - Không đoán số Điều/Khoản nếu tài liệu không ghi rõ.

            3. **KHÔNG CÓ THÔNG TIN**
            - Trả lời nguyên văn:
            "Tài liệu được cung cấp không chứa thông tin để trả lời câu hỏi này."

            ### ĐỊNH DẠNG CÂU TRẢ LỜI

            **1. Câu trả lời trực tiếp:**
            (Trả lời ngắn gọn, đúng trọng tâm).

            **2. Căn cứ pháp lý:**
            - Trích dẫn nội dung liên quan.
            - Nguồn: [Ghi tên file tài liệu tại đây]

            ---
            **LƯU Ý ĐẶC BIỆT**
            - Với câu hỏi "Ai ban hành": chỉ trả lời nếu Context có nêu rõ cơ quan ban hành.
            - Không sử dụng các cụm từ suy đoán như: "theo hiểu biết", "thông thường".
            - Chỉ dùng: "Theo tài liệu được cung cấp".

            ### BẮT ĐẦU TRẢ LỜI:
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