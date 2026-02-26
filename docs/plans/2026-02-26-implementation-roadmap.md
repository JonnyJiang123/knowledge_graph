# Knowledge Graph Platform - 实施路线图

**日期:** 2026-02-26  
**基准文档:** 2026-02-09-architecture-design.md  
**状态:** 基础架构已完成，核心功能待实施

---

## 已完成的基础 (✓)

### Backend Foundation
- ✓ 领域实体: Entity, Relation, GraphProject, DataSource, IngestionJob, User, Project
- ✓ 值对象: EntityType, Industry, Ingestion, RelationType
- ✓ 仓储端口: UserRepository, ProjectRepository, DataSourceRepository, IngestionJobRepository
- ✓ Graph仓储端口与实现: GraphProjectRepository, GraphEntityRepository (MySQL + Neo4j)
- ✓ 基础应用服务: GraphService, IngestionService
- ✓ 基础命令: create_entity, create_relation, create_graph_project, register_data_source, start_ingestion
- ✓ 基础查询: list_neighbors, list_data_sources, get_job_status
- ✓ 基础设施: Celery + Redis队列, LocalStorage, MySQL/Neo4j持久化
- ✓ API路由: auth, graph, ingestion, projects

### Frontend Foundation
- ✓ 基础Pinia stores: auth, graph, ingestion, project
- ✓ Graph Builder页面 (/graph/builder) - 项目/实体/关系创建向导
- ✓ Graph Jobs页面 (/graph/jobs) - 邻居查询与历史记录
- ✓ Ingestion Wizard - 数据摄取向导
- ✓ 基础组件: EntityComposer, RelationComposer, NeighborResultDrawer

---

## Phase 1: 核心知识抽取与NLP模块
**优先级:** P0 (核心功能)  
**预计工期:** 5-7天

### 1.1 Domain Layer - NLP服务
- [ ] `domain/ports/nlp/` - NLP端口定义
  - [ ] `tokenizer.py` - 分词器接口 (Tokenizer Port)
  - [ ] `ner_extractor.py` - 命名实体识别接口 (NERExtractor Port)
- [ ] `domain/services/extraction/` - 知识抽取服务
  - [ ] `knowledge_extractor.py` - NER + 关系抽取编排服务
- [ ] `domain/value_objects/` - 补充值对象
  - [ ] `match_score.py` - 匹配分数 (0-1浮点数验证)
  - [ ] `path_result.py` - 路径查询结果

### 1.2 Infrastructure Layer - NLP适配器
- [ ] `infrastructure/nlp/` - NLP适配器实现
  - [ ] `jieba_tokenizer.py` - Jieba分词实现
  - [ ] `hanlp_ner.py` - HanLP NER实现 (主)
  - [ ] `spacy_ner.py` - spaCy NER实现 (备选)
  - [ ] `relation_extractor.py` - 基于模式+依存句法的关系抽取

### 1.3 Application Layer - 抽取命令
- [ ] `application/commands/extract_knowledge.py` - 运行NER+关系抽取
- [ ] `application/commands/build_graph.py` - 实体/关系持久化到Neo4j
- [ ] `application/commands/merge_entities.py` - 实体消歧/融合
- [ ] `application/services/extraction_pipeline.py` - 分词→NER→关系→融合编排

### 1.4 API Layer - 抽取端点
- [ ] `api/routers/extraction.py` - 知识抽取路由
  - POST `/api/extraction/jobs` - 触发抽取任务
  - GET `/api/extraction/jobs/{job_id}` - 查询抽取任务状态
  - POST `/api/extraction/entities/merge` - 实体融合
- [ ] `api/schemas/extraction.py` - 抽取相关DTO

### 1.5 Tests
- [ ] `tests/unit/domain/test_knowledge_extractor.py`
- [ ] `tests/integration/nlp/test_ner.py`
- [ ] `tests/integration/api/test_extraction_routes.py`

---

## Phase 2: 图谱查询与可视化API
**优先级:** P0 (核心功能)  
**预计工期:** 4-5天

### 2.1 Domain Layer - 查询服务
- [ ] `domain/ports/repositories.py` - 扩展GraphEntityRepository
  - [ ] `search_entities()` - 关键词/条件搜索
  - [ ] `find_paths()` - N度路径查找
  - [ ] `get_subgraph()` - 子图获取

