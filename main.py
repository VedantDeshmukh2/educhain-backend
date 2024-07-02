import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from typing import List
from dotenv import load_dotenv

from educhain import qna_engine, content_engine

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

# Define input models


class MCQRequest(BaseModel):
    subject: str
    grade: int
    topic: str
    num: int
    custom_instructions: str
    is_ncert: bool


class LessonPlanRequest(BaseModel):
    subject: str
    topic: str  # Added topic parameter
    grade: int
    duration: int  # Duration in minutes
    custom_instructions: str


class NCERTLessonPlan(BaseModel):
    subject: str
    topic: str
    grade: int
    duration: str
    objectives: List[str]
    prerequisites: List[str]
    introduction: str
    content_outline: List[str]
    activities: List[str]
    assessment: str
    conclusion: str
    resources: List[str]
    timeline: List[str]

# MCQ generation endpoint


@app.post("/generate-mcq", status_code=status.HTTP_200_OK)
async def api_generate_mcq_questions(request: MCQRequest):
    try:
        result = qna_engine.generate_mcq(
            subject=request.subject,
            grade=request.grade,
            topic=request.topic,
            num=request.num,
            custom_instructions=request.custom_instructions,
            is_ncert=request.is_ncert
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Lesson plan generation endpoint


@app.post("/generate-lesson-plan", status_code=status.HTTP_200_OK)
async def generate_lesson_plan_endpoint(request_body: LessonPlanRequest):
    try:
        subject = request_body.subject
        topic = request_body.topic  # Added topic parameter
        grade = request_body.grade
        duration = request_body.duration
        custom_instructions = request_body.custom_instructions
        lesson_plan = content_engine.generate_lesson_plan(
            subject=subject,
            topic=topic,  # Added topic parameter
            grade=grade,
            duration=duration,
            response_model=NCERTLessonPlan,
            custom_instructions=custom_instructions
        )
        return lesson_plan
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Lesson plan download endpoint


# @app.post("/download-lesson-plan")
# async def download_lesson_plan(lesson_plan: NCERTLessonPlan, file_format: str):
#     try:
#         if file_format.lower() == 'pdf':
#             buffer = create_pdf(lesson_plan)
#             media_type = 'application/pdf'
#             file_extension = 'pdf'
#         elif file_format.lower() == 'doc':
#             buffer = create_doc(lesson_plan)
#             media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
#             file_extension = 'docx'
#         else:
#             raise ValueError("Unsupported file format")

#         return StreamingResponse(
#             io.BytesIO(buffer.getvalue()),
#             media_type=media_type,
#             headers={
#                 "Content-Disposition": f"attachment; filename=lesson_plan.{file_extension}"}
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# Implement the create_pdf and create_doc functions here


# def create_pdf(lesson_plan):
#     # Implementation from your existing code
#     pass


# def create_doc(lesson_plan):
#     # Implementation from your existing code
#     pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
