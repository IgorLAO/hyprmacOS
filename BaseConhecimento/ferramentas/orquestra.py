#!/usr/bin/env python3
"""Orquestrador de agentes autônomos usando FreeLLM (tool calling).

Sub‑comandos:
  adicionar <arquivo.json>
  rodar [-n N] [--max-passos 40] [--timeout 900]
  estado [ID]
  revisar ID aprovado|rejeitado [--nota TEXTO]
  integrar ID
"""

import argparse
import concurrent.futures
import hashlib
import json
import re
import os
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ------------------------------------------------------------
# caminho da raiz (3 níveis acima deste script) e inclusão no PYTHONPATH
# ------------------------------------------------------------
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
from agentes import chave, URL  # noqa: E402

# ------------------------------------------------------------
# Banco SQLite (fila.db) e criação da tabela se necessário
# ------------------------------------------------------------
DB_PATH = RAIZ / ".agentes" / "fila.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS tarefas (
    id TEXT PRIMARY KEY,
    objetivo TEXT,
    criterios TEXT,
    papel TEXT,
    permitidos TEXT,   -- JSON list
    contexto TEXT,     -- JSON list
    depende TEXT,      -- JSON list
    estado TEXT,
    tentativas INTEGER,
    modelo TEXT,
    relatorio TEXT,    -- JSON
    notas TEXT,        -- JSON list (texto)
    criado TEXT,
    atualizado TEXT
);
"""

_LOCK = threading.Lock()


def _conn():
    conn = sqlite3.connect(str(DB_PATH), timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    with _conn() as c:
        c.execute(_TABLE_SQL)


_init_db()


# ------------------------------------------------------------
# Utilitários gerais
# ------------------------------------------------------------


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for blk in iter(lambda: f.read(8192), b""):
            h.update(blk)
    return h.hexdigest()


def _iso_path(tid: str) -> Path:
    return RAIZ / ".agentes" / "iso" / tid


def _base_json_path(tid: str) -> Path:
    return _iso_path(tid) / ".base.json"


def _transcript_path(tid: str) -> Path:
    return RAIZ / ".agentes" / tid / "transcricao.jsonl"


def _load_json(text: str | None) -> Any:
    if not text:
        return None
    return json.loads(text)


def _dump_json(val: Any) -> str:
    return json.dumps(val, ensure_ascii=False)


# ------------------------------------------------------------
# Sub‑comando: adicionar
# ------------------------------------------------------------


def cmd_adicionar(arq: Path):
    dados = json.loads(arq.read_text(encoding="utf-8"))
    with _conn() as c:
        for t in dados:
            cur = c.execute("SELECT 1 FROM tarefas WHERE id=?", (t["id"],)).fetchone()
            if cur:
                print(f"{t['id']}\tjá existe")
                continue
            now = _now()
            c.execute(
                """
                INSERT INTO tarefas (id, objetivo, criterios, papel, permitidos,
                                     contexto, depende, estado, tentativas,
                                     modelo, relatorio, notas, criado, atualizado)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    t["id"],
                    t["objetivo"],
                    t.get("criterios", ""),
                    t["papel"],
                    _dump_json(t.get("permitidos", [])),
                    _dump_json(t.get("contexto", [])),
                    _dump_json(t.get("depende", [])),
                    "pendente",
                    0,
                    "",
                    None,
                    _dump_json([]),
                    now,
                    now,
                ),
            )
            print(f"{t['id']}\tadicionado")


# ------------------------------------------------------------
# Ferramentas expostas ao modelo
# ------------------------------------------------------------


def _tool_schema(name: str, description: str, params: Dict) -> Dict:
    return {"type": "function", "function": {"name": name, "description": description, "parameters": params}}


