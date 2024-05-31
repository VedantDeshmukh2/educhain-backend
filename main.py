import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

from educhain import qna_engine

# Load environment variables
load_dotenv()


app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://educhain.in",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root path
@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Server is running"}


# Define the data model
class GenerateMCQRequest(BaseModel):
    topic: str
    num: int


@app.post("/generate-mcq", status_code=status.HTTP_200_OK)
async def generate_mcq_endpoint(request_body: GenerateMCQRequest):
    try:
        topic = request_body.topic
        num = request_body.num
        questions = qna_engine.generate_mcq(topic=topic, num=num)
        return questions
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
