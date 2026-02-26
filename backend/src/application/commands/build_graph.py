"""图谱构建命令

将抽取的实体和关系构建为知识图谱
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from src.domain.entities.entity import Entity
from src.domain.entities.relation import Relation
from src.domain.value_objects.entity_type import EntityType
from src.domain.value_objects.relation_type import RelationType


@dataclass
class BuildGraphCommand:
    """图谱构建命令
    
    Attributes:
        project_id: 目标项目ID
        owner_id: 用户ID
        entities: 待构建的实体列表
        relations: 待构建的关系列表
        merge_duplicates: 是否合并重复实体
        duplicate_threshold: 实体相似度阈值
    """
    project_id: str
    owner_id: str
    entities: list[dict[str, Any]]
    relations: list[dict[str, Any]]
    merge_duplicates: bool = True
    duplicate_threshold: float = 0.85


@dataclass
class BuildGraphResult:
    """图谱构建结果
    
    Attributes:
        success: 是否成功
        created_entities: 创建的实体数量
        created_relations: 创建的关系数量
        merged_entities: 合并的实体数量
        failed_items: 失败的项目
        errors: 错误信息列表
    """
    success: bool
    created_entities: int = 0
    created_relations: int = 0
    merged_entities: int = 0
    failed_items: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class EntityNormalizer:
    """实体标准化器
    
    负责实体名称的标准化和消歧
    """
    
    def normalize(self, text: str, entity_type: str) -> str:
        """标准化实体名称
        
        Args:
            text: 原始文本
            entity_type: 实体类型
            
        Returns:
            标准化后的文本
        """
        # 去除空白字符
        text = text.strip()
        
        # 企业名称标准化
        if entity_type == "ENTERPRISE":
            # 去除常见的公司后缀以进行匹配
            suffixes = ["有限公司", "有限责任公司", "股份有限公司", "集团"]
            for suffix in suffixes:
                if text.endswith(suffix):
                    return text
        
        # 人名标准化
        if entity_type == "PERSON":
            # 去除称谓
            titles = ["先生", "女士", "博士", "教授"]
            for title in titles:
                if text.endswith(title):
                    return text[:-len(title)]
        
        return text
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度分数 (0-1)
        """
        # 简单的编辑距离相似度
        if text1 == text2:
            return 1.0
        
        # 使用Levenshtein距离
        try:
            import Levenshtein
            return Levenshtein.ratio(text1, text2)
        except ImportError:
            # 如果没有安装python-Levenshtein，使用简单实现
            return self._simple_similarity(text1, text2)
    
    def _simple_similarity(self, text1: str, text2: str) -> float:
        """简单的相似度计算"""
        # 使用字符集合的Jaccard相似度
        set1 = set(text1)
        set2 = set(text2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        return intersection / union


class GraphBuilder:
    """图谱构建器
    
    负责将抽取结果转换为图谱数据并持久化
    """
    
    def __init__(self, normalizer: EntityNormalizer | None = None):
        self._normalizer = normalizer or EntityNormalizer()
        self._entity_map: dict[str, str] = {}  # 文本 -> 实体ID 映射
    
    async def build(
        self,
        command: BuildGraphCommand,
        entity_repo: Any
    ) -> BuildGraphResult:
        """构建图谱
        
        Args:
            command: 构建命令
            entity_repo: 实体仓库
            
        Returns:
            构建结果
        """
        result = BuildGraphResult(success=True)
        
        try:
            # 第一步：创建/合并实体
            entity_id_map = await self._process_entities(
                command, entity_repo, result
            )
            
            # 第二步：创建关系
            await self._process_relations(
                command, entity_repo, entity_id_map, result
            )
            
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
        
        return result
    
    async def _process_entities(
        self,
        command: BuildGraphCommand,
        entity_repo: Any,
        result: BuildGraphResult
    ) -> dict[str, str]:
        """处理实体创建/合并
        
        Returns:
            实体文本到ID的映射
        """
        entity_id_map = {}
        
        for entity_data in command.entities:
            try:
                text = entity_data.get("text", "")
                entity_type = entity_data.get("entity_type", "OTHER")
                
                # 标准化
                normalized_text = self._normalizer.normalize(text, entity_type)
                
                # 检查重复
                if command.merge_duplicates:
                    existing_id = self._find_duplicate(
                        normalized_text,
                        entity_type,
                        entity_id_map
                    )
                    if existing_id:
                        entity_id_map[normalized_text] = existing_id
                        result.merged_entities += 1
                        continue
                
                # 创建实体
                try:
                    entity_type_enum = EntityType(entity_type)
                except ValueError:
                    entity_type_enum = EntityType.ENTERPRISE  # 默认类型
                
                entity = Entity.create(
                    project_id=command.project_id,
                    external_id=normalized_text,
                    type=entity_type_enum,
                    labels=[entity_type],
                    properties=entity_data.get("properties", {})
                )
                
                await entity_repo.merge_entity(entity)
                
                entity_id_map[normalized_text] = entity.id
                result.created_entities += 1
                
            except Exception as e:
                result.failed_items.append({
                    "type": "entity",
                    "data": entity_data,
                    "error": str(e)
                })
        
        return entity_id_map
    
    async def _process_relations(
        self,
        command: BuildGraphCommand,
        entity_repo: Any,
        entity_id_map: dict[str, str],
        result: BuildGraphResult
    ) -> None:
        """处理关系创建"""
        for relation_data in command.relations:
            try:
                source_text = relation_data.get("source_text", "")
                target_text = relation_data.get("target_text", "")
                relation_type = relation_data.get("relation_type", "RELATED_TO")
                
                # 标准化
                source_normalized = self._normalizer.normalize(source_text, "")
                target_normalized = self._normalizer.normalize(target_text, "")
                
                # 查找实体ID
                source_id = entity_id_map.get(source_normalized)
                target_id = entity_id_map.get(target_normalized)
                
                if not source_id or not target_id:
                    result.failed_items.append({
                        "type": "relation",
                        "data": relation_data,
                        "error": "Source or target entity not found"
                    })
                    continue
                
                # 创建关系
                try:
                    relation_type_enum = RelationType(relation_type)
                except ValueError:
                    relation_type_enum = RelationType.OWNS  # 默认类型
                
                relation = Relation.create(
                    project_id=command.project_id,
                    source_id=source_id,
                    target_id=target_id,
                    type=relation_type_enum,
                    properties=relation_data.get("properties", {})
                )
                
                await entity_repo.merge_relation(relation)
                result.created_relations += 1
                
            except Exception as e:
                result.failed_items.append({
                    "type": "relation",
                    "data": relation_data,
                    "error": str(e)
                })
    
    def _find_duplicate(
        self,
        normalized_text: str,
        entity_type: str,
        entity_id_map: dict[str, str]
    ) -> str | None:
        """查找重复实体"""
        for existing_text, entity_id in entity_id_map.items():
            similarity = self._normalizer.calculate_similarity(
                normalized_text,
                existing_text
            )
            if similarity >= 0.85:  # 阈值
                return entity_id
        return None
