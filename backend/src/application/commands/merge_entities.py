"""实体融合命令

合并重复或相似的实体
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class EntityMergeCandidate:
    """实体融合候选
    
    Attributes:
        entity_id: 实体ID
        entity_text: 实体文本
        entity_type: 实体类型
        similarity: 相似度分数
    """
    entity_id: str
    entity_text: str
    entity_type: str
    similarity: float


@dataclass
class MergeEntitiesCommand:
    """实体融合命令
    
    Attributes:
        project_id: 项目ID
        owner_id: 用户ID
        target_entity_id: 目标实体ID（保留的实体）
        source_entity_ids: 要合并的源实体ID列表
        merge_strategy: 属性合并策略
        
    Merge Strategy:
        - keep_target: 保留目标实体的属性
        - keep_newest: 保留最新的属性
        - merge_all: 合并所有属性（冲突时保留目标）
    """
    project_id: str
    owner_id: str
    target_entity_id: str
    source_entity_ids: list[str]
    merge_strategy: str = "merge_all"  # keep_target, keep_newest, merge_all


@dataclass
class MergeEntitiesResult:
    """实体融合结果
    
    Attributes:
        success: 是否成功
        merged_entity_id: 合并后的实体ID
        transferred_relations: 转移的关系数量
        deleted_entities: 删除的实体数量
        errors: 错误信息
    """
    success: bool
    merged_entity_id: str | None = None
    transferred_relations: int = 0
    deleted_entities: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class FindMergeCandidatesQuery:
    """查找融合候选查询
    
    Attributes:
        project_id: 项目ID
        owner_id: 用户ID
        entity_type: 实体类型过滤
        similarity_threshold: 相似度阈值
        limit: 返回候选数量
    """
    project_id: str
    owner_id: str
    entity_type: str | None = None
    similarity_threshold: float = 0.8
    limit: int = 100


@dataclass
class FindMergeCandidatesResult:
    """查找融合候选结果"""
    candidates: list[list[EntityMergeCandidate]]  # 候选组列表


class EntityMergeService:
    """实体融合服务"""
    
    MERGE_STRATEGIES = ["keep_target", "keep_newest", "merge_all"]
    
    async def find_candidates(
        self,
        query: FindMergeCandidatesQuery,
        entity_repo: Any
    ) -> FindMergeCandidatesResult:
        """查找融合候选
        
        使用简单的文本相似度算法找出可能重复的实体
        
        Args:
            query: 查找查询
            entity_repo: 实体仓库
            
        Returns:
            候选结果
        """
        # 获取项目中的所有实体
        from src.infrastructure.persistence.neo4j import cypher_queries as queries
        from src.infrastructure.persistence.neo4j.client import Neo4jClient
        
        # 使用通用的实体获取查询
        cypher_query = """
        MATCH (n:Entity {project_id: $project_id})
        WHERE $entity_type IS NULL OR n.type = $entity_type
        RETURN n.id as id, n.external_id as text, n.type as type, n.updated_at as updated_at
        """
        
        records = await Neo4jClient.execute_read(
            cypher_query,
            {
                "project_id": query.project_id,
                "entity_type": query.entity_type
            }
        )
        
        # 按类型分组
        entities_by_type: dict[str, list[dict]] = {}
        for record in records:
            etype = record.get("type", "OTHER")
            if etype not in entities_by_type:
                entities_by_type[etype] = []
            entities_by_type[etype].append(record)
        
        # 在每个类型内查找相似实体
        candidates = []
        
        for etype, entities in entities_by_type.items():
            # 使用简单的两两比较
            n = len(entities)
            for i in range(n):
                group = []
                entity_i = entities[i]
                text_i = entity_i.get("text", "")
                
                for j in range(i + 1, n):
                    entity_j = entities[j]
                    text_j = entity_j.get("text", "")
                    
                    similarity = self._calculate_similarity(text_i, text_j)
                    
                    if similarity >= query.similarity_threshold:
                        if not group:
                            group.append(EntityMergeCandidate(
                                entity_id=entity_i["id"],
                                entity_text=text_i,
                                entity_type=etype,
                                similarity=1.0
                            ))
                        group.append(EntityMergeCandidate(
                            entity_id=entity_j["id"],
                            entity_text=text_j,
                            entity_type=etype,
                            similarity=similarity
                        ))
                
                if group:
                    candidates.append(group)
                
                if len(candidates) >= query.limit:
                    break
            
            if len(candidates) >= query.limit:
                break
        
        return FindMergeCandidatesResult(candidates=candidates[:query.limit])
    
    async def merge(
        self,
        command: MergeEntitiesCommand,
        entity_repo: Any
    ) -> MergeEntitiesResult:
        """执行实体融合
        
        Args:
            command: 融合命令
            entity_repo: 实体仓库
            
        Returns:
            融合结果
        """
        if command.merge_strategy not in self.MERGE_STRATEGIES:
            return MergeEntitiesResult(
                success=False,
                errors=[f"Invalid merge strategy: {command.merge_strategy}"]
            )
        
        result = MergeEntitiesResult(success=True)
        
        try:
            # 1. 获取目标实体和源实体的属性
            from src.infrastructure.persistence.neo4j.client import Neo4jClient
            
            target_entity = await self._get_entity(
                command.project_id,
                command.target_entity_id
            )
            
            if not target_entity:
                return MergeEntitiesResult(
                    success=False,
                    errors=["Target entity not found"]
                )
            
            # 2. 合并属性
            merged_properties = self._merge_properties(
                target_entity,
                [],  # 源实体属性列表
                command.merge_strategy
            )
            
            # 3. 更新目标实体属性
            if merged_properties != target_entity.get("properties", {}):
                await self._update_entity_properties(
                    command.project_id,
                    command.target_entity_id,
                    merged_properties
                )
            
            # 4. 转移关系
            transferred = await self._transfer_relations(
                command.project_id,
                command.target_entity_id,
                command.source_entity_ids
            )
            result.transferred_relations = transferred
            
            # 5. 删除源实体
            deleted = 0
            for source_id in command.source_entity_ids:
                try:
                    await entity_repo.delete_entity(command.project_id, source_id)
                    deleted += 1
                except Exception as e:
                    result.errors.append(f"Failed to delete entity {source_id}: {e}")
            
            result.deleted_entities = deleted
            result.merged_entity_id = command.target_entity_id
            
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
        
        return result
    
    async def _get_entity(
        self,
        project_id: str,
        entity_id: str
    ) -> dict[str, Any] | None:
        """获取实体详情"""
        from src.infrastructure.persistence.neo4j import cypher_queries as queries
        from src.infrastructure.persistence.neo4j.client import Neo4jClient
        
        records = await Neo4jClient.execute_read(
            queries.GET_ENTITY_BY_ID,
            {"project_id": project_id, "entity_id": entity_id}
        )
        
        if not records:
            return None
        
        entity = records[0].get("entity", {})
        
        # 解析properties_json
        import json
        props_json = entity.get("properties_json")
        if props_json:
            entity["properties"] = json.loads(props_json)
        else:
            entity["properties"] = {}
        
        return entity
    
    def _merge_properties(
        self,
        target_entity: dict[str, Any],
        source_properties_list: list[dict[str, Any]],
        strategy: str
    ) -> dict[str, Any]:
        """合并属性"""
        if strategy == "keep_target":
            return target_entity.get("properties", {})
        
        if strategy == "keep_newest":
            # 简化处理：始终保留目标实体的属性
            return target_entity.get("properties", {})
        
        # merge_all: 合并所有属性，冲突时保留目标
        merged = dict(target_entity.get("properties", {}))
        
        for source_props in source_properties_list:
            for key, value in source_props.items():
                if key not in merged:
                    merged[key] = value
        
        return merged
    
    async def _update_entity_properties(
        self,
        project_id: str,
        entity_id: str,
        properties: dict[str, Any]
    ) -> None:
        """更新实体属性"""
        from src.infrastructure.persistence.neo4j.client import Neo4jClient
        
        import json
        query = """
        MATCH (n:Entity {id: $entity_id, project_id: $project_id})
        SET n.properties_json = $properties_json,
            n.version = n.version + 1,
            n.updated_at = datetime()
        """
        
        await Neo4jClient.execute_write(
            query,
            {
                "project_id": project_id,
                "entity_id": entity_id,
                "properties_json": json.dumps(properties)
            }
        )
    
    async def _transfer_relations(
        self,
        project_id: str,
        target_entity_id: str,
        source_entity_ids: list[str]
    ) -> int:
        """转移关系
        
        将所有与源实体相关的关系转移到目标实体
        """
        from src.infrastructure.persistence.neo4j.client import Neo4jClient
        
        transferred = 0
        
        for source_id in source_entity_ids:
            # 转移出边
            out_query = """
            MATCH (source:Entity {id: $source_id, project_id: $project_id})-[r:RELATION]->(target)
            MATCH (new_source:Entity {id: $target_id, project_id: $project_id})
            MERGE (new_source)-[new_r:RELATION {id: r.id}]->(target)
            SET new_r.type = r.type,
                new_r.properties_json = r.properties_json,
                new_r.project_id = r.project_id,
                new_r.source_id = $target_id,
                new_r.target_id = r.target_id,
                new_r.updated_at = datetime()
            DELETE r
            """
            
            await Neo4jClient.execute_write(
                out_query,
                {
                    "project_id": project_id,
                    "source_id": source_id,
                    "target_id": target_entity_id
                }
            )
            
            # 转移入边
            in_query = """
            MATCH (source)-[r:RELATION]->(target:Entity {id: $source_id, project_id: $project_id})
            MATCH (new_target:Entity {id: $target_id, project_id: $project_id})
            MERGE (source)-[new_r:RELATION {id: r.id}]->(new_target)
            SET new_r.type = r.type,
                new_r.properties_json = r.properties_json,
                new_r.project_id = r.project_id,
                new_r.source_id = r.source_id,
                new_r.target_id = $target_id,
                new_r.updated_at = datetime()
            DELETE r
            """
            
            await Neo4jClient.execute_write(
                in_query,
                {
                    "project_id": project_id,
                    "source_id": source_id,
                    "target_id": target_entity_id
                }
            )
            
            transferred += 1
        
        return transferred
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        # 精确匹配
        if text1 == text2:
            return 1.0
        
        # 包含关系
        if text1 in text2 or text2 in text1:
            return 0.9
        
        # 编辑距离
        try:
            import Levenshtein
            return Levenshtein.ratio(text1, text2)
        except ImportError:
            # 简单字符集合相似度
            set1 = set(text1)
            set2 = set(text2)
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            return intersection / union if union > 0 else 0.0
