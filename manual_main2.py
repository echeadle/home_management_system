from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
import json
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

app = FastAPI()

class ManualUpload(BaseModel):
    appliance_name: str
    file_path: str

class QueryRequest(BaseModel):
    query: str

class Appliance(BaseModel):
     id: int
     name: str
     model_number: str

def load_appliances():
    print("Loading appliances...")
    with open("/app/appliances.json", "r") as f:
        print("Loading appliances successful...")
        return json.load(f)


def get_appliance(appliance_name):
    print(f"Getting {appliance_name}...")
    appliances = load_appliances()
    for appliance in appliances:
          if appliance["name"] == appliance_name:
              print(f"Found {appliance_name}...")
              return appliance
    print(f"Did not find {appliance_name}")
    return None

@app.post("/manuals")
def add_manual(manual: ManualUpload):
    appliance = get_appliance(manual.appliance_name)
    if not appliance:
        print("Appliance not found")
        raise HTTPException(status_code=404, detail="No appliance found")
    
    try:
        print(f"Adding manual from {manual.file_path}...")
        with open("/app/log.txt", "a") as f:
            f.write(f"Adding manual from {manual.file_path}...\n")
        loader = PyPDFLoader(manual.file_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        db = FAISS.from_documents(chunks, embeddings)
        
        print(f"Saving vector store to vectorstores/{appliance['id']}/index.faiss")
        with open("/app/log.txt", "a") as f:
             f.write(f"Saving vector store to vectorstores/{appliance['id']}/index.faiss\n")
        db.save_local(f"vectorstores/{appliance['id']}/index.faiss")
        return {"message": f"Manual ingested for {appliance['name']}"}
    except Exception as e:
          print(f"Error: {e}")
          with open("/app/log.txt", "a") as f:
            f.write(f"Error: {e}\n")
          raise HTTPException(status_code=500, detail="Error ingesting manual")

@app.post("/query/{appliance_name}")
def query_manual(appliance_name: str, query_request: QueryRequest):
    appliance = get_appliance(appliance_name)
    if not appliance:
          raise HTTPException(status_code=404, detail="No appliance found")

    try:
        print(f"Querying {appliance_name}...")
        with open("/app/log.txt", "a") as f:
            f.write(f"Querying {appliance_name}...\n")
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        print(f"Loading vector store from vectorstores/{appliance['id']}/index.faiss")
        with open("/app/log.txt", "a") as f:
            f.write(f"Loading vector store from vectorstores/{appliance['id']}/index.faiss\n")
        db = FAISS.load_local(f"vectorstores/{appliance['id']}/index.faiss", embeddings, allow_dangerous_deserialization=True)
        llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-2024-05-13")
        prompt = PromptTemplate.from_template("Use the context to answer the following question: {question} \n\n Context:{context}")
        retriever = db.as_retriever()
        retrieval_chain = create_retrieval_chain(llm, retriever)
        response = retrieval_chain | StrOutputParser()
        response = response.invoke({"question": query_request.query})
        return {"results":response}
    except Exception as e:
        print(f"Error: {e}")
        with open("/app/log.txt", "a") as f:
             f.write(f"Error: {e}\n")
        raise HTTPException(status_code=500, detail="Error querying manual")