def _definir_ferramentas(permitidos: List[str]) -> List[Dict]:
    # schemas simplificados
    return [
        _tool_schema(
            "ler",
            "Lê linhas de um arquivo dentro do isolamento.",
            {
                "type": "object",
                "properties": {
                    "caminho": {"type": "string"},
                    "inicio": {"type": "integer", "minimum": 1},
                    "fim": {"type": "integer", "minimum": 1},
                },
                "required": ["caminho"],
            },
        ),
        _tool_schema(
            "listar",
            "Lista nomes de arquivos/diretórios.",
            {
                "type": "object",
                "properties": {"caminho": {"type": "string", "default": "."}},
                "required": [],
            },
        ),
        _tool_schema(
            "buscar",
            "Busca regex em arquivos.",
            {
                "type": "object",
                "properties": {"padrao": {"type": "string"}, "caminho": {"type": "string", "default": "."}},
                "required": ["padrao"],
            },
        ),
        _tool_schema(
            "escrever",
            "Sobrescreve um arquivo permitido.",
            {
                "type": "object",
                "properties": {"caminho": {"type": "string"}, "conteudo": {"type": "string"}},
                "required": ["caminho", "conteudo"],
            },
        ),
        _tool_schema(
            "substituir",
            "Substitui uma única ocorrência em arquivo permitido.",
            {
                "type": "object",
                "properties": {"caminho": {"type": "string"}, "antigo": {"type": "string"}, "novo": {"type": "string"}},
                "required": ["caminho", "antigo", "novo"],
            },
        ),
        _tool_schema(
            "executar",
            "Executa um comando bash no diretório de trabalho (sandbox: só o diretório de trabalho e /tmp são graváveis, sem rede, 120 s). Use para rodar testes, py_compile, scripts de verificação, grep etc. Para criar/editar arquivos do projeto use escrever/substituir.",
            {
                "type": "object",
                "properties": {"comando": {"type": "string"}},
                "required": ["comando"],
            },
        ),
        _tool_schema(
            "concluir",
            "Finaliza a tarefa.",
            {
                "type": "object",
                "properties": {
                    "relatorio": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string"},
                            "status": {"type": "string", "enum": ["completed", "blocked"]},
                            "summary": {"type": "string"},
                            "changed_files": {"type": "array", "items": {"type": "string"}},
                            "tests": {"type": "object", "properties": {"passed": {"type": "integer"}, "failed": {"type": "integer"}}},
                            "evidence": {"type": "array", "items": {"type": "string"}},
                            "confidence": {"type": "number"},
                            "issues": {"type": "string"},
                            "next_actions": {"type": "string"},
                        },
                        "required": ["task_id", "status", "summary"],
                    }
                },
                "required": ["relatorio"],
            },
        ),
    ]


def _norm_path(base: Path, caminho: str) -> Path:
    """Normaliza caminho dentro do isolamento; permite leitura de BaseConhecimento/."""
    if caminho.startswith("BaseConhecimento/"):
        return RAIZ / caminho
    p = (base / caminho).resolve()
    if not str(p).startswith(str(base)):
        raise ValueError("caminho fora do isolamento")
    return p


