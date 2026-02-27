"""Tests for domain value objects."""

import pytest

from src.domain.value_objects.match_score import MatchScore
from src.domain.value_objects.path_result import PathNode, PathEdge, PathResult, PathQueryResult


class TestMatchScore:
    """Tests for match score value object."""
    
    def test_valid_score(self):
        score = MatchScore(0.5)
        assert score.value == 0.5
    
    def test_valid_boundary_scores(self):
        assert MatchScore(0.0).value == 0.0
        assert MatchScore(1.0).value == 1.0
    
    def test_invalid_score_raises(self):
        with pytest.raises(ValueError):
            MatchScore(-0.1)
        with pytest.raises(ValueError):
            MatchScore(1.1)
    
    def test_comparison(self):
        score1 = MatchScore(0.3)
        score2 = MatchScore(0.7)
        
        assert score1 < score2
        assert score2 > score1
        assert score1 <= score2
        assert score2 >= score1


class TestPathResult:
    """Tests for path result value object."""
    
    def test_path_properties(self):
        node1 = PathNode("1", "PERSON", "Alice", {})
        node2 = PathNode("2", "PERSON", "Bob", {})
        edge = PathEdge("1", "2", "KNOWS", {})
        
        path = PathResult(
            start_id="1",
            end_id="2",
            nodes=[node1, node2],
            edges=[edge],
            length=1,
            algorithm="shortest_path"
        )
        
        assert path.node_count == 2
        assert path.edge_count == 1
        assert path.start_id == "1"
        assert path.end_id == "2"


class TestPathQueryResult:
    """Tests for path query result."""
    
    def test_shortest_path_selection(self):
        node1 = PathNode("1", "PERSON", "Alice", {})
        node2 = PathNode("2", "PERSON", "Bob", {})
        node3 = PathNode("3", "PERSON", "Charlie", {})
        
        path1 = PathResult("1", "2", [node1, node2], [], 1)
        path2 = PathResult("1", "3", [node1, node2, node3], [], 2)
        
        result = PathQueryResult("1", "3", [path1, path2], 2)
        shortest = result.shortest_path
        
        assert shortest is not None
        assert shortest.length == 1
    
    def test_filter_by_max_length(self):
        node1 = PathNode("1", "PERSON", "Alice", {})
        node2 = PathNode("2", "PERSON", "Bob", {})
        node3 = PathNode("3", "PERSON", "Charlie", {})
        
        path1 = PathResult("1", "2", [node1, node2], [], 1)
        path2 = PathResult("1", "3", [node1, node2, node3], [], 2)
        
        result = PathQueryResult("1", "3", [path1, path2], 2)
        filtered = result.filter_by_max_length(1)
        
        assert len(filtered.paths) == 1
        assert filtered.paths[0].length == 1
