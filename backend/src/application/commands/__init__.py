"""命令层

包含所有写操作命令和对应的处理器
"""

from src.application.commands.create_entity import CreateEntityCommand
from src.application.commands.create_relation import CreateRelationCommand
from src.application.commands.create_graph_project import CreateGraphProjectCommand
from src.application.commands.extract_knowledge import (
    ExtractKnowledgeCommand,
    ExtractionJob,
    ExtractionStatus,
    ExtractionSourceType,
    ExtractedEntity,
    ExtractedRelation,
    ExtractionResult,
    KnowledgeExtractor,
    MockKnowledgeExtractor
)
from src.application.commands.build_graph import (
    BuildGraphCommand,
    BuildGraphResult,
    GraphBuilder
)
from src.application.commands.merge_entities import (
    FindMergeCandidatesQuery,
    FindMergeCandidatesResult,
    MergeEntitiesCommand,
    MergeEntitiesResult,
    EntityMergeService
)
from src.application.commands.create_rule import (
    CreateRuleCommand,
    UpdateRuleCommand,
    DeleteRuleCommand,
    ActivateRuleCommand,
    DeactivateRuleCommand,
)
from src.application.commands.run_reasoning import (
    RunReasoningCommand,
    RunFinanceFraudDetectionCommand,
    RunRiskPropagationCommand,
    RunHealthcareCheckCommand,
)

__all__ = [
    # Graph
    "CreateEntityCommand",
    "CreateRelationCommand",
    "CreateGraphProjectCommand",
    # Extraction
    "ExtractKnowledgeCommand",
    "ExtractionJob",
    "ExtractionStatus",
    "ExtractionSourceType",
    "ExtractedEntity",
    "ExtractedRelation",
    "ExtractionResult",
    "KnowledgeExtractor",
    "MockKnowledgeExtractor",
    # Build
    "BuildGraphCommand",
    "BuildGraphResult",
    "GraphBuilder",
    # Merge
    "FindMergeCandidatesQuery",
    "FindMergeCandidatesResult",
    "MergeEntitiesCommand",
    "MergeEntitiesResult",
    "EntityMergeService",
    # Reasoning Rules
    "CreateRuleCommand",
    "UpdateRuleCommand",
    "DeleteRuleCommand",
    "ActivateRuleCommand",
    "DeactivateRuleCommand",
    # Reasoning Execution
    "RunReasoningCommand",
    "RunFinanceFraudDetectionCommand",
    "RunRiskPropagationCommand",
    "RunHealthcareCheckCommand",
]
