from datetime import datetime

import pytest
from pydantic import ValidationError

from app.notes.schemas import (
    Attribute,
    AttributeType,
    Note,
    NoteType,
    SearchNotesResponse,
)


def test_note_parses_camel_case_response(note_response: dict[str, object]) -> None:
    result = Note.model_validate(note_response)
    assert result.note_id == "evnnmvHTCgIn"
    assert result.title == "My Note"
    assert result.mime == "text/html"
    assert result.blob_id == "DecH36BK5cLX6dYDg5yx"
    assert result.is_protected is False


def test_note_parses_type_as_enum(note_response: dict[str, object]) -> None:
    result = Note.model_validate(note_response)
    assert result.type == NoteType.text


def test_note_parses_dates_as_datetime(note_response: dict[str, object]) -> None:
    result = Note.model_validate(note_response)
    assert isinstance(result.date_created, datetime)
    assert isinstance(result.date_modified, datetime)
    assert isinstance(result.utc_date_created, datetime)
    assert isinstance(result.utc_date_modified, datetime)
    assert result.utc_date_created.tzinfo is not None


def test_note_defaults_empty_lists(note_response: dict[str, object]) -> None:
    result = Note.model_validate(note_response)
    assert result.attributes == []
    assert result.parent_note_ids == []
    assert result.child_note_ids == []
    assert result.parent_branch_ids == []
    assert result.child_branch_ids == []


def test_note_missing_required_field_raises(note_response: dict[str, object]) -> None:
    payload = {k: v for k, v in note_response.items() if k != "noteId"}
    with pytest.raises(ValidationError):
        Note.model_validate(payload)


def test_attribute_parses_type_as_enum() -> None:
    payload = {
        "attributeId": "evnnmvHTCgIn",
        "noteId": "evnnmvHTCgIn",
        "type": "label",
        "name": "book",
        "value": "",
        "position": 10,
        "isInheritable": False,
        "utcDateModified": "2022-03-07T21:54:25.277Z",
    }
    result = Attribute.model_validate(payload)
    assert result.type == AttributeType.label


def test_search_notes_response_parses_results(
    note_response: dict[str, object],
) -> None:
    payload = {"results": [note_response]}
    result = SearchNotesResponse.model_validate(payload)
    assert len(result.results) == 1
    assert result.results[0].note_id == "evnnmvHTCgIn"
    assert result.debug_info is None


def test_search_notes_response_parses_debug_info(
    note_response: dict[str, object],
) -> None:
    payload = {
        "results": [note_response],
        "debugInfo": {"parsedQuery": "something"},
    }
    result = SearchNotesResponse.model_validate(payload)
    assert result.debug_info == {"parsedQuery": "something"}
