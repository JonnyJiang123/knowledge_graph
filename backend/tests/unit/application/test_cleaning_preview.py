import pytest

from src.application.commands.apply_cleaning_preview import (
    ApplyCleaningPreviewCommand,
    apply_cleaning_preview,
)
from src.domain.value_objects.ingestion import CleaningRule, CleaningRuleType


@pytest.mark.asyncio
async def test_apply_cleaning_preview_command(mocker):
    service = mocker.AsyncMock()
    service.apply_rules_to_preview.return_value = [{"is_valid": True}]

    command = ApplyCleaningPreviewCommand(
        artifact_id="artifact-1",
        rules=[
            CleaningRule(
                id="r1",
                field="amount",
                rule_type=CleaningRuleType.RANGE,
                params={"min": 0},
            )
        ],
    )

    result = await apply_cleaning_preview(service, command)

    assert result == [{"is_valid": True}]
    service.apply_rules_to_preview.assert_awaited_once_with("artifact-1", command.rules)
