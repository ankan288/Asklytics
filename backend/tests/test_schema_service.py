"""Production test suite for Schema Introspection Service (compact prompt schemas, column stats, sample rows)."""

import asyncio
import pytest
from app.services import schema_service, csv_service


def test_compact_schema_generation_for_uploaded_dataset():
    csv_bytes = b"category,amount,active\nBooks,15.5,1\nElectronics,99.9,1\nBooks,20.0,0"
    upload_res = asyncio.run(csv_service.process_csv(csv_bytes, "test_schema.csv"))
    ds_id = upload_res["datasource_id"]

    schema_text = schema_service.get_compact_schema(ds_id)

    assert "TABLE uploaded_data" in schema_text
    assert "TOTAL ROWS: 3" in schema_text
    assert "COLUMN STATS:" in schema_text
    assert "SAMPLE ROWS:" in schema_text


def test_rejects_unknown_datasource():
    with pytest.raises(ValueError) as exc:
        schema_service.get_compact_schema("non-existent-ds-id")
    assert "Unknown datasource" in str(exc.value)
