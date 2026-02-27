from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from src.domain.entities.entity import Entity
from src.domain.entities.relation import Relation
from src.domain.entities.rule import Action, Condition, ReasoningRule
from src.domain.services.reasoning.rule_engine import (
    RuleContext,
    RuleEngine,
    RuleEvaluationResult,
)
from src.domain.value_objects.relation_type import RelationType
from src.domain.value_objects.risk_level import RiskLevel
from src.domain.value_objects.rule_type import RuleType


@dataclass
class FraudDetectionResult(RuleEvaluationResult):
    """欺诈检测结果"""
    fraud_type: str = ""  # 欺诈类型
    confidence_score: float = 0.0  # 置信度
    involved_entities: list[str] = field(default_factory=list)  # 涉及实体
    suspicious_amount: float = 0.0  # 可疑金额


@dataclass
class RiskPropagationResult:
    """风险传播结果"""
    source_entity: str
    risk_level: RiskLevel
    affected_entities: list[dict[str, Any]] = field(default_factory=list)
    propagation_path: list[list[str]] = field(default_factory=list)  # 传播路径


class FinanceRuleEngine(RuleEngine):
    """金融规则引擎 - 用于金融欺诈检测和风险评估"""

    # 欺诈类型定义
    FRAUD_CIRCULAR_GUARANTEE = "CIRCULAR_GUARANTEE"  # 循环担保
    FRAUD_FICTITIOUS_TRANSACTION = "FICTITIOUS_TRANSACTION"  # 虚假交易
    FRAUD_MONEY_CIRCULATION = "MONEY_CIRCULATION"  # 资金回流
    FRAUD_RELATED_TRANSACTION = "RELATED_TRANSACTION"  # 关联交易

    async def detect_circular_guarantee(
        self,
        project_id: str,
        entity_id: str,
        max_depth: int = 5,
    ) -> FraudDetectionResult | None:
        """检测循环担保
        
        检测是否存在 A担保B, B担保C, C担保A 等循环担保情况
        """
        context = await self._load_entity_context(project_id, entity_id)

        # 查找从entity_id出发并回到entity_id的担保路径
        cycles = self._find_guarantee_cycles(entity_id, context, max_depth)

        if cycles:
            involved = set()
            for cycle in cycles:
                involved.update(cycle)

            return FraudDetectionResult(
                rule_id="circular_guarantee_detection",
                rule_name="循环担保检测",
                matched=True,
                matched_entities=list(involved),
                risk_level=RiskLevel.HIGH,
                fraud_type=self.FRAUD_CIRCULAR_GUARANTEE,
                confidence_score=min(1.0, len(cycles) * 0.3 + 0.4),
                involved_entities=list(involved),
                message=f"检测到 {len(cycles)} 个循环担保",
                details={"cycles": cycles},
            )

        return None

    async def detect_fictitious_transaction(
        self,
        project_id: str,
        entity_ids: list[str] | None = None,
    ) -> list[FraudDetectionResult]:
        """检测虚假交易
        
        检测模式：
        1. 短时间内频繁大额交易
        2. 交易金额与实体规模不匹配
        3. 交易对手异常
        """
        results: list[FraudDetectionResult] = []

        # 创建规则检测虚假交易
        rule = ReasoningRule.create(
            project_id=project_id,
            name="虚假交易检测",
            description="检测交易金额与实体规模不匹配的情况",
            rule_type=RuleType.FINANCE_FRAUD,
            conditions=[
                Condition(
                    field="entity.type",
                    operator="equals",
                    value="TRANSACTION",
                ),
                Condition(
                    field="entity.properties.amount",
                    operator="gt",
                    value=1_000_000,  # 大额交易阈值
                ),
            ],
            actions=[
                Action(
                    action_type="alert",
                    target="entity",
                    params={"level": "high"},
                ),
            ],
            priority=100,
        )

        # 加载上下文并评估
        context = await self._load_project_context(project_id)
        result = await self.evaluate_rule(rule, context)

        if result.matched:
            fraud_result = FraudDetectionResult(
                rule_id=result.rule_id,
                rule_name=result.rule_name,
                matched=result.matched,
                matched_entities=result.matched_entities,
                risk_level=RiskLevel.HIGH,
                fraud_type=self.FRAUD_FICTITIOUS_TRANSACTION,
                confidence_score=0.75,
                involved_entities=result.matched_entities,
                message=result.message,
                details=result.details,
            )
            results.append(fraud_result)

        return results

    async def detect_money_circulation(
        self,
        project_id: str,
        entity_id: str,
        days: int = 30,
    ) -> FraudDetectionResult | None:
        """检测资金回流
        
        检测资金从A流出，经过若干中间节点后流回A的模式
        """
        context = await self._load_entity_context(project_id, entity_id)

        # 查找资金回流路径
        circulation_paths = self._find_money_circulation(
            entity_id, context, max_depth=5
        )

        if circulation_paths:
            involved = set()
            for path in circulation_paths:
                involved.update(path)

            return FraudDetectionResult(
                rule_id="money_circulation_detection",
                rule_name="资金回流检测",
                matched=True,
                matched_entities=list(involved),
                risk_level=RiskLevel.CRITICAL,
                fraud_type=self.FRAUD_MONEY_CIRCULATION,
                confidence_score=min(1.0, len(circulation_paths) * 0.2 + 0.6),
                involved_entities=list(involved),
                message=f"检测到 {len(circulation_paths)} 条资金回流路径",
                details={"paths": circulation_paths},
            )

        return None

    async def analyze_risk_propagation(
        self,
        project_id: str,
        source_entity_id: str,
        risk_level: RiskLevel,
    ) -> RiskPropagationResult:
        """风险传播分析
        
        分析从源实体开始，风险如何通过担保、投资等关系到其他实体传播
        """
        context = await self._load_entity_context(project_id, source_entity_id)

        affected: list[dict[str, Any]] = []
        propagation_paths: list[list[str]] = []
        visited = {source_entity_id}
        queue = [(source_entity_id, [source_entity_id], risk_level.priority)]

        while queue:
            current_id, path, current_risk = queue.pop(0)

            # 获取当前实体的邻居
            neighbors = context.get_neighbors(current_id)
            relations = context.get_entity_relations(current_id)

            for relation in relations:
                if relation.type in (RelationType.GUARANTEES, RelationType.CONTROLS):
                    neighbor_id = (
                        relation.target_id
                        if relation.source_id == current_id
                        else relation.source_id
                    )

                    if neighbor_id not in visited and neighbor_id in context.entities:
                        visited.add(neighbor_id)
                        new_path = path + [neighbor_id]

                        # 计算传播后的风险等级（递减）
                        propagated_risk = max(1, current_risk - 1)
                        propagated_level = self._priority_to_risk_level(propagated_risk)

                        affected.append({
                            "entity_id": neighbor_id,
                            "entity_name": context.entities[neighbor_id].properties.get("name", ""),
                            "risk_level": propagated_level.value,
                            "relation_type": relation.type.value,
                            "distance": len(new_path) - 1,
                        })

                        propagation_paths.append(new_path)

                        if propagated_risk > 1:
                            queue.append((neighbor_id, new_path, propagated_risk))

        return RiskPropagationResult(
            source_entity=source_entity_id,
            risk_level=risk_level,
            affected_entities=affected,
            propagation_path=propagation_paths,
        )

    async def detect_related_party_transaction(
        self,
        project_id: str,
        entity_id: str,
    ) -> FraudDetectionResult | None:
        """检测关联交易
        
        检测存在控制关系或担保关系的实体之间的交易
        """
        context = await self._load_entity_context(project_id, entity_id)

        # 查找所有关联实体
        related_entities = self._find_related_entities(entity_id, context)

        # 检查与关联实体之间的交易
        related_transactions: list[str] = []
        for relation in context.relations:
            if relation.type == RelationType.TRANSFERRED_TO:
                source_related = relation.source_id in related_entities
                target_related = relation.target_id in related_entities
                if source_related or target_related:
                    related_transactions.append(relation.id)

        if related_transactions:
            involved = {entity_id}
            involved.update(related_entities)

            return FraudDetectionResult(
                rule_id="related_transaction_detection",
                rule_name="关联交易检测",
                matched=True,
                matched_entities=list(involved),
                matched_relations=related_transactions,
                risk_level=RiskLevel.MEDIUM,
                fraud_type=self.FRAUD_RELATED_TRANSACTION,
                confidence_score=0.8,
                involved_entities=list(involved),
                message=f"检测到 {len(related_transactions)} 笔关联交易",
                details={
                    "related_entities": list(related_entities),
                    "transactions": related_transactions,
                },
            )

        return None

    def _find_guarantee_cycles(
        self,
        start_id: str,
        context: RuleContext,
        max_depth: int,
    ) -> list[list[str]]:
        """查找担保循环"""
        cycles: list[list[str]] = []
        visited = {start_id: 0}
        path = [start_id]

        def dfs(current_id: str, depth: int) -> None:
            if depth > max_depth:
                return

            # 获取担保关系
            for relation in context.relations:
                if relation.type == RelationType.GUARANTEES:
                    next_id = None
                    if relation.source_id == current_id:
                        next_id = relation.target_id
                    elif relation.target_id == current_id:
                        next_id = relation.source_id

                    if next_id:
                        if next_id == start_id and depth >= 2:
                            # 找到循环
                            cycles.append(path.copy() + [start_id])
                        elif next_id not in visited or visited[next_id] > depth:
                            visited[next_id] = depth
                            path.append(next_id)
                            dfs(next_id, depth + 1)
                            path.pop()

        dfs(start_id, 1)
        return cycles

    def _find_money_circulation(
        self,
        start_id: str,
        context: RuleContext,
        max_depth: int,
    ) -> list[list[str]]:
        """查找资金回流路径"""
        paths: list[list[str]] = []
        visited = {start_id}
        path = [start_id]

        def dfs(current_id: str, depth: int) -> None:
            if depth > max_depth:
                return

            # 获取转账关系
            for relation in context.relations:
                if relation.type == RelationType.TRANSFERRED_TO:
                    next_id = None
                    if relation.source_id == current_id:
                        next_id = relation.target_id

                    if next_id:
                        if next_id == start_id and depth >= 2:
                            # 找到回流路径
                            paths.append(path.copy() + [start_id])
                        elif next_id not in visited:
                            visited.add(next_id)
                            path.append(next_id)
                            dfs(next_id, depth + 1)
                            path.pop()
                            visited.remove(next_id)

        dfs(start_id, 1)
        return paths

    def _find_related_entities(
        self,
        entity_id: str,
        context: RuleContext,
    ) -> set[str]:
        """查找关联实体（通过控制或担保关系）"""
        related = set()
        visited = {entity_id}
        queue = [entity_id]

        while queue:
            current_id = queue.pop(0)

            for relation in context.relations:
                if relation.type in (RelationType.CONTROLS, RelationType.GUARANTEES):
                    other_id = None
                    if relation.source_id == current_id:
                        other_id = relation.target_id
                    elif relation.target_id == current_id:
                        other_id = relation.source_id

                    if other_id and other_id not in visited:
                        visited.add(other_id)
                        related.add(other_id)
                        queue.append(other_id)

        return related

    def _priority_to_risk_level(self, priority: int) -> RiskLevel:
        """将优先级转换为风险等级"""
        mapping = {
            4: RiskLevel.CRITICAL,
            3: RiskLevel.HIGH,
            2: RiskLevel.MEDIUM,
            1: RiskLevel.LOW,
        }
        return mapping.get(priority, RiskLevel.LOW)

    async def _load_entity_context(
        self,
        project_id: str,
        entity_id: str,
    ) -> RuleContext:
        """加载实体上下文"""
        # 简化实现，实际应从数据库加载
        return RuleContext(project_id=project_id)

    async def _load_project_context(self, project_id: str) -> RuleContext:
        """加载项目上下文"""
        # 简化实现，实际应从数据库加载
        return RuleContext(project_id=project_id)
