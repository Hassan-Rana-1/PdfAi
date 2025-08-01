# import required libraries
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
import InstructorEmbedding 
from langchain_community.llms import HuggingFaceHub

# Extract text from uploaded PDFs
def get_pdf_text(pdf_docs):
    text =""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Split the text from PDfs into smaller chunkz
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator = "\n\n",
        chunk_size = 1000,
        chunk_overlap = 200,
        length_function = len 
    )

    chunks = text_splitter.split_text(text)
    return chunks

# vector embedding and storing using FAISS
def get_vectorstore(text_chunks):
    embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

# using HuggingFace llm as ai gets conversation chain
def get_conversation_chain(vectorstore):
    llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":1024, "max_new_tokens": 50})
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(llm = llm, retriever=vectorstore.as_retriever(), memory = memory)
    return conversation_chain
    


def main():
    load_dotenv() 
    st.set_page_config(page_title="chat with multiple PDFs", page_icon=":books:")

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    st.header("Chat with multiple PDFs :books:")
    st.text_input("Ask a question about your documents:")

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
              # get pdf text
              raw_text = get_pdf_text(pdf_docs)

              # get the text chunks
              text_chunks = get_text_chunks(raw_text)
              # st.write(text_chunks)

              # create vector store
              vectorstore = get_vectorstore(text_chunks)

              # conversation chain
              st.session_state.conversation = get_conversation_chain(vectorstore)

    

if __name__ == '__main__':
    main()