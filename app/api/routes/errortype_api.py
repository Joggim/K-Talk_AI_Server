from fastapi import APIRouter
from typing import List
from app.services.classify_error_service import classify_error_rule_final
from app.services.predict_error_service import predict_error_type
from app.api.schemas.errortype import ErrorRequest

router = APIRouter()

@router.post("/classify")
async def classify(errors: List[ErrorRequest]):
    results = []

    for error in errors:
        rule_type = classify_error_rule_final(
            error.target,
            error.user,
            error.prev,
            error.next,
            error.jamo_index_in_syllable
        )

        if rule_type == "미분류":
            predicted = predict_error_type(
                error.target,
                error.user,
                error.prev,
                error.next,
                error.jamo_index_in_syllable
            )
            error_type = f"{predicted} {error.target}"
        else:
            error_type = f"{rule_type} {error.target}"

        result = error.dict()
        result["error_type"] = error_type
        results.append(result)

    return results