def _executar_ferramenta(nome: str, args: Dict, iso_dir: Path, permitidos: List[str]) -> Tuple[str, Any]:
    """Executa a ferramenta solicitada e devolve (resultado_texto, dados_brutos)."""
    if nome == "ler":
        caminho = _norm_path(iso_dir, args["caminho"])
        ini = int(args.get("inicio", 1))
        fim = int(args.get("fim", ini + 299))
        linhas = caminho.read_text(encoding="utf-8", errors="replace").splitlines()
        trecho = "\n".join(f"{i}\t{linhas[i - 1]}" for i in range(ini, min(fim, len(linhas)) + 1))
        return (trecho, None)

    if nome == "listar":
        caminho = _norm_path(iso_dir, args.get("caminho", "."))
        nomes = [e.name for e in caminho.iterdir()]
        return (", ".join(nomes), None)

    if nome == "buscar":
        caminho = _norm_path(iso_dir, args.get("caminho", "."))
        padrao = args["padrao"]
        import re

        matches = []
        for root, _, files in os.walk(caminho):
            if ".git" in root or "__pycache__" in root:
                continue
            for f in files:
                fp = Path(root) / f
                try:
                    txt = fp.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                for m in re.finditer(padrao, txt):
                    line_no = txt[: m.start()].count("\n") + 1
                    matches.append(f"{fp.relative_to(iso_dir)}:{line_no}:{m.group(0)}")
                    if len(matches) >= 60:
                        break
                if len(matches) >= 60:
                    break
            if len(matches) >= 60:
                break
        return ("\n".join(matches), None)

    if nome in ("escrever", "substituir"):
        caminho = _norm_path(iso_dir, args["caminho"])
        rel = os.path.relpath(caminho, iso_dir)
        if rel not in permitidos:
            raise ValueError(f"arquivo {rel} não está entre os permitidos")
        if nome == "escrever":
            caminho.write_text(args["conteudo"], encoding="utf-8")
            return ("escrito", None)
        else:
            antigo = args["antigo"]
            novo = args["novo"]
            txt = caminho.read_text(encoding="utf-8", errors="replace")
            if txt.count(antigo) != 1:
                raise ValueError("ocorrência única requerida")
            caminho.write_text(txt.replace(antigo, novo, 1), encoding="utf-8")
            return ("substituído", None)

    if nome == "executar":
        # qualquer comando, mas preso: sistema somente leitura, escrita só no isolamento e
        # num /tmp descartável, sem rede, até 8 GB de memória e 120 s (a máquina fica sozinha)
        cmd = args["comando"]
        iso = str(iso_dir)
        sandbox = ["bwrap", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc",
                   "--tmpfs", "/tmp", "--bind", iso, iso, "--chdir", iso,
                   "--unshare-net", "--die-with-parent",
                   "prlimit", f"--as={8 << 30}", "--", "bash", "-c", cmd]
        try:
            proc = subprocess.run(sandbox, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  timeout=120, text=True, errors="replace")
            out = proc.stdout
            if proc.returncode:
                out += f"\n[código de saída {proc.returncode}]"
        except subprocess.TimeoutExpired:
            out = "[tempo esgotado: 120 s]"
        return (out[-4000:] if len(out) > 4000 else out, None)

    if nome == "concluir":
        rel = args["relatorio"]
        return ("concluído", rel)

    raise ValueError(f"ferramenta desconhecida: {nome}")


# ------------------------------------------------------------
# Comunicação com FreeLLM (OpenAI‑compatible)
# ------------------------------------------------------------


MODELOS = os.getenv("FREELLM_MODELOS", "auto").split(",")


def _compactar(mensagens: List[Dict], limite: int = 60000) -> List[Dict]:
    """Cópia do histórico que cabe no contexto: encurta primeiro os resultados de
    ferramentas mais antigos, preservando sistema, enunciado e as 6 últimas mensagens."""
    msgs = [dict(m) for m in mensagens]
    tamanho = lambda: sum(len(json.dumps(m, ensure_ascii=False)) for m in msgs)
    for corte in (2000, 600, 150):
        if tamanho() <= limite:
            break
        for m in msgs[2:-6]:
            c = m.get("content")
            if isinstance(c, str) and len(c) > corte:
                m["content"] = c[:corte] + f"\n[… {len(c) - corte} caracteres omitidos]"
    return msgs


