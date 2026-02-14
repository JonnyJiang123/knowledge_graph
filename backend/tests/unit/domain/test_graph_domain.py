import pytest

from src.domain.entities.entity import Entity
from src.domain.entities.graph_project import GraphProject
from src.domain.entities.relation import Relation
from src.domain.value_objects.entity_type import EntityType
from src.domain.value_objects.relation_type import RelationType


def test_graph_project_adds_entities():
    project = GraphProject.new(name="AML Graph", owner_id="user-1", industry="FINANCE")
    entity = Entity.create(project_id=project.id, external_id="org-1", type=EntityType.ENTERPRISE)

    project.add_entity(entity)

    assert entity.id in project.entities
    assert project.entities[entity.id].project_id == project.id


def test_relation_requires_existing_entities():
    project = GraphProject.new(name="Risk Graph", owner_id="user-1", industry="FINANCE")
    src = Entity.create(project_id=project.id, external_id="p1", type=EntityType.PERSON)
    dst = Entity.create(project_id=project.id, external_id="c1", type=EntityType.ENTERPRISE)

    project.add_entity(src)
    # target entity not added yet, relation should fail
    relation = Relation.create(
        project_id=project.id,
        source_id=src.id,
        target_id=dst.id,
        type=RelationType.OWNS,
    )

    with pytest.raises(ValueError):
        project.add_relation(relation)

    project.add_entity(dst)
    project.add_relation(relation)
    assert relation.id in project.relations


def test_relation_rejects_cross_project_entities():
    project = GraphProject.new(name="Healthcare Graph", owner_id="owner", industry="HEALTHCARE")
    other_project = GraphProject.new(name="Other", owner_id="owner", industry="FINANCE")
    src = Entity.create(project_id=project.id, external_id="drug-1", type=EntityType.DRUG)
    dst = Entity.create(project_id=other_project.id, external_id="symptom-1", type=EntityType.PERSON)

    project.add_entity(src)
    other_project.add_entity(dst)

    relation = Relation.create(
        project_id=project.id,
        source_id=src.id,
        target_id=dst.id,
        type=RelationType.GUARANTEES,
    )
    with pytest.raises(ValueError):
        project.add_relation(relation)


def test_relation_rejects_self_loops():
    project = GraphProject.new(name="Loop Test", owner_id="owner", industry="FINANCE")
    entity = Entity.create(project_id=project.id, external_id="acct", type=EntityType.ACCOUNT)
    project.add_entity(entity)

    with pytest.raises(ValueError):
        Relation.create(
            project_id=project.id,
            source_id=entity.id,
            target_id=entity.id,
            type=RelationType.CONTROLS,
        )
