# RF-01 — Chat interativo via terminal com agente Strands + OpenAI

## 1. Identificação

| Campo       | Valor                                   |
|-------------|-----------------------------------------|
| ID          | RF-01                                   |
| Nome        | Chat interativo via linha de comando    |
| Prioridade  | Alta                                    |
| Atores      | Usuário                                 |

## 2. Descrição

O sistema deve fornecer um **chat interativo executado via linha de comando** (CMD/terminal),
implementado em **Python**, rodando **localmente** na máquina do usuário.

O agente deve ser construído com o **Strands Agents SDK** (AWS) como framework de agente,
utilizando **OpenAI** como provedor do modelo (modelo default: `gpt-4o-mini`,
configurável via `.env`). Todas as configurações sensíveis devem ser lidas de um
arquivo **`.env`**.

O agente é deliberadamente simples: conversação com **memória de sessão persistida em
arquivo local** (válida apenas durante a execução — cada execução inicia uma sessão limpa)
e **uma tool de data/hora atual**.

## 3. Regras de negócio

| ID    | Regra |
|-------|-------|
| RN-01 | A execução deve ser 100% local, iniciada com um comando simples (ex.: `python chat.py`). |
| RN-02 | O chat deve operar em loop: o usuário digita uma mensagem, o agente responde, e o ciclo se repete até o encerramento. |
| RN-03 | O agente deve manter o histórico da conversa durante a sessão, **persistido em arquivo local** (ex.: `sessions/`). O histórico vale apenas durante a execução — cada nova execução inicia com sessão limpa. |
| RN-04 | O chat deve encerrar graciosamente ao digitar `sair`, `exit` ou `quit` (case-insensitive) ou ao pressionar Ctrl+C. |
| RN-05 | O provider é **OpenAI fixo**. O modelo deve ser configurável via variável `MODEL_ID` no `.env`, com `gpt-4o-mini` como default. |
| RN-06 | Autenticação via **`OPENAI_API_KEY`** definida no arquivo `.env`, carregada com `python-dotenv`. O `.env` não deve ser versionado (listar no `.gitignore`) e deve existir um `.env.example` documentando as variáveis. |
| RN-07 | Se `OPENAI_API_KEY` estiver ausente ou inválida, o sistema deve exibir uma mensagem de erro clara orientando o usuário (criar/preencher o `.env`), em vez de um traceback bruto. |
| RN-08 | As dependências devem ser instaláveis via `pip install -r requirements.txt`. |
| RN-09 | As respostas devem ser exibidas **completas** (sem streaming token a token na v1). |
| RN-10 | A inicialização do agente deve ser estruturada de forma a **facilitar a adição de novas tools no futuro** (ex.: criação do agente isolada em função/módulo que aceite uma lista de tools), sem exigir redesign da aplicação. |
| RN-11 | O agente deve possuir uma **tool `current_datetime`** que retorna a data e hora atuais do sistema, permitindo responder perguntas como "que horas são?" ou "que dia é hoje?". |

## 4. Critérios de aceite

| ID    | Critério |
|-------|----------|
| CA-01 | Ao executar o script, o terminal exibe um prompt aguardando a entrada do usuário. |
| CA-02 | Para cada mensagem enviada, a resposta do modelo é exibida no terminal. |
| CA-03 | O agente demonstra memória da sessão (ex.: ao perguntar "qual foi minha primeira mensagem?", responde corretamente) e o histórico é gravado em arquivo local. |
| CA-04 | Digitar `sair`/`exit`/`quit` ou Ctrl+C encerra o programa sem erro. |
| CA-05 | Sem `OPENAI_API_KEY` válida no `.env`, o programa exibe mensagem de erro explicativa e encerra. |
| CA-06 | O modelo utilizado pode ser trocado editando `MODEL_ID` no `.env`, sem alterar o código-fonte. |
| CA-07 | Executando com as configurações default, o agente responde usando OpenAI (`gpt-4o-mini`). |
| CA-08 | Ao perguntar a data ou hora atual, o agente utiliza a tool `current_datetime` e responde com o valor real do sistema. |
| CA-09 | Ao encerrar e executar novamente, o agente inicia uma sessão nova (sem lembrar da conversa anterior). |

## 5. Fora de escopo (v1)

- Interface gráfica, web ou mobile
- Restauração do histórico entre execuções (a memória em arquivo vale apenas durante a execução — ver RN-03)
- Tools além de `current_datetime` (porém o design deve permitir adicioná-las depois — ver RN-10)
- Streaming de resposta token a token (avaliar em versão futura)
- Suporte a outros providers de modelo (ex.: AWS Bedrock)
- Multiagente / orquestração complexa

## 6. Pré-condições e dependências

- Python instalado localmente (versão compatível com `strands-agents`, recomendado 3.10+)
- Chave de API válida da OpenAI definida em `OPENAI_API_KEY` no arquivo `.env`

## 7. Notas de refinamento

- Texto original mencionava "OpenAI e AWS Strands". Confirmado: **provider OpenAI fixo** (suporte a Bedrock fica fora de escopo).
- Defaults confirmados: modelo `gpt-4o-mini`, configurável via `MODEL_ID` no `.env`.
- Memória de sessão **em arquivo local**, válida apenas durante a execução (cada run inicia limpa).
- Tool `current_datetime` incluída no escopo da v1 (RN-11).
- Decisão de UX: resposta completa no terminal (sem streaming) na v1.
- RN-10 mantida para garantir que novas tools possam ser plugadas sem refatoração estrutural.
