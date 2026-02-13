# 数据导入模块使用指南

## 概述

数据导入模块支持从文件或 MySQL 数据库导入数据到知识图谱系统。支持同步（小文件）和异步（大文件）两种处理模式。

## 支持的数据源

### 文件上传
- CSV (.csv)
- Excel (.xlsx)
- 文本文件 (.txt)
- PDF (.pdf)
- Word 文档 (.docx)

### 数据库连接
- MySQL 8.0+

## 环境配置

### 必要的环境变量

```bash
# 文件存储路径
UPLOAD_BASE_DIR=storage/uploads
TEMP_DIR=storage/tmp

# 预览行数限制
PREVIEW_ROW_LIMIT=50

# 加密密钥（用于加密数据库凭据）
# 生成方式: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your-fernet-key-here
```

### Docker 配置

确保 `docker-compose.yml` 中挂载了存储卷：

```yaml
services:
  backend:
    volumes:
      - uploads_data:/app/storage/uploads

  worker:
    volumes:
      - uploads_data:/app/storage/uploads

volumes:
  uploads_data:
```

## 启动服务

### 开发环境

```powershell
# 启动后端服务
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 启动 Celery Worker（新终端）
cd backend
celery -A src.infrastructure.queue.celery_app.celery_app worker -Q ingestion -l info

# 启动前端
cd frontend
npm run dev
```

### Docker 环境

```powershell
cd docker
docker-compose up -d
```

## 使用流程

### 1. 访问导入向导

登录系统后，在侧边栏点击 **数据导入** > **导入向导**。

### 2. 选择数据源类型

- **文件上传**：上传本地文件
- **MySQL 数据库**：连接远程数据库

### 3. 配置数据源

#### 文件上传
1. 拖拽文件到上传区域或点击选择文件
2. 支持最大 100MB 文件
3. 系统会自动检测文件格式

#### MySQL 连接
1. 填写主机地址、端口、数据库名
2. 填写用户名和密码
3. 点击「测试连接」验证配置
4. 可选择指定表名

### 4. 配置清洗规则（可选）

支持的规则类型：
- **非空检查 (NOT_NULL)**：确保字段值不为空
- **范围限制 (RANGE)**：限制数值在指定范围内
- **正则匹配 (REGEX)**：使用正则表达式验证格式
- **去重 (DEDUPE)**：去除重复记录

### 5. 预览并提交

1. 查看数据预览
2. 确认配置摘要
3. 点击「确认提交」

### 6. 查看任务状态

- 访问 **数据导入** > **任务列表** 查看所有任务
- 运行中的任务会自动刷新状态
- 完成后可查看结果文件路径

## 处理模式

### 同步模式
- 条件：文件 ≤5MB 或 ≤10,000 行
- 特点：立即返回结果，无需等待

### 异步模式
- 条件：文件 >5MB 或 >10,000 行
- 特点：后台 Celery Worker 处理，支持进度查询

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/ingestion/templates/cleaning` | GET | 获取清洗规则模板 |
| `/ingestion/sources` | GET | 获取数据源列表 |
| `/ingestion/sources` | POST | 创建数据源 |
| `/ingestion/sources/mysql/test` | POST | 测试 MySQL 连接 |
| `/ingestion/upload/file` | POST | 上传文件 |
| `/ingestion/preview` | POST | 预览清洗结果 |
| `/ingestion/mysql/import` | POST | 启动 MySQL 导入 |
| `/ingestion/jobs` | GET | 获取任务列表 |
| `/ingestion/jobs/{job_id}` | GET | 获取任务详情 |

## 故障排查

### 文件上传失败
1. 检查文件大小是否超过 100MB
2. 检查文件格式是否支持
3. 检查存储目录权限

### MySQL 连接失败
1. 确认网络连通性
2. 检查用户名密码
3. 确认数据库用户有读取权限

### 异步任务卡住
1. 检查 Celery Worker 是否运行
2. 检查 Redis 连接
3. 查看 Worker 日志

## 文件存储结构

```
storage/uploads/
├── {project_id}/
│   ├── raw/           # 原始上传文件
│   │   └── {artifact_id}.{ext}
│   └── clean/         # 清洗后文件
│       └── {job_id}.parquet
```
