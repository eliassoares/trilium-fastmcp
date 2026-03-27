from datetime import datetime

import pytest
from pydantic import ValidationError

from app.general.schemas import AppInfoResponse


def test_parses_camel_case_response(app_info_response: dict[str, object]) -> None:
    result = AppInfoResponse.model_validate(app_info_response)
    assert result.app_version == "0.50.2"
    assert result.db_version == 194
    assert result.sync_version == 25
    assert result.build_revision == "23daaa2387a0655685377f0a541d154aeec2aae8"
    assert result.data_directory == "/home/user/data"
    assert result.clipper_protocol_version == "1.0"


def test_parses_build_date_as_datetime(app_info_response: dict[str, object]) -> None:
    result = AppInfoResponse.model_validate(app_info_response)
    assert isinstance(result.build_date, datetime)
    assert result.build_date.year == 2022
    assert result.build_date.month == 2
    assert result.build_date.day == 9


def test_parses_utc_date_time_as_datetime(app_info_response: dict[str, object]) -> None:
    result = AppInfoResponse.model_validate(app_info_response)
    assert isinstance(result.utc_date_time, datetime)
    assert result.utc_date_time.tzinfo is not None
    assert result.utc_date_time.year == 2022


def test_missing_required_field_raises(app_info_response: dict[str, object]) -> None:
    payload = {k: v for k, v in app_info_response.items() if k != "appVersion"}
    with pytest.raises(ValidationError):
        AppInfoResponse.model_validate(payload)
