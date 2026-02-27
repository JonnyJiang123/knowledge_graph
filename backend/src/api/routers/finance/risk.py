"""信用风险评估路由 - 金融模块"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from src.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/finance/enterprises", tags=["finance"])


@router.get("/{enterprise_id}/risk")
async def get_enterprise_risk(
    enterprise_id: str,
    include_associated: bool = Query(True, description="包含关联企业风险"),
    current_user: dict = Depends(get_current_user),
):
    """获取企业信用风险评分

    综合评估:
    - 基础信用评分
    - 关联风险传播
    - 舆情风险
    - 财务健康度
    """
    try:
        # 调用风险评估服务
        return {
            "enterprise_id": enterprise_id,
            "enterprise_name": "示例企业",
            "overall_score": 75.5,
            "risk_level": "MEDIUM",
            "factors": {
                "credit_score": {
                    "value": 80,
                    "weight": 0.3,
                    "description": "基础信用评分"
                },
                "association_risk": {
                    "value": 65,
                    "weight": 0.25,
                    "description": "关联风险传播"
                },
                "sentiment_risk": {
                    "value": 85,
                    "weight": 0.2,
                    "description": "舆情风险"
                },
                "financial_health": {
                    "value": 70,
                    "weight": 0.25,
                    "description": "财务健康度"
                }
            },
            "associated_risks": [] if not include_associated else [
                {"enterprise_id": "assoc-1", "risk_level": "HIGH", "impact": 0.15}
            ],
            "updated_at": "2026-02-27T10:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"风险评估失败: {str(e)}")


@router.get("/{enterprise_id}/risk/report")
async def get_risk_report(
    enterprise_id: str,
    report_type: str = Query("comprehensive", enum=["comprehensive", "summary"]),
    current_user: dict = Depends(get_current_user),
):
    """获取企业风险报告"""
    return {
        "enterprise_id": enterprise_id,
        "report_type": report_type,
        "generated_at": "2026-02-27T10:00:00Z",
        "sections": [
            {"title": "执行摘要", "content": "..."},
            {"title": "风险分析", "content": "..."},
            {"title": "关联分析", "content": "..."},
            {"title": "建议措施", "content": "..."}
        ]
    }
