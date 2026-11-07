# Plano de Implementação — RF-01 Chat interativo (Strands + OpenAI)

Base: `RF01-chat-interativo.md` (requisito) + `RF01-design.md` (design).

## 1. Agentes e papéis

| Agente | Papel | Responsabilidade |
|---|---|---|
| **Agente Implementador** | Dev | Escrever código e arquivos de configuração conforme o design |
| **Agente Revisor** | Review | Conferir conformidade código × requisito × design (checklist RN/CA) |
| **Agente QA** | Testes | Executar a aplicação e validar critérios de aceite CA-01 a CA-09 |
| **Tech Lead** | Orquestração/acompanhamento | Sequenciar tarefas, aprovar entregas, registrar status e desbloquear dependências |

Restrição: o Agente QA precisa de uma `OPENAI_API_KEY` real no `.env` — dependência do usuário (ver §6).

## 2. Tarefas de implementação

### Fase 1 — Estrutura do projeto (Implementador)

| # | Tarefa | Entrega | RNs |
|---|---|---|---|
| 1.1 | Criar estrutura: `tools/`, `sessions/` (via `.gitkeep` ou em runtime) | Diretórios | — |
| 1.2 | Criar `.gitignore` (`.env`, `sessions/`, `__pycache__/`, `.venv/`) | `.gitignore` | RN-06 |
| 1.3 | Criar `.env.example` com `OPENAI_API_KEY`, `MODEL_ID`, `SYSTEM_PROMPT`, `SESSIONS_DIR` | `.env.example` | RN-05, RN-06 |
| 1.4 | Criar `requirements.txt` (`strands-agents`, `openai`, `python-dotenv`) — validar se provider OpenAI exige extra | `requirements.txt` | RN-08 |

### Fase 2 — Código (Implementador)

| # | Tarefa | Entrega | RNs |
|---|---|---|---|
| 2.1 | Implementar `tools/datetime_tool.py` com `@tool current_datetime()` | `tools/datetime_tool.py` | RN-11 |
| 2.2 | Implementar `agent_factory.py`: `OpenAIModel` + `FileSessionManager` + sessão limpa por execução + `create_agent(tools=...)` injetável | `agent_factory.py` | RN-03, RN-05, RN-10 |
| 2.3 | Implementar `chat.py`: `load_dotenv()`, validação de `OPENAI_API_KEY`, loop REPL, comandos de saída, `KeyboardInterrupt`/`EOFError`, tratamento amigável de erros de API | `chat.py` | RN-01, RN-02, RN-04, RN-07, RN-09 |

### Fase 3 — Revisão (Revisor)

| # | Tarefa | Entrega |
|---|---|---|
| 3.1 | Checklist de conformidade: cada RN-01..RN-11 mapeada ao código | Checklist aprovado/reprovado por item |
| 3.2 | Verificar estilo/simplicidade: código compacto, sem over-engineering, sem segredos em código | Aprovação ou lista de ajustes |
| 3.3 | Correções do review (Implementador) | Código ajustado |

### Fase 4 — Validação (QA)

| # | Tarefa | Critério validado |
|---|---|---|
| 4.1 | `pip install -r requirements.txt` em ambiente limpo (`.venv`) | RN-08 |
| 4.2 | Executar sem `.env`/sem chave → mensagem clara + encerra | CA-05, RN-07 |
| 4.3 | Executar com `.env` válido → prompt aparece | CA-01 |
| 4.4 | Enviar 2+ mensagens → respostas completas no terminal | CA-02, CA-07, RN-09 |
| 4.5 | Perguntar "qual foi minha primeira mensagem?" | CA-03 + arquivo em `sessions/` |
| 4.6 | Perguntar "que horas são?" / "que dia é hoje?" | CA-08 (tool `current_datetime`) |
| 4.7 | `sair`, `exit`, `quit` e Ctrl+C → encerra sem erro | CA-04 |
| 4.8 | Reexecutar → sessão nova, sem memória anterior | CA-09 |
| 4.9 | Trocar `MODEL_ID` no `.env` → funciona sem mudar código | CA-06 |

### Fase 5 — Fechamento (Tech Lead)

| # | Tarefa | Entrega |
|---|---|---|
| 5.1 | Registrar resultado do QA e lições no plano (§4) | Status final |
| 5.2 | Confirmar `.env` fora do versionamento | — |

## 3. Sequência e dependências

```
Fase 1 ──▶ Fase 2 ──▶ Fase 3 ──▶ Fase 4 ──▶ Fase 5
              ▲          │          │
              └──── correções ◄──────┘
```

- 2.x podem ser escritas em uma única sessão (arquivos independentes);
- Fase 4 depende da `OPENAI_API_KEY` do usuário — sem ela, QA fica limitado a 4.1, 4.2 e compilação (`python -m compileall`).

## 4. Acompanhamento

### Status das tarefas

| Tarefa | Agente | Status |
|---|---|---|
| 1.1–1.4 Estrutura | Implementador | Concluído |
| 2.1 Tool datetime | Implementador | Concluído |
| 2.2 agent_factory | Implementador | Concluído |
| 2.3 chat.py | Implementador | Concluído |
| 3.1–3.3 Review | Revisor | Pendente |
| 4.1–4.9 QA | QA | Pendente (aguarda chave) |
| 5.x Fechamento | Tech Lead | Pendente |

### Checkpoints

- **CP-1** (fim Fase 2): código completo + compila sem erros → libera review.
- **CP-2** (fim Fase 3): checklist RN aprovado → libera QA.
- **CP-3** (fim Fase 4): CA-01..CA-09 validados → requisito concluído.

### Definição de pronto (DoD)

- Todos os CAs (01–09) validados pelo QA;
- Nenhum segredo versionado (`.env` no `.gitignore`, sem chave em código);
- `pip install -r requirements.txt && python chat.py` funciona do zero.

## 5. Riscos

| Risco | Mitigação |
|---|---|
| `OPENAI_API_KEY` não disponível para QA | Validar o que der sem chave (4.1, 4.2, compilação); marcar QA como bloqueado parcial |
| API do Strands diferir do design (nomes de classes/extras de instalação) | Implementador consulta docs da versão instalada; Revisor confere imports em runtime |
| ~~`FileSessionManager` não existir com esse nome/assinatura~~ | **Resolvido**: SDK 1.64 usa `strands.session.FileSessionManager` via `session_manager=` — código ajustado e validado |

## 6. Dependência do usuário

- Criar `.env` a partir do `.env.example` com `OPENAI_API_KEY` válida antes do QA (ou fornecer a chave para o ambiente).