def _chamar_modelo(modelo: str, mensagens: List[Dict], ferramentas: List[Dict]) -> Dict:
    payload = {
        "model": modelo,
        "messages": _compactar(mensagens),
        "temperature": 0.2,
        "max_tokens": 8000,
        "tools": ferramentas,
        "tool_choice": "auto",
    }
    req = urllib.request.Request(
        URL + "/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {chave()}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.load(resp)


# ------------------------------------------------------------
# Execução de uma tarefa individual
# ------------------------------------------------------------


def _executar_tarefa(row: sqlite3.Row, max_passos: int, timeout_total: int) -> Tuple[str, str, int, float]:
    tid = row["id"]
    # reserva
    with _conn() as c:
        c.execute("BEGIN IMMEDIATE")
        cur = c.execute("SELECT estado FROM tarefas WHERE id=?", (tid,)).fetchone()
        if not cur or cur[0] != "pendente":
            c.execute("ROLLBACK")
            return (tid, "skip", 0, 0.0)
        c.execute(
            "UPDATE tarefas SET estado='executando', atualizado=? WHERE id=?",
            (_now(), tid),
        )
        c.execute("COMMIT")

    iso_dir = _iso_path(tid)
    iso_dir.mkdir(parents=True, exist_ok=True)

    # copiar estrutura
    for d in ("shell", "tests", "waybar", "scripts", "gtk", "hypr"):
        src = RAIZ / d
        if src.is_dir():
            shutil.copytree(src, iso_dir / d, dirs_exist_ok=True)
    for md in RAIZ.glob("*.md"):
        if md.is_file():
            shutil.copy2(md, iso_dir / md.name)

    # grava .base.json
    permitidos = _load_json(row["permitidos"]) or []
    base = {}
    for rel in permitidos:
        base[rel] = _sha256(RAIZ / rel)
    _base_json_path(tid).write_text(_dump_json(base), encoding="utf-8")

    # mensagens iniciais
    sistema = f"{row['papel']}\nTrabalhe apenas nos arquivos permitidos, leia antes de editar, rode testes pertinentes, corrija erros e termine chamando `concluir`."
    usuario = f"## Objetivo\n{row['objetivo']}\n"
    if row["criterios"]:
        usuario += f"\n## Critérios\n{row['criterios']}\n"
    if row["contexto"]:
        usuario += f"\n## Contexto sugerido\n{row['contexto']}\n"
    if row["notas"]:
        usuario += f"\n## Notas de revisões anteriores\n{row['notas']}\n"

    mensagens = [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}]
    ferramentas = _definir_ferramentas(permitidos)

    # grava transcrição inicial
    _transcript_path(tid).parent.mkdir(parents=True, exist_ok=True)
    with _transcript_path(tid).open("a", encoding="utf-8") as tr:
        for msg in mensagens:
            tr.write(json.dumps(msg, ensure_ascii=False) + "\n")

    passos = 0
    inicio_total = time.monotonic()
    modelo_atual = MODELOS[0] if MODELOS else "auto"
    erros_http = 0
    failed_due_to_error = False
    recent_errors = []
    empty_response_count = 0  # contador de respostas vazias consecutivas
    backoff_sequence = [5, 10, 20, 40, 60]
    backoff_index = 0

    while passos < max_passos and (time.monotonic() - inicio_total) < timeout_total:
        try:
            resp = _chamar_modelo(modelo_atual, mensagens, ferramentas)
        except Exception as e:
            # Processar exceção
            error_str = str(e)
            body = ""
            if isinstance(e, urllib.error.HTTPError):
                try:
                    body = e.read().decode('utf-8', errors='replace')[:500]
                except Exception:
                    body = "(unable to read body)"
                error_str = f"{str(e)} - Body: {body}"

            # Registrar erro na transcrição
            error_info = {"erro": error_str}
            _transcript_path(tid).parent.mkdir(parents=True, exist_ok=True)
            with _transcript_path(tid).open("a", encoding="utf-8") as tr:
                tr.write(json.dumps(error_info, ensure_ascii=False) + "\n")

            # Atualizar lista de erros recentes
            recent_errors.append(error_str)
            if len(recent_errors) > 3:
                recent_errors.pop(0)

            # Verificar se é erro retryable (429, 502, 503, URLError, TimeoutError)
            is_retryable = False
            wait_time = 0
            if isinstance(e, urllib.error.HTTPError):
                if e.code in (429, 502, 503):
                    is_retryable = True
                    # Tentar extrair "Soonest reset ~Ns" do body
                    match = re.search(r'Soonest reset ~(\d+)s', body)
                    if match:
                        wait_time = int(match.group(1)) + 2
                    else:
                        wait_time = backoff_sequence[min(backoff_index, len(backoff_sequence) - 1)]
                        backoff_index = min(backoff_index + 1, len(backoff_sequence) - 1)
                    erros_http += 1
                    if erros_http >= 3:
                        # Rotacionar modelo
                        try:
                            current_index = MODELOS.index(modelo_atual)
                        except ValueError:
                            current_index = 0
                        next_index = (current_index + 1) % len(MODELOS)
                        modelo_atual = MODELOS[next_index]
                        erros_http = 0
                        backoff_index = 0  # reset backoff ao trocar modelo
            elif isinstance(e, (urllib.error.URLError, TimeoutError)):
                is_retryable = True
                wait_time = backoff_sequence[min(backoff_index, len(backoff_sequence) - 1)]
                backoff_index = min(backoff_index + 1, len(backoff_sequence) - 1)

            if is_retryable:
                time.sleep(wait_time)
                continue  # NÃO incrementa passos
            else:
                # Erro não retryable: abortar imediatamente
                failed_due_to_error = True
                break

        # Sucesso na chamada - reset backoff
        backoff_index = 0

        choice = resp.get("choices", [{}])[0]
        msg = choice.get("message", {})
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        tool_calls = msg.get("tool_calls", [])

        # Verificar resposta vazia (content vazio/None e sem tool_calls)
        is_empty = (content is None or content == "") and not tool_calls

        if is_empty:
            empty_response_count += 1
            if empty_response_count <= 3:
                # Não conta como passo, não anexa ao histórico
                # Anexa mensagem user lembrando de usar ferramentas
                mensagens.append({
                    "role": "user",
                    "content": "Use as ferramentas fornecidas e finalize chamando `concluir`."
                })
                # Registra na transcrição que houve resposta vazia
                _transcript_path(tid).parent.mkdir(parents=True, exist_ok=True)
                with _transcript_path(tid).open("a", encoding="utf-8") as tr:
                    tr.write(json.dumps({"role": "assistant", "content": None, "empty": True}, ensure_ascii=False) + "\n")
                continue  # NÃO incrementa passos
            else:
                # Após 3 vazias seguidas, conta como passo e processa normalmente
                pass
        else:
            empty_response_count = 0  # reset contador em resposta válida

        # Resposta válida - conta como passo
        passos += 1
        if passos == int(max_passos * 0.8):
            mensagens.append({"role": "user", "content": (
                "Restam poucos passos. Pare de investigar: faça só o essencial que falta, "
                "valide uma vez e chame concluir com o relatório (status blocked se não deu).")})

        # histórico no formato OpenAI: a mensagem do assistente leva as tool_calls,
        # seguida de um resultado "tool" por chamada
        def _log(obj):
            with _transcript_path(tid).open("a", encoding="utf-8") as tr:
                if isinstance(obj.get("content"), str):
                    obj = {**obj, "content": obj["content"][:20000]}
                tr.write(json.dumps(obj, ensure_ascii=False) + "\n")
        _log({"role": role, "content": content, "tool_calls": tool_calls or None})

        if tool_calls:
            mensagens.append({"role": "assistant", "content": content or "", "tool_calls": tool_calls})
            for tc in tool_calls:
                func = tc.get("function", {})
                nome = func.get("name", "")
                # chamada idêntica já feita: não repete (modelos em laço gastavam 100+ passos)
                chave_call = nome + "\0" + (func.get("arguments") or "")
                vistos = _executar_tarefa.__dict__.setdefault("vistos", {}).setdefault(tid, {})
                if nome not in ("escrever", "substituir", "concluir") and chave_call in vistos:
                    vistos[chave_call][1] += 1
                    resultado, dados = ("[REPETIDA — você já fez exatamente esta chamada; o resultado "
                                        "foi o mesmo abaixo. Não repita: avance para o próximo passo ou "
                                        "chame concluir.]\n" + vistos[chave_call][0][:1500]), None
                else:
                    try:
                        args = json.loads(func.get("arguments") or "{}")
                        resultado, dados = _executar_ferramenta(nome, args, iso_dir, permitidos)
                    except Exception as exc:
                        resultado, dados = f"Erro em {nome}: {type(exc).__name__}: {exc}", None
                    if nome in ("escrever", "substituir"):
                        vistos.clear()      # arquivos mudaram: leituras e testes valem de novo
                    elif nome != "concluir":
                        vistos[chave_call] = [str(resultado), 0]
                if nome == "concluir" and isinstance(dados, dict):
                    _log({"role": "tool", "name": nome, "content": "concluído"})
                    _finalizar(tid, dados, iso_dir, permitidos)
                    estado = "falhou" if dados.get("status") == "blocked" else "entregue"
                    return (tid, estado, passos, round(time.monotonic() - inicio_total, 1))
                resultado = str(resultado)[:6000]
                mensagens.append({"role": "tool", "tool_call_id": tc.get("id", ""), "content": resultado})
                _log({"role": "tool", "name": nome, "content": resultado[:2000]})
        else:
            # modelo respondeu sem tool_calls
            if "concluir" in content.lower():
                # tentativa de extrair JSON manualmente
                try:
                    rel = json.loads(content)
                except Exception:
                    rel = {"task_id": tid, "status": "blocked", "summary": "Concluir chamado sem JSON válido"}
                # grava relatório e finaliza
                _finalizar(tid, rel, iso_dir, permitidos)
                dur = round(time.monotonic() - inicio_total, 1)
                return (tid, "entregue", passos, dur)
            else:
                # resposta de texto não vazio - adiciona ao histórico
                mensagens.append({"role": "assistant", "content": content})
                mensagens.append(
                    {
                        "role": "system",
                        "content": "Use as ferramentas fornecidas e finalize chamando `concluir`.",
                    }
                )
    # timeout ou passos excedidos
    if failed_due_to_error:
        dur = round(time.monotonic() - inicio_total, 1)
        return (tid, "falhou", passos, dur)
    else:
        rel_auto = {
            "task_id": tid,
            "status": "blocked",
            "summary": "Execução interrompida por timeout ou limite de passos.",
            "issues": "\n".join(recent_errors) if recent_errors else "",
        }
        _finalizar(tid, rel_auto, iso_dir, permitidos)
        dur = round(time.monotonic() - inicio_total, 1)
        return (tid, "falhou", passos, dur)


