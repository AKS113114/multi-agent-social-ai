from abc import ABC, abstractmethod
from typing import Dict, Any, Type, TypeVar, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.llm.ollama_client import OllamaClient, ollama_client
from app.orchestration.state import MessageBus
from app.orchestration.messages import AgentMessage

T = TypeVar("T", bound=BaseModel)

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, system_prompt: str, client: Optional[OllamaClient] = None):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.client = client or ollama_client

    def generate_structured(self, user_prompt: str, schema: Type[T], temperature: float = 0.2) -> T:
        """
        Executes Ollama generate_json using the agent's dedicated system prompt.
        """
        return self.client.generate_json(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            schema=schema,
            temperature=temperature
        )

    def generate_text(self, user_prompt: str, temperature: float = 0.7) -> str:
        """
        Executes raw text generation.
        """
        return self.client.generate(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            temperature=temperature
        )

    def log_and_send(
        self,
        db: Session,
        campaign_id: str,
        recipient: str,
        message_type: str,
        payload: Dict[str, Any],
        action: str,
        input_summary: str,
        output_summary: str,
        status: str = "SUCCESS",
        revision_count: int = 0,
        parent_message_id: Optional[str] = None
    ) -> AgentMessage:
        """
        Helper method to log trace and send a message across the bus simultaneously.
        """
        msg = AgentMessage(
            campaign_id=campaign_id,
            sender=self.name,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            parent_message_id=parent_message_id,
            status=status
        )
        MessageBus.send_message(db, msg)
        MessageBus.log_trace(
            db=db,
            campaign_id=campaign_id,
            agent=self.name,
            action=action,
            input_summary=input_summary,
            output_summary=output_summary,
            status=status,
            revision_count=revision_count,
            handoff_to=recipient
        )
        return msg

    @abstractmethod
    def execute(self, db: Session, campaign_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution contract for each specialized agent.
        """
        pass
