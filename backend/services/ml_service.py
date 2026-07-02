# backend/services/ml_service.py

import pickle
import numpy as np
import os

# Path to the saved model
MODEL_PATH = os.path.join("ml_model", "model.pkl")

# Load the model when this module is first imported
# (We load it once, not on every prediction — for efficiency)
_model_data = None

def _load_model():
    """Loads the ML model from disk. Returns None if not found."""
    global _model_data
    
    if _model_data is not None:
        return _model_data  # Already loaded
    
    if not os.path.exists(MODEL_PATH):
        return None  # Model not trained yet
    
    with open(MODEL_PATH, 'rb') as f:
        _model_data = pickle.load(f)
    
    return _model_data


def predict_pass_fail(study_hours: float, quiz_score: float, practice_count: int) -> dict:
    """
    Predicts whether a student will pass or fail.
    
    Args:
        study_hours: Hours studied per day
        quiz_score: Average quiz score (0-100)
        practice_count: Number of practice quizzes taken
    
    Returns:
        dict with 'prediction', 'confidence', 'message'
    """
    
    model_data = _load_model()
    
    if model_data is None:
        # Model hasn't been trained yet — use simple rule-based fallback
        return _rule_based_prediction(study_hours, quiz_score, practice_count)
    
    model = model_data['model']
    scaler = model_data['scaler']
    
    # Prepare input (must be 2D array for sklearn)
    features = np.array([[study_hours, quiz_score, practice_count]])
    
    # Scale using the SAME scaler used during training
    features_scaled = scaler.transform(features)
    
    # Get prediction (0 = FAIL, 1 = PASS)
    prediction_code = model.predict(features_scaled)[0]
    
    # Get probabilities [P(fail), P(pass)]
    probabilities = model.predict_proba(features_scaled)[0]
    confidence = float(max(probabilities))
    
    prediction_label = "PASS" if prediction_code == 1 else "FAIL"
    
    # Create a helpful message
    message = _create_message(prediction_label, confidence, study_hours, quiz_score, practice_count)
    
    return {
        "prediction": prediction_label,
        "confidence": round(confidence, 2),
        "message": message
    }


def _rule_based_prediction(study_hours: float, quiz_score: float, practice_count: int) -> dict:
    """
    Fallback when ML model is not trained yet.
    Uses simple rules to make a prediction.
    """
    score = 0
    
    if study_hours >= 3:
        score += 1
    if quiz_score >= 60:
        score += 1
    if practice_count >= 5:
        score += 1
    
    if score >= 2:
        return {
            "prediction": "PASS",
            "confidence": 0.65,
            "message": "Based on your study habits, you're on track to pass! (Using rule-based prediction — train the ML model for better accuracy)"
        }
    else:
        return {
            "prediction": "FAIL",
            "confidence": 0.65,
            "message": "You might need to study more. Consider increasing study hours and practice. (Using rule-based prediction)"
        }


def _create_message(prediction: str, confidence: float, study_hours, quiz_score, practice_count) -> str:
    """Creates a personalized, helpful message based on the prediction."""
    
    conf_pct = int(confidence * 100)
    
    if prediction == "PASS":
        msg = f"Great news! The model predicts you will PASS with {conf_pct}% confidence. "
        
        # Add specific advice
        if study_hours < 3:
            msg += "Try to increase your daily study time for even better results. "
        if quiz_score < 75:
            msg += "Keep practicing quizzes to improve your scores. "
        if practice_count < 10:
            msg += "More practice tests will strengthen your knowledge. "
        
        if study_hours >= 3 and quiz_score >= 75:
            msg += "You're doing excellent! Keep it up! 🌟"
            
    else:  # FAIL
        msg = f"The model predicts you might struggle. Confidence: {conf_pct}%. "
        msg += "Don't worry — here's how to improve:\n"
        
        if study_hours < 2:
            msg += f"• Increase study time (currently {study_hours}h/day, aim for 3+)\n"
        if quiz_score < 60:
            msg += f"• Focus on improving quiz scores (currently {quiz_score}%, aim for 70+)\n"
        if practice_count < 5:
            msg += f"• Take more practice quizzes (currently {practice_count}, aim for 10+)\n"
        
        msg += "You can improve! Start with small daily improvements. 💪"
    
    return msg