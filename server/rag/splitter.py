from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(docs):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )

    return splitter.split_documents(docs)
