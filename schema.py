from pydantic import BaseModel
from typing import List, Optional, Dict

# class GradingRequest(BaseModel):
#     task_type: str
#     topic: str
#     answer: str
class Answer(BaseModel):
    data: str
    type: str


class GradingRequest(BaseModel):
    assignment_id: str
    question: str
    answers: List[Answer]
    teachers_instructions: str
    knowledge_collection_id: str
    use_course_knowledge_base: bool


class Message(BaseModel):
    role: str
    content: str

class Choice(BaseModel):
    message: Message

class GradingResponse(BaseModel):
    choices: List[Choice]

class ChatBotRequest(BaseModel):
    collections: List[str]
    conversation: List[Dict[str, str]]