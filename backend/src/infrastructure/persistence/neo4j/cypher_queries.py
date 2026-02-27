"""Cypher查询模板集合

用于知识图谱的查询与可视化模块
"""

from __future__ import annotations

# =============================================================================
# 实体搜索查询
# =============================================================================

# 基于关键词搜索实体
SEARCH_ENTITIES = """
MATCH (n:Entity {project_id: $project_id})
WHERE n.external_id CONTAINS $keyword 
   OR n.type CONTAINS $keyword
   OR any(label IN n.labels WHERE label CONTAINS $keyword)
   OR n.properties_json CONTAINS $keyword
RETURN n as entity
ORDER BY n.updated_at DESC
SKIP $offset LIMIT $limit
"""

# 带类型过滤的实体搜索
SEARCH_ENTITIES_BY_TYPE = """
MATCH (n:Entity {project_id: $project_id, type: $entity_type})
WHERE n.external_id CONTAINS $keyword 
   OR any(label IN n.labels WHERE label CONTAINS $keyword)
   OR n.properties_json CONTAINS $keyword
RETURN n as entity
ORDER BY n.updated_at DESC
SKIP $offset LIMIT $limit
"""

# 获取实体总数
COUNT_ENTITIES = """
MATCH (n:Entity {project_id: $project_id})
WHERE ($keyword IS NULL OR n.external_id CONTAINS $keyword)
   AND ($entity_type IS NULL OR n.type = $entity_type)
RETURN count(n) as total
"""

# 获取单个实体详情
GET_ENTITY_BY_ID = """
MATCH (n:Entity {id: $entity_id, project_id: $project_id})
RETURN n as entity
"""

# 更新实体属性
UPDATE_ENTITY = """
MATCH (n:Entity {id: $entity_id, project_id: $project_id})
SET n.labels = $labels,
    n.properties_json = $properties_json,
    n.version = n.version + 1,
    n.updated_at = datetime()
RETURN n as entity
"""

# 删除实体及其关系
DELETE_ENTITY = """
MATCH (n:Entity {id: $entity_id, project_id: $project_id})
DETACH DELETE n
"""

# 批量创建实体
BATCH_CREATE_ENTITIES = """
UNWIND $entities as entity
MERGE (n:Entity {id: entity.id, project_id: $project_id})
ON CREATE SET n.created_at = datetime()
SET n.external_id = entity.external_id,
    n.type = entity.type,
    n.labels = entity.labels,
    n.properties_json = entity.properties_json,
    n.version = coalesce(entity.version, 1),
    n.updated_at = datetime()
RETURN count(n) as created_count
"""

# =============================================================================
# 关系搜索查询
# =============================================================================

# 搜索关系
SEARCH_RELATIONS = """
MATCH (source:Entity {project_id: $project_id})-[r:RELATION]-(target:Entity {project_id: $project_id})
WHERE ($relation_type IS NULL OR r.type = $relation_type)
   AND ($keyword IS NULL OR source.external_id CONTAINS $keyword OR target.external_id CONTAINS $keyword)
RETURN r as relation, source.id as source_id, target.id as target_id
ORDER BY r.updated_at DESC
SKIP $offset LIMIT $limit
"""

# 获取关系总数
COUNT_RELATIONS = """
MATCH (:Entity {project_id: $project_id})-[r:RELATION]-(:Entity {project_id: $project_id})
WHERE ($relation_type IS NULL OR r.type = $relation_type)
RETURN count(r) as total
"""

# 批量创建关系
BATCH_CREATE_RELATIONS = """
UNWIND $relations as rel
MATCH (source:Entity {id: rel.source_id, project_id: $project_id})
MATCH (target:Entity {id: rel.target_id, project_id: $project_id})
MERGE (source)-[r:RELATION {id: rel.id}]->(target)
ON CREATE SET r.created_at = datetime()
SET r.type = rel.type,
    r.project_id = $project_id,
    r.properties_json = rel.properties_json,
    r.source_id = rel.source_id,
    r.target_id = rel.target_id,
    r.updated_at = datetime()
RETURN count(r) as created_count
"""

