"""症状-疾病匹配路由 - 医疗模块"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

from src.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/healthcare/diagnosis", tags=["healthcare"])


class DiagnosisRequest(BaseModel):
    """症状诊断请求"""
    symptoms: List[str]
    patient_age: int | None = None
    patient_gender: str | None = None
    include_related: bool = True


class DiagnosisResponse(BaseModel):
    """症状诊断响应"""
    possible_diseases: List[dict]
    recommended_departments: List[str]
    confidence: float


@router.post("", response_model=DiagnosisResponse)
async def diagnose_symptoms(
    request: DiagnosisRequest,
    current_user: dict = Depends(get_current_user),
):
    """根据症状进行疾病诊断推荐"""
    try:
        # 调用症状匹配服务
        # 示例返回
        return DiagnosisResponse(
            possible_diseases=[
                {
                    "disease_id": "disease-1",
                    "disease_name": "示例疾病A",
                    "match_score": 0.85,
                    "matched_symptoms": ["symptom-1", "symptom-2"],
                    "description": "疾病描述...",
                    "severity": "MEDIUM"
                },
                {
                    "disease_id": "disease-2",
                    "disease_name": "示例疾病B",
                    "match_score": 0.65,
                    "matched_symptoms": ["symptom-1"],
                    "description": "疾病描述...",
                    "severity": "LOW"
                }
            ],
            recommended_departments=["内科", "呼吸科"],
            confidence=0.75
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"诊断失败: {str(e)}")


@router.get("/symptoms")
async def list_common_symptoms(
    category: str | None = None,
    current_user: dict = Depends(get_current_user),
):
    """获取常见症状列表"""
    symptoms = [
        {"id": "symptom-1", "name": "发热", "category": "全身"},
        {"id": "symptom-2", "name": "咳嗽", "category": "呼吸"},
        {"id": "symptom-3", "name": "头痛", "category": "神经"},
        {"id": "symptom-4", "name": "腹痛", "category": "消化"},
    ]

    if category:
        symptoms = [s for s in symptoms if s["category"] == category]

    return {"symptoms": symptoms}
