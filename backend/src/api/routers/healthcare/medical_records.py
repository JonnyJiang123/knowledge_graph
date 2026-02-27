"""病历质控路由 - 医疗模块"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

from src.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/healthcare/records", tags=["healthcare"])


class MedicalRecordQCRequest(BaseModel):
    """病历质控请求"""
    record_id: str
    record_content: dict
    check_rules: List[str] | None = None


class QCReport(BaseModel):
    """质控报告"""
    record_id: str
    overall_score: float
    issues: List[dict]
    suggestions: List[str]
    checked_at: datetime


@router.post("/qc", response_model=QCReport)
async def check_medical_record(
    request: MedicalRecordQCRequest,
    current_user: dict = Depends(get_current_user),
):
    """执行病历质量检查"""
    try:
        # 调用病历质控服务
        # 示例返回
        return QCReport(
            record_id=request.record_id,
            overall_score=85.5,
            issues=[
                {
                    "type": "MISSING_FIELD",
                    "field": "家族史",
                    "severity": "MEDIUM",
                    "message": "家族史字段未填写"
                },
                {
                    "type": "LOGIC_ERROR",
                    "field": "诊断与症状",
                    "severity": "LOW",
                    "message": "诊断与症状描述存在不一致"
                }
            ],
            suggestions=[
                "建议补充完整的家族史信息",
                "请核实诊断与症状的匹配性"
            ],
            checked_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查失败: {str(e)}")


@router.get("/qc/rules")
async def list_qc_rules(
    current_user: dict = Depends(get_current_user),
):
    """获取病历质控规则列表"""
    return {
        "rules": [
            {
                "id": "rule-1",
                "name": "必填字段检查",
                "description": "检查病历中的必填字段是否完整",
                "category": "完整性",
                "enabled": True
            },
            {
                "id": "rule-2",
                "name": "诊断-症状一致性检查",
                "description": "检查诊断与症状描述是否一致",
                "category": "逻辑性",
                "enabled": True
            },
            {
                "id": "rule-3",
                "name": "用药-诊断匹配检查",
                "description": "检查用药是否符合诊断",
                "category": "合理性",
                "enabled": True
            }
        ]
    }
