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
    grade: str
    subject: str
    topic: str
    subtopic: str
    isNcert: bool = False
    numberOfQuestions: int = 5
    customInstructions: str = ""


class LessonPlanRequest(BaseModel):
    subject: str
    topic: str  # Added topic parameter
    grade: int
    duration: int  # Duration in minutes
    custom_instructions: str

class NCERTLessonPlan(BaseModel):
    title: str = Field(description="The title of the lesson plan")
    objectives: List[str] = Field(description="List of learning objectives for the lesson")
    lesson_outline: List[dict] = Field(description="Outline of the lesson with sections and durations")

    class Config:
        extra = "allow"  # This allows for additional fields in the data
# MCQ generation endpoint


@app.post("/generate-mcq", status_code=status.HTTP_200_OK)
async def api_generate_mcq_questions(request: MCQRequest):
    try:
        custom_ncert_template = """
        Generate {num} multiple-choice question (MCQ) based on the given topic and level.
        Provide the question, four answer options, and the correct answer.
        Topic: {topic}
        Subtopic: {subtopic}
        Subject: {subject}
        Grade: {grade}
        """

        result = qna_engine.generate_mcq(
            topic=request.topic,
            num=request.numberOfQuestions,
            subject=request.subject,
            grade=request.grade,
            custom_instructions=custom_ncert_template + request.customInstructions,
            is_ncert=request.isNcert,
            prompt_template=custom_ncert_template,
            subtopic=request.subtopic
        )
        return result
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
# Lesson plan generation endpoint


ncert_lesson_plan_template = """
Generate a comprehensive NCERT-aligned lesson plan for the given subject, topic, grade, and duration.
Ensure that the lesson plan follows NCERT guidelines and curriculum standards.

Subject: {subject}
Topic: {topic}
Grade: {grade}
Duration: {duration} minutes

Include the following details in the lesson plan:
1. Title: A concise title for the lesson plan including the duration.
2. Objectives: List 3-4 specific learning objectives that students will achieve by the end of the lesson.
3. Lesson Outline: Provide a detailed outline of the lesson, including:
   - Introduction
   - Main content sections (covering the key concepts)
   - Activities or demonstrations
   - Review and application
   - Conclusion and assessment
   For each section, include:
   - A brief description of the content or activity
   - The duration in minutes
   - Any specific instructions or notes for the teacher

Ensure that the lesson plan is culturally relevant and appropriate for Indian students, aligning with NCERT standards.
"""


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
            custom_instructions=custom_instructions,
            prompt_template=ncert_lesson_plan_template

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
