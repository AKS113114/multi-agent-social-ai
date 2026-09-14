import json
import logging
from typing import Type, TypeVar, Optional, Dict, Any
import httpx
from pydantic import BaseModel
from app.config import settings
from app.llm.validators import parse_and_validate

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

class OllamaClient:
    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL, model: str = settings.OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = settings.OLLAMA_TIMEOUT

    def health_check(self) -> Dict[str, Any]:
        """
        Verifies local Ollama server is responsive and model is installed.
        """
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code != 200:
                    return {"status": "error", "message": f"Ollama HTTP {res.status_code}"}
                
                data = res.json()
                models = [m.get("name") for m in data.get("models", [])]
                model_found = any(self.model in m for m in models)
                
                return {
                    "status": "ok" if model_found else "warning",
                    "available_models": models,
                    "target_model": self.model,
                    "target_model_installed": model_found,
                    "message": "Ollama running successfully." if model_found else f"Model '{self.model}' not found in Ollama list."
                }
        except Exception as e:
            return {
                "status": "offline",
                "message": f"Ollama is not running at {self.base_url}. Error: {str(e)}"
            }

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7, json_format: bool = False) -> str:
        """
        Generates response from local Ollama model using /api/generate with JSON mode.
        """
        payload = {
            "model": self.model,
            "prompt": f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:",
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        if json_format:
            payload["format"] = "json"
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "").strip()
        except httpx.HTTPError as e:
            logger.error(f"Ollama HTTP request failed: {e}")
            raise RuntimeError(f"Ollama local LLM connection failed: {e}")

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Type[T],
        temperature: float = 0.2,
        max_retries: int = settings.MAX_LLM_RETRIES
    ) -> T:
        """
        Generates structured JSON with Ollama native JSON mode + Pydantic schema validation & repair retries.
        """
        schema_fields = list(schema.model_fields.keys())
        json_instructions = (
            f"\n\nIMPORTANT: Output ONLY a valid JSON object matching this schema.\n"
            f"Required JSON keys: {schema_fields}\n"
            f"Full Schema Format Reference:\n{json.dumps(schema.model_json_schema(), indent=2)}"
        )
        
        full_system_prompt = system_prompt + json_instructions
        current_user_prompt = user_prompt
        last_error = ""

        for attempt in range(1, max_retries + 1):
            try:
                raw_response = self.generate(full_system_prompt, current_user_prompt, temperature=temperature, json_format=True)
                instance, error = parse_and_validate(raw_response, schema)
                
                if instance is not None:
                    return instance
                
                last_error = error
                logger.warning(f"Ollama JSON validation attempt {attempt}/{max_retries} failed: {error}")
                
                current_user_prompt = (
                    f"{user_prompt}\n\n"
                    f"PREVIOUS RESPONSE FAILED SCHEMA VALIDATION:\n"
                    f"Error: {error}\n"
                    f"Previous Output: {raw_response}\n"
                    f"Output ONLY valid JSON matching expected schema fields: {schema_fields}."
                )
            except Exception as e:
                logger.error(f"Exception during generate_json attempt {attempt}: {e}")
                last_error = str(e)
        
        raise ValueError(f"Failed to generate valid JSON for schema '{schema.__name__}' after {max_retries} retries. Last error: {last_error}")

ollama_client = OllamaClient()
