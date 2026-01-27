from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

MAX_CONTEXT_LENGTH = 15000

def built_chain(retriever):
    llm=ChatGroq(
        model='llama-3.1-70b-versatile',
        temperature=0
    )

    template="""
    Bạn là trợ lý AI. Hãy trả lời câu hỏi CHỈ DỰA TRÊN THÔNG TIN TRONG LUẬT DƯỚI ĐÂY.
    Nếu không có thông tin trong Context, hãy trả lời:
    "Tôi không tìm thấy thông tin trong tài liệu."

    Context:
    {context} 

    Câu hỏi:
    {question} """

    prompt=ChatPromptTemplate.from_template(template)
    def docs_to_context(docs):
        context='\n\n'.join(d.page_content for d in docs)
        context=context[:MAX_CONTEXT_LENGTH]
        return context
    rag_chain=({
        'context':retriever|RunnableLambda(docs_to_context),
        'question':RunnablePassthrough()
    }) | prompt | llm | StrOutputParser()

    return rag_chain