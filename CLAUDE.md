# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

智能知识图谱MVP平台 (Intelligent Knowledge Graph MVP Platform) - a lightweight knowledge graph tool for SMEs in financial and healthcare industries. The product enables knowledge graph construction, querying, visualization, and basic reasoning analysis.

Full requirements documented in [知识图谱prd.md](知识图谱prd.md).

## Target Technology Stack

### Frontend
- Vue.js 3.x + Vite (build tool)
- ECharts 5.x (visualization)
- Element Plus (UI components)
- Axios, Vue Router, Pinia

### Backend
- FastAPI 0.100+ (API layer)
- Python 3.9+
- NLP: Jieba (tokenization), spaCy, HanLP (NER)
- Graph algorithms: NetworkX, Neo4j built-in algorithms
- Rule engine: Drools (lightweight) or custom

### Data Layer
- MySQL 8.0 (relational data, logs, settings)
- Neo4j 5.x Community Edition (graph storage)
- Local filesystem + optional cloud storage (Aliyun OSS/Tencent COS)

### Deployment
- Single-node deployment (Windows/Linux)
- Optional Docker containerization
- Monitoring: Prometheus + Grafana

## Architecture

Four-layer modular design:
```
System Management Layer (users, permissions, monitoring, backup)
├─ Industry Customization Layer
│  ├─ Finance: risk analysis, fraud detection, enterprise association
│  └─ Healthcare: symptom-disease matching, drug interactions, medical record QC
├─ Core Function Layer (extraction, modeling, storage, query, visualization, reasoning)
└─ Base Layer (data ingestion, preprocessing)
```

## Key Performance Targets

Based on 8-core 16GB RAM, ≤1M entities, ≤5M relations:
- Single entity query: ≤500ms
- 3-degree path query: ≤1s
- Natural language query: ≤2s (≥85% accuracy)
- 10K node graph load: ≤3s
- Entity recognition accuracy: ≥95%
- Relation extraction accuracy: ≥90%

## Domain-Specific Requirements

### Finance Module
- Enterprise association analysis (3-degree paths)
- Anti-fraud detection (account clustering, suspicious transactions)
- Credit risk assessment reports

### Healthcare Module
- Symptom-disease-department matching
- Drug interaction queries (contraindications per pharmacopeia)
- Medical record logic validation

# language
All code comments should be in Simplified Chinese

# environment
The current system is windows11. Any command execution must be carried out in accordance with the powershell specification, and at the same time, garbled text output in the command line should be avoided
