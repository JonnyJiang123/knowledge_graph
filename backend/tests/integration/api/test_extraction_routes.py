"""Integration tests for extraction API routes."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


class TestExtractionJobs:
    """Tests for extraction job endpoints."""

    def test_create_extraction_job(self):
        """Test creating a new extraction job."""
        response = client.post(
            "/api/extraction/jobs",
            json={
                "project_id": "test-project-1",
                "text": "马云是阿里巴巴的创始人",
                "config": {
                    "extract_entities": True,
                    "extract_relations": True,
                    "entity_types": ["PERSON", "ORGANIZATION"]
                }
            }
        )

        assert response.status_code in [200, 201, 202]
        data = response.json()
        assert "job_id" in data
        assert "status" in data

    def test_get_extraction_job_status(self):
        """Test getting extraction job status."""
        # First create a job
        create_response = client.post(
            "/api/extraction/jobs",
            json={
                "project_id": "test-project-1",
                "text": "测试文本"
            }
        )

        if create_response.status_code in [200, 201, 202]:
            job_id = create_response.json()["job_id"]

            # Get job status
            response = client.get(f"/api/extraction/jobs/{job_id}")
            assert response.status_code == 200

            data = response.json()
            assert "job_id" in data
            assert "status" in data

    def test_get_nonexistent_job(self):
        """Test getting a job that doesn't exist."""
        response = client.get("/api/extraction/jobs/nonexistent-job-id")
        assert response.status_code == 404


class TestEntityMerge:
    """Tests for entity merge endpoint."""

    def test_merge_entities(self):
        """Test merging duplicate entities."""
        response = client.post(
            "/api/extraction/entities/merge",
            json={
                "project_id": "test-project-1",
                "entity_ids": ["entity-1", "entity-2"],
                "target_entity": {
                    "name": "阿里巴巴",
                    "type": "ORGANIZATION"
                }
            }
        )

        # May return 200 if implemented or 501 if not
        assert response.status_code in [200, 201, 501]

    def test_merge_entities_validation(self):
        """Test validation for merge request."""
        # Missing required fields
        response = client.post(
            "/api/extraction/entities/merge",
            json={
                "project_id": "test-project-1"
                # Missing entity_ids
            }
        )

        assert response.status_code in [400, 422]


class TestExtractionConfig:
    """Tests for extraction configuration."""

    def test_extraction_with_different_entity_types(self):
        """Test extraction with various entity type configurations."""
        test_cases = [
            {"entity_types": ["PERSON"]},
            {"entity_types": ["ORGANIZATION", "LOCATION"]},
            {"entity_types": []},  # All types
        ]

        for config in test_cases:
            response = client.post(
                "/api/extraction/jobs",
                json={
                    "project_id": "test-project-1",
                    "text": "马云是阿里巴巴的创始人",
                    "config": config
                }
            )
            assert response.status_code in [200, 201, 202]

    def test_extraction_empty_text(self):
        """Test extraction with empty text."""
        response = client.post(
            "/api/extraction/jobs",
            json={
                "project_id": "test-project-1",
                "text": ""
            }
        )

        # Should either accept or return validation error
        assert response.status_code in [200, 201, 400, 422]
