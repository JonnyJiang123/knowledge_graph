from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

from src.domain.entities.entity import Entity
from src.domain.entities.relation import Relation
from src.domain.entities.rule import Action, Condition, ReasoningRule
from src.domain.value_objects.risk_level import RiskLevel


@dataclass
class RuleContext:
    """规则评估上下文"""
    project_id: str
    entities: dict[str, Entity] = field(default_factory=dict)  # entity_id -> Entity
    relations: list[Relation] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)  # 额外参数

    def add_entity(self, entity: Entity) -> None:
        """添加实体到上下文"""
        self.entities[entity.id] = entity

    def add_relation(self, relation: Relation) -> None:
        """添加关系到上下文"""
        self.relations.append(relation)

    def get_entity_relations(self, entity_id: str) -> list[Relation]:
        """获取与指定实体相关的关系"""
        return [
            r for r in self.relations
            if r.source_id == entity_id or r.target_id == entity_id
        ]

    def get_neighbors(self, entity_id: str) -> list[Entity]:
        """获取相邻实体"""
        neighbor_ids = set()
        for r in self.relations:
            if r.source_id == entity_id:
                neighbor_ids.add(r.target_id)
            elif r.target_id == entity_id:
                neighbor_ids.add(r.source_id)
        return [self.entities[eid] for eid in neighbor_ids if eid in self.entities]


@dataclass
class RuleEvaluationResult:
    """规则评估结果"""
    rule_id: str
    rule_name: str
    matched: bool
    matched_entities: list[str] = field(default_factory=list)  # 匹配的实体ID列表
    matched_relations: list[str] = field(default_factory=list)  # 匹配的关系ID列表
    risk_level: RiskLevel | None = None
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    triggered_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def no_match(
        cls,
        rule_id: str,
        rule_name: str,
        message: str = "",
    ) -> "RuleEvaluationResult":
        return cls(
            rule_id=rule_id,
            rule_name=rule_name,
            matched=False,
            message=message,
        )


class GraphRepository(Protocol):
    """图存储仓库协议"""

    async def get_entities_by_type(
        self,
        project_id: str,
        entity_type: str,
    ) -> list[Entity]:
        """按类型获取实体"""
        ...

    async def get_relations_by_type(
        self,
        project_id: str,
        relation_type: str,
    ) -> list[Relation]:
        """按类型获取关系"""
        ...

    async def find_paths(
        self,
        project_id: str,
        source_id: str,
        target_id: str,
        max_depth: int = 5,
    ) -> list[list[Relation]]:
        """查找两实体间的路径"""
        ...


class RuleEngine:
    """基础规则引擎"""

    def __init__(self, graph_repo: GraphRepository | None = None) -> None:
        self._graph_repo = graph_repo

    async def evaluate_rule(
        self,
        rule: ReasoningRule,
        context: RuleContext,
    ) -> RuleEvaluationResult:
        """评估单条规则"""
        if not rule.is_active:
            return RuleEvaluationResult.no_match(
                rule_id=rule.id,
                rule_name=rule.name,
                message="Rule is inactive",
            )

        # 收集所有满足条件的实体和关系
        matched_entities: list[str] = []
        matched_relations: list[str] = []

        # 评估每个条件
        for condition in rule.conditions:
            if condition.field.startswith("entity."):
                entity_matches = self._evaluate_entity_condition(condition, context)
                matched_entities.extend(entity_matches)
            elif condition.field.startswith("relation."):
                relation_matches = self._evaluate_relation_condition(condition, context)
                matched_relations.extend(relation_matches)

        # 去重
        matched_entities = list(set(matched_entities))
        matched_relations = list(set(matched_relations))

        # 判断是否匹配（简单逻辑：至少有一个条件匹配）
        matched = len(matched_entities) > 0 or len(matched_relations) > 0

        if matched:
            return RuleEvaluationResult(
                rule_id=rule.id,
                rule_name=rule.name,
                matched=True,
                matched_entities=matched_entities,
                matched_relations=matched_relations,
                message=f"Rule matched: {rule.description}",
            )

        return RuleEvaluationResult.no_match(
            rule_id=rule.id,
            rule_name=rule.name,
            message="No matches found",
        )

    async def evaluate_all_rules(
        self,
        rules: list[ReasoningRule],
        context: RuleContext,
    ) -> list[RuleEvaluationResult]:
        """评估所有规则，按优先级排序"""
        # 按优先级降序排序
        sorted_rules = sorted(rules, key=lambda r: r.priority, reverse=True)

        results: list[RuleEvaluationResult] = []
        for rule in sorted_rules:
            result = await self.evaluate_rule(rule, context)
            results.append(result)

        return results

    def _evaluate_entity_condition(
        self,
        condition: Condition,
        context: RuleContext,
    ) -> list[str]:
        """评估实体条件，返回匹配的实体ID列表"""
        matched: list[str] = []
        field_path = condition.field.replace("entity.", "")

        for entity_id, entity in context.entities.items():
            value = self._get_nested_value(entity, field_path)
            if self._evaluate_operator(value, condition.operator, condition.value):
                matched.append(entity_id)

        return matched

    def _evaluate_relation_condition(
        self,
        condition: Condition,
        context: RuleContext,
    ) -> list[str]:
        """评估关系条件，返回匹配的关系ID列表"""
        matched: list[str] = []
        field_path = condition.field.replace("relation.", "")

        for relation in context.relations:
            value = self._get_nested_value(relation, field_path)
            if self._evaluate_operator(value, condition.operator, condition.value):
                matched.append(relation.id)

        return matched

    def _get_nested_value(self, obj: Any, field_path: str) -> Any:
        """获取嵌套属性值"""
        parts = field_path.split(".")
        value: Any = obj

        for part in parts:
            if value is None:
                return None
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None

        return value

    def _evaluate_operator(
        self,
        value: Any,
        operator: str,
        compare_value: Any,
    ) -> bool:
        """评估操作符"""
        if operator == "equals":
            return value == compare_value
        elif operator == "not_equals":
            return value != compare_value
        elif operator == "in":
            if isinstance(compare_value, (list, tuple, set)):
                return value in compare_value
            return value == compare_value
        elif operator == "not_in":
            if isinstance(compare_value, (list, tuple, set)):
                return value not in compare_value
            return value != compare_value
        elif operator == "gt":
            return value is not None and compare_value is not None and value > compare_value
        elif operator == "gte":
            return value is not None and compare_value is not None and value >= compare_value
        elif operator == "lt":
            return value is not None and compare_value is not None and value < compare_value
        elif operator == "lte":
            return value is not None and compare_value is not None and value <= compare_value
        elif operator == "contains":
            if isinstance(value, str) and isinstance(compare_value, str):
                return compare_value in value
            return False
        elif operator == "regex":
            if isinstance(value, str) and isinstance(compare_value, str):
                return re.match(compare_value, value) is not None
            return False
        elif operator == "exists":
            return value is not None
        elif operator == "not_exists":
            return value is None

        return False

    def build_context(
        self,
        project_id: str,
        entities: list[Entity] | None = None,
        relations: list[Relation] | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> RuleContext:
        """构建规则上下文"""
        context = RuleContext(
            project_id=project_id,
            parameters=parameters or {},
        )

        if entities:
            for entity in entities:
                context.add_entity(entity)
        if relations:
            for relation in relations:
                context.add_relation(relation)

        return context
