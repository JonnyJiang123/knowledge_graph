from __future__ import annotations

from enum import Enum


class RuleType(str, Enum):
    """规则类型枚举"""
    # 金融规则
    FINANCE_FRAUD = "FINANCE_FRAUD"  # 金融欺诈检测
    FINANCE_RISK = "FINANCE_RISK"  # 金融风险评估
    FINANCE_ASSOCIATION = "FINANCE_ASSOCIATION"  # 关联分析

    # 医疗规则
    HEALTHCARE_DRUG = "HEALTHCARE_DRUG"  # 药物相互作用
    HEALTHCARE_DIAGNOSIS = "HEALTHCARE_DIAGNOSIS"  # 诊疗合规
    HEALTHCARE_SYMPTOM = "HEALTHCARE_SYMPTOM"  # 症状-疾病匹配

    # 通用规则
    CUSTOM = "CUSTOM"  # 自定义规则

    @classmethod
    def has_value(cls, value: str) -> bool:
        try:
            cls(value)
            return True
        except ValueError:
            return False
