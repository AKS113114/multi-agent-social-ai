import pytest
from pydantic import BaseModel, Field
from app.llm.ollama_client import OllamaClient
from app.llm.validators import parse_and_validate, extract_json_string

class SampleSchema(BaseModel):
    name: str = Field(description="Sample name")
    score: int = Field(description="Sample score")

def test_extract_json_string():
    raw_markdown = "```json\n{\"name\": \"test\", \"score\": 10}\n```"
    cleaned = extract_json_string(raw_markdown)
    assert cleaned == "{\"name\": \"test\", \"score\": 10}"

def test_parse_and_validate_success():
    valid_json = '{"name": "Espresso Machine", "score": 95}'
    instance, error = parse_and_validate(valid_json, SampleSchema)
    assert error is None
    assert instance is not None
    assert instance.name == "Espresso Machine"
    assert instance.score == 95

def test_parse_and_validate_malformed():
    invalid_json = '{"name": "Espresso Machine", "score": "not_an_int"}'
    instance, error = parse_and_validate(invalid_json, SampleSchema)
    assert instance is None
    assert error is not None
    assert "Pydantic Validation Error" in error

def test_ollama_health_check():
    client = OllamaClient()
    health = client.health_check()
    assert "status" in health
    assert health["status"] in ["ok", "warning", "offline"]