# 删除关系
DELETE_RELATION = """
MATCH (:Entity {project_id: $project_id})-[r:RELATION {id: $relation_id}]-(:Entity {project_id: $project_id})
DELETE r
"""

# =============================================================================
# 路径查找查询
# =============================================================================

# 最短路径查找 (使用Neo4j内置算法)
FIND_SHORTEST_PATH = """
MATCH (start:Entity {id: $start_id, project_id: $project_id})
MATCH (end:Entity {id: $end_id, project_id: $project_id})
MATCH path = shortestPath((start)-[:RELATION*1..{max_depth}]-(end))
WITH path, nodes(path) as path_nodes, relationships(path) as path_rels
UNWIND path_nodes as node
WITH path, collect(DISTINCT node) as nodes, path_rels
UNWIND path_rels as rel
RETURN nodes, collect(DISTINCT rel) as relations
"""

# 所有路径查找
FIND_ALL_PATHS = """
MATCH (start:Entity {id: $start_id, project_id: $project_id})
MATCH (end:Entity {id: $end_id, project_id: $project_id})
MATCH path = (start)-[:RELATION*1..{max_depth}]-(end)
WITH path, nodes(path) as path_nodes, relationships(path) as path_rels
UNWIND path_nodes as node
WITH path, collect(DISTINCT node) as nodes, path_rels
UNWIND path_rels as rel
RETURN nodes, collect(DISTINCT rel) as relations
LIMIT $path_limit
"""

# N度邻居查找
FIND_N_DEGREE_NEIGHBORS = """
MATCH path = (start:Entity {id: $start_id, project_id: $project_id})-[:RELATION*1..{depth}]-(neighbor:Entity {project_id: $project_id})
WHERE neighbor.id <> $start_id
WITH neighbor, min(length(path)) as distance
ORDER BY distance
RETURN neighbor as entity, distance
SKIP $offset LIMIT $limit
"""

# =============================================================================
# 子图获取查询
# =============================================================================

# 获取项目完整子图 (带节点数限制)
GET_SUBGRAPH = """
MATCH (n:Entity {project_id: $project_id})
WITH n LIMIT $node_limit
OPTIONAL MATCH (n)-[r:RELATION]-(m:Entity {project_id: $project_id})
WHERE m in [(n)] OR m in [(n)-->() | endNode(n)] OR m in [(n)<--() | startNode(n)]
WITH collect(DISTINCT n) + collect(DISTINCT m) as all_nodes, collect(DISTINCT r) as all_relations
UNWIND all_nodes as node
WITH collect(DISTINCT node) as nodes, all_relations
UNWIND all_relations as rel
RETURN nodes, collect(DISTINCT rel) as relations
"""

# 获取以某节点为中心的子图
GET_EGO_NETWORK = """
MATCH (center:Entity {id: $entity_id, project_id: $project_id})
OPTIONAL MATCH path = (center)-[:RELATION*1..{depth}]-(neighbor:Entity {project_id: $project_id})
WITH center, neighbor, path
ORDER BY length(path)
WITH center, collect(DISTINCT neighbor)[0..{limit}] as neighbors, collect(DISTINCT path) as paths
UNWIND paths as p
UNWIND relationships(p) as rel
WITH center, neighbors, collect(DISTINCT rel) as relations
UNWIND ([center] + neighbors) as node
RETURN collect(DISTINCT node) as nodes, relations
"""

# 获取社区子图 (基于节点类型或标签)
GET_COMMUNITY_SUBGRAPH = """
MATCH (n:Entity {project_id: $project_id})
WHERE ($entity_type IS NULL OR n.type = $entity_type)
   AND ($label IS NULL OR $label IN n.labels)
WITH n LIMIT $node_limit
OPTIONAL MATCH (n)-[r:RELATION]-(m:Entity {project_id: $project_id})
WITH collect(DISTINCT n) + collect(DISTINCT m) as all_nodes, collect(DISTINCT r) as all_relations
UNWIND all_nodes as node
WITH collect(DISTINCT node) as nodes, all_relations
UNWIND all_relations as rel
RETURN nodes, collect(DISTINCT rel) as relations
"""

# =============================================================================
# 中心性分析查询 (GDS库)
# =============================================================================

