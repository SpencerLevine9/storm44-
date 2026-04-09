from typing import List
from pydantic import BaseModel, Field, field_validator, model_validator


class QuizRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="Topic to generate quiz questions from")
    source_ids: List[str] = Field(default_factory=list, description="Selected sources to use")
    count: int = Field(10, ge=5, le=20, description="Number of quiz questions to generate")


class QuizQuestion(BaseModel):
    question: str = Field(..., description="Quiz question")
    options: List[str] = Field(..., description="Exactly 4 multiple choice options")
    correct_answer: str = Field(..., description="Correct answer")
    explanation: str = Field(..., description="Short explanation of why the answer is correct")
   
    @field_validator("options")
    @classmethod
    def validate_options(cls, v: List[str]) -> List[str]:
        if len(v) != 4:
            raise ValueError("Quiz questions must have exactly 4 options")
        if len(set(v)) != 4:
            raise ValueError("Quiz options must be unique")
        return v

    @model_validator(mode="after")
    def validate_correct_answer_in_options(self):
        if self.correct_answer not in self.options:
            raise ValueError("correct_answer must be one of the options")
        return self




class QuizResponse(BaseModel):
    questions: List[QuizQuestion] = Field(default_factory=list, description="Generated quiz questions")