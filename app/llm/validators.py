import json
import re
from typing import Type, TypeVar, Tuple, Optional
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

def extract_json_string(text: str) -> str:
    """
    Extracts valid JSON from raw text response, removing markdown ```json wrappers if present.
    """
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    first_brace = min(
        [pos for pos in [text.find('{'), text.find('[')] if pos != -1],
        default=-1
    )
    last_brace = max(
        [text.rfind('}'), text.rfind(']')],
        default=-1
    )
    
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return text[first_brace:last_brace + 1].strip()
        
    return text

def parse_and_validate(text: str, schema: Type[T]) -> Tuple[Optional[T], Optional[str]]:
    """
    Parses string into JSON and validates against a Pydantic model.
    Handles small LLM structural quirks (e.g. list returned instead of object with list field, control chars).
    """
    cleaned_json = extract_json_string(text)
    data = None
    try:
        data = json.loads(cleaned_json, strict=False)
    except json.JSONDecodeError:
        # Fallback sanitization for unescaped newlines in LLM output strings
        try:
            sanitized = re.sub(r'[\r\n]+', ' ', cleaned_json)
            data = json.loads(sanitized, strict=False)
        except json.JSONDecodeError as e:
            return None, f"JSON Decode Error: {str(e)}"

    try:
        # Fallback fix if LLM returns a raw list for a schema expecting a list field (e.g. ContentOutput)
        if isinstance(data, list) and hasattr(schema, "model_fields") and "posts" in schema.model_fields:
            data = {"posts": data}
            
        # Fallback fix if LLM echoes '$defs' schema definition wrapper
        if isinstance(data, dict) and "$defs" in data and "posts" not in data:
            for k, v in data.items():
                if isinstance(v, list):
                    data = {"posts": v}
                    break

        validated = schema.model_validate(data)
        return validated, None
    except ValidationError as e:
        return None, f"Pydantic Validation Error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected Parsing Error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected Parsing Error: {str(e)}"
