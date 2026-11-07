from datetime import datetime

from strands import tool


@tool
def current_datetime() -> str:
    """Retorna a data e hora atuais do sistema local, no formato AAAA-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
