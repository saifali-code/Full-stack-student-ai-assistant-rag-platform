# backend/routers/prediction.py

from fastapi import APIRouter, Depends
from backend.schemas.schemas import PredictRequest, PredictResponse
from backend.services.ml_service import predict_pass_fail
from backend.auth_utils import get_current_user
from backend.models.models import User

router = APIRouter(tags=["Prediction"])


@router.post("/predict", response_model=PredictResponse)
def predict(
    request: PredictRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Predicts whether a student will pass based on:
    - study_hours: How many hours they study per day
    - quiz_score: Their average quiz score
    - practice_count: How many quizzes they've taken
    
    Uses a trained Decision Tree ML model to make the prediction.
    """
    
    result = predict_pass_fail(
        study_hours=request.study_hours,
        quiz_score=request.quiz_score,
        practice_count=request.practice_count
    )
    
    return PredictResponse(
        prediction=result["prediction"],
        confidence=result["confidence"],
        message=result["message"]
    )