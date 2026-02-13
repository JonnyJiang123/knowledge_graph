from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class DataSourceType(str, Enum):
    FILE = "FILE"
    MYSQL = "MYSQL"


class FileFormat(str, Enum):
    CSV = "CSV"
    XLSX = "XLSX"
    TXT = "TXT"
    PDF = "PDF"
    DOCX = "DOCX"


class CleaningRuleType(str, Enum):
    NOT_NULL = "NOT_NULL"
    RANGE = "RANGE"
    REGEX = "REGEX"
    DEDUPE = "DEDUPE"


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ProcessingMode(str, Enum):
    SYNC = "SYNC"
    ASYNC = "ASYNC"


@dataclass(frozen=True)
class CleaningRule:
    id: str
    field: str
    rule_type: CleaningRuleType
    params: dict[str, Any]
    message: Optional[str] = None


@dataclass(frozen=True)
class FileArtifact:
    artifact_id: str
    project_id: str
    stored_path: str
    file_format: FileFormat
    size_bytes: int
    uploaded_by: str
    checksum: Optional[str] = None
