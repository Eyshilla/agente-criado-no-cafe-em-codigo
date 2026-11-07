import os
import shutil
from datetime import datetime

from strands import Agent
from strands.models.openai import OpenAIModel
from strands.session import FileSessionManager

from tools.datetime_tool import current_datetime

DEFAULT_SYSTEM_PROMPT = "Você é um assistente prestativo. Responda em português."


def create_agent(tools: list | None = None) -> Agent:
    sessions_dir = os.getenv("SESSIONS_DIR", "sessions")

    # Cada execução inicia com sessão limpa (RN-03 / CA-09)
    if os.path.isdir(sessions_dir):
        shutil.rmtree(sessions_dir)

    model = OpenAIModel(
        client_args={"api_key": os.environ["OPENAI_API_KEY"]},
        model_id=os.getenv("MODEL_ID", "gpt-4o-mini"),
    )

    return Agent(
        model=model,
        tools=tools or [current_datetime],
        system_prompt=os.getenv("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT),
        session_manager=FileSessionManager(
            session_id=f"session-{datetime.now():%Y%m%d-%H%M%S}",
            storage_dir=sessions_dir,
        ),
    )
