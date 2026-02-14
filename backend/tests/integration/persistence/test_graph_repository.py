import pytest
from uuid import uuid4

from src.domain.entities.entity import Entity
from src.domain.entities.relation import Relation
from src.domain.value_objects.entity_type import EntityType
from src.domain.value_objects.relation_type import RelationType
from src.infrastructure.persistence.neo4j.graph_repository import Neo4jGraphRepository


def _sample_entity(project_id: str, external_id: str, entity_type: EntityType) -> Entity:
    return Entity.create(
        project_id=project_id,
        external_id=external_id,
        type=entity_type,
        labels=["Test"],
        properties={"name": external_id},
    )


@pytest.mark.asyncio
async def test_merge_entities_and_find_neighbors(neo4j_repo: Neo4jGraphRepository):
    project_id = str(uuid4())
    entity_a = _sample_entity(project_id, "company-a", EntityType.ENTERPRISE)
    entity_b = _sample_entity(project_id, "company-b", EntityType.ENTERPRISE)

    await neo4j_repo.merge_entity(entity_a)
    await neo4j_repo.merge_entity(entity_b)

    relation = Relation.create(
        project_id=project_id,
        source_id=entity_a.id,
        target_id=entity_b.id,
        type=RelationType.OWNS,
        properties={"weight": 0.8},
    )
    await neo4j_repo.merge_relation(relation)

    graph = await neo4j_repo.find_neighbors(project_id, entity_a.id, depth=1)

    entity_ids = {item["id"] for item in graph["entities"]}
    assert entity_a.id in entity_ids
    assert entity_b.id in entity_ids

    relation_ids = {item["id"] for item in graph["relations"]}
    assert relation.id in relation_ids


@pytest.mark.asyncio
async def test_delete_relation_and_entity(neo4j_repo: Neo4jGraphRepository):
    project_id = str(uuid4())
    entity_a = _sample_entity(project_id, "merchant-x", EntityType.ENTERPRISE)
    entity_b = _sample_entity(project_id, "merchant-y", EntityType.ENTERPRISE)

    await neo4j_repo.merge_entity(entity_a)
    await neo4j_repo.merge_entity(entity_b)

    relation = Relation.create(
        project_id=project_id,
        source_id=entity_a.id,
        target_id=entity_b.id,
        type=RelationType.GUARANTEES,
        properties={"score": 0.4},
    )
    await neo4j_repo.merge_relation(relation)

    await neo4j_repo.delete_relation(project_id, relation.id)
    graph_after_relation_delete = await neo4j_repo.find_neighbors(project_id, entity_a.id, depth=1)
    assert graph_after_relation_delete["relations"] == []

    # recreate relation and remove an entity to ensure cascading removal
    await neo4j_repo.merge_relation(relation)
    await neo4j_repo.delete_entity(project_id, entity_a.id)
    graph_after_entity_delete = await neo4j_repo.find_neighbors(project_id, entity_b.id, depth=1)
    assert {item["id"] for item in graph_after_entity_delete["entities"]} == {entity_b.id}
    assert graph_after_entity_delete["relations"] == []
