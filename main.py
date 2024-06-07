import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, ValidationError
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


# Define the data model
class GenerateMCQRequest(BaseModel):
    topic: str
    num: int


class GenerateLessonPlanRequest(BaseModel):
    subject: str
    grade: int
    duration: int  # Duration in minutes


class GenerateQuestionPaperRequest(BaseModel):
    subject: str
    grade_level: int
    num_questions: int
    question_types: List[str] = ['multiple_choice',
                                 'fill_in_the_blank', 'short_answer']
    time_limit: Optional[int] = None  # Time limit in minutes
    difficulty_level: Optional[str] = None  # e.g., 'easy', 'medium', 'hard'
    topics: Optional[List[str]] = None  # List of specific topics to include


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


@app.post("/generate-lesson-plan", status_code=status.HTTP_200_OK)
async def generate_lesson_plan_endpoint(request_body: GenerateLessonPlanRequest):
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


# @app.post("/generate-question-paper", status_code=status.HTTP_200_OK)
# async def generate_question_paper_endpoint(request_body: GenerateQuestionPaperRequest):
#     try:
#         subject = request_body.subject
#         grade_level = request_body.grade_level
#         num_questions = request_body.num_questions
#         question_types = request_body.question_types
#         time_limit = request_body.time_limit
#         difficulty_level = request_body.difficulty_level
#         topics = request_body.topics

#         question_paper = question_paper_generator.generate(
#             subject=subject,
#             grade_level=grade_level,
#             num_questions=num_questions,
#             question_types=question_types,
#             time_limit=time_limit,
#             difficulty_level=difficulty_level,
#             topics=topics
#         )
#         return question_paper
#     except ValidationError as e:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