def _finalizar(tid: str, relatorio: Dict, iso_dir: Path, permitidos: List[str]):
    # calcula arquivos realmente modificados
    base = _load_json(_base_json_path(tid).read_text(encoding="utf-8"))
    mudancas = []
    for rel in permitidos:
        iso_fp = iso_dir / rel
        if not iso_fp.is_file():
            continue
        sha_iso = _sha256(iso_fp)
        sha_base = base.get(rel)
        if sha_iso != sha_base:
            mudancas.append(rel)
    relatorio["changed_files"] = mudancas

    with _conn() as c:
        c.execute(
            "UPDATE tarefas SET estado=?, relatorio=?, modelo=?, atualizado=? WHERE id=?",
            (
                "entregue" if relatorio.get("status") == "completed" else "falhou",
                _dump_json(relatorio),
                MODELOS[0] if MODELOS else "auto",
                _now(),
                tid,
            ),
        )


# ------------------------------------------------------------
# Sub‑comando: rodar
# ------------------------------------------------------------


def _liberar_travadas():
    with _conn() as c:
        c.execute(
            "UPDATE tarefas SET estado='pendente' WHERE estado='executando' AND datetime(atualizado) < datetime('now','-30 minutes')"
        )


def _dependencias_ok(dep_ids: List[str]) -> bool:
    if not dep_ids:
        return True
    with _conn() as c:
        placeholders = ",".join("?" for _ in dep_ids)
        cur = c.execute(
            f"SELECT id, estado FROM tarefas WHERE id IN ({placeholders})", dep_ids
        )
        estados = {row[0]: row[1] for row in cur.fetchall()}
    for d in dep_ids:
        if estados.get(d) not in ("aprovado", "integrado"):
            return False
    return True


