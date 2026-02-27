"""药物相互作用路由 - 医疗模块"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

from src.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/healthcare/drugs", tags=["healthcare"])


class DrugInteractionRequest(BaseModel):
    """药物相互作用检查请求"""
    drug_ids: List[str]
    include_food_interactions: bool = False


class DrugInteraction(BaseModel):
    """药物相互作用"""
    drug_a_id: str
    drug_a_name: str
    drug_b_id: str
    drug_b_name: str
    interaction_type: str  # CONTRAINDICATION, CAUTION, INFO
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    recommendation: str


class DrugInteractionResponse(BaseModel):
    """药物相互作用检查响应"""
    interactions: List[DrugInteraction]
    has_contraindication: bool
    summary: str


@router.post("/interactions", response_model=DrugInteractionResponse)
async def check_drug_interactions(
    request: DrugInteractionRequest,
    current_user: dict = Depends(get_current_user),
):
    """检查药物相互作用"""
    try:
        # 调用药物相互作用检查服务
        # 示例返回
        interactions = [
            DrugInteraction(
                drug_a_id="drug-1",
                drug_a_name="药物A",
                drug_b_id="drug-2",
                drug_b_name="药物B",
                interaction_type="CAUTION",
                severity="MEDIUM",
                description="两药合用可能增加副作用风险",
                recommendation="建议间隔2小时服用，监测不良反应"
            )
        ]

        return DrugInteractionResponse(
            interactions=interactions,
            has_contraindication=any(
                i.interaction_type == "CONTRAINDICATION" for i in interactions
            ),
            summary=f"发现{len(interactions)}个药物相互作用"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查失败: {str(e)}")


@router.get("/search")
async def search_drugs(
    query: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
):
    """搜索药物"""
    # 示例数据
    drugs = [
        {"id": "drug-1", "name": "药物A", "category": "抗生素"},
        {"id": "drug-2", "name": "药物B", "category": "镇痛药"},
    ]

    return {"drugs": drugs[:limit]}


@router.get("/{drug_id}/interactions")
async def get_drug_interactions(
    drug_id: str,
    current_user: dict = Depends(get_current_user),
):
    """获取指定药物的所有已知相互作用"""
    return {
        "drug_id": drug_id,
        "interactions": []
    }
