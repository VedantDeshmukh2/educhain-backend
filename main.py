from fastapi import FastAPI
from pydantic import BaseModel
from starlette.requests import Request

from educhain import Educhain

app = FastAPI()


@app.get("/")
def read_root():
    return {"message":"Server Running"}


class GenerateQuestionsRequest(BaseModel):
    topic: str
    num_questions: int
    difficulty: str

@app.post("/generate-questions")
async def generate_questions(request: GenerateQuestionsRequest):
    topic = request.topic
    num_questions = request.num_questions
    difficulty = request.difficulty

    generated_questions = Educhain.generate_mcq(topic=topic, level=difficulty, num=num_questions)

    return {"questions": generated_questions}



class LessonPlanGenerationParameters(BaseModel):
    topic: str
    level: str = "Beginner"

@app.post("/generate-lesson-plan")
async def generate_lesson_plan(request: Request, params: LessonPlanGenerationParameters):
    request_body = await request.json()
    params = params.dict()
    
    topic = params["topic"]
    level = params["level"]

    # Generate the lesson plan
    lesson_plan = Educhain.content_engine.generate_lesson_plan(topic, level)

    return {"lesson_plan": lesson_plan}