def cmd_executar(n: int | None, max_passos: int, timeout: int):
    _liberar_travadas()
    with _conn() as c:
        c.row_factory = sqlite3.Row
        rows = c.execute("SELECT * FROM tarefas WHERE estado IN ('pendente','rejeitado')").fetchall()
    prontas = [r for r in rows if _dependencias_ok(_load_json(r["depende"]) or [])]
    if not prontas:
        return
    if n is None:
        cpu = os.cpu_count() or 1
        n = max(1, min(len(prontas), cpu // 4, 4))
    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as ex:
        futs = {
            ex.submit(_executar_tarefa, r, max_passos, timeout): r["id"] for r in prontas
        }
        for f in concurrent.futures.as_completed(futs):
            tid = futs[f]
            try:
                tid, estado, passos, secs = f.result()
                print(f"{tid}\t{estado}\t{passos}\t{secs}s")
            except Exception as e:
                print(f"{tid}\terro\t{e}")


# ------------------------------------------------------------
# Sub‑comando: estado
# ------------------------------------------------------------


def cmd_estado(tid: str | None):
    with _conn() as c:
        c.row_factory = sqlite3.Row
        if tid:
            row = c.execute("SELECT * FROM tarefas WHERE id=?", (tid,)).fetchone()
            if not row:
                print("tarefa não encontrada")
                return
            print(_dump_json(_load_json(row["relatorio"])))
        else:
            rows = c.execute("SELECT id, objetivo, estado, modelo FROM tarefas ORDER BY id").fetchall()
            for r in rows:
                print(f"{r['id']}\t{r['estado']}\t{r['modelo'] or ''}\t{r['objetivo'][:30]}")


# ------------------------------------------------------------
# Sub‑comando: revisar
# ------------------------------------------------------------


def cmd_revisar(tid: str, decisao: str, nota: str):
    with _conn() as c:
        row = c.execute("SELECT tentativas, notas FROM tarefas WHERE id=?", (tid,)).fetchone()
        if not row:
            print("tarefa não encontrada")
            return
        tentativas = row["tentativas"]
        notas = _load_json(row["notas"]) or []
        if decisao == "aprovado":
            novo_estado = "aprovado"
        else:
            notas.append(nota)
            if tentativas < 3:
                novo_estado = "pendente"
            else:
                novo_estado = "falhou"
        c.execute(
            "UPDATE tarefas SET estado=?, notas=?, atualizado=? WHERE id=?",
            (novo_estado, _dump_json(notas), _now(), tid),
        )
        print(f"{tid}\t{novo_estado}")


# ------------------------------------------------------------
# Sub‑comando: integrar
# ------------------------------------------------------------


def cmd_integrar(tid: str):
    with _conn() as c:
        row = c.execute("SELECT estado, permitidos FROM tarefas WHERE id=?", (tid,)).fetchone()
        if not row:
            print("tarefa não encontrada")
            return
        if row["estado"] != "aprovado":
            print("tarefa não está aprovada")
            return
        permitidos = _load_json(row["permitidos"]) or []
        iso_dir = _iso_path(tid)
        base = _load_json(_base_json_path(tid).read_text(encoding="utf-8"))
        conflitos = []
        for rel in permitidos:
            src = iso_dir / rel
            if not src.is_file():
                continue
            dst = RAIZ / rel
            sha_base = base.get(rel)
            sha_atual = _sha256(dst) if dst.is_file() else None
            if sha_base is not None and sha_atual != sha_base:
                conflitos.append(rel)
        if conflitos:
            print("Conflitos detectados, abortando:", ", ".join(conflitos))
            return
        for rel in permitidos:
            src = iso_dir / rel
            if not src.is_file():
                continue
            dst = RAIZ / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        c.execute("UPDATE tarefas SET estado='integrado', atualizado=? WHERE id=?", (_now(), tid))
        print(f"{tid}\tintegrado")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    add = sub.add_parser("adicionar")
    add.add_argument("arquivo", type=Path)

    run = sub.add_parser("rodar")
    run.add_argument("-n", type=int, default=None)
    run.add_argument("--max-passos", type=int, default=40)
    run.add_argument("--timeout", type=int, default=900)

    est = sub.add_parser("estado")
    est.add_argument("id", nargs="?")

    rev = sub.add_parser("revisar")
    rev.add_argument("id")
    rev.add_argument("decisao", choices=["aprovado", "rejeitado"])
    rev.add_argument("--nota", default="")

    intg = sub.add_parser("integrar")
    intg.add_argument("id")

    args = ap.parse_args()

    if args.cmd == "adicionar":
        cmd_adicionar(args.arquivo)
    elif args.cmd == "rodar":
        cmd_executar(args.n, args.max_passos, args.timeout)
    elif args.cmd == "estado":
        cmd_estado(args.id)
    elif args.cmd == "revisar":
        cmd_revisar(args.id, args.decisao, args.nota)
    elif args.cmd == "integrar":
        cmd_integrar(args.id)


if __name__ == "__main__":
    main()