### 2.2 Infrastructure Layer - 查询实现
- [ ] `infrastructure/persistence/neo4j/cypher_queries.py` - Cypher查询模板
  - [ ] 实体搜索查询
  - [ ] 路径查找查询 (最短路径、所有路径)
  - [ ] 子图提取查询
- [ ] `infrastructure/persistence/neo4j/graph_algorithms.py` - Neo4j GDS算法
  - [ ] 中心性分析 (PageRank, Betweenness)
  - [ ] 社区发现 (Louvain)

### 2.3 Application Layer - 查询命令
- [ ] `application/queries/search_entities.py` - 实体搜索
- [ ] `application/queries/find_paths.py` - 路径查找
- [ ] `application/queries/get_graph_visualization.py` - 获取可视化数据
- [ ] `application/queries/analyze_centrality.py` - 中心性分析
- [ ] `application/queries/natural_language_query.py` - NL→Cypher转换 (基础版)
- [ ] `application/services/query_service.py` - 查询路由与缓存

### 2.4 API Layer - 查询与可视化端点
- [ ] `api/routers/entities.py` - 实体CRUD与批量操作
  - GET `/api/entities` - 搜索实体
  - GET `/api/entities/{id}` - 获取实体详情
  - PUT `/api/entities/{id}` - 更新实体
  - DELETE `/api/entities/{id}` - 删除实体
  - POST `/api/entities/batch` - 批量操作
- [ ] `api/routers/relations.py` - 关系CRUD与批量操作
  - GET `/api/relations` - 搜索关系
  - POST `/api/relations/batch` - 批量创建关系
- [ ] `api/routers/query.py` - 查询路由
  - POST `/api/query/search` - 条件搜索
  - POST `/api/query/paths` - 路径查找
  - POST `/api/query/nl` - 自然语言查询
- [ ] `api/routers/visualization.py` - 可视化数据
  - GET `/api/visualization/graph` - 获取图数据 (nodes + edges for ECharts)
  - GET `/api/visualization/centrality` - 中心性分析结果
- [ ] `api/schemas/visualization.py` - 可视化DTO (GraphData, Node, Edge)

### 2.5 Frontend - 查询组件
- [ ] `components/query/SearchBar.vue` - 搜索栏
- [ ] `components/query/NLQueryInput.vue` - 自然语言查询输入
- [ ] `components/query/PathFinder.vue` - 路径查找器
- [ ] `components/query/ResultList.vue` - 结果列表
- [ ] `stores/query.ts` - 查询状态管理
- [ ] `pages/query/QueryBuilder.vue` - 查询构建页面

### 2.6 Tests
- [ ] `tests/unit/application/test_query_service.py`
- [ ] `tests/integration/persistence/test_graph_queries.py`
- [ ] `tests/integration/api/test_query_routes.py`

---

## Phase 3: 推理规则引擎
**优先级:** P1 (增值功能)  
**预计工期:** 4-5天

### 3.1 Domain Layer - 规则引擎
- [ ] `domain/entities/rule.py` - 推理规则定义实体
- [ ] `domain/value_objects/risk_level.py` - 风险等级枚举 (LOW, MEDIUM, HIGH)
- [ ] `domain/services/reasoning/` - 推理服务
  - [ ] `rule_engine.py` - 基础规则评估引擎
  - [ ] `finance_rules.py` - 金融规则 (欺诈检测、风险传播)
  - [ ] `healthcare_rules.py` - 医疗规则 (药物相互作用、症状匹配)

### 3.2 Application Layer - 推理命令
- [ ] `application/commands/create_rule.py` - 创建推理规则
- [ ] `application/commands/run_reasoning.py` - 执行推理

### 3.3 API Layer - 推理端点
- [ ] `api/routers/reasoning.py` - 推理路由
  - GET/POST `/api/reasoning/rules` - 规则CRUD
  - POST `/api/reasoning/run` - 触发推理
  - GET `/api/reasoning/results/{job_id}` - 获取推理结果

### 3.4 Frontend - 推理组件
- [ ] `stores/reasoning.ts` - 推理状态管理
- [ ] `pages/reasoning/RuleManager.vue` - 规则管理页面
- [ ] `pages/reasoning/ReasoningResults.vue` - 推理结果页面

### 3.5 Tests
- [ ] `tests/unit/domain/test_rule_engine.py`
- [ ] `tests/integration/api/test_reasoning_routes.py`

---

## Phase 4: 金融行业模块
**优先级:** P1 (垂直行业)  
**预计工期:** 3-4天

