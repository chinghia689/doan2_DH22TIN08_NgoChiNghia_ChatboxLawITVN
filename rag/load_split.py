import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredWordDocumentLoader

def load_split(folder_path):
    all_file=[]

    file=os.listdir(folder_path)

    file_w=[f for f in file if f.endswith('.docx')]

    for file_name in file_w:
        file_path=os.path.join(folder_path,file_name)

        loader=UnstructuredWordDocumentLoader(file_path)
        docs=loader.load()

        all_file.extend(docs)

    spliter=RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=200
    )
    return spliter.split_documents(all_file)