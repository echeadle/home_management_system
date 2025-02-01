from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class ManualUpload(BaseModel):
    appliance_name: str
    file_path: str

@app.post("/manuals")
def add_manual(manual: ManualUpload):
    return {"message": "Manual Uploaded"}