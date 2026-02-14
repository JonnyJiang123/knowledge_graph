from __future__ import annotations

import json
from typing import Any, Dict, List, Type

from neo4j.graph import Node, Relationship

from src.domain.entities.entity import Entity
from src.domain.entities.relation import Relation
from src.domain.ports.repositories import GraphEntityRepository
from src.infrastructure.persistence.neo4j.client import Neo4jClient


class Neo4jGraphRepository(GraphEntityRepository):
    def __init__(self, client: Type[Neo4jClient] = Neo4jClient):
        self._client = client

    async def merge_entity(self, entity: Entity) -> Entity:
        query = """
        MERGE (n:Entity {id: $id, project_id: $project_id})
        ON CREATE SET n.created_at = datetime()
        SET n.external_id = $external_id,
            n.type = $type,
            n.labels = $labels,
            n.properties_json = $properties_json,
            n.version = $version,
            n.updated_at = datetime()
        RETURN n
        """
        params = {
            "id": entity.id,
            "project_id": entity.project_id,
            "external_id": entity.external_id,
            "type": entity.type.value if hasattr(entity.type, "value") else entity.type,
            "labels": entity.labels,
            "properties_json": json.dumps(entity.properties),
            "version": entity.version,
        }
        await self._client.execute_write(query, params)
        return entity

    async def merge_relation(self, relation: Relation) -> Relation:
        query = """
        MATCH (source:Entity {id: $source_id, project_id: $project_id})
        MATCH (target:Entity {id: $target_id, project_id: $project_id})
        MERGE (source)-[r:RELATION {id: $id}]->(target)
        ON CREATE SET r.created_at = datetime()
        SET r.type = $type,
            r.project_id = $project_id,
            r.properties_json = $properties_json,
            r.source_id = $source_id,
            r.target_id = $target_id,
            r.updated_at = datetime()
        RETURN r
        """
        params = {
            "id": relation.id,
            "project_id": relation.project_id,
            "source_id": relation.source_id,
            "target_id": relation.target_id,
            "type": relation.type.value if hasattr(relation.type, "value") else relation.type,
            "properties_json": json.dumps(relation.properties),
        }
        result = await self._client.execute_write(query, params)
        if not result:
            raise ValueError("Source or target entity not found for relation merge")
        return relation

    async def delete_entity(self, project_id: str, entity_id: str) -> None:
        query = """
        MATCH (n:Entity {id: $entity_id, project_id: $project_id})
        DETACH DELETE n
        """
        await self._client.execute_write(query, {"entity_id": entity_id, "project_id": project_id})

    async def delete_relation(self, project_id: str, relation_id: str) -> None:
        query = """
        MATCH (:Entity {project_id: $project_id})-[r:RELATION {id: $relation_id}]-(:Entity {project_id: $project_id})
        DELETE r
        """
        await self._client.execute_write(query, {"relation_id": relation_id, "project_id": project_id})

    async def find_neighbors(self, project_id: str, entity_id: str, depth: int = 1) -> dict[str, list[Any]]:
        depth = max(depth, 0)
        node_pattern = self._pattern(depth, include_zero=True)
        nodes_query = f"""
        MATCH path = (start:Entity {{id: $entity_id, project_id: $project_id}})-[:RELATION{node_pattern}]-(neighbor:Entity {{project_id: $project_id}})
        RETURN DISTINCT neighbor AS node
        """
        nodes_records = await self._client.execute_read(
            nodes_query, {"entity_id": entity_id, "project_id": project_id}
        )

        entities = [_node_to_dict(record["node"]) for record in nodes_records]

        relations: List[Dict[str, Any]] = []
        if depth > 0:
            rel_pattern = self._pattern(depth, include_zero=False)
            rel_query = f"""
            MATCH path = (start:Entity {{id: $entity_id, project_id: $project_id}})-[:RELATION{rel_pattern}]-(neighbor:Entity {{project_id: $project_id}})
            UNWIND relationships(path) AS rel
            WITH DISTINCT rel
            RETURN rel AS rel, startNode(rel).id AS source_id, endNode(rel).id AS target_id
            """
            rel_records = await self._client.execute_read(
                rel_query, {"entity_id": entity_id, "project_id": project_id}
            )
            relations = [
                _relation_to_dict(record["rel"], record["source_id"], record["target_id"])
                for record in rel_records
            ]

        return {"entities": entities, "relations": relations}

    @staticmethod
    def _pattern(depth: int, *, include_zero: bool) -> str:
        if include_zero:
            return f"*0..{depth}"
        upper = max(depth, 1)
        return f"*1..{upper}"


def _node_to_dict(node: Node) -> Dict[str, Any]:
    data = dict(node)
    data.setdefault("labels", [])
    props_json = data.pop("properties_json", None)
    if props_json:
        data["properties"] = json.loads(props_json)
    else:
        data.setdefault("properties", {})
    return data


def _relation_to_dict(rel: Relationship, source_id: str, target_id: str) -> Dict[str, Any]:
    data = dict(rel)
    data["source_id"] = source_id
    data["target_id"] = target_id
    data["label"] = rel.type
    props_json = data.pop("properties_json", None)
    if props_json:
        data["properties"] = json.loads(props_json)
    else:
        data.setdefault("properties", {})
    return data
