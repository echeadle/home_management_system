from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
import json
from dotenv import load_dotenv


load_dotenv()

def create_vector_store(appliance_name, file_path):
    print(f"Creating vector store for {appliance_name}")
    try:
        with open("./appliances.json", "r") as f:
            appliances = json.load(f)
    except Exception as e:
        print(f"Error loading appliances file: {e}")
        return
    appliance = None
    for app_data in appliances:
        if app_data["name"] == appliance_name:
            appliance = app_data
            break
    if not appliance:
        print(f"Could not find appliance for {appliance_name}")
        return

    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        db = FAISS.from_documents(chunks, embeddings)
        
        print(f"Saving vector store to /app/vectorstores/{appliance['id']}/index.faiss")
        db.save_local(f"vectorstores/{appliance['id']}/index.faiss")
        print("Vector store created")

    except Exception as e:
          print(f"Error: {e}")
          return
    
if __name__ == "__main__":
     appliance_name = "Refrigerator"
     file_path = "/app/manuals/Refrigerator.pdf"
     create_vector_store(appliance_name, file_path)