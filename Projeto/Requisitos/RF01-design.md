# Design — RF-01 Chat interativo via terminal (Strands + OpenAI)

Documento de design técnico do requisito `RF01-chat-interativo.md`.

## 1. Visão geral da arquitetura

Aplicação Python de linha de comando em loop REPL. Um único processo local:
o usuário digita no terminal, o agente Strands envia a conversa ao modelo da
OpenAI e a resposta completa é exibida no terminal.

```
Usuário → terminal (input) → chat.py → Agent (Strands)
                                        ├── OpenAIModel (API OpenAI)
                                        ├── tools: [current_datetime]
                                        └── FileSessionManager → sessions/
              terminal (print) ← resposta ←┘
```

## 2. Estrutura de arquivos

```
Projeto/
├── chat.py                 # entrypoint: carrega .env, valida config, loop REPL
├── agent_factory.py        # cria e configura o Agent (modelo, tools, memória)
├── tools/
│   └── datetime_tool.py    # tool current_datetime
├── sessions/               # histórico de sessão (gerado em runtime)
├── .env                    # configuração real (não versionado)
├── .env.example            # template das variáveis
├── requirements.txt
└── Requisitos/
    ├── RF01-chat-interativo.md
    └── RF01-design.md
```

Separação em módulos pequenos (entrypoint / fábrica do agente / tools) para
atender RN-10: adicionar uma tool futura = criar o arquivo em `tools/` e
incluí-la na lista, sem tocar no loop do chat.

## 3. Componentes

### 3.1 `chat.py` — entrypoint

Responsabilidades:

1. `load_dotenv()` no início do `main()`.
2. Validar `OPENAI_API_KEY`: se ausente, imprimir mensagem orientando a criar
   o `.env` a partir do `.env.example` e encerrar com `sys.exit(1)` (RN-07).
3. Criar o agente via `agent_factory.create_agent()`.
4. Loop REPL:
   - `input("Você: ")`;
   - `sair` / `exit` / `quit` (case-insensitive) ou linha vazia de encerramento → break;
   - chamar `agent(mensagem)` e imprimir a resposta completa (RN-09);
   - capturar `KeyboardInterrupt` e `EOFError` para encerrar graciosamente (RN-04);
   - capturar exceções da chamada ao agente e exibir mensagem amigável,
     sem derrubar o loop (erro de rede, rate limit etc.).

### 3.2 `agent_factory.py` — criação do agente

```python
def create_agent(tools: list | None = None) -> Agent
```

- **Modelo**: `OpenAIModel` de `strands.models.openai`, com
  `model_id=os.getenv("MODEL_ID", "gpt-4o-mini")` e
  `client_args={"api_key": os.environ["OPENAI_API_KEY"]}`.
- **Tools**: `tools or [current_datetime]` — lista injetável (RN-10, RN-11).
- **Memória**: `FileSessionManager` do Strands
  (`strands.session.FileSessionManager`), apontando
  para `./sessions/` (RN-03).
- **Sessão limpa por execução**: na criação do agente, remover/ignorar o estado
  anterior — usar `session_id` único por execução (ex.: timestamp/uuid) ou
  limpar o diretório `sessions/` no startup (CA-09).
- `system_prompt` simples (ex.: "Você é um assistente prestativo. Responda em
  português."), configurável via `SYSTEM_PROMPT` no `.env` (opcional).

### 3.3 `tools/datetime_tool.py` — tool de data/hora

```python
from strands import tool
from datetime import datetime

@tool
def current_datetime() -> str:
    """Retorna a data e hora atuais do sistema local."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

O decorator `@tool` do Strands gera o spec automaticamente a partir da
assinatura + docstring. Sem parâmetros — o modelo chama quando precisar da
data/hora atual.

## 4. Configuração (`.env`)

`.env.example` versionado:

```env
# Obrigatória
OPENAI_API_KEY=sk-...

# Opcionais
MODEL_ID=gpt-4o-mini
SYSTEM_PROMPT=Você é um assistente prestativo. Responda em português.
SESSIONS_DIR=sessions
```

Carregamento com `python-dotenv`. `.env` e `sessions/` listados no `.gitignore`.

## 5. Dependências (`requirements.txt`)

```
strands-agents
openai
python-dotenv
```

> Verificado na implementação (`strands-agents 1.64.0`): o provider OpenAI usa
> `strands.models.openai.OpenAIModel` e exige apenas o pacote `openai`.
> A persistência de sessão usa `strands.session.FileSessionManager`
> (parâmetro `session_manager` do `Agent`).

## 6. Fluxo de execução

```
main()
 ├─ load_dotenv()
 ├─ valida OPENAI_API_KEY ──ausente──▶ mensagem de erro + exit(1)
 ├─ create_agent()
 │    ├─ limpa/isola sessão anterior em sessions/
 │    ├─ OpenAIModel(MODEL_ID)
 │    └─ Agent(model, tools=[current_datetime], session_manager=FileSessionManager)
 └─ loop:
      ├─ input() ──sair/exit/quit/Ctrl+C──▶ encerra graciosamente
      └─ agent(msg) → print(resposta)
                      └── erro de API → mensagem amigável, continua o loop
```

## 7. Tratamento de erros

| Cenário | Comportamento |
|---|---|
| `OPENAI_API_KEY` ausente | Mensagem orientando a criar `.env` + `exit(1)` (RN-07, CA-05) |
| Chave inválida / erro de API | Mensagem amigável no loop; programa continua |
| `Ctrl+C` / `Ctrl+D` | Encerra com mensagem de despedida, sem traceback (CA-04) |
| Falha ao gravar `sessions/` | Log de aviso; conversa continua em memória |

## 8. Rastreabilidade

| Regra | Onde é atendida |
|---|---|
| RN-01 (execução local) | `python chat.py` |
| RN-02 (loop) | `chat.py` REPL |
| RN-03 (memória em arquivo) | `FileSessionManager` → `sessions/` |
| RN-04 (encerramento) | `chat.py`: comandos de saída + `KeyboardInterrupt` |
| RN-05 (modelo configurável) | `MODEL_ID` no `.env` |
| RN-06 (`.env` + chave) | `python-dotenv`, `OPENAI_API_KEY`, `.env.example`, `.gitignore` |
| RN-07 (erro de credencial) | validação no startup + mensagens amigáveis |
| RN-08 (deps) | `requirements.txt` |
| RN-09 (resposta completa) | `print(agent(msg))` — modo padrão do Strands |
| RN-10 (extensibilidade) | `create_agent(tools=...)` + diretório `tools/` |
| RN-11 (tool data/hora) | `tools/datetime_tool.py` |
