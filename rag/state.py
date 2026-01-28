from typing import List, TypedDict, Optional
from langchain_core.documents import Document

class GraphState(TypedDict):
    question: str
    document: Optional[List[Document]]
    generation: str
    input_type: Optional[str]  # greeting, identity, thanks, help, legal_question