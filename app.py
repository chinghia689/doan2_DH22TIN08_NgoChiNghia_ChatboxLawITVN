import os
from dotenv import load_dotenv
from rag.load_split import load_split
from rag.embedding import get_embeddings
from rag.retriever import retriever
from rag.graph import RAGGraph

load_dotenv()
api_key=os.getenv('GROQ_API_KEY')
if not api_key:
    raise('Not key')

dir_file=os.path.dirname(os.path.abspath(__file__))
path_folder=os.path.join(dir_file,'data')

doc=load_split(path_folder)
embeddings=get_embeddings()
retrievers=retriever(doc,embeddings)
rag_system=RAGGraph(retrievers)
print(f'Nhap cau hoi vao day: ')
while True:
    print(f'Ban: ')
    query=input()
    if query.lower() in ['exit','quit']:
        break
    if not query.strip():
        continue

    inputs={'question':query}

    final_answer=''

    for output in rag_system.app.stream(inputs):
        for node,result in output.items():
            if 'generation' in result:
                final_answer= result['generation']
    print(f'AI: {final_answer}')

