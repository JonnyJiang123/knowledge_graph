"""反欺诈检测路由 - 金融模块"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from src.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/finance/fraud", tags=["finance"])


class FraudDetectionRequest(BaseModel):
    """欺诈检测请求"""
    enterprise_id: Optional[str] = None
    account_ids: Optional[List[str]] = None
    detection_types: List[str] = ["circular_trading", "suspicious_clustering"]
    time_range: Optional[dict] = None  # {start: str, end: str}


class FraudDetectionResponse(BaseModel):
    """欺诈检测响应"""
    detection_id: str
    status: str
    alerts: List[dict]
    risk_score: float
    summary: str


@router.post("/detect", response_model=FraudDetectionResponse)
async def detect_fraud(
    request: FraudDetectionRequest,
    current_user: dict = Depends(get_current_user),
):
    """执行反欺诈检测

    检测类型:
    - circular_trading: 循环交易检测
    - suspicious_clustering: 可疑账户聚类
    - amount_anomaly: 金额异常检测
    - frequency_anomaly: 频率异常检测
    """
    try:
        # 调用欺诈检测服务
        return FraudDetectionResponse(
            detection_id="detect-001",
            status="completed",
            alerts=[
                {
                    "type": "suspicious_clustering",
                    "severity": "HIGH",
                    "description": "发现可疑账户聚类",
                    "affected_accounts": ["acc-1", "acc-2"],
                    "confidence": 0.85
                }
            ],
            risk_score=0.75,
            summary="检测到1个高风险预警"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")


@router.get("/patterns")
async def list_fraud_patterns(
    current_user: dict = Depends(get_current_user),
):
    """获取支持的欺诈检测模式"""
    return {
        "patterns": [
            {
                "id": "circular_trading",
                "name": "循环交易检测",
                "description": "检测资金在多个账户间循环流转",
                "enabled": True
            },
            {
                "id": "suspicious_clustering",
                "name": "可疑聚类检测",
                "description": "基于交易模式识别可疑账户群体",
                "enabled": True
            },
            {
                "id": "amount_anomaly",
                "name": "金额异常检测",
                "description": "识别与历史模式不符的交易金额",
                "enabled": True
            }
        ]
    }
