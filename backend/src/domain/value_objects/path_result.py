"""Path result value object for graph queries."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class PathNode:
    """A node in a path result."""
    id: str
    type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PathEdge:
    """An edge in a path result."""
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PathResult:
    """Result of a path finding query.
    
    Immutable value object representing a path from start to end.
    """
    start_id: str
    end_id: str
    nodes: List[PathNode]
    edges: List[PathEdge]
    length: int
    algorithm: str = "default"  # shortest_path, all_paths, etc.
    score: Optional[float] = None  # relevance or similarity score
    
    @property
    def node_count(self) -> int:
        """Number of nodes in the path."""
        return len(self.nodes)
    
    @property
    def edge_count(self) -> int:
        """Number of edges in the path."""
        return len(self.edges)


@dataclass
class PathQueryResult:
    """Result of a path query that may contain multiple paths."""
    start_id: str
    end_id: str
    paths: List[PathResult] = field(default_factory=list)
    total_count: int = 0
    
    def __post_init__(self):
        if self.total_count == 0 and self.paths:
            self.total_count = len(self.paths)
    
    @property
    def shortest_path(self) -> Optional[PathResult]:
        """Get the shortest path among results."""
        if not self.paths:
            return None
        return min(self.paths, key=lambda p: p.length)
    
    def filter_by_max_length(self, max_length: int) -> "PathQueryResult":
        """Filter paths by maximum length."""
        filtered = [p for p in self.paths if p.length <= max_length]
        return PathQueryResult(
            start_id=self.start_id,
            end_id=self.end_id,
            paths=filtered,
            total_count=len(filtered)
        )
