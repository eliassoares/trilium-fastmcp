from datetime import datetime

import pytest
from pydantic import ValidationError

from app.branch.schemas import Branch


@pytest.fixture
def branch_response() -> dict[str, object]:
    return {
        "branchId": "root_evnnmvHTCgIn",
        "noteId": "evnnmvHTCgIn",
        "parentNoteId": "root",
        "prefix": None,
        "notePosition": 10,
        "isExpanded": False,
        "utcDateModified": "2022-03-07T21:54:25.277Z",
    }


def test_branch_parses_camel_case_response(branch_response: dict[str, object]) -> None:
    result = Branch.model_validate(branch_response)
    assert result.branch_id == "root_evnnmvHTCgIn"
    assert result.note_id == "evnnmvHTCgIn"
    assert result.parent_note_id == "root"
    assert result.note_position == 10
    assert result.is_expanded is False
    assert result.prefix is None


def test_branch_parses_utc_date_modified_as_datetime(
    branch_response: dict[str, object],
) -> None:
    result = Branch.model_validate(branch_response)
    assert isinstance(result.utc_date_modified, datetime)
    assert result.utc_date_modified is not None
    assert result.utc_date_modified.tzinfo is not None


def test_branch_branch_id_is_optional(branch_response: dict[str, object]) -> None:
    payload = {k: v for k, v in branch_response.items() if k != "branchId"}
    result = Branch.model_validate(payload)
    assert result.branch_id is None


def test_branch_utc_date_modified_is_optional(
    branch_response: dict[str, object],
) -> None:
    payload = {k: v for k, v in branch_response.items() if k != "utcDateModified"}
    result = Branch.model_validate(payload)
    assert result.utc_date_modified is None


def test_branch_missing_required_note_id_raises(
    branch_response: dict[str, object],
) -> None:
    payload = {k: v for k, v in branch_response.items() if k != "noteId"}
    with pytest.raises(ValidationError):
        Branch.model_validate(payload)


def test_branch_missing_required_parent_note_id_raises(
    branch_response: dict[str, object],
) -> None:
    payload = {k: v for k, v in branch_response.items() if k != "parentNoteId"}
    with pytest.raises(ValidationError):
        Branch.model_validate(payload)
