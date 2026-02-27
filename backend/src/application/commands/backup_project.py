"""项目备份命令"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class BackupResult:
    """备份结果"""
    backup_id: str
    status: str  # success, failed, partial
    path: str
    size_bytes: int
    projects_backed_up: list[str]
    errors: list[str]
    created_at: datetime


class BackupService:
    """备份服务"""

    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def backup_project(
        self,
        project_id: str,
        include_graph: bool = True,
        include_documents: bool = True
    ) -> BackupResult:
        """备份单个项目"""
        backup_id = f"backup-{project_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        backup_dir = self.storage_path / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)

        errors = []

        try:
            # 备份图谱数据
            if include_graph:
                await self._backup_graph_data(project_id, backup_dir / "graph")

            # 备份文档
            if include_documents:
                await self._backup_documents(project_id, backup_dir / "documents")

            # 备份元数据
            await self._backup_metadata(project_id, backup_dir / "metadata.json")

            # 计算大小
            size_bytes = self._calculate_dir_size(backup_dir)

            return BackupResult(
                backup_id=backup_id,
                status="success" if not errors else "partial",
                path=str(backup_dir),
                size_bytes=size_bytes,
                projects_backed_up=[project_id],
                errors=errors,
                created_at=datetime.now()
            )

        except Exception as e:
            return BackupResult(
                backup_id=backup_id,
                status="failed",
                path=str(backup_dir),
                size_bytes=0,
                projects_backed_up=[],
                errors=[str(e)],
                created_at=datetime.now()
            )

    async def backup_multiple(
        self,
        project_ids: list[str],
        include_graph: bool = True,
        include_documents: bool = True
    ) -> BackupResult:
        """备份多个项目"""
        backup_id = f"backup-multi-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        backup_dir = self.storage_path / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)

        errors = []
        backed_up = []

        for project_id in project_ids:
            try:
                result = await self.backup_project(
                    project_id,
                    include_graph,
                    include_documents
                )
                if result.status in ("success", "partial"):
                    backed_up.append(project_id)
                errors.extend(result.errors)
            except Exception as e:
                errors.append(f"Project {project_id}: {str(e)}")

        size_bytes = self._calculate_dir_size(backup_dir)

        return BackupResult(
            backup_id=backup_id,
            status="success" if len(backed_up) == len(project_ids)
                   else "partial" if backed_up else "failed",
            path=str(backup_dir),
            size_bytes=size_bytes,
            projects_backed_up=backed_up,
            errors=errors,
            created_at=datetime.now()
        )

    async def _backup_graph_data(self, project_id: str, output_dir: Path) -> None:
        """备份图谱数据"""
        output_dir.mkdir(parents=True, exist_ok=True)
        # TODO: 导出Neo4j数据

    async def _backup_documents(self, project_id: str, output_dir: Path) -> None:
        """备份文档"""
        output_dir.mkdir(parents=True, exist_ok=True)
        # TODO: 复制文档文件

    async def _backup_metadata(self, project_id: str, output_path: Path) -> None:
        """备份元数据"""
        import json
        metadata = {
            "project_id": project_id,
            "backed_up_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        output_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2))

    def _calculate_dir_size(self, path: Path) -> int:
        """计算目录大小"""
        total = 0
        for f in path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
        return total
