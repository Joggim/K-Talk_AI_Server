from fastapi import APIRouter
from app.services.classify_error_service import classify_error_rule_final
from app.services.predict_error_service import predict_error_type
from app.api.schemas.errortype import ErrorRequest

router = APIRouter()

@router.post("/classify")
async def classify(error: ErrorRequest):
    rule_type = classify_error_rule_final(
        error.target,
        error.user,
        error.prev,
        error.next,
        error.jamo_index_in_syllable
    )

    if rule_type == "미분류":
        error_type = predict_error_type(
            error.target,
            error.user,
            error.prev,
            error.next,
            error.jamo_index_in_syllable
        )
    else:
        error_type = rule_type

    return {"final_result": f"{error_type} {error.target}"}