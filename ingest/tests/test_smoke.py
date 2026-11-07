"""Smoke tests: the package installs, and its key dependencies import and work."""

import importlib
import io

import pytest

import meridian_ingest


def test_entry_point_runs(capsys):
    meridian_ingest.main()
    assert "meridian-ingest" in capsys.readouterr().out

@pytest.mark.parametrize("module", ["pydantic", "fastavro", "confluent_kafka"])
def test_dependency_imports(module):
    importlib.import_module(module)

def test_pydantic_validates_input():
    from pydantic import BaseModel, Field, ValidationError

    class Event(BaseModel):
        tenant_id: str
        tokens: int = Field(ge=0)

    assert Event(tenant_id = "t00", tokens = 5).tokens == 5
    with pytest.raises(ValidationError):
        Event(tenant_id = "t00", tokens = -1)

def test_avro_round_trip():
    import fastavro

    schema = fastavro.parse_schema(
            {
                "type": "record",
                "name": "Ping",
                "fields": [
                    {"name": "tenant_id", "type": "string"},
                    {"name": "tokens", "type": "int"},
                ],
            }
    )
    record = {"tenant_id": "t00", "tokens": 42}
    buffer = io.BytesIO()
    fastavro.schemaless_writer(buffer, schema, record)
    buffer.seek(0)
    assert fastavro.schemaless_reader(buffer, schema) == record


def test_kafka_client_library_loads():
    import confluent_kafka

    librdkafka_version, _ = confluent_kafka.libversion()
    assert librdkafka_version


