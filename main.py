import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from typing import List, Optional
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


class MCQRequest(BaseModel):
    topic: str
    num: int


class LessonPlanRequest(BaseModel):
    subject: str
    grade: int
    duration: int  # Duration in minutes


class QuestionPaperRequest(BaseModel):
    subject: str
    grade_level: int
    num_questions: int
    question_types: List[str] = ["multiple_choice"]
    time_limit: Optional[int] = None
    difficulty_level: Optional[str] = None
    topics: Optional[List[str]] = None


@app.post("/generate-mcq", status_code=status.HTTP_200_OK)
async def generate_mcq_endpoint(request_body: MCQRequest):
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


@app.post("/generate-lesson-plan", status_code=status.HTTP_200_OK)
async def generate_lesson_plan_endpoint(request_body: LessonPlanRequest):
    try:
        subject = request_body.subject
        level = request_body.level
        duration = request_body.duration
        lesson_plan = content_engine.generate_lesson_plan(
            subject=subject, level=level, duration=duration)
        return lesson_plan
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/generate-question-paper", status_code=status.HTTP_200_OK)
async def generate_question_paper_endpoint(request_body: QuestionPaperRequest):
    try:
        subject = request_body.subject
        grade_level = request_body.grade_level
        num_questions = request_body.num_questions
        question_types = request_body.question_types
        time_limit = request_body.time_limit
        difficulty_level = request_body.difficulty_level
        topics = request_body.topics

        question_paper = content_engine.generate_question_paper(
            subject=subject,
            grade_level=grade_level,
            num_questions=num_questions,
            question_types=question_types,
            time_limit=time_limit,
            difficulty_level=difficulty_level,
            topics=topics
        )
        return question_paper
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
