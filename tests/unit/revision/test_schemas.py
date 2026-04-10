from datetime import datetime

import pytest
from pydantic import ValidationError

from app.note.schemas import NoteType
from app.revision.schemas import Revision


def test_revision_parses_camel_case_response(
    revision_response: dict[str, object],
) -> None:
    result = Revision.model_validate(revision_response)
    assert result.revision_id == "yujrHQa6XfFI"
    assert result.note_id == "evnnmvHTCgIn"
    assert result.title == "My Note"
    assert result.mime == "text/html"
    assert result.blob_id == "DecH36BK5cLX6dYDg5yx"
    assert result.is_protected is False
    assert result.content_length == 584


def test_revision_parses_type_as_enum(revision_response: dict[str, object]) -> None:
    result = Revision.model_validate(revision_response)
    assert result.type == NoteType.text


def test_revision_parses_dates_as_datetime(
    revision_response: dict[str, object],
) -> None:
    result = Revision.model_validate(revision_response)
    assert isinstance(result.date_last_edited, datetime)
    assert isinstance(result.date_created, datetime)
    assert isinstance(result.utc_date_last_edited, datetime)
    assert isinstance(result.utc_date_created, datetime)
    assert isinstance(result.utc_date_modified, datetime)
    assert result.utc_date_created.tzinfo is not None


def test_revision_content_length_is_optional(
    revision_response: dict[str, object],
) -> None:
    payload = {k: v for k, v in revision_response.items() if k != "contentLength"}
    result = Revision.model_validate(payload)
    assert result.content_length is None


def test_revision_missing_required_field_raises(
    revision_response: dict[str, object],
) -> None:
    payload = {k: v for k, v in revision_response.items() if k != "revisionId"}
    with pytest.raises(ValidationError):
        Revision.model_validate(payload)