### 4.1 Domain Layer - 金融特定服务
- [ ] `domain/services/analysis/centrality_analyzer.py` - 核心节点识别
- [ ] `domain/services/reasoning/finance_rules.py` - 金融推理规则
  - 关联分析规则
  - 欺诈检测规则
  - 风险传播算法

### 4.2 Application Layer - 金融查询
- [ ] `application/queries/analyze_enterprise.py` - 企业关联分析

### 4.3 API Layer - 金融端点
- [ ] `api/routers/finance/` - 金融行业路由
  - [ ] `association.py` - 企业关联分析
    - GET `/api/finance/enterprises/{id}/associations` - 企业关联图谱
  - [ ] `fraud.py` - 反欺诈检测
    - POST `/api/finance/fraud/detect` - 欺诈检测
  - [ ] `risk.py` - 信用风险评估
    - GET `/api/finance/enterprises/{id}/risk` - 风险评分
- [ ] `api/schemas/industry/finance.py` - 金融DTO (RiskReport, FraudAlert, AssociationGraph)

### 4.4 Frontend - 金融模块
- [ ] `pages/finance/EnterpriseAnalysis.vue` - 企业分析页面
- [ ] `pages/finance/RiskDashboard.vue` - 风险仪表板
- [ ] `components/industry/finance/RiskScoreCard.vue` - 风险评分卡
- [ ] `components/industry/finance/AssociationGraph.vue` - 关联图谱

### 4.5 Tests
- [ ] `tests/unit/domain/test_finance_rules.py`
- [ ] `tests/integration/api/finance/test_finance_routes.py`

---

## Phase 5: 医疗行业模块
**优先级:** P1 (垂直行业)  
**预计工期:** 3-4天

### 5.1 Domain Layer - 医疗特定服务
- [ ] `domain/services/matching/symptom_disease_matcher.py` - 症状-疾病匹配
- [ ] `domain/services/reasoning/healthcare_rules.py` - 医疗推理规则
  - 药物相互作用规则
  - 症状匹配规则

### 5.2 Application Layer - 医疗查询
- [ ] `application/queries/match_symptoms.py` - 症状→疾病匹配
- [ ] `application/queries/check_drug_interaction.py` - 药物相互作用检查

### 5.3 API Layer - 医疗端点
- [ ] `api/routers/healthcare/` - 医疗行业路由
  - [ ] `diagnosis.py` - 症状-疾病匹配
    - POST `/api/healthcare/diagnosis` - 症状诊断
  - [ ] `drugs.py` - 药物相互作用
    - POST `/api/healthcare/drugs/interactions` - 检查药物相互作用
  - [ ] `medical_records.py` - 病历质控
    - POST `/api/healthcare/records/qc` - 病历质量检查
- [ ] `api/schemas/industry/healthcare.py` - 医疗DTO (DiagnosisResult, DrugInteraction, QCReport)

### 5.4 Frontend - 医疗模块
- [ ] `pages/healthcare/DiagnosisAssistant.vue` - 诊断助手
- [ ] `pages/healthcare/DrugChecker.vue` - 药物检查器
- [ ] `components/industry/healthcare/SymptomSelector.vue` - 症状选择器
- [ ] `components/industry/healthcare/DiagnosisResult.vue` - 诊断结果

### 5.5 Tests
- [ ] `tests/unit/domain/test_healthcare_rules.py`
- [ ] `tests/integration/api/healthcare/test_healthcare_routes.py`

---

## Phase 6: 系统管理与监控
**优先级:** P2 (运维支持)  
**预计工期:** 2-3天

### 6.1 Application Layer - 系统服务
- [ ] `application/commands/backup_project.py` - 项目备份

### 6.2 Infrastructure Layer - 扩展
- [ ] `infrastructure/queue/tasks/reasoning_task.py` - 推理后台任务
- [ ] `infrastructure/queue/tasks/backup_task.py` - 备份后台任务
- [ ] `infrastructure/monitoring/` - 监控适配器
  - [ ] `metrics.py` - 指标收集
  - [ ] `health_checks.py` - 健康检查

### 6.3 API Layer - 系统端点
- [ ] `api/routers/jobs.py` - 后台任务状态轮询
  - GET `/api/jobs/{job_id}` - 任务状态查询
  - GET `/api/jobs/{job_id}/progress` - 任务进度
