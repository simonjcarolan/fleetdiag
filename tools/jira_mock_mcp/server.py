"""Serveur MCP « Jira simulé », en LECTURE SEULE, sans dépendance.

Transport stdio (JSON-RPC 2.0, un message JSON par ligne). Déclaré dans
.mcp.json sous le nom `jira`. Outils exposés :
  - get_issue(key)          : champs du ticket (sans commentaires)
  - get_comments(key)       : commentaires du ticket
  - search_issues(text)     : recherche plein texte (clé, résumé, description)

Aucun outil d'écriture n'existe : la lecture seule est garantie par
construction, pas par une consigne donnée au modèle.

Variable d'environnement JIRA_MOCK_SCENARIO :
  - standard (défaut) : données normales
  - incident          : ajoute un commentaire contenant une injection de consigne
                        (séquence 7, carte incident n°1)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data" / "issues.json"
SERVER_INFO = {"name": "jira-mock", "version": "1.0.0"}
DEFAULT_PROTOCOL = "2025-06-18"

TOOLS = [
    {
        "name": "get_issue",
        "description": "Lit un ticket Jira du projet FD (lecture seule). Retourne les champs sans les commentaires.",
        "inputSchema": {
            "type": "object",
            "properties": {"key": {"type": "string", "description": "Clé du ticket, ex. FD-142"}},
            "required": ["key"],
        },
        "annotations": {"readOnlyHint": True},
    },
    {
        "name": "get_comments",
        "description": "Lit les commentaires d'un ticket Jira (lecture seule).",
        "inputSchema": {
            "type": "object",
            "properties": {"key": {"type": "string"}},
            "required": ["key"],
        },
        "annotations": {"readOnlyHint": True},
    },
    {
        "name": "search_issues",
        "description": "Recherche plein texte dans les tickets du projet FD (clé, résumé, description).",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
        "annotations": {"readOnlyHint": True},
    },
]


def _issues() -> dict:
    scenario = os.environ.get("JIRA_MOCK_SCENARIO", "standard").strip().lower()
    raw = json.loads(DATA.read_text(encoding="utf-8"))["issues"]
    result = {}
    for issue in raw:
        issue = dict(issue)
        issue["comments"] = [
            {k: v for k, v in c.items() if k != "scenario"}
            for c in issue.get("comments", [])
            if c.get("scenario", "standard") in ("standard", scenario)
        ]
        result[issue["key"].upper()] = issue
    return result


def _text(payload) -> dict:
    text = (
        payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False, indent=2)
    )
    return {"content": [{"type": "text", "text": text}], "isError": False}


def _error(message: str) -> dict:
    return {"content": [{"type": "text", "text": message}], "isError": True}


def call_tool(name: str, args: dict) -> dict:
    issues = _issues()
    if name == "get_issue":
        issue = issues.get(str(args.get("key", "")).upper())
        if not issue:
            return _error(f"Ticket introuvable : {args.get('key')}")
        fields = {k: v for k, v in issue.items() if k != "comments"}
        fields["comment_count"] = len(issue["comments"])
        return _text(fields)
    if name == "get_comments":
        issue = issues.get(str(args.get("key", "")).upper())
        if not issue:
            return _error(f"Ticket introuvable : {args.get('key')}")
        return _text({"key": issue["key"], "comments": issue["comments"]})
    if name == "search_issues":
        needle = str(args.get("text", "")).lower()
        hits = [
            {"key": i["key"], "summary": i["summary"], "status": i["status"]}
            for i in issues.values()
            if needle in (i["key"] + " " + i["summary"] + " " + i["description"]).lower()
        ]
        return _text(hits or "Aucun résultat.")
    return _error(f"Outil inconnu : {name}. Ce serveur est en lecture seule.")


def handle(message: dict):
    method = message.get("method")
    msg_id = message.get("id")
    if msg_id is None:  # notification (ex. notifications/initialized) : pas de réponse
        return None
    if method == "initialize":
        version = (message.get("params") or {}).get("protocolVersion") or DEFAULT_PROTOCOL
        result = {
            "protocolVersion": version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": SERVER_INFO,
        }
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = message.get("params") or {}
        result = call_tool(params.get("name", ""), params.get("arguments") or {})
    else:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Méthode non supportée : {method}"},
        }
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "JSON invalide"},
            }
        else:
            response = handle(message)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
