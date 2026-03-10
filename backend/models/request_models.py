from pydantic import BaseModel
from typing import List


class StepAnalysis(BaseModel):
    step: str
    status: str  # 'correct' | 'incorrect'
    explanation: str


class SolveRequest(BaseModel):
    problem: str
    student_solution: str


class SolveResponse(BaseModel):
    analysis: List[StepAnalysis]
    correct_solution: str