- [ ] `api/routers/system/` - 系统管理路由
  - [ ] `monitoring.py` - 健康检查与指标
    - GET `/api/system/health` - 健康检查
    - GET `/api/system/metrics` - 系统指标
  - [ ] `logs.py` - 操作日志
    - GET `/api/system/logs` - 查询操作日志
  - [ ] `backup.py` - 备份/恢复触发
    - POST `/api/system/backup` - 触发备份
    - POST `/api/system/restore` - 恢复备份

### 6.4 Frontend - 系统管理
- [ ] `stores/notification.ts` - 通知状态管理
- [ ] `stores/settings.ts` - 用户设置
- [ ] `pages/system/JobMonitor.vue` - 任务监控页面
- [ ] `pages/system/SystemLogs.vue` - 系统日志页面
- [ ] `components/common/NotificationToast.vue` - 通知提示

### 6.5 Tests
- [ ] `tests/integration/api/system/test_monitoring.py`

---

## Phase 7: 前端可视化与交互增强
**优先级:** P1 (用户体验)  
**预计工期:** 4-5天

### 7.1 核心可视化组件
- [ ] `components/graph/GraphCanvas.vue` - ECharts图谱画布封装
- [ ] `components/graph/NodeTooltip.vue` - 节点悬停提示
- [ ] `components/graph/FilterPanel.vue` - 实体/关系过滤器
- [ ] `components/graph/LayoutSwitcher.vue` - 布局切换 (力导向/层次/环形)
- [ ] `components/graph/ExportDialog.vue` - PNG/JSON导出对话框
- [ ] `stores/visualization.ts` - 可视化状态管理 (布局模式、过滤器、缩放级别)

### 7.2 数据摄取组件完善
- [ ] `components/extraction/FileUploader.vue` - 文件上传组件
- [ ] `components/extraction/DatabaseConnector.vue` - 数据库连接组件
- [ ] `components/extraction/DataPreview.vue` - 数据预览组件
- [ ] `components/extraction/JobProgress.vue` - 任务进度组件 (已有基础)
- [ ] `composables/useJobPolling.ts` - 任务轮询组合式函数

### 7.3 页面完善
- [ ] `pages/graph/GraphVisualization.vue` - 图谱可视化页面 (基于GraphCanvas)
- [ ] `pages/extraction/ExtractionManager.vue` - 知识抽取管理页面
- [ ] `pages/Dashboard.vue` - 仪表板页面增强

### 7.4 布局与路由
- [ ] `layouts/DashboardLayout.vue` - 仪表板布局
- [ ] `router/index.ts` - 路由配置更新

---

## 实施优先级建议

### 立即开始 (P0 - 核心功能)
1. **Phase 1** - NLP模块是知识抽取的核心，必须先实现
2. **Phase 2** - 查询与可视化是使用图谱的基础功能
3. **Phase 7** - 前端可视化组件 (与Phase 2并行)

### 短期跟进 (P1 - 增值功能)
4. **Phase 3** - 推理规则引擎 (依赖Phase 1)
5. **Phase 4** - 金融行业模块 (依赖Phase 2, 3)
6. **Phase 5** - 医疗行业模块 (依赖Phase 2, 3)

### 后期完善 (P2 - 运维支持)
7. **Phase 6** - 系统管理与监控 (独立模块)

---

## 技术债务与优化

### 待优化项
- [ ] 完善错误处理: `api/middleware/error_handler.py` 补充DomainError映射
- [ ] 依赖注入容器: `api/dependencies/container.py` 实现完整DI
- [ ] 文件解析器: `infrastructure/storage/file_parsers/` PDF/Word解析器
- [ ] 云存储适配器: `infrastructure/storage/aliyun_oss.py`
- [ ] 缓存策略: `infrastructure/cache/redis_cache.py` 实现Redis缓存

---

## 当前代码统计

### Backend
- Python文件: 70+
- 单元测试: 9个测试文件
- 集成测试: 8个测试文件
- E2E测试: 1个测试文件

### Frontend
- TypeScript/Vue文件: 40+
- 单元测试: 4个测试文件
- Pinia stores: 4个
- API客户端: 4个

---

## 预计总工期

- **Phase 1 (NLP)**: 5-7天
- **Phase 2 (查询)**: 4-5天
- **Phase 3 (推理)**: 4-5天
- **Phase 4 (金融)**: 3-4天
- **Phase 5 (医疗)**: 3-4天
- **Phase 6 (系统)**: 2-3天
- **Phase 7 (前端)**: 4-5天

**总计**: 25-33天 (单人全栈开发)  
**并行开发**: 15-20天 (前后端并行)