# PageRank 中心性分析
PAGERANK = """
CALL gds.pageRank.stream($graph_name, {
    maxIterations: $max_iterations,
    dampingFactor: $damping_factor,
    relationshipWeightProperty: $weight_property
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id as entity_id,
       gds.util.asNode(nodeId).external_id as name,
       gds.util.asNode(nodeId).type as entity_type,
       score
ORDER BY score DESC
LIMIT $limit
"""

# Betweenness 中心性分析
BETWEENNESS = """
CALL gds.betweenness.stream($graph_name, {
    samplingSize: $sampling_size,
    samplingSeed: $sampling_seed
})
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).id as entity_id,
       gds.util.asNode(nodeId).external_id as name,
       gds.util.asNode(nodeId).type as entity_type,
       score
ORDER BY score DESC
LIMIT $limit
"""

# Degree 中心性 (简单版，不需要GDS)
DEGREE_CENTRALITY = """
MATCH (n:Entity {project_id: $project_id})
OPTIONAL MATCH (n)-[r:RELATION]-()
WITH n, count(r) as degree
RETURN n.id as entity_id,
       n.external_id as name,
       n.type as entity_type,
       degree as score
ORDER BY degree DESC
LIMIT $limit
"""

# =============================================================================
# 社区发现查询 (GDS库)
# =============================================================================

# Louvain 社区发现
LOUVAIN_COMMUNITY = """
CALL gds.louvain.stream($graph_name, {
    maxLevels: $max_levels,
    maxIterations: $max_iterations,
    tolerance: $tolerance,
    relationshipWeightProperty: $weight_property
})
YIELD nodeId, communityId, intermediateCommunityIds
RETURN gds.util.asNode(nodeId).id as entity_id,
       gds.util.asNode(nodeId).external_id as name,
       gds.util.asNode(nodeId).type as entity_type,
       communityId as community_id
ORDER BY communityId DESC
"""

# Label Propagation 社区发现
LABEL_PROPAGATION = """
CALL gds.labelPropagation.stream($graph_name, {
    maxIterations: $max_iterations,
    relationshipWeightProperty: $weight_property
})
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).id as entity_id,
       gds.util.asNode(nodeId).external_id as name,
       gds.util.asNode(nodeId).type as entity_type,
       communityId as community_id
ORDER BY communityId DESC
"""

# =============================================================================
# 图投影管理查询 (GDS)
# =============================================================================

# 创建图投影
CREATE_GRAPH_PROJECTION = """
CALL gds.graph.project(
    $graph_name,
    ['Entity'],
    {
        RELATION: {
            orientation: 'UNDIRECTED'
        }
    },
    {
        nodeProperties: ['type', 'external_id'],
        relationshipProperties: $weight_property
    }
)
YIELD graphName, nodeCount, relationshipCount
RETURN graphName, nodeCount, relationshipCount
"""

# 删除图投影
DROP_GRAPH_PROJECTION = """
CALL gds.graph.drop($graph_name, false)
YIELD graphName
RETURN graphName
"""

# 检查图投影是否存在
CHECK_GRAPH_EXISTS = """
RETURN gds.graph.exists($graph_name) as exists
"""

# =============================================================================
# 统计分析查询
# =============================================================================

# 获取项目统计信息
GET_PROJECT_STATS = """
MATCH (n:Entity {project_id: $project_id})
OPTIONAL MATCH (n)-[r:RELATION]-()
WITH count(DISTINCT n) as entity_count, count(DISTINCT r) as relation_count
MATCH (n:Entity {project_id: $project_id})
WITH entity_count, relation_count, collect(DISTINCT n.type) as entity_types
RETURN entity_count, relation_count, entity_types
"""

# 获取实体类型分布
GET_ENTITY_TYPE_DISTRIBUTION = """
MATCH (n:Entity {project_id: $project_id})
RETURN n.type as type, count(n) as count
ORDER BY count DESC
"""

# 获取关系类型分布
GET_RELATION_TYPE_DISTRIBUTION = """
MATCH (:Entity {project_id: $project_id})-[r:RELATION]-(:Entity {project_id: $project_id})
RETURN r.type as type, count(r) as count
ORDER BY count DESC
"""
