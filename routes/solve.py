from fastapi import APIRouter, HTTPException
from models.request_models import SolveRequest, SolveResponse
from services.ai_service import ai_service

router = APIRouter()


@router.post("/solve", response_model=SolveResponse)
async def solve_math_problem(request: SolveRequest):
    """
    Analyze a student's math solution and provide step-by-step feedback
    """
    try:
        # Validate input
        if not request.problem.strip():
            raise HTTPException(status_code=400, detail="Problem cannot be empty")
        
        if not request.student_solution.strip():
            raise HTTPException(status_code=400, detail="Student solution cannot be empty")
        
        # Call AI service to analyze the solution
        result = await ai_service.analyze_solution(request.problem, request.student_solution)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
