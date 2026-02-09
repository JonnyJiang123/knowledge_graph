import pytest
from src.domain.entities.user import User
from src.domain.entities.project import Project
from src.domain.value_objects.industry import Industry


def test_user_can_manage_own_project():
    """测试用户可以管理自己的项目"""
    user = User(
        id="user-1",
        username="testuser",
        email="test@example.com",
        hashed_password="hash",
    )
    project = Project(
        id="proj-1",
        name="My Project",
        industry=Industry.FINANCE,
        owner_id="user-1",
    )

    assert user.can_manage_project(project) is True


def test_user_cannot_manage_other_project():
    """测试用户不能管理其他人的项目"""
    user = User(
        id="user-1",
        username="testuser",
        email="test@example.com",
        hashed_password="hash",
    )
    project = Project(
        id="proj-1",
        name="Other Project",
        industry=Industry.FINANCE,
        owner_id="user-2",
    )

    assert user.can_manage_project(project) is False


def test_superuser_can_manage_any_project():
    """测试超级用户可以管理任何项目"""
    superuser = User(
        id="admin-1",
        username="admin",
        email="admin@example.com",
        hashed_password="hash",
        is_superuser=True,
    )
    project = Project(
        id="proj-1",
        name="Other Project",
        industry=Industry.HEALTHCARE,
        owner_id="user-2",
    )

    assert superuser.can_manage_project(project) is True


def test_project_industry_string_conversion():
    """测试项目行业字符串自动转换为枚举"""
    project = Project(
        id="proj-1",
        name="Test",
        industry="FINANCE",  # 字符串，不是枚举
        owner_id="user-1",
    )

    assert project.industry == Industry.FINANCE
    assert isinstance(project.industry, Industry)
